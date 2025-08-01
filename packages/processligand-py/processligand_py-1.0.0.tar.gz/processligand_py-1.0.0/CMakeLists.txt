# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(processligand_builder C)

include(FetchContent)

set(PROCESSLIGAND_EXE_PATH "" CACHE FILEPATH "Path to the pre-compiled ProcessLigand executable")
# Automatically append .exe on Windows if it's missing
if(WIN32)
    if(NOT "${PROCESSLIGAND_EXE_PATH}" MATCHES "\\.exe$")
        set(PROCESSLIGAND_EXE_PATH "${PROCESSLIGAND_EXE_PATH}.exe" CACHE FILEPATH "Path to the pre-compiled ProcessLigand executable" FORCE)
    endif()
endif()

if(NOT PROCESSLIGAND_EXE_PATH)
    message(FATAL_ERROR "Path to ProcessLigand not set. Please set PROCESSLIGAND_EXE_PATH.")
endif()

add_executable(ProcessLigand IMPORTED GLOBAL)

set_target_properties(ProcessLigand PROPERTIES
    IMPORTED_LOCATION "${PROCESSLIGAND_EXE_PATH}"
)

set(PROCESSLIGAND_EXECUTABLE $<TARGET_FILE:ProcessLigand>)

install(PROGRAMS ${PROCESSLIGAND_EXECUTABLE}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/processligandpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/processligandpy/processligand_wrapper.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)