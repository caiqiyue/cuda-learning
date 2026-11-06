你混淆的是两个不同场景：

```
int* p;   // 声明：p 是指针
*p = 10;  // 表达式：解引用 p
```

在**声明中**，\`*\` 表示“指针类型”；在\**表达式中**，\`\*p\` 表示“访问指针指向的对象”。

---

## 一、普通变量和常量

```
int p;
```

`p` 是一个普通 `int` 变量，可以修改。

```
const int p;
int const p;
```

这两种写法完全等价：

```
p 是一个 const int
```

`p` 本身不能修改。

```
const int p = 10;
p = 20; // 错误
```

---

## 二、指针

```
int* p;
```

读作：

```
p 是一个指针，指向 int
```

也可以写成：

```
int *p;
```

空格位置不影响含义。

```
int value = 10;
int* p = &value;

*p = 20; // 通过指针修改 value
```

这里：

```
p   // 指针中保存的地址
*p  // 指针指向的 int 对象
```

---

## 三、带括号的 `int (*p)`

```
int (*p);
```

这里的括号没有改变含义，仍然是：

```
p 是一个指向 int 的指针
```

通常直接写：

```
int* p;
```

更清楚。

括号在复杂声明中才特别重要：

```
int (*p)(int);
```

这表示：

```
p 是一个函数指针
指向一个接收 int、返回 int 的函数
```

对比：

```
int* p(int);
```

这表示：

```
p 是一个函数
接收 int
返回 int*
```

---

# 四、\`const\` 和指针

判断时看 `const` 修饰谁。

## 1. 指向 const int 的指针

```
const int* p;
int const* p;
```

这两种写法完全等价：

```
p 是指针
p 指向一个 const int
```

可以改变指针指向：

```
int a = 10;
int b = 20;

const int* p = &a;
p = &b;       // 可以
```

不能通过 `p` 修改对象：

```
*p = 30;      // 错误
```

注意，原对象本身不一定是 const：

```
int a = 10;
const int* p = &a;

a = 20;       // 可以直接修改 a
```

只是不能通过 `p` 修改。

---

## 2. const 指针

```
int* const p = nullptr;
```

读作：

```
p 是一个 const 指针，指向 int
```

指针本身不能改变指向：

```
int a = 10;
int b = 20;

int* const p = &a;

*p = 30;  // 可以修改 a
p = &b;   // 错误，p 不能改指向
```

---

## 3. 指向 const int 的 const 指针

```
const int* const p = nullptr;
```

或者：

```
int const* const p = nullptr;
```

含义：

```
p 不能改变指向
不能通过 p 修改对象
```

这是两层 `const`：

```
左边的 const：对象不能通过指针修改
右边的 const：指针本身不能改指向
```

---

## 五、你写的 `const int const *p`

```
const int const* p;
```

这是错误写法，因为同一个 `int` 被重复加了两次 `const`。

如果你想表达：

```
指向 const int 的指针
```

写：

```
const int* p;
```

如果你想表达：

```
指向 const int 的 const 指针
```

写：

```
const int* const p;
```

---

# 六、引用

## 1. `const int& p`

```
const int& p;
```

这是合法写法，表示：

```
p 是 int 的 const 引用
```

也可以写成：

```
int const& p;
```

两者等价。

引用不是指针，不需要使用 `*` 解引用：

```
int value = 10;
const int& ref = value;

std::cout << ref; // 直接使用
```

不能通过它修改对象：

```
ref = 20; // 错误
```

---

## 2. `int& const p`

```
int& const p;
```

这是错误写法。

引用本身不能再加 `const`。引用一旦绑定对象，就不能改绑到另一个对象，因此不存在“const 引用本身”这个独立概念。

正确写法是：

```
const int& p;
```

它表示“引用一个不能修改的 int 对象”。

---

## 3. `const int& const p`

```
const int& const p;
```

也是错误写法。

引用不能加第二个 `const`。正确写法：

```
const int& p;
```

---

# 七、总表


| 写法                 | 含义                        | 是否能改指向 | 是否能改对象 |
| -------------------- | --------------------------- | -----------: | -----------: |
| `int p`              | 普通`int`                   |            - |         可以 |
| `const int p`        | const`int`                  |            - |       不可以 |
| `int const p`        | 与上面相同                  |            - |       不可以 |
| `int* p`             | 指向可修改`int`的指针       |         可以 |         可以 |
| `const int* p`       | 指向 const`int`的指针       |         可以 |       不可以 |
| `int const* p`       | 与上面相同                  |         可以 |       不可以 |
| `int* const p`       | const 指针，指向可修改`int` |       不可以 |         可以 |
| `const int* const p` | const 指针，指向 const`int` |       不可以 |       不可以 |
| `const int& p`       | const`int`的引用            |       不适用 |       不可以 |
| `int& const p`       | 非法                        |            - |            - |
| `const int& const p` | 非法                        |            - |            - |

---

## 八、最实用的阅读方法

从变量名开始，向外读：

```
const int* const p;
```

从 `p` 开始：

```
p
p 是 const
p 是指针
p 指向 const int
```

所以：

```
p 是一个 const 指针，指向 const int
```

再看：

```
const int& p;
```

从 `p` 开始：

```
p 是一个引用
p 引用 const int
```

因此：

```
p 是 const int 的引用
```

最后记住：

```
声明中的 *：表示指针
表达式中的 *p：表示解引用

声明中的 &：表示引用
表达式中的 &p：表示取地址
```
