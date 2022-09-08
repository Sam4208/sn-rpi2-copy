project(Plugin_Shell)
cmake_minimum_required(VERSION 2.8)
SET(CMAKE_DEBUG_POSTFIX "d")

if ( EXISTS ${BUILD_PLATFORM_TYPE} )
         #SET(BUILD_PLATFORM_TYPE "_X86")
elseif()
        SET(BUILD_PLATFORM_TYPE "_X86")
endif()

    
MESSAGE( STATUS "" )
MESSAGE( STATUS "==============================================" )
MESSAGE( STATUS "Now configuring serveur_OPCUA CMakeLists.txt" )
MESSAGE( STATUS "==============================================" )

    include_directories(${CMAKE_CURRENT_SOURCE_DIR})
    link_directories(${CMAKE_CURRENT_SOURCE_DIR}/share)
IF (UNIX)
    INCLUDE_DIRECTORIES()
    ADD_DEFINITIONS(-Wall)
    SET(PLATTFORM_LIBS pthread rt dl)
ENDIF (UNIX)


# create library
add_library(
         ${PROJECT_NAME}
	SHARED
	shell.cpp
        )
TARGET_LINK_LIBRARIES(${PROJECT_NAME} PluginBase)
set_target_properties( PROPERTIES DEBUG_POSTFIX "d")

# configure output path
INSTALL(TARGETS  ${PROJECT_NAME}
        RUNTIME DESTINATION ../bin${BUILD_PLATFORM_TYPE}
        LIBRARY DESTINATION ../lib${BUILD_PLATFORM_TYPE}
        ARCHIVE DESTINATION ../lib${BUILD_PLATFORM_TYPE}
)
