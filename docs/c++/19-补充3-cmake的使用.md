# C++ 工程补充笔记：\`#include\`、CMake 与第三方库

## 一、\`#include\` 的作用

```
#include "student.h"
#include <vector>
```

`#include` 是预处理指令。

在编译之前，预处理器会读取对应文件，并把其内容插入当前源文件中。

例如：

```
#include "student.h"
```

可以近似理解为：

```
// 把 student.h 的内容复制到这里
```

它主要解决的是：

> 让当前源文件看到其他文件中的声明、类型和接口。

但 `#include` 本身不会自动把函数实现链接进程序。函数实现仍然需要通过 `.cpp` 文件或库文件参与编译和链接。

---

# 二、\`<...>\` 和 `"..."` 的区别

## 1. 尖括号

```
#include <iostream>
#include <vector>
#include <memory>
```

通常用于：

* C++ 标准库
* 系统库
* 已安装的第三方库

编译器通常会优先搜索系统和编译器配置的头文件目录。

---

## 2. 双引号

```
#include "student.h"
#include "config.h"
```

通常用于：

* 当前项目自己的头文件
* 项目内部的模块文件
* 相对路径下的头文件

编译器通常会优先搜索当前源文件相关目录，然后再搜索其他配置的头文件目录。

---

## 3. 对比示例

项目结构：

```
project/
├── main.cpp
└── student.h
```

`main.cpp`：

```
#include "student.h"
#include <iostream>
```

推荐规则：

```
#include <iostream>   // 标准库
#include <vector>      // 标准库
#include "student.h"   // 项目自己的头文件
```

需要注意：

> `<...>` 和 `"..."` 不是绝对的“系统库”和“自定义库”分类，而是默认搜索路径不同。

---

# 三、C++ 如何使用第三方代码？

使用第三方库通常需要两部分：

```
头文件
    ↓
提供声明，让编译器知道有哪些函数和类型

库文件或源代码
    ↓
提供真正的函数实现，供链接器使用
```

例如：

```
#include <some_library.h>
```

只说明当前文件要使用这个库的接口。

最终构建时还需要：

* 找到头文件目录
* 编译第三方源代码，或者找到已经编译好的库
* 把库链接到自己的程序

因此：

```
include 解决“看见声明”
link    解决“找到实现”
```

---

# 四、CMake 是什么？

CMake 是一个**构建系统生成工具**。

它本身不是编译器，而是根据项目配置生成构建文件，然后调用：

* g++
* clang++
* MSVC
* Ninja
* Make

等工具完成编译和链接。

CMake 主要负责：

* 管理多个 `.cpp` 文件
* 指定 C++ 标准
* 添加头文件目录
* 添加库文件
* 下载第三方依赖
* 生成可执行程序
* 区分 Debug 和 Release
* 适配不同操作系统和编译器

---

# 五、基本项目结构

```
my_project/
├── CMakeLists.txt
├── main.cpp
├── student.cpp
└── student.h
```

其中：


| 文件             | 作用               |
| ---------------- | ------------------ |
| `CMakeLists.txt` | CMake 的项目配置   |
| `main.cpp`       | 程序入口           |
| `student.cpp`    | 函数实现           |
| `student.h`      | 函数声明和类型定义 |

---

# 六、最简单的 `CMakeLists.txt`

```
cmake_minimum_required(VERSION 3.20)

project(student_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(student_app
    main.cpp
    student.cpp
)
```

## 关键部分

### 指定最低 CMake 版本

```
cmake_minimum_required(VERSION 3.20)
```

### 定义项目名称

```
project(student_app LANGUAGES CXX)
```

### 指定 C++ 标准

```
set(CMAKE_CXX_STANDARD 17)
```

### 创建可执行程序

```
add_executable(student_app
    main.cpp
    student.cpp
)
```

这里的 `student_app` 是目标名称，也决定最终程序名称：

```
student_app.exe
```

---

# 七、CMake 的构建流程

在项目根目录执行：

```
cmake -S . -B build
```

含义：


| 参数       | 含义                      |
| ---------- | ------------------------- |
| `-S .`     | 源代码目录是当前目录      |
| `-B build` | 将构建文件放入`build`目录 |

这一步叫：

```
配置阶段
```

CMake 会：

* 读取 `CMakeLists.txt`
* 检查编译器
* 检查依赖
* 生成 Ninja、Make 或 Visual Studio 工程文件

然后执行：

```
cmake --build build
```

这一步叫：

```
构建阶段
```

它会：

* 编译 `.cpp`
* 生成目标文件
* 链接库
* 生成 `.exe`

运行程序：

```
.\build\student_app.exe
```

---

# 八、为什么使用单独的 `build` 目录？

推荐结构：

```
my_project/
├── CMakeLists.txt
├── main.cpp
├── student.cpp
├── student.h
└── build/
```

源代码和构建产物分开有很多好处：

* 源代码目录保持整洁
* 编译中间文件集中保存
* 可以随时删除 `build`
* 不影响源代码
* 便于 Debug 和 Release 分离

删除构建目录后，可以重新生成：

```
Remove-Item -Recurse -Force build
cmake -S . -B build
cmake --build build
```

---

# 九、CMake 下载第三方库

CMake 可以通过 `FetchContent` 自动下载外部代码。

例如下载 ggml：

```
include(FetchContent)

FetchContent_Declare(
    ggml
    URL https://github.com/ggml-org/ggml/archive/refs/heads/master.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(ggml)
```

这段配置表示：

1. 声明一个叫 `ggml` 的外部依赖
2. 下载 ggml 压缩包
3. 解压源码
4. 加入 ggml 自己的 CMake 工程
5. 编译出 ggml 库目标

通常会被下载到：

```
build/_deps/
```

---

# 十、完整的 ggml 项目配置

项目结构：

```
ggml_demo/
├── CMakeLists.txt
└── main.cpp
```

## `CMakeLists.txt`

```
cmake_minimum_required(VERSION 3.20)

project(ggml_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 关闭 ggml 的测试、示例和服务器
set(GGML_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_SERVER OFF CACHE BOOL "" FORCE)

include(FetchContent)

FetchContent_Declare(
    ggml
    URL https://github.com/ggml-org/ggml/archive/refs/heads/master.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(ggml)

add_executable(ggml_demo
    main.cpp
)

target_link_libraries(ggml_demo
    PRIVATE
        ggml::ggml
)
```

## `main.cpp`

```
#include "ggml.h"

#include <iostream>

int main()
{
    ggml_init_params params{};

    params.mem_size = 16 * 1024 * 1024;
    params.mem_buffer = nullptr;
    params.no_alloc = false;

    ggml_context* context = ggml_init(params);

    if (context == nullptr)
    {
        std::cerr << "failed to create ggml context\n";
        return 1;
    }

    ggml_tensor* tensor = ggml_new_tensor_1d(
        context,
        GGML_TYPE_F32,
        4
    );

    if (tensor == nullptr)
    {
        std::cerr << "failed to create tensor\n";
        ggml_free(context);
        return 1;
    }

    ggml_set_name(tensor, "demo_tensor");

    std::cout << "tensor name: "
              << ggml_get_name(tensor)
              << '\n';

    std::cout << "tensor elements: "
              << ggml_nelements(tensor)
              << '\n';

    std::cout << "tensor bytes: "
              << ggml_nbytes(tensor)
              << '\n';

    ggml_free(context);

    return 0;
}
```

---

# 十一、\`target\_link\_libraries\` 的作用

```
target_link_libraries(ggml_demo
    PRIVATE
        ggml::ggml
)
```

表示：

> 将 `ggml::ggml` 这个库链接到 `ggml_demo` 程序。

同时，CMake 目标通常会自动传递：

* ggml 的头文件目录
* 必要的编译选项
* ggml 的依赖库
* 平台相关设置

所以代码中可以直接写：

```
#include "ggml.h"
```

不一定需要手动写：

```
include_directories(...)
```

现代 CMake 更推荐：

```
target_link_libraries(...)
```

让依赖通过目标传播。

---

# 十二、同时使用自己的代码和第三方库

例如：

```
project/
├── CMakeLists.txt
├── main.cpp
├── student.cpp
└── student.h
```

`main.cpp` 同时使用：

```
#include "student.h"
#include "ggml.h"
```

对应的 CMake：

```
cmake_minimum_required(VERSION 3.20)

project(student_ggml_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(GGML_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_SERVER OFF CACHE BOOL "" FORCE)

include(FetchContent)

FetchContent_Declare(
    ggml
    URL https://github.com/ggml-org/ggml/archive/refs/heads/master.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(ggml)

add_executable(student_ggml_app
    main.cpp
    student.cpp
)

target_link_libraries(student_ggml_app
    PRIVATE
        ggml::ggml
)
```

这里：

```
add_executable(student_ggml_app
    main.cpp
    student.cpp
)
```

表示编译自己的两个源文件。

```
target_link_libraries(student_ggml_app
    PRIVATE
        ggml::ggml
)
```

表示额外链接 ggml。

最终生成：

```
student_ggml_app.exe
```

---

# 十三、完整构建命令

在包含 `CMakeLists.txt` 的目录执行：

```
cmake -S . -B build
```

然后：

```
cmake --build build
```

运行：

```
.\build\student_ggml_app.exe
```

完整流程：

```
CMakeLists.txt
      ↓
cmake -S . -B build
      ↓
配置项目、下载依赖、生成构建文件
      ↓
cmake --build build
      ↓
编译源文件、编译第三方库、执行链接
      ↓
生成 .exe
```

---

# 十四、构建系统中的几个重要概念

## 1. 源文件

```
.cpp
```

保存具体实现，需要被编译。

## 2. 头文件

```
.h
.hpp
```

保存声明、类型和接口，通常被 `#include`。

## 3. 目标

```
add_executable(student_app ...)
```

定义一个构建目标。

目标可以是：

* 可执行程序
* 静态库
* 动态库
* 接口库

## 4. 库

第三方库可能以这些形式存在：

```
.a
.lib
.dll
```

或者直接以源代码形式加入项目。

## 5. 链接

把多个目标文件和库组合成最终程序：

```
main.cpp
student.cpp
ggml
标准库
      ↓
最终可执行程序
```

---

# 十五、核心知识总结

```
#include <...>
    通常用于标准库、系统库和已安装库

#include "..."
    通常用于项目自己的头文件

CMakeLists.txt
    描述项目如何构建

FetchContent
    让 CMake 自动获取外部依赖

add_executable
    创建可执行程序目标

target_link_libraries
    将库链接到目标程序

cmake -S . -B build
    配置项目并生成构建文件

cmake --build build
    编译和链接项目

build/
    保存构建产物和第三方依赖
```

最重要的关系是：

```
#include
    让编译器看到声明

.cpp 文件
    提供函数实现

第三方库
    提供外部实现

CMake
    管理源文件、库、编译和链接过程
```
