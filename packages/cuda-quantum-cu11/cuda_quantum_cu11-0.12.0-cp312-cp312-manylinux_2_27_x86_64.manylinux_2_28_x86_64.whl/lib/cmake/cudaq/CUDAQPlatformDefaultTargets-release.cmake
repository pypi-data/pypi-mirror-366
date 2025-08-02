#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudaq::cudaq-platform-default" for configuration "Release"
set_property(TARGET cudaq::cudaq-platform-default APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudaq::cudaq-platform-default PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "cudaq::cudaq"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcudaq-platform-default.so"
  IMPORTED_SONAME_RELEASE "libcudaq-platform-default.so"
  )

list(APPEND _cmake_import_check_targets cudaq::cudaq-platform-default )
list(APPEND _cmake_import_check_files_for_cudaq::cudaq-platform-default "${_IMPORT_PREFIX}/lib/libcudaq-platform-default.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
