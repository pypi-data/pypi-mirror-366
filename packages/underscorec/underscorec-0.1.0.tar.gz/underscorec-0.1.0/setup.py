"""
Setup script for underscorec C extension with PyTorch C++ API support.
Configuration is in pyproject.toml, this just handles the C extension build.
"""
from setuptools import setup, Extension
import numpy
import torch
import torch.utils.cpp_extension

# Get PyTorch include directories and libraries
torch_includes = torch.utils.cpp_extension.include_paths()
torch_libraries = torch.utils.cpp_extension.library_paths()

setup(
    ext_modules=[
        Extension(
            "underscorec.underscorec",
            sources=[
                "src/underscorec/underscorec.cpp",
                "src/underscorec/underscorec_numpy.cpp",
                "src/underscorec/underscorec_torch.cpp"
            ],
            include_dirs=[
                "src/underscorec",  # For local headers
                numpy.get_include()
            ] + torch_includes,
            library_dirs=torch_libraries,
            libraries=['torch', 'torch_cpu'],
            language='c++',  # Enable C++ compilation
            extra_compile_args=['-std=c++17'],  # PyTorch requires C++17
        )
    ]
)