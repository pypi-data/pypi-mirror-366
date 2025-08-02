cmake_minimum_required(VERSION 3.18)

# Force Ninja generator on Windows if using MinGW
if(WIN32 AND NOT DEFINED CMAKE_GENERATOR)
  set(CMAKE_GENERATOR "Ninja")
endif()

project(axon-py LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# For MinGW on Windows
if(WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

file(GLOB_RECURSE CSRC_FILES "axon/csrc/*.c" "axon/csrc/*.cpp")
file(GLOB_RECURSE INC_FILES "axon/inc/*.h" "axon/inc/*.hpp")

message(STATUS "Found source files: ${CSRC_FILES}")
message(STATUS "Found header files: ${INC_FILES}")

if(NOT CSRC_FILES)
  message(FATAL_ERROR "No source files found in axon/csrc/")
endif()

add_library(array SHARED ${CSRC_FILES})
target_include_directories(array PRIVATE axon/inc)
target_link_libraries(array PRIVATE Python::Module)

if(WIN32)
  set_target_properties(array PROPERTIES SUFFIX ".pyd")
else()
  set_target_properties(array PROPERTIES PREFIX "lib")
endif()

install(TARGETS array DESTINATION axon COMPONENT python_modules)
install(DIRECTORY axon/ DESTINATION axon COMPONENT python_modules FILES_MATCHING PATTERN "*.py")