cmake_minimum_required(VERSION 3.22.1)

include($ENV{DEVKIT_LOCATION}/cmake/pluginEntry.cmake)

set(PROJECT_NAME SnapToTheGround)

set(SOURCE_FILES src/main.cpp)

set(LIBRARIES 
    OpenMaya Foundation
)

build_plugin()
