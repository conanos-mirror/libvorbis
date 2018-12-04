from conans import ConanFile, CMake, tools
from conanos.build import config_scheme
import os
import shutil

class LibVorbisConan(ConanFile):
    name = "libvorbis"
    version = "1.3.6"
    description = "The VORBIS audio codec library"
    url = "http://github.com/bincrafters/conan-vorbis"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindVORBIS.cmake", 'vorbis.pc.in','vorbisenc.pc.in','vorbisfile.pc.in']
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': False, 'fPIC': True }
    requires = "libogg/1.3.3@conanos/stable"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        tools.get("https://github.com/xiph/vorbis/archive/v%s.tar.gz" % self.version)
        os.rename("vorbis-%s" % self.version, self._source_subfolder)
        for name in ['vorbis','vorbisenc','vorbisfile']:
            shutil.copy('%s.pc.in'%name, dst=self._source_subfolder)

    def build(self):
        self.cmake_build()
        
    def cmake_build(self):
        #if self.settings.os == "Linux":
        #    if 'LDFLAGS' in os.environ:
        #        os.environ['LDFLAGS'] = os.environ['LDFLAGS'] + ' -lm'
        #    else:
        #        os.environ['LDFLAGS'] = '-lm'
        cmake = CMake(self)
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

