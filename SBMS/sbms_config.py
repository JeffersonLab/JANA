#####################################################################
# This is used to create 2 files that contain configuration information
# for JANA. Specifically, what external packages are present so that
# support is compiled into JANA for them. This comes in 2 places
# (hence, the 2 files). The first is the jana_config.h file which
# defines values that are used by preprocessor directives to include
# (or not) support for 3rd party packges at compile time. The second
# is the jana-config script that can be used by packages using JANA
# as 3rd party so that they can obtain the correct compiler flags and
# libraries to link against this version of JANA.
#
# Historically, the jana_config.h header and jana-config script
# files were produced by the configure script. jana_config.h lived in the
# src/JANA directory while compilation took place and was copied to the install
# directory by "make" during the install phase. This prevented multiple
# platforms from compiling simultaneously (since their configurations
# could be different).
#
# This system will re-generate these files each time scons
# is run and place them in the platform-specific build directory tree
# to allow simultaneous builds.
# The functions here are called from the bottom of the top-level SConstruct
# file.
#
# Dec. 10, 2013  DL
#####################################################################
import os, sys
import subprocess
import datetime
import distutils
from stat import *

##################################
# which
#
# small utility to find if a specified program is in our PATH
# (copied from the web)
##################################
def which(program):
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
		
	for path in os.environ["PATH"].split(os.pathsep):
		path = path.strip('"')
		exe_file = os.path.join(path, program)
		if is_exe(exe_file):
			return exe_file
	return None

##################################
# mk_jana_config_h
##################################
def mk_jana_config_h(env):
	ofdirname = '#src/.%s/JANA' % env['OSNAME']
	ofdir = '%s' % env.Dir(ofdirname)
	ofname = '%s/jana_config.h' % ofdir
	print 'sbms : Making jana_config.h in %s' % ofdir
	
	# ROOT
	HAVE_ROOT = 0
	if(os.getenv('ROOTSYS') != None): HAVE_ROOT = 1
	
	# XERCES
	HAVE_XERCES = 0
	XERCES3 = 0
	XERCESCROOT = os.getenv('XERCESCROOT')
	if(XERCESCROOT != None):
		HAVE_XERCES = 1
		xerces3file = '%s/include/xercesc/dom/DOMImplementationList.hpp' % XERCESCROOT
		if(os.path.isfile(xerces3file)): XERCES3 = 1

	# CCDB
	HAVE_CCDB = 0
	if(os.getenv('CCDB_HOME') != None): HAVE_CCDB = 1
		
	str = ''
	
	# Header
	str += '//\n'
	str += '// This file was generated by the SBMS system (see SBMS/sbms_config.py)\n'
	str += '//\n'
	str += '// Generation date: %s\n' % datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	str += '//\n'
	str += '//       User: %s\n' % os.getenv('USER', 'Unknown')
	str += '//       Host: %s\n' % os.getenv('HOST', 'Unknown')
	str += '//   platform: %s' % subprocess.Popen(["uname", "-a"], stdout=subprocess.PIPE).communicate()[0]
	str += '// BMS_OSNAME: %s\n' % env['OSNAME']
	str += '\n'
	str += '\n'

	str += '#define HAVE_ROOT     %d\n' % HAVE_ROOT
	str += '#define HAVE_XERCES   %d\n' % HAVE_XERCES
	str += '#define XERCES3       %d\n' % XERCES3
	str += '#define HAVE_CCDB     %d\n' % HAVE_CCDB

	str += '\n'
	str += '\n'

	# Make sure output directory eists
	try:
		os.makedirs(ofdir)
	except OSError:
		pass

	# Write to file
	f = open(ofname, 'w')
	f.write(str)
	f.close()
	os.chmod(ofname, S_IRUSR + S_IWUSR + S_IRGRP + S_IWGRP + S_IROTH )
	


##################################
# mk_jana_config_script
##################################
def mk_jana_config_script(env):
	ofdirname = '#%s/bin' % env['OSNAME']
	ofdir = '%s' % env.Dir(ofdirname)
	ofname = '%s/jana-config' % ofdir
	print 'sbms : Making jana-config in %s' % ofdir

	JANA_INSTALL_DIR = '%s' % env.Dir("#/%s" % env['OSNAME']).abspath
	
	# ROOT
	HAVE_ROOT = 0
	ROOTCFLAGS = ''
	ROOTGLIBS = ''
	if(os.getenv('ROOTSYS') != None):
		HAVE_ROOT = 1
		ROOTCFLAGS = subprocess.Popen(["root-config", "--cflags"], stdout=subprocess.PIPE).communicate()[0][:-1]
		ROOTGLIBS = subprocess.Popen(["root-config", "--glibs"], stdout=subprocess.PIPE).communicate()[0][:-1]

	# XERCES
	HAVE_XERCES = 0
	XERCES_CPPFLAGS = ''
	XERCES_LDFLAGS = ''
	XERCES_LIBS = ''
	XERCESCROOT = os.getenv('XERCESCROOT')
	if(XERCESCROOT != None):
		HAVE_XERCES = 1
		XERCES_CPPFLAGS = "-I%s/include -I%s/include/xercesc" % (XERCESCROOT, XERCESCROOT)
		XERCES_LDFLAGS = "-L%s/lib" % (XERCESCROOT)
		XERCES_LIBS = "-lxerces-c"

	# CMSG
	HAVE_CMSG = 0
	CMSG_CPPFLAGS = ''
	CMSG_LDFLAGS = ''
	CMSG_LIBS = ''
	CMSGROOT = os.getenv('CMSGROOT')
	if(CMSGROOT != None):
		HAVE_CMSG = 1
		CMSG_CPPFLAGS = "-I%s/include" % (CMSGROOT)
		CMSG_LDFLAGS = "-L%s/lib" % (CMSGROOT)
		CMSG_LIBS = "-lcmsg -lcmsgxx -lcmsgRegex"

	# MYSQL
	HAVE_MYSQL = 0
	MYSQL_CFLAGS = ''
	MYSQL_LDFLAGS = ''
	MYSQL_VERSION = ''
	mysql_config = which('mysql_config')
	if mysql_config != None:
		HAVE_MYSQL = 1
		MYSQL_CFLAGS = subprocess.Popen(["mysql_config", "--cflags"], stdout=subprocess.PIPE).communicate()[0][:-1]
		MYSQL_LDFLAGS = subprocess.Popen(["mysql_config", "--libs"], stdout=subprocess.PIPE).communicate()[0][:-1]
		MYSQL_VERSION = subprocess.Popen(["mysql_config", "--version"], stdout=subprocess.PIPE).communicate()[0][:-1]

	# CURL
	HAVE_CURL = 0
	CURL_CFLAGS = ''
	CURL_LDFLAGS = ''
	curl_config = which('curl-config')
	if curl_config != None:
		HAVE_CURL = 1
		CURL_CFLAGS = subprocess.Popen(["curl-config", "--cflags"], stdout=subprocess.PIPE).communicate()[0][:-1]
		CURL_LDFLAGS = subprocess.Popen(["curl-config", "--libs"], stdout=subprocess.PIPE).communicate()[0][:-1]

	# CCDB
	HAVE_CCDB = 0
	CCDB_CPPFLAGS = ''
	CCDB_LDFLAGS = ''
	CCDB_LIBS = ''
	ccdb_home = os.getenv('CCDB_HOME')
	if(ccdb_home != None):
		HAVE_CCDB = 1
		CCDB_CPPFLAGS = "-I%s/include" % (ccdb_home)
		CCDB_LDFLAGS = "-L%s/lib" % (ccdb_home)
		CCDB_LIBS = "-lccdb"

	# Read in entire jana-congfig.in file as a single string
	ifname = env.File("#/SBMS/jana-config.in").abspath
	with open (ifname, "r") as myfile:

		# Read in file
		str=myfile.read()

		# Replace strings
		str = str.replace("@BMS_OSNAME@", env['OSNAME'])

		str = str.replace("@HAVE_MYSQL@", '%d' % HAVE_MYSQL)
		str = str.replace("@HAVE_XERCES@", '%d' % HAVE_XERCES)
		str = str.replace("@HAVE_ROOT@", '%d' % HAVE_ROOT)
		str = str.replace("@HAVE_CMSG@", '%d' % HAVE_CMSG)
		str = str.replace("@HAVE_CURL@", '%d' % HAVE_CURL)
		str = str.replace("@HAVE_CCDB@", '%d' % HAVE_CCDB)

		str = str.replace("@MYSQL_CFLAGS@", '%s' % MYSQL_CFLAGS)
		str = str.replace("@MYSQL_LDFLAGS@", '%s' % MYSQL_LDFLAGS)
		str = str.replace("@MYSQL_VERSION@", '%s' % MYSQL_VERSION)

		str = str.replace("@XERCES_CPPFLAGS@", '%s' % XERCES_CPPFLAGS)
		str = str.replace("@XERCES_LDFLAGS@", '%s' % XERCES_LDFLAGS)
		str = str.replace("@XERCES_LIBS@", '%s' % XERCES_LIBS)

		str = str.replace("@ROOTCFLAGS@", '%s' % ROOTCFLAGS)
		str = str.replace("@ROOTGLIBS@", '%s' % ROOTGLIBS)

		str = str.replace("@CMSG_CPPFLAGS@", '%s' % CMSG_CPPFLAGS)
		str = str.replace("@CMSG_LDFLAGS@", '%s' % CMSG_LDFLAGS)
		str = str.replace("@CMSG_LIBS@", '%s' % CMSG_LIBS)

		str = str.replace("@CURL_CFLAGS@", '%s' % CURL_CFLAGS)
		str = str.replace("@CURL_LDFLAGS@", '%s' % CURL_LDFLAGS)

		str = str.replace("@CCDB_CPPFLAGS@", '%s' % CCDB_CPPFLAGS)
		str = str.replace("@CCDB_LDFLAGS@", '%s' % CURL_LDFLAGS)
		str = str.replace("@CCDB_LIBS@", '%s' % CCDB_LIBS)

		str = str.replace("@JANA_INSTALL_DIR@", '%s' % JANA_INSTALL_DIR)

		# Make sure output directory eists
		try:
			os.makedirs(ofdir)
		except OSError:
			pass

		# Write to file
		f = open(ofname, 'w')
		f.write(str)
		f.close()
		os.chmod(ofname, S_IRWXU + S_IRGRP + S_IXGRP + S_IROTH + S_IXOTH)



