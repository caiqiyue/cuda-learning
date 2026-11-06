# 08｜C++ 流程控制与枚举类型：if、switch、enum、循环与跳转（Python 对照笔记）

> **学习背景**：已有 Python 基础，正在通过 Windows + VS Code + MSYS2（G++）系统学习 C++，后续目标是能读懂和调试 `llama.cpp`、`ggml` 等推理框架源码。  
> **编译标准**：本文示例以 C++17 为基础。  
> **本节目标**：不只记语法，还要知道代码**什么时候执行、什么时候跳过、什么时候重复、什么时候退出**。

---

## 0. 先建立整体认识：流程控制是什么？

程序通常从上往下执行，但现实逻辑不是永远顺序执行：

- **分支判断**：满足条件执行 A，否则执行 B → `if / else if / else`、`switch`。
- **重复执行**：只要条件满足，就反复运行一段代码 → `while`、`for`。
- **改变执行位置**：跳过本轮、退出循环、结束函数、跳到标签 → `continue`、`break`、`return`、`goto`。
- **为状态取名字**：用有意义的名字表示一组离散状态 → `enum`、`enum class`（它们是**类型声明**，本身不是控制流语句）。

**一句话概括**：`if / switch` 决定**选哪条路**，`while / for` 决定**走多少次**，`break / continue / return / goto` 决定**何时停止或改变路线**。

| Python | C++ | 主要差异 |
|---|---|---|
| `if / elif / else` | `if / else if / else` | C++ 用 `()` 表达条件、`{}` 包围语句块，不靠缩进确定结构 |
| `match / case`（Python 3.10+） | `switch / case` | **不等价**：Python `match` 是更广泛的模式匹配；C++ `switch` 主要对整数、字符、枚举值等离散值分支 |
| `while` | `while` | 语义相似，C++ 条件要能转换为 `bool` |
| `for x in iterable` | `for (初始化; 条件; 更新)` | C++ 既有传统三段式 `for`，也有 `for (auto x : container)` 范围循环 |
| `break` / `continue` | `break` / `continue` | 含义很接近，但 `break` 还可以退出 `switch` |
| `enum.Enum` | `enum class` / `enum` | C++ 的枚举是编译期定义的枚举类型 |
| 没有普通的 `goto` | `goto` | C++ 支持，但通常应避免 |

---

## 1. `if`：如果条件成立，就执行

### 1.1 基本语法

```cpp
if (条件表达式) {
    // 条件为 true 时执行
}
```

例如：

```cpp
#include <iostream>

int main() {
    int age = 20;

    if (age >= 18) {
        std::cout << "成年人\n";
    }

    return 0;
}
```

执行过程：计算 `age >= 18` → 得到 `true` → 执行 `{}` 中代码。条件为 `false` 时跳过。

**Python 对照：**

```python
age = 20
if age >= 18:
    print("成年人")
```

- Python 使用冒号和缩进定义代码块。
- C++ 使用小括号 `()` 放条件，用花括号 `{}` 定义代码块；每条普通语句后一般有分号 `;`。
- C++ 的 `if`、`else` 后面在只有一条语句时可省略 `{}`，**初学阶段建议始终写上花括号**，避免增添第二条语句时出错。

### 1.2 条件一定要写成 `bool` 吗？

不一定，但条件表达式必须能转换为 `bool`：

```cpp
int count = 3;
if (count) {           // 非 0 -> true
    std::cout << "有数据\n";
}
```

为了阅读清晰，一般更推荐：

```cpp
if (count != 0) { /* ... */ }
```

与 Python 的区别：Python 空列表、空字符串等也有“真值”规则；C++ 没有完全对应的通用规则。例如 C++ 的 `std::string` 不能直接写成 `if (name)`，通常写 `if (!name.empty())`。

---

## 2. `if ... else`：二选一

```cpp
int score = 58;

if (score >= 60) {
    std::cout << "及格\n";
} else {
    std::cout << "不及格\n";
}
```

**执行规则**：条件为真执行 `if` 分支，否则执行 `else` 分支；正常情况下两个分支**只会执行其中一个**。

Python 写法：

```python
if score >= 60:
    print("及格")
else:
    print("不及格")
```

---

## 3. `else if`：多条件分支

```cpp
int score = 85;

if (score >= 90) {
    std::cout << "优秀\n";
} else if (score >= 80) {
    std::cout << "良好\n";
} else if (score >= 60) {
    std::cout << "及格\n";
} else {
    std::cout << "不及格\n";
}
```

运行结果：

```text
良好
```

关键机制：**从上到下判断，遇到第一个为真的分支后执行它，后续 `else if` 不再判断**。

为什么顺序重要？下面的代码有逻辑问题：

```cpp
if (score >= 60) {
    std::cout << "及格\n";
} else if (score >= 90) {
    std::cout << "优秀\n";
}
```

`score = 95` 时第一项已经成立，因此永远不会走到“优秀”。多档评分时通常**先判断限制更严格的条件**。

Python 对应 `elif`，而 C++ 的 `else if` 是 **`else` 和 `if` 两个关键字**，不是一个独立的 `elif` 关键字。

### 常见错误：`=` 和 `==`

```cpp
int a = 2;
if (a = 3) {  // 允许编译，但这先把 a 赋成 3，之后条件为 true
    // ...
}
```

想比较是否相等，应写 `if (a == 3)`。实际项目里可开启编译警告 `-Wall -Wextra` 辅助发现风险。

---

## 4. `switch / case`：按一个值选择分支

当条件是“同一个值分别等于 1、2、3 时执行不同动作”，可以使用 `switch`。

```cpp
#include <iostream>

int main() {
    int day = 2;

    switch (day) {
        case 1:
            std::cout << "星期一\n";
            break;
        case 2:
            std::cout << "星期二\n";
            break;
        case 3:
            std::cout << "星期三\n";
            break;
        default:
            std::cout << "其他日期\n";
            break;
    }

    return 0;
}
```

输出 `星期二`。

| 语法 | 含义 |
|---|---|
| `switch (day)` | 先求出 `day` 的值，选择匹配的分支 |
| `case 1:` | 匹配值为 `1` 的分支标签 |
| `break;` | 退出整个 `switch` |
| `default:` | 没有任何 `case` 匹配时执行；可不写 |

### 4.1 不写 `break` 会怎样？——贯穿执行（fallthrough）

```cpp
int n = 1;
switch (n) {
    case 1:
        std::cout << "A\n";
    case 2:
        std::cout << "B\n";
        break;
    default:
        std::cout << "C\n";
}
```

输出：

```text
A
B
```

`case 1` 匹配后，由于没有 `break`，会**继续执行后面的语句**，即使并未匹配 `case 2`。这叫 *fallthrough*。

- 无意贯穿：通常是 Bug。
- 有意贯穿：可用 C++17 `[[fallthrough]];` 明确表达；或者多个 `case` 共用处理语句：

```cpp
switch (n) {
    case 1:
    case 2:
        std::cout << "1 或 2\n";
        break;
    default:
        break;
}
```

### 4.2 为什么 `switch` 不能直接比较 `std::string`？

```cpp
std::string command = "run";
// switch (command) { ... } // 不合法
```

传统 C++ `switch` 的控制表达式是**整数或枚举等允许的类型**，`case` 标签必须是编译期可确定的常量表达式，而且同一 `switch` 中值不能重复。

要比较字符串，通常使用 `if / else if`：

```cpp
if (command == "run") {
    // ...
} else if (command == "stop") {
    // ...
}
```

**Python 对照**：Python 3.10+ 的 `match` 支持结构解构、模式匹配、守卫条件等，能力更广；不要简单把它等同于 C++ `switch`。

### 4.3 `case` 中定义变量的注意事项

`case` 标签本身不会创建新作用域。若在不同分支中声明局部变量（尤其带初始化的变量），建议用 `{}` 包起来：

```cpp
switch (day) {
    case 1: {
        int x = 10;
        std::cout << x << '\n';
        break;
    }
    case 2: {
        int x = 20;
        std::cout << x << '\n';
        break;
    }
    default:
        break;
}
```

---

## 5. `enum`：给一组离散状态起名字

**`enum` 不属于“循环和判断语句”，它是定义枚举类型的语法。** 它很适合和 `switch` 配合使用。

设想程序状态：0=停止、1=运行、2=暂停。如果直接写数字，可读性很差。

### 5.1 传统枚举 `enum`

```cpp
enum State {
    Stopped,
    Running,
    Paused
};

State state = Running;
```

未指定数值时，通常从 `0` 开始依次递增：`Stopped=0`、`Running=1`、`Paused=2`。也可以手动指定：

```cpp
enum ErrorCode {
    Ok = 0,
    InvalidInput = 100,
    NetworkError = 200
};
```

### 5.2 更推荐掌握 `enum class`（C++11）

```cpp
enum class State {
    Stopped,
    Running,
    Paused
};

State state = State::Running;
```

优势：

- 通过 `State::Running` 明确属于哪个枚举类型。
- 不会像传统枚举那样将枚举项名称引入外围作用域。
- 不会隐式转换为普通整数，更不容易把不同含义的数字混用。

### 5.3 枚举和 `switch` 一起使用

```cpp
#include <iostream>

enum class State {
    Stopped,
    Running,
    Paused
};

int main() {
    State state = State::Running;

    switch (state) {
        case State::Stopped:
            std::cout << "已停止\n";
            break;
        case State::Running:
            std::cout << "运行中\n";
            break;
        case State::Paused:
            std::cout << "已暂停\n";
            break;
    }
}
```

Python 对照：

```python
from enum import Enum

class State(Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2

state = State.RUNNING
if state is State.RUNNING:
    print("运行中")
```

**研究推理框架时的用途**：表示运行状态、设备/后端类别、错误码、量化类型等。读取代码时，遇到 `enum class` 要想到“这不是任意数字，而是一组被命名的合法状态”。

---

## 6. `while`：条件成立就不断重复

### 6.1 基本语法

```cpp
while (条件) {
    // 重复执行
}
```

例如：

```cpp
int i = 0;
while (i < 3) {
    std::cout << i << '\n';
    ++i;
}
```

输出：

```text
0
1
2
```

执行顺序：**先判断条件 → 为真执行循环体 → 回去再次判断 → 直到条件为假**。

Python 对照：

```python
i = 0
while i < 3:
    print(i)
    i += 1
```

### 6.2 最常见错误：忘记更新循环变量

```cpp
int i = 0;
while (i < 3) {
    std::cout << i << '\n';
    // 漏掉 ++i，可能成为无限循环
}
```

`while (true)` 可以表示有意设计的无限循环，但通常需要退出条件：

```cpp
while (true) {
    int num;
    if (!(std::cin >> num)) {
        break; // 输入失败或遇到文件结束
    }
    if (num == 0) {
        break;
    }
    std::cout << "输入：" << num << '\n';
}
```

`std::cin >> num` 的返回值可以在条件语境中判断输入流是否正常，这是一种常见 C++ 用法。

### 6.3 补充：`do ... while`

```cpp
int i = 5;
do {
    std::cout << i << '\n';
    ++i;
} while (i < 3);
```

即使条件一开始为假，仍会执行**至少一次**。注意结尾 `while (...);` 的分号。Python 没有完全相同的原生语法。

---

## 7. `for`：通常用于已知迭代步骤的循环

### 7.1 三段式 `for`

```cpp
for (初始化; 条件; 更新) {
    // 循环体
}
```

例如：

```cpp
for (int i = 0; i < 5; ++i) {
    std::cout << i << '\n';
}
```

输出 `0 1 2 3 4`（逐行）。

执行顺序：

1. 只执行**一次**初始化 `int i = 0`。
2. 判断 `i < 5`；为假则退出循环。
3. 执行循环体。
4. 执行更新 `++i`，再回到第 2 步。

**Python 对照**：

```python
for i in range(5):
    print(i)
```

注意 `range(5)` 在 Python 中产生迭代序列，而 C++ 三段式 `for` 的控制方式是初始化/条件/更新，并不完全是同一个机制。

### 7.2 范围 `for`：更像 Python 的 `for ... in ...`

```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<int> nums = {10, 20, 30};

    for (int x : nums) {
        std::cout << x << '\n';
    }
}
```

如果要**修改容器中的元素**，可使用引用：

```cpp
for (int& x : nums) {
    x *= 2;
}
```

- `int x`：拿到每个元素的值（拷贝）。
- `int& x`：绑定到原元素，修改 `x` 就是在修改容器中的元素。
- `const int& x`：不复制并保证不通过这个引用修改元素；对于较大的对象经常更合适。

这也会和你后面学习 C++ 的**引用（reference）**连接起来。

### 7.3 `for` 与 `while` 怎么选？

- 按索引、指定次数执行：`for` 通常更直观。
- 重复直到满足某个状态、读到文件结束：`while` 通常更直观。
- 遍历数组或容器：优先考虑范围 `for`。

两者在很多场景可以互相改写，主要差别是组织代码的可读性。

---

## 8. `break`：退出**最近一层**循环或 `switch`

### 8.1 退出循环

```cpp
for (int i = 0; i < 5; ++i) {
    if (i == 3) {
        break;
    }
    std::cout << i << ' ';
}
```

输出：

```text
0 1 2
```

当 `i == 3`，立即结束循环，不再执行剩余迭代。

### 8.2 嵌套循环中的 `break`

```cpp
for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
        if (j == 1) break;
        std::cout << '(' << i << ',' << j << ") ";
    }
}
```

`break` 只退出**内层 `for (j ...)`**，外层 `for (i ...)` 还会继续。

在 `switch` 中，`break` 退出的是 `switch`，不一定退出外面的循环。

---

## 9. `continue`：跳过**本轮剩余语句**，进入下一轮

```cpp
for (int i = 0; i < 5; ++i) {
    if (i == 2) {
        continue;
    }
    std::cout << i << ' ';
}
```

输出：

```text
0 1 3 4
```

与 `break` 的区别：

- `break`：循环直接结束。
- `continue`：循环**不结束**，只跳过当前这一轮剩余语句。

**重要细节**：

- 在传统 `for` 中，`continue` 会先进入更新步骤（如 `++i`），之后再判断条件。
- 在 `while` 中，`continue` 会返回条件判断，因此**注意不要漏掉更新变量**，否则容易无限循环：

```cpp
int i = 0;
while (i < 5) {
    if (i == 2) {
        ++i;          // 先更新再 continue
        continue;
    }
    std::cout << i << ' ';
    ++i;
}
```

**额外易混点：**如果 `switch` 位于 `for / while` 循环内部，`switch` 里面的 `continue` 会作用于**外围循环**（前提是存在这种外围循环），而 `break` 则退出 `switch`。

---

## 10. `return`：结束当前函数（和 break/continue 对比）

虽然这次截图主题没有单列 `return`，但它和 `break`、`continue` 太容易混淆，建议一起记。

```cpp
int findFirstPositive(const std::vector<int>& nums) {
    for (int x : nums) {
        if (x > 0) {
            return x; // 直接结束整个函数
        }
    }
    return -1;
}
```

| 语句 | 作用范围 | Python 类比 |
|---|---|---|
| `break` | 最内层循环或 `switch` | `break`（Python 没有 switch 场景） |
| `continue` | 当前最近一层循环的本轮执行 | `continue` |
| `return` | 当前整个函数 | `return` |
| `goto` | 跳转到同一函数中的某个标签，受语言规则限制 | 没有直接对应 |

---

## 11. `goto`：跳转到同一个函数内部的标签（了解即可）

```cpp
#include <iostream>

int main() {
    int n = 0;

start:
    std::cout << n << ' ';
    ++n;

    if (n < 3) {
        goto start;
    }

    std::cout << '\n';
    return 0;
}
```

输出：

```text
0 1 2
```

这里的 `start:` 是**标签（label）**，`goto start;` 会改变执行位置。

为什么一般不推荐？

- 很容易使执行流程变得难以追踪。
- 条件判断与循环能覆盖绝大多数日常需求。
- 可能引入难以维护的跳转关系。
- **不能随意跨越变量初始化**；C++ 对 `goto` 进入某些局部变量作用域有规则限制。

上面的例子，更推荐改成：

```cpp
for (int n = 0; n < 3; ++n) {
    std::cout << n << ' ';
}
```

以后读旧式 C/C++、底层库源码时可能看到 `goto cleanup;` 的错误清理写法。**了解它能做什么即可，不要把它当成首选结构。**

---

## 12. 横向对比：选分支、循环、跳转

| 目标 | 优先考虑 | 理由 |
|---|---|---|
| 判断年龄是否成年 | `if` | 单一真假条件 |
| 按分数区间分级 | `if / else if / else` | 需要比较范围、顺序判断 |
| 按数字命令 `0/1/2` 分支 | `switch` | 单个离散值匹配 |
| 给命令状态命名 | `enum class` | 避免到处出现含义不明的数字 |
| 从 0 遍历到 n-1 | `for` | 次数和更新关系清晰 |
| 读输入直到结束 | `while` | 终止时机由条件控制 |
| 跳过不合法数据 | `continue` | 只跳过本次循环 |
| 找到目标就停止搜索 | `break` 或 `return` | 前者退出循环，后者退出函数 |
| 强行跳到指定标签 | `goto`（一般避免） | 易损害结构化控制流 |

### 写 C++ 时还要注意两个差异

1. **作用域**：`{}` 中定义的局部变量通常只在相应作用域内有效；Python `if / for` 的普通代码块一般不会创建独立的局部作用域。
2. **表达式里的类型**：比较、逻辑运算通常产生 `bool` 值；`std::cout` 默认把 `true/false` 输出成 `1/0`，可以使用 `std::boolalpha` 输出文字。

---

## 13. 综合案例：枚举 + if + switch + for + continue + break

> 场景：模拟处理一批推理请求。输入中 `-1` 表示无效请求，`0` 表示停止处理，其余为请求 token 数。通过 `enum class` 表达处理状态。这是学习练习，不是 llama.cpp 的真实调度实现。

```cpp
#include <iostream>
#include <vector>

enum class RunState {
    Ready,
    Processing,
    Stopped
};

int main() {
    std::vector<int> requests = {8, -1, 16, 0, 32};
    RunState state = RunState::Ready;

    for (int tokens : requests) {
        if (tokens < 0) {
            std::cout << "跳过非法请求\n";
            continue;
        } else if (tokens == 0) {
            state = RunState::Stopped;
            break;
        } else {
            state = RunState::Processing;
            std::cout << "处理 token 数：" << tokens << '\n';
        }
    }

    switch (state) {
        case RunState::Ready:
            std::cout << "状态：就绪\n";
            break;
        case RunState::Processing:
            std::cout << "状态：处理中\n";
            break;
        case RunState::Stopped:
            std::cout << "状态：已停止\n";
            break;
    }

    return 0;
}
```

预期输出：

```text
处理 token 数：8
跳过非法请求
处理 token 数：16
状态：已停止
```

请你自己回答：

- 为什么没有处理最后的 `32`？因为遇到 `tokens == 0` 时执行了 `break`。
- 为什么 `-1` 不会进入状态切换？因为 `continue` 跳过了当前这轮余下的代码。
- 为什么 `RunState::Stopped` 比直接写数字 `2` 更容易维护？它明确说明了状态的含义。

**编译运行（在 VS Code PowerShell 中）：**

```powershell
g++ -std=c++17 -Wall -Wextra -g -O0 .\control_flow.cpp -o .\control_flow.exe
.\control_flow.exe
```

前提：把示例保存为 `control_flow.cpp`，并在对应目录下运行命令。`-Wall -Wextra` 开启常见编译警告；`-g -O0` 便于以后使用 GDB 单步观察分支和循环。

---

## 14. 小练习（先自己想，再看答案）

### 练习 1：判断最终输出

```cpp
int n = 7;
if (n > 0) {
    std::cout << "A";
} else if (n > 5) {
    std::cout << "B";
}
```

**答案：**`A`，因为第一个条件已经为真。

### 练习 2：`switch` 贯穿

```cpp
int v = 1;
switch (v) {
    case 1: std::cout << "A";
    case 2: std::cout << "B"; break;
    default: std::cout << "C";
}
```

**答案：**`AB`；`case 1` 缺少 `break`。

### 练习 3：`continue` 和 `break`

```cpp
for (int i = 0; i < 6; ++i) {
    if (i == 2) continue;
    if (i == 4) break;
    std::cout << i << ' ';
}
```

**答案：**`0 1 3`。`2` 被跳过，遇到 `4` 结束循环。

### 练习 4：修改 `while` 中的 Bug

```cpp
int i = 0;
while (i < 5) {
    if (i == 2) continue;
    ++i;
}
```

**问题：**到 `i == 2` 时无限循环。**改法：**确保执行 `continue` 之前也更新 `i`；或者重构循环逻辑，避免提前 `continue` 跳过更新语句。

### 练习 5：枚举判断

尝试定义一个 `enum class QuantType { FP32, FP16, NVFP4 };`，再写一个 `switch` 输出每种格式的名称。

**提示：**`case QuantType::FP32:`，每个 `case` 别忘了处理 `break`。

---

## 15. 常见错误速查表

| 错误 | 为什么有问题 | 如何修正 |
|---|---|---|
| `if (x = 3)` | 把赋值写成比较，可能意外改变 `x` | `if (x == 3)` |
| `if (x > 0); { ... }` | 分号结束 `if`，后面的块不是条件分支 | 去掉 `if` 后的分号 |
| `else if` 的条件顺序写反 | 前面的宽松条件抢先匹配 | 先放更严格/更明确的条件 |
| `switch (std::string)` | `switch` 不支持该控制类型 | 使用 `if / else if` |
| `case` 忘记 `break` | 可能无意贯穿到后面分支 | 添加 `break`，或明确标记有意贯穿 |
| `while` 不改变条件相关状态 | 循环可能永远不结束 | 保证循环条件有机会变成 `false` |
| `while` 中更新之前 `continue` | 可能反复处理同一个值 | 先更新变量或改写逻辑 |
| 想用 `break` 退出所有嵌套循环 | `break` 仅退出最近一层循环 | 用函数加 `return`、标志变量等合理设计 |
| 把 `goto` 当常规循环 | 跳转关系难以维护 | 优先结构化循环、函数拆分 |

---

## 16. 本节核心记忆卡（文字版）

> **分支**：`if` 判断条件真假；`else if` 从上到下匹配；`switch` 用于同一个离散值的多分支。  
> **枚举**：`enum class` 为有限状态起明确名字，常与 `switch` 配合。  
> **循环**：`while` 先判断再重复；传统 `for` = 初始化、条件、更新；范围 `for` 遍历元素。  
> **跳转**：`continue` 跳过本轮；`break` 退出最近一层循环或 switch；`return` 退出函数；`goto` 跳标签，不建议常规使用。  
> **Python 对照**：Python 的 `elif` ≈ C++ 的 `else if`；Python `for ... in ...` 更像 C++ 的范围 `for`，而不是传统三段式 `for`。

### 后续可以衔接的内容

下一步建议学习 **数组、`std::vector`、函数与参数传递、指针和引用**。这时再回头看 `for (int& x : nums)`、`enum class`、`switch (type)`，就可以逐步理解底层推理框架里按数据类型分发计算 Kernel 的代码结构。

---

**备注**：本笔记以 C++17 的主流写法为准；如果以后研究 `llama.cpp` 源码，注意具体版本与构建配置。`switch / enum` 的示例是为了讲语言机制，并不表示所有框架都采用相同的枚举定义或调度方式。
