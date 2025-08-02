#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "nvqir::nvqir" for configuration "Release"
set_property(TARGET nvqir::nvqir APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nvqir::nvqir PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnvqir.so"
  IMPORTED_SONAME_RELEASE "libnvqir.so"
  )

list(APPEND _cmake_import_check_targets nvqir::nvqir )
list(APPEND _cmake_import_check_files_for_nvqir::nvqir "${_IMPORT_PREFIX}/lib/libnvqir.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
