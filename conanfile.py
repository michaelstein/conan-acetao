from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class AcetaoConan(ConanFile):
	name = "acetao"
	version = "7.0.6"
	url = "https://www.dre.vanderbilt.edu/~schmidt/TAO.html"
	settings = "os", "compiler", "build_type", "arch"
	tool_requires = "strawberryperl/5.30.0.1", "msys2/cci.latest"
	options = {
		"shared": [True, False],
		"fPIC": [True, False]
	}
	default_options = {
		"shared": False,
		"fPIC": True
	}
	short_paths = True
	_source_subfolder = "source_subfolder"
	_install_subfolder = "install_subfolder"

	def config_options(self):
		if self.settings.os == "Windows":
			del self.options.fPIC

	def source(self):
		versionUnderscore = self.version.replace(".", "_")
		tools.get("https://github.com/DOCGroup/ACE_TAO/releases/download/ACE%%2BTAO-%s/ACE+TAO-%s.tar.bz2" % (versionUnderscore, self.version))
		tools.rename("ACE_wrappers", self._source_subfolder)

	def _configureAutotools(self):
		buildType = self.settings.get_safe("build_type", default="Release")

		with open(os.path.join(self._source_subfolder, "ace", "config.h"), "w") as f:
			f.write("#include \"ace/config-win32.h\"\n")

		with open(os.path.join(self._source_subfolder, "include", "makeinclude", "platform_macros.GNU"), "w") as f:
			f.write("c++11=1\n")
			f.write("buildbits=64\n")
			if not self.options.shared:
				f.write("static_libs_only=1\n")
			f.write("debug=%s\n" % "1" if buildType == "Debug" else "0")
			f.write("include $(ACE_ROOT)/include/makeinclude/platform_mingw32.GNU\n")
			f.write("INSTALL_PREFIX=%s\n" % tools.unix_path(os.path.join(self.build_folder, self._install_subfolder)))

	def _buildAutotoolsPath(self, path):
		with tools.chdir(path):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			envVars["TAO_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder, "TAO"))
			
			autotools.make(vars=envVars)
			autotools.install(vars=envVars)

	def build(self):
		if self.settings.os == "Windows" and self.settings.compiler == "gcc":
			self._configureAutotools()
			self._buildAutotoolsPath(os.path.join(self._source_subfolder, "ace"))
			self._buildAutotoolsPath(os.path.join(self._source_subfolder, "apps", "gperf", "src"))
			self._buildAutotoolsPath(os.path.join(self._source_subfolder, "TAO", "TAO_IDL"))
			self._buildAutotoolsPath(os.path.join(self._source_subfolder, "TAO", "tao"))

	def package(self):
		self.copy("*.h", dst="include", src="hello")
		self.copy("*hello.lib", dst="lib", keep_path=False)
		self.copy("*.dll", dst="bin", keep_path=False)
		self.copy("*.so", dst="lib", keep_path=False)
		self.copy("*.dylib", dst="lib", keep_path=False)
		self.copy("*.a", dst="lib", keep_path=False)

	def package_info(self):
		self.cpp_info.libs = tools.collect_libs(self)
