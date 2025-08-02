#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cudaq::cudaq-python-interop" for configuration "Release"
set_property(TARGET cudaq::cudaq-python-interop APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cudaq::cudaq-python-interop PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "cudaq::cudaq"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcudaq-python-interop.so"
  IMPORTED_SONAME_RELEASE "libcudaq-python-interop.so"
  )

list(APPEND _cmake_import_check_targets cudaq::cudaq-python-interop )
list(APPEND _cmake_import_check_files_for_cudaq::cudaq-python-interop "${_IMPORT_PREFIX}/lib/libcudaq-python-interop.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
