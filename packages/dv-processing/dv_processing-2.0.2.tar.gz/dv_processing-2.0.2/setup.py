import os
import platform
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

global extra_cmake_args
extra_cmake_args = [
    "-DDVP_ENABLE_TESTS=OFF",
    "-DDVP_ENABLE_SAMPLES=OFF",
    "-DDVP_ENABLE_UTILITIES=OFF",
    "-DDVP_ENABLE_BENCHMARKS=OFF",
    "-DDVP_ENABLE_PYTHON=ON",
    "-DDVP_ENABLE_PYTHON_STUBGEN=OFF",
]

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):

    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


class CMakeBuild(build_ext):

    def build_extension(self, ext: CMakeExtension) -> None:
        # Must be in this form due to bug in .resolve() only fixed in Python 3.10+
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)  # type: ignore[no-untyped-call]
        extdir = ext_fullpath.parent.resolve()

        # Using this requires trailing slash for auto-detection & inclusion of
        # auxiliary "native" libs

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")

        # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
        # from Python.
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        ]
        build_args = []
        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        # In this example, we pass in the version to C++. You might not need to.
        # cmake_args += [f"-DEXAMPLE_VERSION_INFO={self.distribution.get_version()}"]  # type: ignore[attr-defined]

        # Pass Python3 executable path to CMake after external args (eg. VCPKG toolchain files)
        cmake_args += [f"-DPython3_EXECUTABLE={sys.executable}"]

        # Add custom CMake arguments needed for build features
        global extra_cmake_args
        cmake_args += extra_cmake_args

        if self.compiler.compiler_type != "msvc":
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in CMake
            # 3.15+.
            if not cmake_generator or cmake_generator == "Ninja":
                try:
                    import ninja

                    ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                    cmake_args += [
                        "-GNinja",
                        f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                    ]
                except ImportError:
                    pass

        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"]
                build_args += ["--config", cfg]

        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{self.parallel}"]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        ret = subprocess.run(["cmake", ext.sourcedir, *cmake_args], cwd=build_temp, check=True)
        print("Called cmake with: " + str(ret.args))
        ret = subprocess.run(["cmake", "--build", ".", "--target", "dv_processing", *build_args],
                             cwd=build_temp,
                             check=True)
        print("Called cmake with: " + str(ret.args))


def parse_gplusplus_major_version(gpp_path):
    try:
        p = subprocess.Popen([gpp_path, "--version"], stdout=subprocess.PIPE)
        out, _ = p.communicate()
        if p.returncode == 0:
            output_text = out.decode('UTF-8')
            prog = re.compile(r"^(\S+)\s\(.*\)\s(\d+)\.\d+\.\d+.*")
            result = prog.match(output_text)
            if result is not None and result[1][0:3] == "g++":
                return int(result[2])
    except FileNotFoundError:
        pass
    return None


def verify_and_configure_compiler():
    # This verify and check only relevant on linux
    if platform.system() != 'Linux':
        return

    version = parse_gplusplus_major_version("g++")
    if version is not None and version >= 13:
        # default compiler seems fine, continue
        return
    try:
        version = parse_gplusplus_major_version(os.environ["CXX"])
        if version is not None and version >= 13:
            # A preset compiler found, it seems suitable
            return
    except KeyError:
        pass

    version = parse_gplusplus_major_version("g++-13")
    if version is not None and version >= 13:
        global extra_cmake_args
        print("Detected installation of g++13, it will be used for compilation")
        extra_cmake_args += ["-DCMAKE_C_COMPILER=gcc-13", "-DCMAKE_CXX_COMPILER=g++-13"]
        return

    # None of the above worked. Print a warning.
    print("Compatible GCC compiler was not found.", file=sys.stderr)
    print("Compiler compatibility verification failed, compilation will use system compiler.", file=sys.stderr)
    print("This might fail!", file=sys.stderr)


def get_version():
    # If a VERSION.txt exists, we use its content as version number.
    try:
        with open('VERSION.txt', 'r') as version_file:
            return version_file.read()
    except IOError:
        print("Using git hash")

    # Else we're a git-build, so we use the git hash.
    # Format it to be PEP440 compliant for pip/wheel compatibility.
    gitTag = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    return "9999.dev0+git{:s}".format(gitTag)


# Initial setup
verify_and_configure_compiler()

setup(
    name="dv_processing",
    version=get_version(),
    author="iniVation AG",
    author_email="support@inivation.com",
    description="Generic algorithms for event cameras.",
    long_description="",
    ext_modules=[CMakeExtension(".")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    install_requires=["numpy"],
    python_requires=">=3.8",
)
