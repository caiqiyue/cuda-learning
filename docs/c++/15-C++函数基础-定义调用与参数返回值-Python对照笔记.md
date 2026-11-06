# 15｜C++ 函数基础：定义、调用、形参与实参、返回值——Python 对照笔记

> **学习环境：** Windows + VS Code + MSYS2 UCRT64 / G++，以 **C++17** 为例。  
> **本节来源：** 根据课程的 5 张截图，依照「为什么需要函数 → 函数结构 → 参数与返回值 → 定义与调用 → 范围随机数示例」展开；另用 **【补充理解】** 标记 Python 对照、代码规范和运行机制。  
> **学习目标：** 学完能独立定义、调用 `get_max()`、`get_random_num()` 这样的简单函数，理解调用者如何传参以及如何接收返回值。

---

## 1. 函数是什么？为什么需要？

课程给出的定义是：

> **函数（Function）是提前封装好的、可以重复使用的、完成特定功能的独立代码单元。**

截图用「获取一定范围内的随机整数」举例。如果主函数需要分别生成 `[1, 5]`、`[10, 100]`、`[100, 10000]` 的随机数，不封装就要把相似的代码写三遍：

```cpp
// 示意：核心步骤重复了 3 次
std::random_device rd1;
std::mt19937 gen1(rd1());
std::uniform_int_distribution<int> dis1(1, 5);
int random_number1 = dis1(gen1);

std::random_device rd2;
std::mt19937 gen2(rd2());
std::uniform_int_distribution<int> dis2(10, 100);
int random_number2 = dis2(gen2);

std::random_device rd3;
std::mt19937 gen3(rd3());
std::uniform_int_distribution<int> dis3(100, 10000);
int random_number3 = dis3(gen3);
```

把「**根据上下界生成一个随机整数**」封装成函数后，调用者只需要写：

```cpp
int random_number1 = get_random_num(1, 5);
int random_number2 = get_random_num(10, 100);
int random_number3 = get_random_num(100, 10000);
```

**函数带来的好处：**

1. **提前封装：** 把一段有明确目的的逻辑集中到一个地方。
2. **重复使用：** 可以多次调用同一个函数，传不同参数。
3. **完成特定功能：** 一个函数最好承担相对清晰的职责，例如取最大值或生成随机数。
4. **方便修改：** 以后改随机数生成逻辑时，通常只需修改函数内部，不必逐个修改调用位置。

**Python 对照：** 这与你在 Python 中用 `def` 封装重复逻辑的目的几乎一致，区别主要在 **C++ 需要声明参数和返回值的类型**。

---

## 2. 函数的基本结构：看懂每一部分

截图给出的框架是：

```text
返回值类型 函数名称(参数列表)
{
    函数体
    return 返回值;
}
```

看一个可以直接编译的例子：

```cpp
int get_max(int a, int b)
{
    int result = a;

    if (b > result) {
        result = b;
    }

    return result;
}
```

| 组成部分 | 代码 | 含义 |
|---|---|---|
| 返回值类型 | `int` | 函数执行后提供一个 `int` 结果 |
| 函数名 | `get_max` | 通过这个名称调用函数 |
| 参数列表 | `(int a, int b)` | 接收调用者传来的两个整数 |
| 函数体 | `{ ... }` | 真正执行的代码 |
| 返回语句 | `return result;` | 把结果交给调用者，同时结束函数执行 |

**特别注意：** 课程随机数示意中写成 `int get_random_num(min, max)`，是为了突出结构而省略了参数类型；**真正的 C++17 源代码必须写成** `int get_random_num(int min, int max)`。同样，主函数应写 `int main()`，而不是把截图中的 `int main` 当作完整函数头直接照抄。

### Python 版本

```python
def get_max(a: int, b: int) -> int:
    result = a
    if b > result:
        result = b
    return result
```

| 对比 | Python | C++ |
|---|---|---|
| 定义函数 | `def get_max(...):` | `int get_max(...) { ... }` |
| 参数类型 | 类型提示一般不在运行时强制约束 | `int a` 是函数参数的类型声明 |
| 返回类型 | `-> int` 是类型提示 | 函数前面的 `int` 是返回类型声明 |
| 函数体范围 | 依靠缩进 | 依靠 `{ }` |
| 结束语句 | `return result` | `return result;` |

---

## 3. 函数定义与函数调用：两件不同的事

**定义函数**是告诉编译器「这个函数要做什么」：

```cpp
int get_max(int a, int b)
{
    return a > b ? a : b;
}
```

**调用函数**才是要求执行它：

```cpp
int answer = get_max(3, 5);
```

可以把调用过程理解为：

```text
main() 中执行 get_max(3, 5)
             │
             ▼
      a 接收 3，b 接收 5
             │
             ▼
      执行 get_max 函数体
             │
             ▼
          return 5
             │
             ▼
      回到 main()，answer 得到 5
```

### 完整可运行程序

```cpp
#include <iostream>

// 先定义函数
int get_max(int a, int b)
{
    int result = a;
    if (b > result) {
        result = b;
    }
    return result;
}

int main()
{
    int answer = get_max(3, 5);
    std::cout << "max = " << answer << '\n';
    return 0;
}
```

输出：

```text
max = 5
```

注意：**函数被定义，不代表其中的代码会自动执行。** 上例中进入 `main()` 后，遇到 `get_max(3, 5)` 才调用 `get_max()`。

---

## 4. 形参（Formal Parameters）和实参（Arguments）

截图重点标注了：

```cpp
int get_max(int a, int b)  // a 和 b 是形参
{
    return a > b ? a : b;
}

int main()
{
    int answer = get_max(3, 5); // 3 和 5 是实参
    return 0;
}
```

- **形参：** 出现在函数**定义**的参数列表中，是函数内部接收数据的变量，例如 `a`、`b`。
- **实参：** 调用函数时实际提供的表达式或数据，例如 `3`、`5`；也可以是变量：`get_max(x, y)`。

可以理解为：

```text
函数定义： int get_max(int a, int b)
                       ↑      ↑
                      形参   形参

函数调用： get_max(3, 5)
                   ↑  ↑
                  实参 实参
```

### 【补充理解】C++ 默认是按值传参

在本节的写法中，形参 `a` 和 `b` 是**独立的局部 `int` 对象**，获得实参的值，而不是直接与外部变量共用同一份整数存储。

```cpp
#include <iostream>

void change(int a)
{
    a = 100;
}

int main()
{
    int x = 10;
    change(x);
    std::cout << x << '\n';  // 仍然是 10
}
```

`change(x)` 会用 `x` 的值初始化形参 `a`，所以修改 `a` 不会改变 `x`。

Python 中 `def change(a): ...` 也有形参和实参，但 Python 采用**对象引用传递（共享对象引用的传递机制）**，不能简单地认为 Python 函数总在「复制对象」。对于 Python 可变对象，函数内的原地修改可能被调用者观察到。C++ 后面还要学习**引用参数 `int&` 和指针参数 `int*`**，用来直接操作调用方对象，本节先掌握值传参。

---

## 5. 返回类型与 `return`：到底返回了什么？

课程的 `get_max` 和 `get_random_num` 都把最终计算出的结果返回给调用者。

```cpp
int get_max(int a, int b)
{
    if (a > b) {
        return a;
    }
    return b;
}
```

这里：

- 函数头部的 `int` 声明返回结果应是整数类型。
- `return a;` 把当前结果返回给调用者，并**立即结束这一次函数调用**。
- 如果执行了 `return a;`，下面的 `return b;` 就不会再执行。

调用时有两种常见用法：

```cpp
int answer = get_max(3, 5);     // 用变量接收返回值
std::cout << get_max(8, 2);     // 直接使用返回值
```

### 不需要返回值怎么办？`void`

```cpp
#include <iostream>

void say_hello()
{
    std::cout << "Hello!\n";
}

int main()
{
    say_hello();
    return 0;
}
```

`void` 表示函数不提供常规返回值，不需要写 `return 某个值;`；如有需要，可以使用 `return;` 提前结束函数。

**注意：** 不能把一般 `int` 返回类型的函数写成存在某条执行路径却不返回值。正常情况下应确保所有可以走到函数末尾的路径都返回适合的结果。`main()` 有特殊规则：执行到末尾等价于 `return 0;`，不过学习阶段显式写出更清楚。

---

## 6. 课程重点例子：把生成随机数封装成函数

截图中的核心意图是，把下面这几步封装起来：

1. 准备随机数种子/随机设备：`std::random_device`。
2. 创建随机数生成引擎：`std::mt19937`。
3. 创建整数均匀分布：`std::uniform_int_distribution<int>`。
4. 生成并返回一个处于指定范围的整数。

### C++17 完整代码

```cpp
#include <iostream>
#include <random>

// 获取 [min, max] 范围内的随机整数（包含两端）
int get_random_num(int min, int max)
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dis(min, max);
    return dis(gen);
}

int main()
{
    int random_number1 = get_random_num(1, 5);
    int random_number2 = get_random_num(10, 100);
    int random_number3 = get_random_num(100, 10000);

    std::cout << "number1 = " << random_number1 << '\n';
    std::cout << "number2 = " << random_number2 << '\n';
    std::cout << "number3 = " << random_number3 << '\n';

    return 0;
}
```

输出示例（每次运行可能不同）：

```text
number1 = 4
number2 = 72
number3 = 5621
```

### 拆解函数中的每一句

| 语句 | 作用 |
|---|---|
| `int get_random_num(int min, int max)` | 声明接收两个整数，返回一个整数 |
| `std::random_device rd;` | 创建用于获取随机种子的设备对象 |
| `std::mt19937 gen(rd());` | 用种子初始化伪随机数引擎 |
| `std::uniform_int_distribution<int> dis(min, max);` | 配置均匀整数分布，范围两端都包括 |
| `return dis(gen);` | 使用引擎生成整数并把它返回 |

**本节不必深究 `mt19937` 算法。** 你现在主要关注：函数把重复的步骤封装起来，`min`、`max` 由调用者提供，函数使用 `return` 给出结果。

> **关于截图写法的两点修正：** ① 参数应显式写出类型 `int min, int max`；② 代码使用 `<random>`、`std::` 且 `main()` 带括号，才是完整可编译的现代 C++ 示例。这里的示例每调用一次都重新创建引擎，便于理解但不一定适合性能敏感的实际项目；真实项目会考虑复用生成引擎。并且需要保证 `min <= max`。

### Python 对照

```python
import random

def get_random_num(min_value: int, max_value: int) -> int:
    return random.randint(min_value, max_value)

number1 = get_random_num(1, 5)
number2 = get_random_num(10, 100)
number3 = get_random_num(100, 10000)

print(number1, number2, number3)
```

Python 的 `random.randint(a, b)` 与本节 `uniform_int_distribution<int>(a, b)` 在**端点是否包含**这一点上相同；它们的底层实现和随机数状态管理不要求相同。

---

## 7. 函数的书写位置：为什么要先定义或先声明？【补充理解】

如果一个普通函数要在 `main()` 中调用，编译器读到调用位置时，需要知道它的声明（名称、参数类型、返回类型等）。

### 方法 A：把函数定义放在 `main()` 前面

```cpp
int add(int a, int b)
{
    return a + b;
}

int main()
{
    int x = add(1, 2);
    return 0;
}
```

### 方法 B：先声明，后定义

```cpp
#include <iostream>

int add(int a, int b);  // 函数声明（原型），没有函数体

int main()
{
    std::cout << add(1, 2) << '\n';
    return 0;
}

int add(int a, int b)   // 函数定义
{
    return a + b;
}
```

**区别：**

- **声明（Declaration）：** 告诉编译器函数叫什么、参数与返回类型是什么。
- **定义（Definition）：** 真正提供函数体，实现具体功能。
- **调用（Call）：** 让程序执行函数的逻辑。

这与之前学过的 `.h / .hpp` 和 `.cpp` 文件拆分有直接关系，后面正式学习多文件函数时再深入。

**还要注意：** 在标准 C++17 中，不能像某些语言一样直接在 `main()` 的函数体内部再定义一个普通命名函数。一般把它定义在外部；后续会学习 Lambda 表达式。

---

## 8. 函数调用时，局部变量与内存会怎样？【补充理解】

结合你上一节关于栈、堆、指针和生命周期的知识：

```cpp
int get_max(int a, int b)
{
    int result = a;
    if (b > result) result = b;
    return result;
}

int main()
{
    int x = 3;
    int y = 5;
    int answer = get_max(x, y);
    return 0;
}
```

在一个常见的、未优化的运行模型里：

```text
main 函数正在执行
  x = 3, y = 5
       │
       └─ 调用 get_max(x, y)
                 │
                 ├─ 创建这一调用的形参 a、b
                 ├─ 创建局部变量 result
                 ├─ 计算 result = 5
                 └─ return 5
       │
       └─ 回到 main，answer = 5
```

`get_max()` 的形参 `a`、`b` 以及局部变量 `result` 在这次调用结束后生命周期结束；`main()` 中的 `x`、`y`、`answer` 是不同对象。

**严格说明：** 这些局部对象不一定真的全部占有独立的栈内存，编译器也可能把它们放在寄存器中或优化掉。但**函数调用、局部作用域、值传参与生命周期的语义**仍然成立。

---

## 9. 常见错误与容易误解的地方

| 错误或误区 | 更准确的理解 |
|---|---|
| `int get_random_num(min, max)` | C++17 参数需要写类型，如 `int min, int max` |
| `int main` | 定义主函数需要 `int main()`，后面再接 `{}` |
| 定义了函数就会自动运行 | 只有执行到调用语句才会进入函数；`main()` 是特殊的程序入口 |
| 形参和实参是同一个变量 | 本节的 `int` 参数默认按值传递，形参是独立对象 |
| `return` 只是产生结果，不影响流程 | 执行 `return` 会立即结束本次函数调用 |
| `get_max(3, 5)` 会永久创建 `a`、`b` | 形参属于这次调用，调用结束后生命周期结束 |
| C++ 可以直接在 `main` 里定义普通函数 | 标准 C++17 不支持普通函数的嵌套定义 |
| `get_random_num(1, 5)` 不可能得到 5 | `uniform_int_distribution<int>(1, 5)` 含上界 5 |
| Python 的 `-> int` 等同于 C++ 的 `int` 返回类型 | Python 类型提示一般不负责运行时强制检查；C++ 类型由语言规则检查 |
| 生成随机数一定要每次重建引擎 | 这是课程里便于展示函数封装的简单写法，实际程序可复用引擎 |

### 三个最容易遗漏的语法细节

```cpp
int add(int a, int b)   // 参数需要标注 int
{
    return a + b;       // 语句结尾需要分号
}

int main()              // main 后必须有 ()
{
    int result = add(3, 5);
    return 0;
}
```

---

## 10. 自己动手做三个实验

### 练习 1：把重复代码封装为函数

编写 `int square(int x)`，实现平方运算：

```cpp
square(3)  // 返回 9
square(5)  // 返回 25
```

### 练习 2：实现三个数取最大值

写一个 `int get_max3(int a, int b, int c)`，让调用：

```cpp
get_max3(10, 30, 20)
```

返回 `30`。你可以复用本节的 `get_max()` 函数，而不必从头写比较逻辑。

### 练习 3：观察按值传参

预测并运行：

```cpp
#include <iostream>

void change(int x)
{
    x = 99;
    std::cout << "inside: " << x << '\n';
}

int main()
{
    int n = 10;
    change(n);
    std::cout << "outside: " << n << '\n';
}
```

思考为什么函数内部打印 `99`，外部仍然是 `10`。

<details>
<summary>参考答案（做完再看）</summary>

```cpp
int square(int x) { return x * x; }

int get_max(int a, int b) { return a > b ? a : b; }

int get_max3(int a, int b, int c)
{
    return get_max(get_max(a, b), c);
}
```

练习 3 输出：

```text
inside: 99
outside: 10
```

因为按值传参只修改了形参 `x`，没有修改 `main()` 的局部变量 `n`。

</details>

---

## 11. Windows + G++ 编译命令

把第 3 节的完整示例存为 `function_01.cpp`，在 VS Code 的 PowerShell 中运行：

```powershell
g++ -std=c++17 -Wall -Wextra -pedantic .\function_01.cpp -o .\function_01.exe
.\function_01.exe
```

随机数示例另存为 `function_random.cpp`：

```powershell
g++ -std=c++17 -Wall -Wextra -pedantic .\function_random.cpp -o .\function_random.exe
.\function_random.exe
```

每个文件各有一个 `main()` 没有问题；**只要分别编译为独立的可执行程序**，就不会因为多个 `main()` 而出现重复定义。这和你之前学过的多 `main()` 规则一致。

---

## 12. 本节总结：5 句话建立函数的完整概念

1. **函数是可重复调用的独立功能单元**，用于封装特定逻辑，减少重复。
2. **函数定义由返回类型、函数名、参数列表和函数体构成**，例如 `int get_max(int a, int b) { ... }`。
3. **形参是函数接收数据的局部变量；实参是调用时提供的值或表达式**。本节 `int` 参数使用按值传参。
4. **`return` 把结果交给调用者并立即结束函数**；不需要返回结果的函数可使用 `void`。
5. **先让编译器知道函数声明，再在程序中调用**。函数是否复用与它被调用多少次有关，并不意味着代码会自动执行。

**一句话记住：**调用者通过**实参**给函数提供输入；函数通过**形参**接收数据、在**函数体**中处理，再用 **`return`** 把结果交还调用者。

**下一节建议：**函数的**默认参数、函数重载、传值/引用/指针传参**。你之前刚学习过指针、结构体和智能指针，理解函数如何传递不同类型的对象会非常关键。
