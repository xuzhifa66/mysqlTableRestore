# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /opt/mydumper-0.9.3

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /opt/mydumper-0.9.3

# Include any dependencies generated for this target.
include CMakeFiles/myloader.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/myloader.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/myloader.dir/flags.make

CMakeFiles/myloader.dir/myloader.c.o: CMakeFiles/myloader.dir/flags.make
CMakeFiles/myloader.dir/myloader.c.o: myloader.c
	$(CMAKE_COMMAND) -E cmake_progress_report /opt/mydumper-0.9.3/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building C object CMakeFiles/myloader.dir/myloader.c.o"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -o CMakeFiles/myloader.dir/myloader.c.o   -c /opt/mydumper-0.9.3/myloader.c

CMakeFiles/myloader.dir/myloader.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/myloader.dir/myloader.c.i"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -E /opt/mydumper-0.9.3/myloader.c > CMakeFiles/myloader.dir/myloader.c.i

CMakeFiles/myloader.dir/myloader.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/myloader.dir/myloader.c.s"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -S /opt/mydumper-0.9.3/myloader.c -o CMakeFiles/myloader.dir/myloader.c.s

CMakeFiles/myloader.dir/myloader.c.o.requires:
.PHONY : CMakeFiles/myloader.dir/myloader.c.o.requires

CMakeFiles/myloader.dir/myloader.c.o.provides: CMakeFiles/myloader.dir/myloader.c.o.requires
	$(MAKE) -f CMakeFiles/myloader.dir/build.make CMakeFiles/myloader.dir/myloader.c.o.provides.build
.PHONY : CMakeFiles/myloader.dir/myloader.c.o.provides

CMakeFiles/myloader.dir/myloader.c.o.provides.build: CMakeFiles/myloader.dir/myloader.c.o

# Object files for target myloader
myloader_OBJECTS = \
"CMakeFiles/myloader.dir/myloader.c.o"

# External object files for target myloader
myloader_EXTERNAL_OBJECTS =

myloader: CMakeFiles/myloader.dir/myloader.c.o
myloader: CMakeFiles/myloader.dir/build.make
myloader: /usr/lib64/mysql/libmysqlclient.so
myloader: /usr/lib64/libpthread.so
myloader: /usr/lib64/libm.so
myloader: /usr/lib64/librt.so
myloader: /usr/lib64/libdl.so
myloader: /usr/lib64/libglib-2.0.so
myloader: /usr/lib64/libgthread-2.0.so
myloader: /usr/lib64/libpcre.so
myloader: /usr/lib64/libz.so.1
myloader: CMakeFiles/myloader.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking C executable myloader"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/myloader.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/myloader.dir/build: myloader
.PHONY : CMakeFiles/myloader.dir/build

CMakeFiles/myloader.dir/requires: CMakeFiles/myloader.dir/myloader.c.o.requires
.PHONY : CMakeFiles/myloader.dir/requires

CMakeFiles/myloader.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/myloader.dir/cmake_clean.cmake
.PHONY : CMakeFiles/myloader.dir/clean

CMakeFiles/myloader.dir/depend:
	cd /opt/mydumper-0.9.3 && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /opt/mydumper-0.9.3 /opt/mydumper-0.9.3 /opt/mydumper-0.9.3 /opt/mydumper-0.9.3 /opt/mydumper-0.9.3/CMakeFiles/myloader.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/myloader.dir/depend
