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

	def _buildAutotoolsAce(self):
		buildType = self.settings.get_safe("build_type", default="Release")

		with open(os.path.join(self._source_subfolder, "ace", "config.h"), "w") as f:
			f.write("#include \"ace/config-win32.h\"\n")

		with open(os.path.join(self._source_subfolder, "include", "makeinclude", "platform_macros.GNU"), "w") as f:
			f.write("buildbits=64\n")
			f.write("debug=%s\n" % "1" if buildType == "Debug" else "0")
			f.write("include $(ACE_ROOT)/include/makeinclude/platform_mingw32.GNU\n")
			f.write("rand_r_issue=1\n")
			f.write("INSTALL_PREFIX=%s\n" % tools.unix_path(os.path.join(self.build_folder, self._install_subfolder)))

		args = ""
		if not self.options.shared:
			args = "static_libs_only=1"

		with tools.chdir(os.path.join(self._source_subfolder, "ace")):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			
			autotools.make(args=args, vars=envVars)
			autotools.install(vars=envVars)

	def _buildAutotoolsAce(self):
		buildType = self.settings.get_safe("build_type", default="Release")

		with open(os.path.join(self._source_subfolder, "ace", "config.h"), "w") as f:
			f.write("#include \"ace/config-win32.h\"\n")

		with open(os.path.join(self._source_subfolder, "include", "makeinclude", "platform_macros.GNU"), "w") as f:
			f.write("c++11=1\n")
			f.write("buildbits=64\n")
			f.write("debug=%s\n" % "1" if buildType == "Debug" else "0")
			f.write("include $(ACE_ROOT)/include/makeinclude/platform_mingw32.GNU\n")
			f.write("rand_r_issue=1\n")
			f.write("INSTALL_PREFIX=%s\n" % tools.unix_path(os.path.join(self.build_folder, self._install_subfolder)))

		args = ""
		if not self.options.shared:
			args = "static_libs_only=1"

		with tools.chdir(os.path.join(self._source_subfolder, "ace")):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			
			autotools.make(args=args, vars=envVars)
			autotools.install(vars=envVars)

	def _buildAutotoolsGperf(self):
		with tools.chdir(os.path.join(self._source_subfolder, "apps", "gperf", "src")):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			
			autotools.make(vars=envVars)
			autotools.install(vars=envVars)

	def _buildAutotoolsTaoIdl(self):
		with tools.chdir(os.path.join(self._source_subfolder, "TAO", "TAO_IDL")):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			envVars["TAO_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder, "TAO"))
			
			autotools.make(vars=envVars)
			autotools.install(vars=envVars)

	def _buildAutotoolsTaoLib(self):
		with tools.chdir(os.path.join(self._source_subfolder, "TAO", "tao")):
			autotools = AutoToolsBuildEnvironment(self, win_bash=True)
			
			envVars = autotools.vars
			envVars["ACE_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder))
			envVars["TAO_ROOT"] = tools.unix_path(os.path.join(self.build_folder, self._source_subfolder, "TAO"))
			
			autotools.make(vars=envVars)
			autotools.install(vars=envVars)

	def build(self):
		if self.settings.os == "Windows" and self.settings.compiler == "gcc":
			self._buildAutotoolsAce()
			self._buildAutotoolsGperf()
			self._buildAutotoolsTaoIdl()
			self._buildAutotoolsTaoLib()

	def package(self):
		self.copy("*.h", dst="include", src="hello")
		self.copy("*hello.lib", dst="lib", keep_path=False)
		self.copy("*.dll", dst="bin", keep_path=False)
		self.copy("*.so", dst="lib", keep_path=False)
		self.copy("*.dylib", dst="lib", keep_path=False)
		self.copy("*.a", dst="lib", keep_path=False)

	def package_info(self):
		self.cpp_info.libs = tools.collect_libs(self)
