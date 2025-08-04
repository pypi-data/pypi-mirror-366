#ifndef PEERTALK_CLIENT_H
#define PEERTALK_CLIENT_H

#include <stdint.h>
#include <stdio.h>
#include "usbmuxd.h"
#include <stdlib.h>
#include <string>
#include <vector>
#include <pybind11/pybind11.h>
#include <thread>
#include <mutex>
#include <atomic>
// #include <fmt/format.h>

namespace pypeertalk
{

struct PeerTalkHeader
{
    uint32_t ns_error;
    uint32_t frame_type;
    uint32_t frame_tag;
    uint32_t body_size;
};

PeerTalkHeader get_peer_talk_header(uint8_t* buffer);

// void interruptable_sleep(int ms);

class DeviceInfo
{
    public:
    uint32_t product_id;
    std::string udid;
    uint32_t handle;

    DeviceInfo(uint32_t product_id, std::string udid, uint32_t handle) : product_id(product_id), udid(udid), handle(handle) {}
    std::string to_string() const{
        // return fmt::format("DeviceInfo(product_id={}, udid={}, handle={})", product_id, udid, handle);
        return "DeviceInfo(product_id=" + std::to_string(product_id) + ", udid=" + udid + ", handle=" + std::to_string(handle) + ")";
    }
};

std::vector<DeviceInfo> get_connected_devices();

class PeerTalkClient
{
    public:
        PeerTalkClient(const DeviceInfo &device, int port);
        ~PeerTalkClient();
        
        pybind11::bytes get_latest_message(int timeout_ms);
        
    private:
        DeviceInfo device_;
        int port_;
        std::atomic<bool> received_new_message_{ false };
        int received_message_size_{ 0 };
        bool is_connected_{ false };
        int socket_handle_{ -1 };
        std::mutex update_message_mutex_;
        std::vector<uint8_t> message_buffer_;


        bool connect_to_device_();
        void run_communication_thread_();
        uint32_t receive_whole_buffer_(int socket_handle, uint8_t* output_buffer, uint32_t num_bytes_to_read);
        std::thread communication_thread_;
};
}

#endif