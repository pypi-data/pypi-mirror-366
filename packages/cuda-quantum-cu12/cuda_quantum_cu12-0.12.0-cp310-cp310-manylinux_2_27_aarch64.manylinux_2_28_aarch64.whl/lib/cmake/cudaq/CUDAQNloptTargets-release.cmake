#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudaq::cudaq-nlopt" for configuration "Release"
set_property(TARGET cudaq::cudaq-nlopt APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudaq::cudaq-nlopt PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcudaq-nlopt.so"
  IMPORTED_SONAME_RELEASE "libcudaq-nlopt.so"
  )

list(APPEND _cmake_import_check_targets cudaq::cudaq-nlopt )
list(APPEND _cmake_import_check_files_for_cudaq::cudaq-nlopt "${_IMPORT_PREFIX}/lib/libcudaq-nlopt.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
