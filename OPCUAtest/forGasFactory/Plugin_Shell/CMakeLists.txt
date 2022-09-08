PROJECT (Plugin_Shell)
CMAKE_MINIMUM_REQUIRED (VERSION 2.8)

if (CMAKE_BUILD_TYPE STREQUAL Debug)
      SET(CMAKE_DEBUG_POSTFIX "d")
endif (CMAKE_BUILD_TYPE STREQUAL Debug)


# convert build type to lower case
IF (CMAKE_BUILD_TYPE)
  STRING(TOLOWER ${CMAKE_BUILD_TYPE} CMAKE_BUILD_TYPE_TOLOWER)
ELSE(CMAKE_BUILD_TYPE)
  # set default configuration to release
  SET(CMAKE_BUILD_TYPE "Release")
  STRING(TOLOWER ${CMAKE_BUILD_TYPE} CMAKE_BUILD_TYPE_TOLOWER)
ENDIF(CMAKE_BUILD_TYPE)


IF (UNIX)
    INCLUDE_DIRECTORIES()
    ADD_DEFINITIONS(-Wall)
    SET(PLATTFORM_LIBS pthread rt ssl xml2 crypto)
ENDIF (UNIX)

add_library(
        ${PROJECT_NAME} 
        SHARED
        shell.cpp)


install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ../bin
        LIBRARY DESTINATION ../plugins
        ARCHIVE DESTINATION ../plugins
)

