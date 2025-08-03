from setuptools import setup, Extension, find_packages
import pybind11
import sys
import multiprocessing

extra_compile_args = [
    "-O3",
    "-march=native",
    "-ffast-math",
    "-fopenmp",
]

if sys.platform == "win32":
    extra_compile_args = ["/O2", "/arch:AVX2", "/openmp"]
    extra_link_args = []
else:
    extra_link_args = ["-fopenmp"]

ext_modules = [
    Extension(
        "lightbinpack.cpp.ffd",
        ["lightbinpack/cpp/ffd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.nf",
        ["lightbinpack/cpp/nf.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.bfd",
        ["lightbinpack/cpp/bfd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.obfd",
        ["lightbinpack/cpp/obfd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.obfdp",
        ["lightbinpack/cpp/obfdp.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.ogbfd",
        ["lightbinpack/cpp/ogbfd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.ogbfdp",
        ["lightbinpack/cpp/ogbfdp.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.ohgbfd",
        ["lightbinpack/cpp/ohgbfd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.radix_sort",
        ["lightbinpack/cpp/radix_sort.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.radix_merge",
        ["lightbinpack/cpp/radix_merge.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.oshgbfd",
        ["lightbinpack/cpp/oshgbfd.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "lightbinpack.cpp.load_balance",
        ["lightbinpack/cpp/load_balance.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    name="lightbinpack",
    version="0.1.1",
    author="TechxGenus",
    description="A lightweight library for solving bin packing problems",
    url="https://github.com/TechxGenus/LightBinPack",
    packages=find_packages(),
    package_data={
        "lightbinpack": ["cpp/*.cpp"],
    },
    ext_modules=ext_modules,
    python_requires=">=3.6",
    install_requires=[
        "pybind11>=2.6.0",
        "numpy>=1.19.0",
    ],
    zip_safe=False,
    options={
        "build_ext": {
            "parallel": multiprocessing.cpu_count() // 2 + 1,
        }
    },
)
