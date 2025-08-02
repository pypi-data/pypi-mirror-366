from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11

ext_modules = [
    Pybind11Extension(
        "lsdembed._lsd_core",
        ["src/lsd_engine.cpp", "src/python_bindings.cpp"],
        include_dirs=[
            pybind11.get_include(),
            "src",  # Add src directory to include paths
        ],
        cxx_std=17,
        define_macros=[("VERSION_INFO", '"0.1.0"')],
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)