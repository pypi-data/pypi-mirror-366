#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "lsd_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_lsd_core, m) {
    py::class_<lsdembed::LSDParams>(m, "LSDParams")
        .def(py::init<>())
        .def_readwrite("d", &lsdembed::LSDParams::d)
        .def_readwrite("dt", &lsdembed::LSDParams::dt)
        .def_readwrite("alpha", &lsdembed::LSDParams::alpha)
        .def_readwrite("beta", &lsdembed::LSDParams::beta)
        .def_readwrite("gamma", &lsdembed::LSDParams::gamma)
        .def_readwrite("r_cutoff", &lsdembed::LSDParams::r_cutoff)
        .def_readwrite("scale", &lsdembed::LSDParams::scale)
        .def_readwrite("seed", &lsdembed::LSDParams::seed);
    
    py::class_<lsdembed::LSDEngine>(m, "LSDEngine")
        .def(py::init<const lsdembed::LSDParams&>())
        .def("embed_tokens", &lsdembed::LSDEngine::embed_tokens)
        .def("embed_chunks", &lsdembed::LSDEngine::embed_chunks)
        .def("set_params", &lsdembed::LSDEngine::set_params)
        .def("get_params", &lsdembed::LSDEngine::get_params);
}