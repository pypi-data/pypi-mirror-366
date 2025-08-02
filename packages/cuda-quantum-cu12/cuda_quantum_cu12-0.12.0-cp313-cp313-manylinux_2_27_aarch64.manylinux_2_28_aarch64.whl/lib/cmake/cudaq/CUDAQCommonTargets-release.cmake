#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudaq::cudaq-common" for configuration "Release"
set_property(TARGET cudaq::cudaq-common APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudaq::cudaq-common PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcudaq-common.so"
  IMPORTED_SONAME_RELEASE "libcudaq-common.so"
  )

list(APPEND _cmake_import_check_targets cudaq::cudaq-common )
list(APPEND _cmake_import_check_files_for_cudaq::cudaq-common "${_IMPORT_PREFIX}/lib/libcudaq-common.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
