import sys
import os
import subprocess
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

here = os.path.abspath(os.path.dirname(__file__))

class BuildExt(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type
        print(f"Detected compiler: {compiler}")

        # Default C++20 args
        if compiler == "msvc":
            cpp_args = ["/std:c++20"]
            link_args = []
        else:
            cpp_args = ["-std=c++20"]
            link_args = []

            # macOS-specific SDK configuration
            if sys.platform == "darwin":
                sdk_path = subprocess.check_output(
                    ["xcrun", "--sdk", "macosx", "--show-sdk-path"]
                ).decode().strip()
                cpp_args += [
                    "-stdlib=libc++",
                    "-mmacosx-version-min=10.9",
                    "-isysroot", sdk_path,
                ]
                link_args += [
                    "-stdlib=libc++",
                    "-mmacosx-version-min=10.9",
                    "-isysroot", sdk_path,
                ]

        for ext in self.extensions:
            ext.extra_compile_args = cpp_args
            ext.extra_link_args = link_args

        super().build_extensions()

ext_modules = [
    Extension(
        name="pypearl._pypearl",
        sources=[
            "src/pybinding/binding.cpp",
            "src/pybinding/layerbinding.cpp",
            "src/pybinding/matrixbinding.cpp",
            "src/pybinding/activationbinding/relubinding.cpp",
            "src/pybinding/activationbinding/softmaxbinding.cpp",
            "src/pybinding/lossbinding/ccebinding.cpp",
            "src/pybinding/optimizerbinding/sgdbinding.cpp",
            "src/pybinding/modelbinding/modelbinding.cpp",
        ],
        include_dirs=[
            os.path.join(here, "src"),
            os.path.join(here, "src", "pybinding"),
        ],
        language="c++",
    ),
]

setup(
    name="pypearl",
    version="0.5.1",
    author="Brody Massad",
    author_email="brodymassad@gmail.com",
    description="An efficient Machine Learning Library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    packages=find_packages(),
    package_data={
        "pypearl": ["*.pyi", "py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)
