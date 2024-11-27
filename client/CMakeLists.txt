cmake_minimum_required(VERSION 3.27)
project(client)

set(CMAKE_CXX_STANDARD 17)
add_executable(client main.cpp)
set(RAYLIB_VERSION 4.5.0)
find_package(raylib ${RAYLIB_VERSION} QUIET) # QUIET or REQUIRED
if (NOT raylib_FOUND) # If there's none, fetch and build raylib
    include(FetchContent)
    FetchContent_Declare(
            raylib
            DOWNLOAD_EXTRACT_TIMESTAMP OFF
            URL https://github.com/raysan5/raylib/archive/refs/tags/${RAYLIB_VERSION}.tar.gz
    )
    FetchContent_GetProperties(raylib)
    if (NOT raylib_POPULATED) # Have we downloaded raylib yet?
        set(FETCHCONTENT_QUIET NO)
        FetchContent_Populate(raylib)
        set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE) # don't build the supplied examples
        add_subdirectory(${raylib_SOURCE_DIR} ${raylib_BINARY_DIR})
    endif()
endif()
target_link_libraries(${PROJECT_NAME} raylib)
if (${PLATFORM} STREQUAL "Web")
    # Tell Emscripten to build an example.html file.
    set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".html")
endif()

# Checks if OSX and links appropriate frameworks (Only required on MacOS)
if (APPLE)
    target_link_libraries(${PROJECT_NAME} "-framework IOKit")
    target_link_libraries(${PROJECT_NAME} "-framework Cocoa")
    target_link_libraries(${PROJECT_NAME} "-framework OpenGL")
endif()
set(BOOST_ROOT "C:/Users/benra/Downloads/boost_1_86_0/boost_1_86_0/")
set(BOOST_LIBRARYDIR "C:/Users/benra/Downloads/boost_1_86_0/boost_1_86_0/stage/lib")
set(Boost_INCLUDE_DIR "C:/Users/benra/Downloads/boost_1_86_0/boost_1_86_0")
set(Boost_SYSTEM_LIBRARY "C:/Users/benra/Downloads/boost_1_86_0/boost_1_86_0/stage/lib/boost_system-vc143-mt-x64-1_86.lib")


# Specify Boost details
set(Boost_NO_SYSTEM_PATHS ON)
set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED ON)

# Verbose finding
find_package(Boost REQUIRED COMPONENTS system)

# Debug information
if(NOT Boost_FOUND)
    message(FATAL_ERROR "Boost not found. Details: ${Boost_ERROR_REASON}")
endif()

# Include and link
target_include_directories(${PROJECT_NAME} PRIVATE ${Boost_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} ${Boost_LIBRARIES} ws2_32)
#set(CMAKE_EXE_LINKER_FLAGS "-static")
