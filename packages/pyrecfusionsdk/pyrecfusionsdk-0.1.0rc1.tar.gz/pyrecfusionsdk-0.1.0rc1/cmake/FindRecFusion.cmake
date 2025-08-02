include(CheckCXXSourceCompiles)

function(find_recfusionsdk)
    # Development RecFusionSDK path
    set(RF_DEV_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third-party/RecFusionSDK/")

    find_path(
        RECFUSION_INCLUDE_DIR
        NAMES RecFusion.h
        HINTS $ENV{RECFUSION_SDK}/include ${RF_DEV_DIR}/include
    )

    if(NOT RECFUSION_INCLUDE_DIR)
        return()
    endif()

    find_library(
        RECFUSION_LIBRARY
        NAMES RecFusionSDK
        HINTS $ENV{RECFUSION_SDK}/lib ${RF_DEV_DIR}/lib
    )

    if(NOT RECFUSION_LIBRARY)
        return()
    endif()

    # These variables are used by check_cxx_source_compiles()
    # to compile the C++/RecFusionSDK snippet
    set(CMAKE_REQUIRED_FLAGS)
    set(CMAKE_REQUIRED_INCLUDES ${RECFUSION_INCLUDE_DIR})
    set(CMAKE_REQUIRED_LIBRARIES ${RECFUSION_LIBRARY})

    # Compile a test program which imports the RecFusionSDK library
    # and runs one instruction
    check_cxx_source_compiles(
        [=[
#include <RecFusion.h>

using namespace RecFusion;

int main() {
  RecFusionSDK::majorVersion();
}
]=]
        RECFUSION_links
        SRC_EXT
        cpp
    )
    if(NOT RECFUSION_links)
        return()
    endif()

    set(RECFUSION_FOUND ${RECFUSION_links} PARENT_SCOPE)
    set(RECFUSION_INCLUDE_DIR ${CMAKE_REQUIRED_INCLUDES} PARENT_SCOPE)
    set(RECFUSION_LIBRARY ${CMAKE_REQUIRED_LIBRARIES} PARENT_SCOPE)
endfunction()

find_recfusionsdk()

# Define the RecFusion target if the SDK was found!
if(RECFUSION_FOUND)
    if(NOT TARGET RecFusion::RecFusion_CXX)
        add_library(RecFusion::RecFusion_CXX INTERFACE IMPORTED)
        set_property(
            TARGET RecFusion::RecFusion_CXX
            PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${RECFUSION_INCLUDE_DIR}"
        )
        set_property(
            TARGET RecFusion::RecFusion_CXX
            PROPERTY INTERFACE_LINK_LIBRARIES "${RECFUSION_LIBRARY}"
        )
    endif()
endif()

message(STATUS "Found RecFusionSDK: ${RECFUSION_FOUND}")
if(RECFUSION_FOUND)
    message(STATUS "Found RecFusionSDK library: ${RECFUSION_LIBRARY}")
    message(
        STATUS
        "Found RecFusionSDK include directory: ${RECFUSION_INCLUDE_DIR}"
    )
endif()
