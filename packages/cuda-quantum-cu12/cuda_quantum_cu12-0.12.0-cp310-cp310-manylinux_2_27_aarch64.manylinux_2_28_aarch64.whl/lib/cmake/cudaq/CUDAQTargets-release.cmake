#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudaq::cudaq" for configuration "Release"
set_property(TARGET cudaq::cudaq APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudaq::cudaq PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "nvqir::nvqir"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcudaq.so"
  IMPORTED_SONAME_RELEASE "libcudaq.so"
  )

list(APPEND _cmake_import_check_targets cudaq::cudaq )
list(APPEND _cmake_import_check_files_for_cudaq::cudaq "${_IMPORT_PREFIX}/lib/libcudaq.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
