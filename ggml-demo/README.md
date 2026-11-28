# ggml 从零跑通

一个**单文件脚本** `run_ggml_demo.py`，把 ggml 从「下载数据 → 编译 → 训练 → 推理 → 读源码」的
完整链路跑一遍。所有参数和环境变量都写在脚本里，**不需要任何命令行参数**。

```bash
python ggml-demo/run_ggml_demo.py
```

> 需要 `numpy` 和 `cffi`（Step 5 的 Python 调用要用）。
> 本机可用解释器：`D:\python\python.exe`（Python 3.13，已装好 numpy 2.4.4 / cffi 2.0.0）。

---

## 一、这台 Windows 能不能跑 ggml？

结论：**能，CPU 后端完全可用；CUDA 后端也可行（需要用 Visual Studio 生成器单独编一份）。**

| 项目 | 情况 |
|---|---|
| OS | Windows 11 Pro 10.0.26200 |
| CPU | Intel Core i5-14600KF（14 核 / 20 线程） |
| 指令集 | SSE3 / SSSE3 / AVX / **AVX2** / AVX_VNNI / BMI2 / F16C / FMA（无 AVX-512） |
| 内存 | 31.8 GB |
| 显卡 | NVIDIA RTX 4070 Ti SUPER，16 GB，compute capability **8.9** |
| CUDA Toolkit | **11.8**（`D:\Cuda`），另有 11.3（`D:\Cuda113`） |
| 编译器 | MSYS2 UCRT64 gcc/g++ 16.2.0；另有 Visual Studio 2019 Professional + VC.Tools |
| 构建工具 | CMake 4.4.5、Ninja 1.13.2、OpenMP 5.2 |

### CPU 后端（已实测）

脚本每一步都跑通了：编译 → 训练 30 epoch → 10000 张测试图推理 → **97.93%** 准确率。
i5-14600KF 有 AVX2 + AVX_VNNI，ggml 会自动用上，10 GB 级的小模型推理完全够用。

### CUDA 后端（**已实测跑通**）

硬件完全够：显卡是 sm_89（Ada），**CUDA 11.8 就支持 sm_89** ✅

唯一的坎是工具链：`nvcc` 在 Windows 上**只接受 MSVC 作宿主编译器**，
不能和上面的 MinGW g++ 混用；而 VS 2019 生成器又要求装「CUDA VS 集成」组件（本机没装），
所以走 **`vcvars64.bat` + Ninja** 这条路。仓库里已经写好并验证过的脚本：

```bash
cmd //c ggml-demo\build_ggml_cuda.bat 89     # 89 = Ada (4070 Ti SUPER / 4090)
```

想用脚本一键跑 GPU，把 `run_ggml_demo.py` 里 `CONFIG["use_cuda"]` 改成 `True` 即可
（它会自动调用上面那个 bat，并把 `D:\Cuda\bin` 加进 PATH 以加载 CUDA 运行时 DLL）。

**实测结果**（本机，RTX 4070 Ti SUPER）：

| | CPU 后端 | CUDA 后端 |
|---|---|---|
| 训练 30 epoch | 19 秒 | **5.4 秒** |
| 10000 张推理 | 0.09 秒 | 0.10 秒（模型太小，GPU 启动开销占大头） |
| 准确率 | 97.93% | **97.93%**（完全一致） |

ggml 启动时的输出：

```
ggml_cuda_init: found 1 CUDA devices (Total VRAM: 16375 MiB):
  Device 0: NVIDIA GeForce RTX 4070 Ti SUPER, compute capability 8.9, VMM: yes
mnist_model: using CUDA0 (NVIDIA GeForce RTX 4070 Ti SUPER) as primary backend
```

建议后续升到 **CUDA 12.8+**：ggml 主干的 CUDA 代码对 12.8/12.9 有专门的新特性分支，
11.8 虽然还兼容，但能用的优化少一些。

---

## 二、模型：极小的 MNIST 全连接网络

用的是 ggml 自带的 `examples/mnist`，**模型是脚本自己训练出来的**，不是下载来的：

| | |
|---|---|
| 架构 | `mnist-fc`（784 → 500 → 10 全连接 + ReLU） |
| 参数量 | 784×500 + 500 + 500×10 + 10 = **397,510** |
| 文件大小 | **1.52 MB**（GGUF / F32） |
| 训练 | ggml 自己的优化器 `ggml-opt`，30 epoch，CPU 上约 **19 秒** |
| 准确率 | **97.93%**（10000 张测试图） |

想换成卷积网络？把 `CONFIG["model_arch"]` 改成 `"mnist-cnn"` 即可
（`ggml/examples/mnist/mnist-train-cnn.py` 是 PyTorch 版，但 ggml 自己的
`mnist-train mnist-cnn ...` 也能纯 ggml 训练）。

---

## 三、脚本做了什么

```
Step 0  环境自检    CPU 指令集（由 ggml 自己探测）/ 内存 / 显卡 / 编译器 / CUDA
Step 1  准备数据    自动下载 MNIST(IDX) + 校验 magic number
Step 2  编译 ggml   CPU 后端 + 共享库 + mnist-train/mnist-eval
Step 3  训练模型    调用 ggml 的 mnist-train
Step 4  官方评测    调用 ggml 的 mnist-eval
Step 5  手写前向    ★ 用 Python 直接调 ggml 的 C API，自己搭计算图
Step 6  汇总报告
```

跑 GPU 版：把 `CONFIG["use_cuda"]` 改成 `True`，脚本会自动调 `build_ggml_cuda.bat` 编译 CUDA 后端。

### Step 5 是重点：用 Python 直接调 ggml 的 C API

脚本里手写了一份 cffi 绑定（只声明用到的那部分 `ggml.h` / `gguf.h` / `ggml-backend.h`），
然后自己搭了一个前向计算图：

```
images[784, B] ──mul_mat(w1)──▶ [500, B] ──add(b1)──▶ relu ──┐
                                                                ├─mul_mat(w2)─▶ [10,B] ──add(b2)──▶ logits
```

对照 C++ 版本就是 `ggml/examples/mnist/mnist-common.cpp` 里的 `mnist_model_build()`。

跑出来的准确率和 ggml 官方 `mnist-eval` **完全一致（97.93%）**，两条独立实现互相印证。

---

## 四、踩过的坑（都写进脚本注释了）

1. **`0xC0000139 找不到入口点`**
   exe 用 GCC 16 编译，但 Windows 加载 DLL 时从 Git Bash 的 `/mingw64/bin` 挑到了一份
   更老的 `libstdc++-6.dll`。解法：把 UCRT64 的运行时 DLL 拷到 exe 旁边（脚本 Step 2 会做）。

2. **numpy 数组布局**
   ggml 的张量是 `ne[0]` 连续的，`ne=(784, B)` 的扁平内存顺序是「第 0 张图的所有像素 →
   第 1 张图的所有像素 → …」，正好等于 numpy 的 `(B, 784)` 行主序。
   所以**写完不能 `.T` 转置**——转置后 `tobytes()` 会按行主序重排，数据错位，
   表现是准确率掉到 10% 左右。

3. **`ggml_set_param()` 不要在推理图里调**
   那个标志是给训练用的。加上它 ggml 会换一条 matmul 路径（权重是否 repack），
   浮点累加顺序不同，实测 5/10000 个边界样本翻转，97.93% → 97.88%。

4. **缓冲区分配顺序**
   必须先 `ggml_backend_sched_alloc_graph()` 给计算图分配后端缓冲区，
   再 `ggml_backend_tensor_set()` 灌数据，否则 `tensor->buffer` 还是 NULL，ggml 直接断言失败。

---

## 五、接下来读什么

| 文件 | 看什么 |
|---|---|
| `ggml/examples/simple/simple-backend.cpp` | **最小**的后端调度示例，几百行看懂 ggml 怎么跑一张图 |
| `ggml/examples/mnist/mnist-common.cpp` | 建图 + 读写 GGUF + 训练/评测的完整实现 |
| `ggml/examples/mnist/mnist-eval.cpp` | 推理入口，怎么把模型喂进后端 |
| `ggml/src/ggml.c` | ggml 核心：张量、图、算子 |
| `ggml/src/ggml-cpu/ggml-cpu.cpp` | CPU 后端怎么执行每个算子 |
| `ggml/include/ggml.h` | 全部 C API 声明 |
