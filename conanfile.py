from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os,shutil

class LibdcaConan(ConanFile):
    name = "libdca"
    version = "0.0.6"
    description = "ibdca is a free library for decoding DTS Coherent Acoustics streams"
    url = "https://github.com/conanos/libdca"
    homepage = "https://www.videolan.org/developers/libdca.html"
    license = "GPL-v2"
    win_module_defs = ["libdca.def","libao.def"]
    win_projs = ["dcadec.sln","dcadec.vcxproj","libao.vcxproj","libdca.vcxproj"]
    exports = ["COPYING","inttypes.h", "shared/*"] + win_module_defs
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_="http://download.videolan.org/pub/videolan/libdca/{version}/libdca-{version}.tar.bz2"
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            for i in ["inttypes.h"] + self.win_module_defs:
                shutil.copy2(os.path.join(self.source_folder,i), os.path.join(self.source_folder,self._source_subfolder,"vc++",i))
            sln_folder = "shared" if self.options.shared else "static"
            for i in self.win_projs:
                shutil.copy2(os.path.join(self.source_folder,sln_folder,i), os.path.join(self.source_folder,self._source_subfolder,"vc++",i))

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    _args = ["--prefix=%s/builddir"%(os.getcwd())]
        #    autotools = AutoToolsBuildEnvironment(self)
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"])
        #    autotools.install()
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"vc++")):
                msbuild = MSBuild(self)
                msbuild.build("dcadec.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        excludes="*.a" if self.options.shared else  "*.so*"
        #        self.copy("*", src="%s/builddir"%(os.getcwd()), excludes=excludes)
        if self.settings.os == 'Windows':
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join("vc++",platforms.get(str(self.settings.arch)),str(self.settings.build_type))
            for i in ["libdca", "libao"]:
                self.copy("%s.*"%(i), dst=os.path.join(self.package_folder,"lib"),
                          src=os.path.join(self.build_folder,self._source_subfolder,output_rpath), excludes=["%s.dll"%(i),"%s.tlog"%(i)])
                self.copy("%s.dll"%(i), dst=os.path.join(self.package_folder,"bin"),
                          src=os.path.join(self.build_folder,self._source_subfolder,output_rpath))
            self.copy("dca.h", dst=os.path.join(self.package_folder,"include"),
                      src=os.path.join(self.build_folder,self._source_subfolder,"include"))
            self.copy("audio_out.h", dst=os.path.join(self.package_folder,"include"),
                      src=os.path.join(self.build_folder,self._source_subfolder,"include"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

