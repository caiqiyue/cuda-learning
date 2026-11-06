# 05｜C++ 整型与浮点型详解（Python 对照笔记）

> **学习背景**：已经会 Python，正在 Windows + VS Code + MSYS2 UCRT64（G++）环境中学习 C++。  
> **资料范围**：根据本次提供的六张课程截图整理：整型种类与大小、signed/unsigned 取值范围、浮点型精度、`sizeof`、输出格式、常量字面量类型和后缀。  
> **阅读提示**：保留课程的主要知识脉络；涉及不同平台的地方用「⚠️ 补充辨析」标记，避免将某个操作系统上的结果误认为 C++ 语言的统一规定。

## 一、整体认识：整型与浮点型有什么区别？

```cpp
int age = 21;          // 整型：通常用于表示离散的整数数量
double height = 180.5; // 浮点型：用于表示带小数、或者数量级很大/很小的近似数
```

| 对比 | 整型（integer） | 浮点型（floating-point） |
|---|---|---|
| 典型类型 | `short`、`int`、`long`、`long long` | `float`、`double`、`long double` |
| 主要用途 | 计数、数组下标（常用其他适当类型）、整数运算 | 小数、科学计算、模型数值计算 |
| 核心限制 | **可表示整数的范围**受到位数限制 | **精度**和可表示数值范围均有限 |
| Python 对照 | Python 的 `int` 通常不受固定 32/64 位范围限制 | Python 内置 `float` 通常是 IEEE 754 双精度，接近 C++ `double` |

**复习之前的「变量」概念**：如 `int age = 21;`，`int` 指定如何表示和操作数据，`age` 是变量名，`21` 是初始值。数据最终以二进制形式表示；类型决定它的解释规则。

---

## 二、C++ 整型的种类与占用空间

课程图片首先介绍了 `short`、`int`、`long`、`long long`。在你目前的 **Windows x64 + MSYS2/G++** 环境中，通常可按下表理解：

| 类型 | 常见字节数 | 位数 | 说明 |
|---|---:|---:|---|
| `short` | 2 | 16 bit | 短整型 |
| `int` | 4 | 32 bit | 整型，最常用 |
| `long` | 4 | 32 bit | 长整型；**Windows x64 常见仍是 4 字节** |
| `long long` | 8 | 64 bit | 长长整型 |

**字节和位**：`1 byte = 8 bits`，因此 4 字节通常是 32 位，8 字节通常是 64 位。

### 2.1 为什么 `long` 在 Windows 和 Linux 可能不一样？

课程图片提到：`long` 在 Windows 常为 4 字节，在 Linux 64 位环境常为 8 字节。这是因为不同平台的数据模型不同：

- **Windows x64 常见 LLP64**：`int` 32 位，`long` 32 位，指针 64 位，`long long` 64 位。
- **Linux x86-64 常见 LP64**：`int` 32 位，`long` 64 位，指针 64 位，`long long` 64 位。

⚠️ **补充辨析**：以上是常见环境的实际情况，不是说 C++ 标准强制所有电脑上的 `long` 都占特定字节数。要在当前环境中确认，请用 `sizeof`。

### 2.2 用 `sizeof` 查看实际占用空间

`sizeof(类型)` 或 `sizeof(对象)` 返回所占**字节数**，而不是比特数：

```cpp
#include <iostream>

int main() {
    std::cout << "short: " << sizeof(short) << " bytes\n";
    std::cout << "int: " << sizeof(int) << " bytes\n";
    std::cout << "long: " << sizeof(long) << " bytes\n";
    std::cout << "long long: " << sizeof(long long) << " bytes\n";
    return 0;
}
```

在你的 Windows x64 编译环境中，常见结果依次为 `2 / 4 / 4 / 8`。如果换到 Linux x64，`long` 可能显示为 `8`。

**Python 对照**：`sys.getsizeof(21)` 得到的是 Python 对象的内存占用信息（含对象管理开销），并不是「C++ 的 `int` 占多少字节」，不能直接对比。

---

## 三、有符号（signed）与无符号（unsigned）整数

### 3.1 什么是有符号与无符号？

```cpp
int a = -10;          // 有符号 int：可以表示负数
signed int b = -10;   // signed int 与 int 表示同一类型
unsigned int c = 10;  // 无符号 int：不用于表示负数
```

- **signed**：能够表示负数、零和正数。
- **unsigned**：只表示非负整数，因而在相同位宽下，上限更大。
- 对 `short / int / long / long long`，**省略 `signed` 时默认是有符号的**。

### 3.2 为什么相同位宽，取值范围不同？

设总位宽为 `n`，对现代常见的二进制补码整数：

- **有符号 n 位**：\(-2^{n-1}\) 到 \(2^{n-1}-1\)
- **无符号 n 位**：\(0\) 到 \(2^n-1\)

例如 8 位整数：

| 类型 | 范围 |
|---|---|
| 8 位有符号 | -128 ～ 127 |
| 8 位无符号 | 0 ～ 255 |

原因可以直观理解为：有符号整数需要编码负数，因此不能把所有位模式都用于非负数。

### 3.3 课程中的常用取值范围表

下表按课程截图的**典型 16/32/64 位**情况整理：

| 类型 | 典型位宽 | 典型取值范围 |
|---|---:|---|
| `signed short` / `short` | 16 | -32768 ～ 32767 |
| `unsigned short` | 16 | 0 ～ 65535 |
| `signed int` / `int` | 32 | -2147483648 ～ 2147483647 |
| `unsigned int` | 32 | 0 ～ 4294967295 |
| `signed long` / `long` | 32 或 64 | 32 位时与上面 `int` 相同；64 位时为 -2^63 ～ 2^63−1 |
| `unsigned long` | 32 或 64 | 32 位时 0 ～ 2^32−1；64 位时 0 ～ 2^64−1 |
| `signed long long` / `long long` | 64 | -9223372036854775808 ～ 9223372036854775807 |
| `unsigned long long` | 64 | 0 ～ 18446744073709551615 |

**实用查看方法**：使用 `<limits>` 查询编译器当前的真实范围，而不是靠死记：

```cpp
#include <iostream>
#include <limits>

int main() {
    std::cout << "int min = " << std::numeric_limits<int>::min() << '\n';
    std::cout << "int max = " << std::numeric_limits<int>::max() << '\n';
    std::cout << "unsigned int max = "
              << std::numeric_limits<unsigned int>::max() << '\n';
    return 0;
}
```

### 3.4 有符号与无符号的边界问题

```cpp
unsigned int x = 0;
--x;  // 无符号运算按模 2^N 回绕；常见 32 位 unsigned int 时得到 4294967295
```

⚠️ **注意**：无符号运算按位宽取模；**有符号整数发生算术溢出是未定义行为**，不能简单认为 `int` 最大值再加 1 一定变为最小值。初学时避免让数值超过类型范围。

> **关联大模型量化**：以后操作 Q4、NVFP4 的原始数据时常看到 `uint8_t`，即「恰好 8 位的无符号整数类型」（在支持它的环境中）。这里强调的是**底层位存储**，不是说 NVFP4 数值本身就是普通无符号整数。

---

## 四、C++ 浮点型的种类与精度

课程图片将浮点型分为 `float`、`double`、`long double`：

| 类型 | 常见占用空间 | 参考有效十进制数字 | 说明 |
|---|---:|---:|---|
| `float` | 4 字节 | 约 6～7 位 | 单精度浮点数；常见 IEEE 754 FP32 |
| `double` | 8 字节 | 约 15～16 位 | 双精度浮点数；常见 IEEE 754 FP64 |
| `long double` | 随编译器/平台变化，如 8 或 16 字节，也可能有其他布局 | 可能与 `double` 相同，也可能约 18～19 位 | 扩展精度浮点类型，**不是永远 16 字节、18～19 位** |

**特别注意：**浮点类型没有 `unsigned float`、`signed double` 这样的合法类型写法。浮点数本身能够表示正负值，但不能用整数的 `signed/unsigned` 限定符声明它们。

### 4.1 什么是「有效位数」？

有效位数不是小数点后有多少位，而是一个数字中**能可靠表达的总有效十进制数字数量**。

例如：

- `1234567.0` 有 7 个非前导零有效数字；
- `1.234567` 也有 7 个有效数字；
- `1234567890.0` 则需要更多有效数字才能完全保持原值。

课程截图中的：

```cpp
float num1 = 1234567890;
float num2 = 1.234567890f;
```

都是为了说明：`float` 的存储精度有限。**超出精度后不是简单把后面的十进制数字「剪掉」**，而是舍入到附近可表示的二进制浮点数。默认显示的位数与内部实际存储精度也不是一回事。

### 4.2 为什么 `float` 和 `double` 能保存小数？

在最常见的 IEEE 754 格式中，浮点值由符号位、指数位、有效数部分组成。

| 格式 | 符号位 | 指数位 | 尾数字段 |
|---|---:|---:|---:|
| FP32 (`float` 常见实现) | 1 | 8 | 23 |
| FP64 (`double` 常见实现) | 1 | 11 | 52 |

可以先记住：**double 通常比 float 多了不少精度，并具有更大的指数范围**。现在不必深入研究 IEEE 754 编码；等学习 FP16、BF16、NVFP4 时再把指数和尾数联系起来。

### 4.3 查看 `sizeof` 和实际浮点精度

```cpp
#include <iostream>
#include <limits>

int main() {
    std::cout << "float: " << sizeof(float)
              << " bytes, digits10=" << std::numeric_limits<float>::digits10 << '\n';
    std::cout << "double: " << sizeof(double)
              << " bytes, digits10=" << std::numeric_limits<double>::digits10 << '\n';
    std::cout << "long double: " << sizeof(long double)
              << " bytes, digits10=" << std::numeric_limits<long double>::digits10 << '\n';
    return 0;
}
```

这里 `digits10` 是一个**保证在限定条件下十进制表示可往返保持的有效数字数量指标**；可能分别看到 `6`、`15` 和由平台决定的第三个值。它与课程中用于直观解释的「约 6～7 位」「约 15～16 位」不矛盾。

---

## 五、浮点输出：`fixed`、`width`、`setprecision` 到底在控制什么？

课程截图出现：

```cpp
std::cout << std::fixed;
std::cout.width(20);
std::cout << num2 << "," << sizeof(num2) << std::endl;
```

这些操作控制的是**输出显示格式**，不是改变 `num2` 在内存里保存的数值，也不是给浮点数增加真实精度。

| 写法 | 作用 |
|---|---|
| `std::fixed` | 采用固定小数点表示法 |
| `std::setprecision(n)` | 配合 `fixed` 时设置**小数点后 n 位**；默认格式下语义不同 |
| `std::cout.width(20)` | 只给**紧接着的下一项输出**设置最小字段宽度 20，不是最大长度，也不改变变量字节数 |
| `sizeof(num2)` | 询问变量类型的字节数 |

推荐用下面这个完整实验：

```cpp
#include <iostream>
#include <iomanip>

int main() {
    float a = 1.23456789f;
    double b = 1.23456789;

    std::cout << "default float: " << a << '\n';
    std::cout << "fixed float: " << std::fixed << std::setprecision(9) << a << '\n';
    std::cout << "fixed double: " << b << '\n';
    std::cout << "width example: [" << std::setw(20) << b << "]\n";
    std::cout << "sizeof(float)=" << sizeof(a) << '\n';
    return 0;
}
```

即使让 `float` 显示 9 位小数，也不能凭空找回它在存储时已经失去的精度。

**Python 对照**：

```python
x = 1.23456789
print(f"{x:.9f}")  # 格式化显示，不会改变 x 的底层精度
```

---

## 六、常量、字面量和后缀（课程重点）

课程还讨论了下面这句：

```cpp
std::cout << "我出生于：" << 2001 << "年\n";
```

这里的 `2001` 不是变量，而是一个**整数字面量**（literal）。C++ 编译器会根据字面量形式、数值大小、进制和后缀决定它的类型。

### 6.1 整数字面量

```cpp
2001       // 没有后缀的十进制整数，能装进 int 时类型为 int
2001U      // unsigned int
2001L      // long
2001LL     // long long
2001ULL    // unsigned long long
```

- `U` / `u`：表示无符号相关候选类型；
- `L` / `l`：表示 `long` 相关候选类型；
- `LL` / `ll`：表示 `long long` 相关候选类型；
- 后缀可以按规则组合，例如 `ULL`。

⚠️ **补充辨析**：课程的「整数范围不足就自动扩容」可以用来理解**一个整数字面量在编译期选择类型**的过程，但不要理解为「已经声明的 `int` 变量，运行时装不下就自动变成 `long long`」。另外，十进制和非十进制整数字面量选择候选类型的顺序并不完全相同。

### 6.2 浮点数字面量

```cpp
1.23      // 通常是 double
1.23f     // float
1.23F     // float
1.23L     // long double
```

- `f` / `F`：`float`；
- `l` / `L`：`long double`；
- **普通 `1.23` 本身默认是 `double`**。

⚠️ **课程截图需要更正的一点**：普通标准 C++ 并没有通用的 `D` 后缀用来指定 `double`；不加后缀的十进制浮点字面量默认就是 `double`。另外，浮点字面量超出对应类型可表示范围不会简单「自动扩容为 long double」，应根据所写后缀和编译规则判断。

**Python 对照**：

```python
n = 2001     # Python int，不会默认限定在 C++ int 的 32 位范围
x = 1.23     # Python float，通常是双精度
```

---

## 七、为什么说 C++ 的类型跟你未来研究的量化有关？

这部分是对课程内容的**学习迁移拓展**，不是截图里的原始章节。

| 课程里的概念 | 量化/推理工程里常遇到的东西 |
|---|---|
| `float`（常见 FP32） | 原始模型权重、Scale、误差计算 |
| `double` | 需要更高精度的统计或验证（是否使用视任务而定） |
| `uint8_t` | 保存 8 位原始数据，或打包存放两个 4-bit 数据 |
| 有符号/无符号 | 区分 `int8_t` 编码数值和原始字节解释 |
| 位宽与范围 | 理解数值溢出、截断、低比特表示 |
| `sizeof` | 检查量化结构体、Block 的存储开销 |

请区分：**C++ 内置数值类型**（如 `int`、`float`）和**量化格式**（如 Q4、Q8、MXFP4、NVFP4）不是一回事。后者通常还规定打包方式、Scale、Block 等规则。

---

## 八、完整练习：在 Windows 的 VS Code 中一次查看整型和浮点型

将以下代码保存为 `integer_float_types.cpp`：

```cpp
#include <iostream>
#include <limits>
#include <iomanip>

int main() {
    std::cout << "=== Integer sizes (bytes) ===\n";
    std::cout << "short: " << sizeof(short) << '\n';
    std::cout << "int: " << sizeof(int) << '\n';
    std::cout << "long: " << sizeof(long) << '\n';
    std::cout << "long long: " << sizeof(long long) << '\n';

    std::cout << "\n=== Integer ranges ===\n";
    std::cout << "int: " << std::numeric_limits<int>::min()
              << " ~ " << std::numeric_limits<int>::max() << '\n';
    std::cout << "unsigned int: 0 ~ "
              << std::numeric_limits<unsigned int>::max() << '\n';

    std::cout << "\n=== Floating point ===\n";
    std::cout << "float: " << sizeof(float)
              << " bytes, digits10=" << std::numeric_limits<float>::digits10 << '\n';
    std::cout << "double: " << sizeof(double)
              << " bytes, digits10=" << std::numeric_limits<double>::digits10 << '\n';
    std::cout << "long double: " << sizeof(long double)
              << " bytes, digits10=" << std::numeric_limits<long double>::digits10 << '\n';

    float f = 1.23456789f;
    double d = 1.23456789;
    std::cout << std::fixed << std::setprecision(9);
    std::cout << "float value:  " << f << '\n';
    std::cout << "double value: " << d << '\n';

    return 0;
}
```

在 VS Code 的 PowerShell 终端（已配置 G++）运行：

```powershell
g++ -std=c++17 -Wall -Wextra .\integer_float_types.cpp -o .\integer_float_types.exe
.\integer_float_types.exe
```

### 练习时重点观察

1. Windows 下 `sizeof(long)` 是否为 4？
2. `int` 与 `unsigned int` 的最大值是否相同？为什么？
3. `sizeof(float)` 和 `sizeof(double)` 是多少？
4. `float` 和 `double` 在输出更多小数时有什么差别？
5. 为什么 `std::setprecision(9)` 不能让 `float` 真正拥有 9 位小数精度？

---

## 九、一页记忆总结

1. **整型主要关注位宽与取值范围**：`short`、`int`、`long`、`long long`；同位宽下 `unsigned` 只表示非负数，但上限更大。
2. **浮点型同时关注范围和精度**：`float` 通常 4 字节、`double` 通常 8 字节、`long double` 由实现决定。
3. **有效位数 ≠ 小数点后位数**；`fixed` / `setprecision` / `width` 只控制输出格式。
4. **`sizeof` 测的是字节数**，具体大小以你的编译器/平台为准。
5. **字面量的类型与变量的类型是两回事**：`2001` 通常是 `int`，`2001LL` 是 `long long`；`1.23` 通常是 `double`，`1.23f` 是 `float`。
6. **Python 的 `int` 不需要你手动指定 32/64 位；C++ 要认真考虑类型范围。**
7. **未来量化开发要把「数值格式」和「用于保存它的 C++ 数据结构」区分开。**

> **下一节衔接建议**：`const`、变量初始化、自动类型推导 `auto`、强制类型转换，再进入数组、指针和位运算，最终理解 `uint8_t` 如何存储 Q4/NVFP4 的原始编码。
