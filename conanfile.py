from conans import ConanFile, CMake, tools
import os

from conanos.build import config_scheme

class LibVorbisConan(ConanFile):
    name = "libvorbis"
    version = "1.3.6"
    description = "The VORBIS audio codec library"
    url = "http://github.com/bincrafters/conan-vorbis"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindVORBIS.cmake",
                       'vorbis.pc.in','vorbisenc.pc.in','vorbisfile.pc.in']
    source_subfolder = "source_subfolder"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    requires = "libogg/1.3.3@conanos/stable"
    generators = "cmake"
    source_subfolder = "source_subfolder"
	
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        tools.get("https://github.com/xiph/vorbis/archive/v%s.tar.gz" % self.version)
        os.rename("vorbis-%s" % self.version, self.source_subfolder)
        #if self.settings.os == 'Windows':
        #    with tools.chdir(self.source_subfolder):
        #        tools.replace_in_file('vorbis.pc.in', 'Libs.private: -lm', 'Libs.private:')
        import shutil
        for name in ['vorbis','vorbisenc','vorbisfile']:
            shutil.copy('%s.pc.in'%name, dst=self.source_subfolder)

    @property
    def _msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def build(self):
        if self._msvc:
            self.cmake_build()
        else:
            self.gcc_build()

    def cmake_build(self):
        if self.settings.os == "Linux":
            if 'LDFLAGS' in os.environ:
                os.environ['LDFLAGS'] = os.environ['LDFLAGS'] + ' -lm'
            else:
                os.environ['LDFLAGS'] = '-lm'
        cmake = CMake(self)
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(build_folder='~build')
        cmake.build()
        cmake.install()

    def gcc_build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH':'%s/lib/pkgconfig'%(self.deps_cpp_info["libogg"].rootpath)
                }):

                self.run('rm ltmain.sh')
                _args = ['--prefix=%s/builddir'%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()),]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])

                self.run('sh autogen.sh %s'%(' '.join(_args)))#space
                self.run('make -j2')
                self.run('make install')

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

