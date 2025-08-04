#include "peertalk_client.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>

namespace py = pybind11;

namespace pypeertalk
{

PeerTalkHeader get_peer_talk_header(uint8_t* buffer)
{
    uint32_t ns_error = buffer[0] << 24 | buffer[1] << 16 | buffer[2] << 8 | buffer[3];
    uint32_t frame_type = buffer[4] << 24 | buffer[5] << 16 | buffer[6] << 8 | buffer[7];
    uint32_t frame_tag = buffer[8] << 24 | buffer[9] << 16 | buffer[10] << 8 | buffer[11];
    uint32_t body_size = buffer[12] << 24 | buffer[13] << 16 | buffer[14] << 8 | buffer[15];
    return PeerTalkHeader{ns_error, frame_type, frame_tag, body_size};
}


void interruptable_sleep(double seconds)
{
    py::gil_scoped_release release; // Release the GIL for C++ execution

    auto start_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed_seconds;

    // Sleep in small increments and check for interrupts
    while (true)
    {
        elapsed_seconds = std::chrono::high_resolution_clock::now() - start_time;
        if (elapsed_seconds.count() >= seconds)
        {
            break; // Target sleep duration reached
        }

        // Calculate remaining time or a small chunk
        double remaining_seconds = seconds - elapsed_seconds.count();
        double sleep_chunk = std::min(remaining_seconds, 0.001); // Sleep for 1ms at a time

        std::this_thread::sleep_for(std::chrono::duration<double>(sleep_chunk));

        // Reacquire GIL temporarily to check for Python signals
        py::gil_scoped_acquire acquire;
        if (PyErr_CheckSignals() != 0)
        {
            // A Python error (like KeyboardInterrupt) is pending
            throw py::error_already_set(); // Re-raise the Python exception
        }
    }
}


std::vector<DeviceInfo> get_connected_devices()
{
    usbmuxd_device_info_t* device_info_list;
    int num_devices = usbmuxd_get_device_list( &device_info_list );
    std::vector<DeviceInfo> available_devices;

    for ( int dev_idx = 0; dev_idx < num_devices; dev_idx++ )
    {
        const auto &dev = device_info_list[ dev_idx ];
        if ( dev.conn_type != CONNECTION_TYPE_USB ) continue;

        DeviceInfo curr_dev_info(
            dev.product_id,
            std::string( dev.udid ),
            dev.handle
        );
        printf("Found device product_id %d, udid %s\n", curr_dev_info.product_id, curr_dev_info.udid.c_str());

        available_devices.push_back( curr_dev_info );
    }

    usbmuxd_device_list_free( &device_info_list );

    return available_devices;
}

PeerTalkClient::PeerTalkClient(const DeviceInfo &device, int port) : device_(device), port_(port)
{
    while(true)
    {
        if (connect_to_device_())
        {
            break;
        }
        printf("Failed to connect to device %s. Retrying...\n", device_.udid.c_str());
        // interruptable_sleep(1000);
        interruptable_sleep(1.0);
        // std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}

PeerTalkClient::~PeerTalkClient()
{
    is_connected_ = false;
    communication_thread_.join();
    usbmuxd_disconnect(socket_handle_);
    printf("Disconnected from device %s\n", device_.udid.c_str());
}

bool PeerTalkClient::connect_to_device_()
{
    // Ensure we are indeed connected before continuing.
    int socket_no = usbmuxd_connect( device_.handle, port_ );
    if ( socket_no < 0 )
    { return false; }

    // We are successfully connected, start runloop.
    is_connected_ = true;
    socket_handle_ = socket_no;

    // Create thread that is going to execute runloop.
    communication_thread_ = std::thread( &PeerTalkClient::run_communication_thread_, this );
    return true;
}

pybind11::bytes PeerTalkClient::get_latest_message(int timeout_ms)
{
    auto start_time = std::chrono::steady_clock::now();
    while(true)
    {
        if (received_new_message_.load())
        {
            {
                auto copy_start_time = std::chrono::steady_clock::now();
                std::lock_guard<std::mutex> guard(update_message_mutex_);
                received_new_message_.store(false);
                pybind11::bytes message_bytes(reinterpret_cast<char *>(message_buffer_.data()), received_message_size_);
                auto copy_end_time = std::chrono::steady_clock::now();
                auto copy_duration = std::chrono::duration_cast<std::chrono::milliseconds>(copy_end_time - copy_start_time);
                // printf("get_latest_message: Copy %u bytes in %dms\n", received_message_size_, copy_duration.count());
                // message_buffer_.clear();
                return message_bytes;
            }
        }
        std::this_thread::sleep_for(std::chrono::microseconds(1));
        if (std::chrono::steady_clock::now() - start_time > std::chrono::milliseconds(timeout_ms))
        {
            return pybind11::bytes();
        }
    }

}

uint32_t PeerTalkClient::receive_whole_buffer_(int socket_handle, uint8_t* output_buffer, uint32_t num_bytes_to_read)
{
    uint32_t num_total_received_bytes = 0;
    while ( num_total_received_bytes < num_bytes_to_read )
    {
        uint32_t num_rest_bytes = num_bytes_to_read - num_total_received_bytes;
        uint32_t num_actually_received_bytes = 0;
        if ( 0 != usbmuxd_recv( socket_handle, (char*) (output_buffer + num_total_received_bytes), num_rest_bytes,
                                &num_actually_received_bytes ))
        {
            return num_total_received_bytes;
        }
        num_total_received_bytes += num_actually_received_bytes;
    }
    return num_total_received_bytes;
}

void PeerTalkClient::run_communication_thread_()
{

    while ( is_connected_ )
    {
        uint32_t num_bytes_to_read = sizeof(PeerTalkHeader);
        uint8_t* buffer = new uint8_t[num_bytes_to_read];
        receive_whole_buffer_(socket_handle_, buffer, num_bytes_to_read);
        PeerTalkHeader header = get_peer_talk_header(buffer);
        delete[] buffer;

        if ( header.body_size > message_buffer_.size() )
        {
            message_buffer_.resize(header.body_size);
        }
        auto start_time = std::chrono::steady_clock::now();
        {
            std::lock_guard<std::mutex> guard(update_message_mutex_);
            receive_whole_buffer_(socket_handle_, message_buffer_.data(), header.body_size);
            received_new_message_.store(true);
            received_message_size_ = header.body_size;
        }
        auto receive_end_time = std::chrono::steady_clock::now();

        auto receive_duration = std::chrono::duration_cast<std::chrono::milliseconds>(receive_end_time - start_time);
        // printf("Receive %u bytes in %dms\n", header.body_size, receive_duration.count());
    }
}

}