#include "peertalk_client.h"
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(pypeertalk_core, m)
{
    py::class_<pypeertalk::DeviceInfo>(m, "DeviceInfo")
        .def(py::init<uint32_t, std::string, uint32_t>())
        .def_readwrite("product_id", &pypeertalk::DeviceInfo::product_id)
        .def_readwrite("udid", &pypeertalk::DeviceInfo::udid)
        .def_readwrite("handle", &pypeertalk::DeviceInfo::handle)
        .def("__str__", &pypeertalk::DeviceInfo::to_string);

    py::class_<pypeertalk::PeerTalkClient>(m, "PeerTalkClient")
        .def(py::init<const pypeertalk::DeviceInfo &, int>())
        .def("get_latest_message", &pypeertalk::PeerTalkClient::get_latest_message);

    m.def("get_connected_devices", &pypeertalk::get_connected_devices);

}