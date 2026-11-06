# 14｜C++ 结构体（struct）：成员、数组、指针与内存——Python 对照笔记

> 学习阶段：Windows + VS Code + MSYS2 UCRT64 / G++，以 **C++17** 为主要实验标准。  
> 本篇根据本节课程的 6 张截图整理，按「定义结构体 → 默认成员值 → 结构体数组 → 结构体指针 → 指针数组/动态数组 → 内存理解」展开，并补充 Python 对照及截图中的易混淆细节。

## 1. 为什么需要结构体？

如果要保存一位学生的信息，独立变量可以这样写：

```cpp
std::string name = "小明";
std::string major_code = "003032";
int dormitory_num = 1;
```

但是当有很多学生时，信息就很难作为一个整体管理。结构体（`struct`）允许我们**自己定义一个类型，把不同类型的相关成员组织在一起**。

```cpp
#include <string>

struct Student {
    std::string name;
    std::string major_code;
    int dormitory_num;
};  // 注意结尾的分号
```

现在 `Student` 是一个**类型名**，`name`、`major_code`、`dormitory_num` 是它的**数据成员**。这段代码定义类型，并不会自动创建某个具体学生对象。

**Python 类比**：类似用 `@dataclass` 声明一个数据类：

```python
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    major_code: str
    dormitory_num: int

s1 = Student("小明", "003032", 1)
```

区别：Python 的名字通常绑定到对象，C++ 的 `Student s1` 则声明一个具体的、具有 `Student` 类型的对象。C++ 成员的内存布局与生命周期也更加直接地由类型决定。

## 2. 声明、初始化与访问成员：`.`

```cpp
Student s1 = {"小明", "003032", 1};
std::cout << s1.name << '\n';
std::cout << s1.dormitory_num << '\n';

s1.dormitory_num = 3;  // 修改成员
```

拆开来看：

| 写法 | 含义 |
|---|---|
| `struct Student { ... };` | 定义结构体类型 |
| `Student s1` | 创建一个 `Student` 对象，变量名叫 `s1` |
| `{...}` | 按成员声明顺序进行聚合初始化（本例） |
| `s1.name` | 使用 `.` 访问对象的成员 |
| `s1.dormitory_num = 3` | 修改对象的一个成员 |

在 **C++ 中**，定义了 `Student` 后，通常直接写 `Student s1;`，不用像某些 C 语言教材那样每次写 `struct Student s1;`；两种形式在这里都可以使用。

### 创建对象与声明类型有什么区别？

```cpp
struct Student { int age; }; // 定义“模板/类型”
Student a{18};              // 创建具体对象 a
Student b{20};              // 创建另一个独立对象 b
```

`a` 和 `b` 有各自独立的成员数据，修改 `a.age` 不影响 `b.age`。

## 3. 结构体成员的默认值

截图中的 `Student` 给专业代码和宿舍号设了默认值：

```cpp
#include <string>

struct Student {
    std::string name;
    std::string major_code = "003032";
    int dormitory_num = 1;
};

Student s1{"小明"};                 // 其余两项沿用默认值
Student s2{"小红", "003001", 3};   // 显式提供的值覆盖默认值
```

`Student s1{"小明"}` 的结果：

| 成员 | 结果 | 来源 |
|---|---|---|
| `name` | `"小明"` | 显式初始化 |
| `major_code` | `"003032"` | 默认成员初始化器 |
| `dormitory_num` | `1` | 默认成员初始化器 |

**注意截图中 `.name:`、`.major_code:`、`.dormitory_num:` 这样的灰色小标签：**它们很可能是 VS Code 的 **inlay hints（行内参数/成员名称提示）**，不是源码的真实字符。如果需要写 C++17 代码，使用上面的**按顺序初始化**即可。

C++20 支持真正的指定成员初始化语法：

```cpp
// 需要 C++20；成员指定顺序须符合声明顺序
Student s3{.name = "小明", .major_code = "003001", .dormitory_num = 3};
```

不要把编辑器显示的 `.name:` 标签直接复制成 C++ 代码；真正的 C++20 语法使用 `=`。

## 4. 结构体数组：同一类型的多个对象

截图说明了：**结构体是一种自定义类型，也可以成为数组的元素类型。**

```cpp
Student students[3] = {
    {"小明"},
    {"小红", "003001", 2},
    {"小刚", "003002", 3}
};

std::cout << students[0].name << '\n';
students[1].dormitory_num = 5;
```

- `students` 是一个**数组对象**，包含 3 个 `Student` 元素。
- `students[0]` 是一个 `Student` 对象，所以用 `students[0].name` 取其成员。
- 对于本例这类简单结构体，数组元素可连续存放；各 `Student` 对象之间的步长是 `sizeof(Student)`，而不一定是所有成员 `sizeof` 的简单相加。
- 数组长度固定；如果希望运行时扩容，优先使用 `std::vector<Student>`。

**Python 类比**：

```python
students = [Student("小明", "003032", 1), Student("小红", "003001", 2)]
print(students[0].name)
```

Python `list` 通常存放的是对象引用；C++ 的 `Student students[3]` 则直接包含三个 `Student` 元素对象。

### 初始化和后续赋值不是一回事

```cpp
Student students[2] = {{"甲"}, {"乙"}};  // 声明时初始化整个数组
students[0] = Student{"丙", "003009", 4}; // 对已有元素赋值
// students = ...;                          // 内置数组整体不能用 = 重新赋值
```

## 5. 结构体指针：`&`、`*`、`.` 与 `->`

截图先给出已有结构体对象的地址，再演示通过 `new` 动态创建结构体。

```cpp
Student stu{"小明", "003001", 5};
Student* p = &stu;

std::cout << stu.name << '\n';    // 对象：用 .
std::cout << p->name << '\n';     // 指针：用 ->
std::cout << (*p).name << '\n';   // 同样正确
```

**最重要的等式：**

```cpp
p->name  ==  (*p).name
```

这里比较的是两种访问表达式的效果：`*p` 先访问 `p` 指向的结构体对象，随后 `.` 访问它的成员。括号不能省略成 `*p.name`，因为成员访问符 `.` 的优先级更高。

| 表达式 | 结果/意义 |
|---|---|
| `stu` | 结构体对象 |
| `&stu` | 结构体对象的地址 |
| `p` | 保存 `stu` 地址的指针变量 |
| `*p` | 通过指针访问整个 `stu` 对象 |
| `stu.name` | 直接访问对象成员 |
| `p->name` | 通过指针访问成员 |
| `&p` | 指针变量 `p` 自己的地址 |

### 用内存地址理解

假设 `stu` 在 `0x1000`，而指针 `p` 自己在 `0x2000`：

```text
栈 / 当前作用域中的对象（示意）

地址 0x2000： p ──保存 0x1000 ─────┐
                                   │
地址 0x1000： stu <─────────────────┘
              ├─ name
              ├─ major_code
              └─ dormitory_num
```

`p` 本身只保存**地址**，并没有复制 `stu` 这三个成员。执行 `p->dormitory_num = 6` 修改的是同一个 `stu` 对象。

## 6. 使用 `new` 动态创建结构体

```cpp
Student* p = new Student{"小明", "003001", 5};
std::cout << p->name << '\n';
p->dormitory_num = 6;

delete p;
p = nullptr;
```

和你之前学习的 `int* p = new int(10)` 同样可以理解为两个不同实体：

- 局部指针变量 `p`：在常见 64 位程序中通常占 8 字节，保存地址。
- `new Student{...}` 创建的动态 `Student` 对象：大小由 `sizeof(Student)` 决定，包括其成员和可能的内存对齐；`std::string` 成员还可能单独管理额外动态存储。

**`delete p` 销毁动态对象并释放相应存储，不是销毁局部指针变量 `p`。** 删除之后旧地址不可再解引用，因此经常把 `p` 置为 `nullptr`。

> 现代 C++ 更推荐 `std::unique_ptr<Student>`、`std::make_unique<Student>()` 来管理动态对象；这里保留 `new/delete` 是为了理解课程中的内存机制。

## 7. 结构体数组与指针：两种方式

### 方式 A：指针指向已有数组首元素

```cpp
Student arr[3] = {
    {"甲"}, {"乙"}, {"丙", "003001", 3}
};

Student* p = arr; // 这里 arr 转换为指向首元素的指针

std::cout << p[0].name << '\n';
std::cout << p[1].name << '\n';
std::cout << (p + 2)->name << '\n';
```

`p[i]` 等价于 `*(p+i)`，因此 `p[i].name` 是有效写法。`arr` **本身是数组，不是指针变量**，只是在这里发生了数组到指针的转换。

### 方式 B：动态分配结构体数组

```cpp
Student* p = new Student[3]{
    {"甲"},
    {"乙"},
    {"丙", "003001", 3}
};

std::cout << p[0].name << '\n';
std::cout << p[2].dormitory_num << '\n';

delete[] p; // new[] 必须与 delete[] 对应
p = nullptr;
```

**注意**：这里连续的是 3 个 `Student` 对象的数组布局；其中 `std::string` 对象内部管理的字符存储不保证全部紧挨在一起。

### 更推荐的现代写法

```cpp
#include <vector>
std::vector<Student> students = {{"甲"}, {"乙"}, {"丙"}};
students.push_back(Student{"丁", "003003", 4});
```

`std::vector` 管理可扩容的元素存储，无须自己匹配 `new[]/delete[]`。

## 8. 一次看懂成员、内存与 `sizeof`

你学过的 `int age = 20` 只有一个普通数据成员；结构体则是一个**由多个成员组成的对象**。

```cpp
struct Sample {
    char flag;  // 通常 1 字节
    int value;  // Windows GCC x64 通常 4 字节
};
```

如果把 `sizeof(Sample)` 想成 `1 + 4 = 5` 就可能出错，因为编译器通常要为成员对齐插入**填充字节（padding）**。在常见环境中可能得到 8 字节，具体结果要以编译器与平台为准。

```cpp
#include <iostream>

struct Sample { char flag; int value; };

int main() {
    std::cout << sizeof(char) << '\n';
    std::cout << sizeof(int) << '\n';
    std::cout << sizeof(Sample) << '\n';
}
```

对于包含 `std::string` 的结构体，更不能只凭字符串文字的长度推算 `sizeof(Student)`：字符串对象本身具有实现相关的表示形式。

## 9. 和 Python 的核心区别

| 主题 | Python | C++ |
|---|---|---|
| 把不同字段组织在一起 | `dataclass`、普通类、字典 | `struct`、`class` |
| 访问属性/成员 | `student.name` | 对象 `stu.name`；指针 `p->name` |
| 多个学生 | `list[Student]` | `Student arr[N]` 或 `std::vector<Student>` |
| 对象内存管理 | Python 运行时通常自动管理 | 自动对象、RAII 容器或显式动态分配 |
| 类型与布局 | 对象布局由 Python 实现决定 | 结构体字段类型明确，布局/对齐可进一步分析 |

> Python 中的 `student.name` 和 C++ 中的 `stu.name` 写法接近，但 Python 对象与 C++ 结构体的内存模型不同。切勿把 Python `list` 当成 C++ 的结构体数组。

## 10. 与 ggml / llama.cpp 的联系（拓展）

之后阅读量化源码时，你会看到把数值数据与元数据放在一个结构体中的设计。例如**仅作为教学示意、不是实际库定义**：

```cpp
#include <cstdint>

struct QuantBlockExample {
    float scale;
    std::uint8_t packed[16];
};
```

- `scale` 存储某种缩放参数；
- `packed` 存储一段打包后的字节；
- 一组 `QuantBlockExample` 可以形成连续的块数组；
- `QuantBlockExample* p` 可以通过 `p[i].scale` 或 `(p+i)->scale` 访问第 `i` 块。

这一节理解的 `struct`、数组、指针和内存布局，正好是继续阅读量化 Block 结构的基础。

## 11. 综合实验（适配 G++ / C++17）

将代码保存为 `struct_test.cpp`：

```cpp
#include <iostream>
#include <string>
#include <vector>

struct Student {
    std::string name;
    std::string major_code = "003032";
    int dormitory_num = 1;
};

int main() {
    Student s1{"Alice"};
    Student s2{"Bob", "003001", 3};

    std::cout << s1.name << ": " << s1.major_code << ", "
              << s1.dormitory_num << '\n';

    Student* p = &s2;
    p->dormitory_num = 5;
    std::cout << s2.name << ": " << (*p).dormitory_num << '\n';

    Student arr[2] = {s1, s2};
    std::cout << arr[0].name << " / " << arr[1].name << '\n';

    Student* dynamic_arr = new Student[2]{{"Carol"}, {"Dave", "003003", 4}};
    std::cout << dynamic_arr[0].name << " / " << dynamic_arr[1].name << '\n';
    delete[] dynamic_arr;
    dynamic_arr = nullptr;

    std::vector<Student> students = {s1, s2};
    students.push_back(Student{"Eve"});
    std::cout << "vector size = " << students.size() << '\n';

    std::cout << "sizeof(Student) = " << sizeof(Student) << '\n';
    return 0;
}
```

在 PowerShell 中编译、运行：

```powershell
g++ -std=c++17 -Wall -Wextra -pedantic struct_test.cpp -o struct_test.exe
.\struct_test.exe
```

其中 `sizeof(Student)` 结果依赖于你的标准库实现和 ABI，不必与其他电脑完全相同。

## 12. 常见误区与本节总结

| 容易混淆的说法 | 更准确的理解 |
|---|---|
| `struct` 声明就申请了一位学生的数据空间 | 先定义的是**类型**，之后创建对象才有具体成员数据 |
| 结构体只能包含不同类型成员 | 可以包含不同类型，也可以多个成员相同类型 |
| `struct` 成员只能用 `.` 访问 | 对象用 `.`；指向对象的指针用 `->` |
| `Student* p` 保存了完整的 Student 数据 | `p` 保存地址；数据属于它指向的对象 |
| 结构体数组就是指针数组 | `Student arr[N]` 的元素是 `Student`，`Student* ptrs[N]` 的元素才是指针 |
| `new Student[3]` 之后可以 `delete p` | 必须匹配 `delete[] p` |
| `sizeof(Student)` 等于各成员字节数简单相加 | 可能存在内存对齐和填充 |
| VS Code 的 `.name:` 提示就是 C++ 初始化代码 | 通常是编辑器提示；C++20 真正指定初始化写作 `.name = ...` |

### 快速自测

1. `struct Student { ... };` 与 `Student stu{...};` 哪个是类型定义，哪个创建对象？
2. `Student* p = &stu;` 中，`p`、`*p`、`&p` 分别是什么意思？
3. 为什么 `stu.name` 和 `p->name` 都正确，但 `p.name` 不正确？
4. `Student arr[3]` 与 `Student* arr[3]` 在元素类型上有什么区别？
5. `new Student[3]` 为什么必须用 `delete[]`？

**参考答案：**（1）前者定义类型，后者创建对象。（2）所指对象地址、所指结构体对象、指针自身地址。（3）`p` 是指针而非结构体对象。（4）前者每个元素是结构体，后者每个元素是结构体指针。（5）数组形式的动态分配要与数组形式释放匹配。

---

**本节核心一句话：**`struct` 负责把多个成员组织成一种类型；结构体对象保存具体成员数据；结构体数组把多个对象连续组织；结构体指针保存对象地址，通过 `->` 访问成员。理解这些，再读复杂的 C++ 类和 ggml 数据结构就容易得多。
