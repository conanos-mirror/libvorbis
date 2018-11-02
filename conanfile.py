from conans import ConanFile, CMake, tools
import os

class LibvorbisConan(ConanFile):
    name = "libvorbis"
    version = "1.3.5"
    description = "Vorbis audio compression reference implementation"
    url = "https://github.com/conanos/libvorbis"
    homepage = 'https://xiph.org/vorbis/'
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "libogg/1.3.3@conanos/dev"

    source_subfolder = "source_subfolder"

    def source(self):
        url_ = 'http://downloads.xiph.org/releases/vorbis/{name}-{version}.tar.gz'.format(name=self.name, version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
    
    def build(self):
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

