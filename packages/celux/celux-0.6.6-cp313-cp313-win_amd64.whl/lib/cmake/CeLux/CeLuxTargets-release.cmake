#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CeLux::CeLuxLib" for configuration "Release"
set_property(TARGET CeLux::CeLuxLib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CeLux::CeLuxLib PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/CeLuxLib.lib"
  )

list(APPEND _cmake_import_check_targets CeLux::CeLuxLib )
list(APPEND _cmake_import_check_files_for_CeLux::CeLuxLib "${_IMPORT_PREFIX}/lib/CeLuxLib.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
