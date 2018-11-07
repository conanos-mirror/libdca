from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class LibdcaConan(ConanFile):
    name = "libdca"
    version = "0.0.5"
    description = "ibdca is a free library for decoding DTS Coherent Acoustics streams"
    url = "https://github.com/conan-multimedia/libdca"
    homepage = "https://www.videolan.org/developers/libdca.html"
    license = "GPL"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("http://download.videolan.org/pub/videolan/libdca/0.0.5/{name}-{version}.tar.bz2".format(name=self.name,version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            _args = ["--prefix=%s/builddir"%(os.getcwd())]
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=_args)
            autotools.make(args=["-j4"])
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                excludes="*.a" if self.options.shared else  "*.so*"
                self.copy("*", src="%s/builddir"%(os.getcwd()), excludes=excludes)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

