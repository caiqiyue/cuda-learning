cmake_minimum_required(VERSION 3.20)

project(student_ggml_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 关闭 ggml 自己的测试、示例和服务器
set(GGML_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_SERVER OFF CACHE BOOL "" FORCE)

# 优先使用仓库内 vendored 的 ggml 源码（上游 git 历史已删除），
# 这样构建不再需要联网下载，源码与本项目真正合为一体。
set(GGML_LOCAL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../ggml)

if(EXISTS ${GGML_LOCAL_DIR}/CMakeLists.txt)
    message(STATUS "使用本地 ggml 源码: ${GGML_LOCAL_DIR}")
    add_subdirectory(${GGML_LOCAL_DIR} ${CMAKE_CURRENT_BINARY_DIR}/ggml-build)
else()
    # 兜底：本地没有 vendored 源码时，从网络下载
    message(STATUS "未找到本地 ggml 源码，回退到网络下载")
    include(FetchContent)
    set(FETCHCONTENT_UPDATES_DISCONNECTED ON)

    FetchContent_Declare(
        ggml
        URL https://github.com/ggml-org/ggml/archive/refs/heads/master.tar.gz
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )

    FetchContent_MakeAvailable(ggml)
endif()

add_executable(student_ggml_app
    main.cpp
    student.cpp
)

target_link_libraries(student_ggml_app
    PRIVATE
        ggml::ggml
)