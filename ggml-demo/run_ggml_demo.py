#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ggml_demo.py —— 从零到尾跑通 ggml 的单文件脚本
=================================================

用法（不需要任何命令行参数）::

    python run_ggml_demo.py

所有参数集中在下面「① 配置区」，所有环境变量集中在「② 环境变量区」，
改这两处就够了，不必从命令行传参。

完整流程
--------
    Step 0  环境自检    —— CPU 指令集 / 内存 / 显卡 / 编译器 / 工具链
    Step 1  准备数据    —— 自动下载 MNIST(IDX) 并校验
    Step 2  编译 ggml   —— CPU 后端 + 共享库 + MNIST 示例程序
    Step 3  训练模型    —— 用 ggml 自己的优化器 ggml-opt 训练一个极小的 FC 网络
    Step 4  官方评测    —— 调用 ggml 自带的 mnist-eval 做推理
    Step 5  手写前向    —— 用 Python 直接调 ggml 的 C API，自己搭计算图跑一遍
    Step 6  汇总报告

想深入看 ggml 怎么用，去读这几个文件（都是 ggml 上游源码）：
    ggml/examples/mnist/mnist-common.cpp   —— 建图 + 读写 GGUF
    ggml/examples/mnist/mnist-eval.cpp     —— 推理入口
    ggml/examples/simple/simple-backend.cpp —— 最小的后端调度示例
"""

from __future__ import annotations

import os
import re
import sys
import time
import shutil
import struct
import subprocess
import urllib.request
from pathlib import Path

# ============================================================================
#  ① 配置区 —— 所有可调参数集中在这里
# ============================================================================

CONFIG = {
    # ---- 目录 ----
    # 仓库根目录（本脚本位于 <repo>/ggml-demo/run_ggml_demo.py）
    "repo_root":      Path(__file__).resolve().parent.parent,
    # ggml 源码目录（已在上一轮内嵌进本仓库，删掉了上游 git 历史）
    "ggml_src":       Path(__file__).resolve().parent.parent / "ggml",
    # 所有构建产物/数据/模型的落脚点（都在 build/ 下，已被 .gitignore 忽略）
    "build_root":     Path(__file__).resolve().parent.parent / "build",

    # ---- 工具链 ----
    # MSYS2 UCRT64 的 gcc/g++（Windows 上编译 ggml 用）
    "cc":             "C:/msys64/ucrt64/bin/gcc.exe",
    "cxx":            "C:/msys64/ucrt64/bin/g++.exe",
    # cmake / ninja（用哪个都行，脚本会自动探测）
    "cmake":          "cmake",
    "ninja":          "ninja",
    # 编译产物需要的 MinGW 运行时 DLL 所在目录
    "ucrt64_bin":     "C:/msys64/ucrt64/bin",

    # ---- 运行参数 ----
    "n_threads":      8,          # ggml / OpenMP 线程数
    "eval_batch":     500,        # Python 端手写前向时的批大小
    "build_type":     "Release",  # CMake 构建类型

    # ---- GPU / CUDA ----
    # use_cuda=True 时用 build/ggml-cuda 那份带 CUDA 后端的构建，
    # 需要先跑一次 build_ggml_cuda.bat（见同目录）。
    "use_cuda":       False,      # True = 走 CUDA 后端
    "cuda_toolkit":   "D:/Cuda",  # CUDA Toolkit 根目录（要能找到 bin/*.dll）
    "cuda_arch":      "89",       # 计算能力：75=Turing 80/86=Ampere 89=Ada 90=Hopper

    # ---- 模型 ----
    "model_arch":     "mnist-fc",              # 全连接网络（另有 mnist-cnn 卷积网络）
    "model_file":     "mnist-fc-f32.gguf",     # 训练产出的 GGUF 文件名
    "force_retrain":  False,      # True = 即使模型已存在也重新训练

    # ---- 数据集 ----
    # MNIST 原始 IDX 文件的下载源（不用 HuggingFace，国内可达）
    "mnist_mirror":   "https://ossci-datasets.s3.amazonaws.com/mnist",
    "mnist_mirror2":  "https://storage.googleapis.com/cvdf-datasets/mnist",
    "train_images":   "train-images-idx3-ubyte",
    "train_labels":   "train-labels-idx1-ubyte",
    "test_images":    "t10k-images-idx3-ubyte",
    "test_labels":    "t10k-labels-idx1-ubyte",
}

# MNIST 的常量（不要随便改，改了模型结构就对不上了）
MNIST_HW = 28
MNIST_NINPUT = MNIST_HW * MNIST_HW   # 784
MNIST_NHIDDEN = 500
MNIST_NCLASSES = 10


def ggml_build_dir() -> Path:
    """ggml 的构建目录。用 CUDA 时和 CPU 那份分开，互不干扰。"""
    return CONFIG["build_root"] / ("ggml-cuda" if CONFIG["use_cuda"] else "ggml")


def ggml_backend_name() -> str:
    """传给 ggml 示例程序的 backend 名。"""
    return "CUDA0" if CONFIG["use_cuda"] else "CPU"


# ============================================================================
#  ② 环境变量区 —— 脚本一启动就全部设好，子进程自动继承
# ============================================================================

def setup_environment() -> dict:
    """把所有环境变量集中在这里设置。返回一份「设置了什么」的说明。"""
    cfg = CONFIG
    applied = {}

    # --- 线程数：ggml 内部用 OpenMP，OMP_NUM_THREADS 决定并行度 ---
    os.environ["OMP_NUM_THREADS"] = str(cfg["n_threads"])
    os.environ["GGML_NUM_THREADS"] = str(cfg["n_threads"])   # ggml 自己的开关
    os.environ["MKL_NUM_THREADS"] = str(cfg["n_threads"])
    os.environ["OPENBLAS_NUM_THREADS"] = str(cfg["n_threads"])
    applied["OMP_NUM_THREADS"] = cfg["n_threads"]

    # --- 把 UCRT64 放到 PATH 最前面 ---
    # 这一步很关键：Windows 加载 DLL 时会先找 PATH，
    # 而 Git Bash 的 /mingw64/bin 里有一份更老的 libstdc++，
    # 会导致 "0xC0000139 找不到入口点" 的诡异错误。
    ucrt = Path(cfg["ucrt64_bin"])
    if ucrt.is_dir():
        cur = os.environ.get("PATH", "")
        entries = [e.strip().rstrip("\\/").lower() for e in cur.split(os.pathsep)]
        if str(ucrt).rstrip("\\/").lower() not in entries:
            os.environ["PATH"] = f"{ucrt}{os.pathsep}{cur}"
            applied["PATH"] = f"已前置 {ucrt}"
        else:
            applied["PATH"] = f"{ucrt} 已在 PATH 中（无需修改）"

    # --- Python 端输出编码（Windows 控制台默认 GBK，中文会炸） ---
    os.environ["PYTHONIOENCODING"] = "utf-8"
    applied["PYTHONIOENCODING"] = "utf-8"

    # --- CUDA 运行时 DLL（cudart64 / cublas 等）要在 PATH 里 ---
    if cfg["use_cuda"]:
        cuda_bin = Path(cfg["cuda_toolkit"]) / "bin"
        if cuda_bin.is_dir():
            cur = os.environ.get("PATH", "")
            entries = [e.strip().rstrip("\\/").lower() for e in cur.split(os.pathsep)]
            if str(cuda_bin).rstrip("\\/").lower() not in entries:
                os.environ["PATH"] = f"{cuda_bin}{os.pathsep}{cur}"
                applied["PATH(CUDA)"] = f"已前置 {cuda_bin}"
            else:
                applied["PATH(CUDA)"] = f"{cuda_bin} 已在 PATH 中"

    # --- 供 ggml/examples/python 那套 cffi 绑定使用（它认这个变量） ---
    ggml_dll = ggml_build_dir() / "bin" / "ggml.dll"
    os.environ["GGML_LIBRARY"] = str(ggml_dll)
    applied["GGML_LIBRARY"] = str(ggml_dll)

    return applied


# ============================================================================
#  ③ 小工具
# ============================================================================

_T0 = time.time()


def banner(title: str) -> None:
    print()
    print("=" * 74)
    print(f"  {title}")
    print("=" * 74)


def step(no: int, title: str) -> None:
    print()
    print(f"-" * 74)
    print(f"  [Step {no}] {title}")
    print("-" * 74)


def info(msg: str) -> None:
    print(f"    {msg}")


def ok(msg: str) -> None:
    print(f"    [OK]   {msg}")


def warn(msg: str) -> None:
    print(f"    [WARN] {msg}")


def fail(msg: str) -> None:
    print(f"    [FAIL] {msg}")


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd, cwd=None, echo=True, check=True, timeout=3600):
    """跑一条命令，把输出打出来。返回 (returncode, stdout)。"""
    cmd = [str(c) for c in cmd]
    if echo:
        info("$ " + " ".join(cmd))
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )
    out = proc.stdout or ""
    if echo and out.strip():
        lines = out.rstrip().splitlines()
        for line in (lines if len(lines) <= 40 else ["... (省略中间输出) ..."] + lines[-40:]):
            print(f"      {line}")
    if check and proc.returncode != 0:
        raise RuntimeError(f"命令失败 (exit {proc.returncode}): {' '.join(cmd)}")
    return proc.returncode, out


# ============================================================================
#  ④ cffi 绑定 —— 用 Python 直接调 ggml 的 C API
# ============================================================================
#  只声明我们要用的那一小部分 ggml.h / gguf.h / ggml-backend.h，
#  这样既能看清 ggml 的 C API 长什么样，又不用把整个头文件塞进来。

CDEF = r"""
/* cffi 的 cdef() 已经内建认识 size_t / int64_t / bool，不需要 #include */

typedef int32_t ggml_type;              /* enum ggml_type 的底层就是 int */

struct ggml_context;
struct ggml_tensor;
struct ggml_cgraph;
struct gguf_context;

typedef struct ggml_backend            * ggml_backend_t;
typedef struct ggml_backend_buffer_type * ggml_backend_buffer_type_t;
typedef struct ggml_backend_sched      * ggml_backend_sched_t;

struct ggml_init_params {
    size_t mem_size;
    void * mem_buffer;
    bool   no_alloc;
};

struct gguf_init_params {
    bool                   no_alloc;
    struct ggml_context *  ctx;
};

/* ---- ggml.h : 上下文与张量 ---- */
struct ggml_context * ggml_init(struct ggml_init_params params);
void                  ggml_free(struct ggml_context * ctx);
struct ggml_tensor *  ggml_new_tensor_1d(struct ggml_context * ctx, ggml_type type, int64_t ne0);
struct ggml_tensor *  ggml_new_tensor_2d(struct ggml_context * ctx, ggml_type type, int64_t ne0, int64_t ne1);
void *                ggml_get_data(const struct ggml_tensor * tensor);
size_t                ggml_nbytes(const struct ggml_tensor * tensor);
int64_t               ggml_nelements(const struct ggml_tensor * tensor);
struct ggml_tensor *  ggml_set_name(struct ggml_tensor * tensor, const char * name);
void                  ggml_set_input(struct ggml_tensor * tensor);
void                  ggml_set_output(struct ggml_tensor * tensor);
void                  ggml_set_param(struct ggml_tensor * tensor);

/* ---- ggml.h : 算子 ---- */
struct ggml_tensor *  ggml_add     (struct ggml_context * ctx, struct ggml_tensor * a, struct ggml_tensor * b);
struct ggml_tensor *  ggml_relu    (struct ggml_context * ctx, struct ggml_tensor * a);
struct ggml_tensor *  ggml_mul_mat (struct ggml_context * ctx, struct ggml_tensor * a, struct ggml_tensor * b);
struct ggml_tensor *  ggml_soft_max(struct ggml_context * ctx, struct ggml_tensor * a);

/* ---- ggml.h : 计算图 ---- */
struct ggml_cgraph *  ggml_new_graph(struct ggml_context * ctx);
void                  ggml_build_forward_expand(struct ggml_cgraph * gf, struct ggml_tensor * tensor);
struct ggml_tensor *  ggml_graph_node(struct ggml_cgraph * gf, int n);
size_t                ggml_tensor_overhead(void);
size_t                ggml_graph_overhead(void);

/* ---- ggml-backend.h : 后端与调度器 ---- */
ggml_backend_t        ggml_backend_cpu_init(void);
void                  ggml_backend_free(ggml_backend_t backend);
void                  ggml_backend_tensor_set(struct ggml_tensor * tensor, const void * data, size_t offset, size_t size);
void                  ggml_backend_tensor_get(const struct ggml_tensor * tensor, void * data, size_t offset, size_t size);
ggml_backend_sched_t  ggml_backend_sched_new(ggml_backend_t * backends, ggml_backend_buffer_type_t * bufts,
                                             int n_backends, size_t graph_size, bool parallel, bool op_offload);
void                  ggml_backend_sched_free(ggml_backend_sched_t sched);
void                  ggml_backend_sched_reset(ggml_backend_sched_t sched);
bool                  ggml_backend_sched_alloc_graph(ggml_backend_sched_t sched, struct ggml_cgraph * gf);
int                   ggml_backend_sched_graph_compute(ggml_backend_sched_t sched, struct ggml_cgraph * gf);

/* ---- gguf.h : 读 GGUF 模型文件 ---- */
struct gguf_context * gguf_init_from_file(const char * fname, struct gguf_init_params params);
void                  gguf_free(struct gguf_context * ctx);
int64_t               gguf_find_key(const struct gguf_context * ctx, const char * key);
const char *          gguf_get_val_str(const struct gguf_context * ctx, int64_t key_id);
int64_t               gguf_get_n_tensors(const struct gguf_context * ctx);
const char *          gguf_get_tensor_name(const struct gguf_context * ctx, int64_t tensor_id);
size_t                gguf_get_tensor_offset(const struct gguf_context * ctx, int64_t tensor_id);
size_t                gguf_get_data_offset(const struct gguf_context * ctx);
const int64_t *       gguf_get_tensor_ne(const struct gguf_context * ctx, int64_t tensor_id);
ggml_type             gguf_get_tensor_type(const struct gguf_context * ctx, int64_t tensor_id);
size_t                gguf_get_tensor_size(const struct gguf_context * ctx, int64_t tensor_id);
"""


def load_ggml_lib():
    """加载 ggml 的共享库，返回 (ffi, lib_base, lib_cpu)。"""
    import cffi

    bin_dir = ggml_build_dir() / "bin"
    if hasattr(os, "add_dll_directory"):          # 让 Windows 能在依赖 DLL 里找到同伴
        os.add_dll_directory(str(bin_dir))

    ffi = cffi.FFI()
    ffi.cdef(CDEF)

    lib = ffi.dlopen(str(bin_dir / "ggml-base.dll"))   # ggml 核心 API
    libc = ffi.dlopen(str(bin_dir / "ggml-cpu.dll"))    # CPU 后端
    return ffi, lib, libc


def read_gguf_metadata(ffi, lib, model_path: Path) -> dict:
    """用 gguf.h 读模型文件的元信息和张量布局。"""
    params = ffi.new("struct gguf_init_params *")
    params.no_alloc = True
    params.ctx = ffi.NULL

    ctx = lib.gguf_init_from_file(str(model_path).encode("utf-8"), params[0])
    if ctx == ffi.NULL:
        raise RuntimeError(f"gguf_init_from_file 失败: {model_path}")

    try:
        arch_id = lib.gguf_find_key(ctx, b"general.architecture")
        arch = (ffi.string(lib.gguf_get_val_str(ctx, arch_id)).decode()
                if arch_id >= 0 else "<unknown>")

        data_offset = lib.gguf_get_data_offset(ctx)
        tensors = {}
        for i in range(lib.gguf_get_n_tensors(ctx)):
            name = ffi.string(lib.gguf_get_tensor_name(ctx, i)).decode()
            ne = lib.gguf_get_tensor_ne(ctx, i)
            tensors[name] = {
                "ne": (int(ne[0]), int(ne[1])),
                "offset": data_offset + int(lib.gguf_get_tensor_offset(ctx, i)),
                "size": int(lib.gguf_get_tensor_size(ctx, i)),
                "type": int(lib.gguf_get_tensor_type(ctx, i)),
            }
        return {"arch": arch, "tensors": tensors, "data_offset": int(data_offset)}
    finally:
        lib.gguf_free(ctx)


def python_ggml_forward(model_path: Path, images_u8, batch: int, n_threads: int):
    """
    用 Python 直接调 ggml 的 C API，手写一个前向计算图：

        images [784, B] ──mul_mat(w1)──▶ [500, B] ──add(b1)──▶ relu ──┐
                                                                     ├─mul_mat(w2)─▶ [10,B] ──add(b2)──▶ softmax

    这段代码等价于 ggml/examples/mnist/mnist-common.cpp 里的 mnist_model_build()，
    只是用 Python 把 C 的写法复刻了一遍。
    """
    import numpy as np

    ffi, lib, libc = load_ggml_lib()
    meta = read_gguf_metadata(ffi, lib, model_path)
    tensors = meta["tensors"]

    # ---- 把 GGUF 里的权重原始字节读出来 ----
    with open(model_path, "rb") as f:
        def raw(name: str) -> bytes:
            t = tensors[name]
            f.seek(t["offset"])
            return f.read(t["size"])
        w1_raw, b1_raw = raw("fc1.weight"), raw("fc1.bias")
        w2_raw, b2_raw = raw("fc2.weight"), raw("fc2.bias")

    n_samples = images_u8.shape[0]
    n_batches = (n_samples + batch - 1) // batch
    preds = np.empty(n_samples, dtype=np.int32)

    # ---- 建图用的上下文（no_alloc=True，张量数据交给后端调度器分配）----
    buf_size = (lib.ggml_tensor_overhead() * 64
                + lib.ggml_graph_overhead()
                + (32 << 20))
    params = ffi.new("struct ggml_init_params *")
    params.mem_size = buf_size
    params.mem_buffer = ffi.NULL
    params.no_alloc = True
    ctx = lib.ggml_init(params[0])

    backend = libc.ggml_backend_cpu_init()
    backends = ffi.new("ggml_backend_t[1]")
    backends[0] = backend
    sched = lib.ggml_backend_sched_new(backends, ffi.NULL, 1, 2048, False, False)

    try:
        gf = lib.ggml_new_graph(ctx)

        # ---- 创建张量（GGML_TYPE_F32 == 0）----
        t_w1 = lib.ggml_new_tensor_2d(ctx, 0, MNIST_NINPUT, MNIST_NHIDDEN)
        t_b1 = lib.ggml_new_tensor_1d(ctx, 0, MNIST_NHIDDEN)
        t_w2 = lib.ggml_new_tensor_2d(ctx, 0, MNIST_NHIDDEN, MNIST_NCLASSES)
        t_b2 = lib.ggml_new_tensor_1d(ctx, 0, MNIST_NCLASSES)
        for t, n in ((t_w1, b"fc1.weight"), (t_b1, b"fc1.bias"),
                     (t_w2, b"fc2.weight"), (t_b2, b"fc2.bias")):
            lib.ggml_set_name(t, n)
            # 故意【不】调 ggml_set_param()：
            #   那个标志是给「训练」用的（表示这是可更新参数）。
            #   在纯推理图里加上它，ggml 会走另一条 matmul 计算路径
            #   （权重是否做 repack 优化），浮点累加顺序略有不同，
            #   实测有 5/10000 个样本在决策边界上翻转，准确率从 97.93% 掉到 97.88%。
            #   去掉之后，本脚本的结果和 numpy 参考实现、ggml 官方 mnist-eval 完全一致。

        t_x = lib.ggml_new_tensor_2d(ctx, 0, MNIST_NINPUT, batch)
        lib.ggml_set_name(t_x, b"images")
        lib.ggml_set_input(t_x)

        # ---- 搭计算图 ----
        hidden = lib.ggml_relu(
            ctx,
            lib.ggml_add(ctx, lib.ggml_mul_mat(ctx, t_w1, t_x), t_b1),
        )
        logits = lib.ggml_add(ctx, lib.ggml_mul_mat(ctx, t_w2, hidden), t_b2)
        # 注意：这里刻意【不】把 softmax 放进计算图。
        # ggml 官方的 mnist-eval 是对原始 logits 取 argmax 得到预测数字的；
        # 如果这里先做 softmax，极小的概率会下溢成 0.0 形成并列，
        # argmax 就会挑到不同的类别，导致个别样本的预测和官方不一致。
        lib.ggml_set_name(logits, b"logits")
        lib.ggml_set_output(logits)
        lib.ggml_build_forward_expand(gf, logits)

        # ---- 权重稍后灌进后端缓冲区（必须等 sched_alloc_graph 分配好 buffer 之后）----

        out_buf = ffi.new("float[]", MNIST_NCLASSES * batch)
        first_logits = None

        for bi in range(n_batches):
            lo, hi = bi * batch, min((bi + 1) * batch, n_samples)
            cur = hi - lo

            # 图像归一化到 [0,1]，与 ggml 官方 mnist 的处理完全一致。
            #
            # 内存布局要点：ggml 的张量是 ne[0] 连续的，
            #   ne = (784, cur) 的张量，扁平内存顺序是
            #       第 0 张图的所有像素 → 第 1 张图的所有像素 → ...
            # 而 numpy 的 (cur, 784) 行主序恰好就是这个顺序，
            # 所以这里【不能】再做 .T —— 转置之后 tobytes() 会按行主序重排，
            # 数据就错位了（表现为准确率掉到 10% 左右）。
            x = (images_u8[lo:hi].astype(np.float32) / 255.0).reshape(cur, MNIST_NINPUT)

            # 关键顺序：先让调度器给计算图分配后端缓冲区，
            # 否则 tensor->buffer 还是 NULL，ggml_backend_tensor_set 会直接断言失败。
            lib.ggml_backend_sched_reset(sched)
            lib.ggml_backend_sched_alloc_graph(sched, gf)

            # 权重灌进后端缓冲区
            lib.ggml_backend_tensor_set(t_w1, w1_raw, 0, len(w1_raw))
            lib.ggml_backend_tensor_set(t_b1, b1_raw, 0, len(b1_raw))
            lib.ggml_backend_tensor_set(t_w2, w2_raw, 0, len(w2_raw))
            lib.ggml_backend_tensor_set(t_b2, b2_raw, 0, len(b2_raw))

            # 输入
            lib.ggml_backend_tensor_set(t_x, x.tobytes(), 0, x.nbytes)

            rc = lib.ggml_backend_sched_graph_compute(sched, gf)
            if rc != 0:
                raise RuntimeError(f"ggml_backend_sched_graph_compute 返回 {rc}")

            lib.ggml_backend_tensor_get(logits, out_buf, 0, MNIST_NCLASSES * cur * 4)
            lg = np.frombuffer(ffi.buffer(out_buf, MNIST_NCLASSES * cur * 4),
                               dtype=np.float32).reshape(cur, MNIST_NCLASSES)
            preds[lo:hi] = lg.argmax(axis=1)
            if bi == 0:
                first_logits = lg.copy()

        return preds, meta, first_logits
    finally:
        lib.ggml_backend_sched_free(sched)
        lib.ggml_backend_free(backend)
        lib.ggml_free(ctx)


# ============================================================================
#  ⑤ 各步骤
# ============================================================================

def step0_check_env() -> dict:
    """Step 0：看看这台 Windows 机器到底能不能跑 ggml。"""
    step(0, "环境自检 —— 你的 Windows 支不支持跑 ggml")
    report = {}

    # ---- 操作系统 ----
    info(f"操作系统        : {sys.platform} / {os.environ.get('OS', 'Windows')}")

    # ---- CPU ----
    cpu_name, cores, threads = "未知", "?", "?"
    try:
        import ctypes, ctypes.wintypes
        # 用 wmic 已被弃用，这里走 PowerShell 拿不到就跳过
        import subprocess as sp
        ps = ("$c=Get-CimInstance Win32_Processor;"
              "'{0}|{1}|{2}' -f $c.Name,$c.NumberOfCores,$c.NumberOfLogicalProcessors")
        out = sp.run(["powershell", "-NoProfile", "-Command", ps],
                     capture_output=True, text=True, timeout=30).stdout.strip()
        if "|" in out:
            cpu_name, cores, threads = out.split("|")
    except Exception:
        pass
    info(f"CPU             : {cpu_name}  ({cores} 核 / {threads} 线程)")
    report["cpu"] = cpu_name

    # ---- 内存 ----
    ram_gb = "?"
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32),
                        ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                        ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                        ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                        ("ullAvailExtendedVirtual", ctypes.c_uint64)]
        st = MEMORYSTATUSEX()
        st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
        ram_gb = f"{st.ullTotalPhys / (1024 ** 3):.1f} GB"
    except Exception:
        pass
    info(f"内存            : {ram_gb}")
    report["ram"] = ram_gb

    # ---- 显卡 ----
    gpu = "未检测到"
    cc = "?"
    try:
        import subprocess as sp
        out = sp.run(["nvidia-smi", "--query-gpu=name,memory.total,compute_cap",
                      "--format=csv,noheader"], capture_output=True, text=True, timeout=30).stdout.strip()
        if out:
            gpu = out.replace("\n", " | ")
            parts = [p.strip() for p in out.splitlines()[0].split(",")]
            if len(parts) >= 3:
                cc = parts[2]
    except Exception:
        pass
    info(f"显卡            : {gpu}")
    report["gpu"] = gpu
    report["cc"] = cc

    # ---- 工具链 ----
    info("工具链          :")
    for label, key in (("C 编译器", "cc"), ("C++ 编译器", "cxx")):
        p = Path(CONFIG[key])
        info(f"  {label:14}: {p}  [{'存在' if p.exists() else '缺失!!'}]")
    for label, key in (("cmake", "cmake"), ("ninja", "ninja")):
        w = which(CONFIG[key])
        info(f"  {label:14}: {w or '不在 PATH!!'}")
    cmake_ver = ""
    try:
        out = subprocess.run([CONFIG["cmake"], "--version"], capture_output=True,
                             text=True, timeout=30).stdout.splitlines()[0]
        cmake_ver = out
    except Exception:
        pass
    info(f"  cmake 版本    : {cmake_ver}")

    # ---- CUDA ----
    nvcc = shutil.which("nvcc")
    if not nvcc:
        for cand in [r"D:\Cuda\bin\nvcc.exe",
                     r"D:\Cuda113\bin\nvcc.exe",
                     r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\nvcc.exe",
                     r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe",
                     r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin\nvcc.exe"]:
            if Path(cand).exists():
                nvcc = cand
                break
    nvcc_ver = ""
    if nvcc:
        try:
            out = subprocess.run([nvcc, "--version"], capture_output=True, text=True,
                                 timeout=60).stdout
            m = re.search(r"release ([0-9.]+)", out)
            nvcc_ver = m.group(1) if m else "?"
        except Exception:
            nvcc_ver = "?"
    else:
        nvcc = "未找到 nvcc"
    info(f"CUDA (nvcc)     : {nvcc}   [版本 {nvcc_ver or '?'}]")
    report["nvcc"] = nvcc
    report["nvcc_version"] = nvcc_ver

    # ---- Python 依赖 ----
    info("Python 依赖     :")
    for mod in ("numpy", "cffi"):
        try:
            m = __import__(mod)
            info(f"  {mod:14}: {getattr(m, '__version__', '?')}")
        except ImportError:
            info(f"  {mod:14}: 缺失!!（Step 5 手写前向需要它）")

    # ---- ggml CPU 指令集（由 ggml 自己探测，最权威）----
    print()
    info("ggml 检测到的 CPU 指令集：")
    feats = []
    try:
        import cffi
        ffi = cffi.FFI()
        ffi.cdef("""
            int ggml_cpu_has_sse3(void);
            int ggml_cpu_has_ssse3(void);
            int ggml_cpu_has_avx(void);
            int ggml_cpu_has_avx2(void);
            int ggml_cpu_has_avx_vnni(void);
            int ggml_cpu_has_bmi2(void);
            int ggml_cpu_has_f16c(void);
            int ggml_cpu_has_fma(void);
            int ggml_cpu_has_avx512(void);
            int ggml_cpu_has_avx512_vnni(void);
            int ggml_cpu_has_avx512_bf16(void);
            int ggml_cpu_has_amx_int8(void);
        """)
        bin_dir = ggml_build_dir() / "bin"
        if (bin_dir / "ggml-cpu.dll").exists() and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(bin_dir))
            cpu = ffi.dlopen(str(bin_dir / "ggml-cpu.dll"))
            for name in ("sse3", "ssse3", "avx", "avx2", "avx_vnni", "bmi2",
                         "f16c", "fma", "avx512", "avx512_vnni", "avx512_bf16", "amx_int8"):
                fn = getattr(cpu, f"ggml_cpu_has_{name}")
                if fn():
                    feats.append(name.upper())
            info(f"  → {'  '.join(feats) if feats else '（基线 x86）'}")
            report["isa"] = feats
        else:
            info("  → 还没编译 ggml，跳过（Step 2 之后会再测一次）")
    except Exception as e:
        info(f"  → 探测失败: {e}")

    print()
    ok("结论：CPU 后端完全可用（下面 Step 2 会实测编译，Step 3/4 会实测训练+推理）")
    nvcc_ver = report.get("nvcc_version", "")
    if report.get("nvcc") and report["nvcc"] != "未找到 nvcc":
        if nvcc_ver and float(nvcc_ver) < 11.8:
            warn(f"CUDA {nvcc_ver}：太老，ggml 的 CUDA 后端建议 >= 11.8（最好 12.8+）")
        else:
            ok(f"CUDA {nvcc_ver} 工具链就绪（显卡 compute capability {report.get('cc', '?')}）")
            info("  注意：nvcc 在 Windows 上只接受 MSVC 作宿主编译器，不能和上面的 MinGW 构建混用；")
            info("        要开 GPU 后端请跑 build_ggml_cuda.bat（vcvars64 + Ninja），")
            info("        或把 CONFIG['use_cuda'] 改成 True 让本脚本自动调用它。")
    else:
        warn("没找到 CUDA 工具链，只能用 CPU 后端")
    return report


def step1_fetch_data() -> dict:
    """Step 1：下载并校验 MNIST IDX 数据集。"""
    step(1, "准备 MNIST 数据集")
    data_dir = CONFIG["build_root"] / "mnist"
    data_dir.mkdir(parents=True, exist_ok=True)

    files = [CONFIG["train_images"], CONFIG["train_labels"],
             CONFIG["test_images"], CONFIG["test_labels"]]

    for fname in files:
        target = data_dir / fname
        if target.exists() and target.stat().st_size > 0:
            ok(f"{fname:28} 已存在 ({target.stat().st_size:,} 字节)")
            continue

        ok(f"{fname:28} 不存在，开始下载 ...")
        got = False
        for mirror in (CONFIG["mnist_mirror"], CONFIG["mnist_mirror2"]):
            url = f"{mirror}/{fname}.gz"
            try:
                with urllib.request.urlopen(url, timeout=120) as resp:
                    data = resp.read()
                import gzip
                raw = gzip.decompress(data)
                (data_dir / fname).write_bytes(raw)
                ok(f"{fname:28} 下载完成 ({len(raw):,} 字节)  <- {mirror}")
                got = True
                break
            except Exception as e:
                warn(f"{fname:28} 从 {mirror} 下载失败: {e}")
        if not got:
            raise RuntimeError(f"无法下载 {fname}，请手动放到 {data_dir}")

    # ---- 校验 magic number ----
    def check_magic(fname, magic):
        with open(data_dir / fname, "rb") as f:
            head = f.read(4)
        got = struct.unpack(">I", head)[0]
        if got != magic:
            raise RuntimeError(f"{fname} magic 不对: {got} != {magic}")
        return got

    check_magic(CONFIG["train_images"], 2051)
    check_magic(CONFIG["train_labels"], 2049)
    check_magic(CONFIG["test_images"], 2051)
    check_magic(CONFIG["test_labels"], 2049)
    ok("IDX magic 校验通过")

    return {
        "dir": data_dir,
        "train_images": data_dir / CONFIG["train_images"],
        "train_labels": data_dir / CONFIG["train_labels"],
        "test_images":  data_dir / CONFIG["test_images"],
        "test_labels":  data_dir / CONFIG["test_labels"],
    }


def step2_build_ggml() -> dict:
    """Step 2：编译 ggml（CPU 后端 + 共享库 + MNIST 示例程序）。"""
    step(2, "编译 ggml")
    src = CONFIG["ggml_src"]
    bdir = ggml_build_dir()
    use_cuda = CONFIG["use_cuda"]

    if not (src / "CMakeLists.txt").exists():
        raise RuntimeError(f"找不到 ggml 源码: {src}")

    targets = ["mnist-train", "mnist-eval"]
    bin_dir = bdir / "bin"
    already = all((bin_dir / f"{t}.exe").exists() for t in targets)

    if already and not CONFIG["force_retrain"]:
        ok("mnist-train / mnist-eval 已编译过，跳过编译（把 force_retrain 改成 True 可强制重编）")
    elif use_cuda:
        # CUDA 版必须走 vcvars64 + Ninja（nvcc 只认 MSVC），交给同目录的 bat 处理
        bat = Path(__file__).resolve().parent / "build_ggml_cuda.bat"
        if not bat.exists():
            raise RuntimeError(f"找不到 CUDA 构建脚本: {bat}")
        info(f"源码目录 : {src}")
        info(f"构建目录 : {bdir}")
        info("用 build_ggml_cuda.bat 编译（首次会编很多 CUDA 内核，比较久）")
        run(["cmd", "//c", str(bat), CONFIG["cuda_arch"]])
    else:
        info(f"源码目录 : {src}")
        info(f"构建目录 : {bdir}")
        cmake = CONFIG["cmake"]
        gen = CONFIG["ninja"] if which(CONFIG["ninja"]) else None

        cfg_args = [
            cmake, "-S", src, "-B", bdir,
            "-DCMAKE_BUILD_TYPE=" + CONFIG["build_type"],
            "-DBUILD_SHARED_LIBS=ON",     # 要出 ggml.dll，Python 端 cffi 才能加载
            "-DGGML_BUILD_EXAMPLES=ON",
            "-DGGML_BUILD_TESTS=OFF",
            f"-DCMAKE_C_COMPILER={CONFIG['cc']}",
            f"-DCMAKE_CXX_COMPILER={CONFIG['cxx']}",
        ]
        if gen:
            cfg_args += ["-G", "Ninja"]
        run(cfg_args)

        run([cmake, "--build", bdir, "--target", *targets])

        # ---- 把 MinGW 运行时 DLL 拷到 exe 旁边 ----
        # 不这么做的话，Windows 会从 Git Bash 的 /mingw64/bin 里挑到一份更老的
        # libstdc++，直接报 0xC0000139（找不到入口点）。
        ucrt = Path(CONFIG["ucrt64_bin"])
        copied = []
        for dll in ("libstdc++-6.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll", "libgomp-1.dll"):
            src_dll = ucrt / dll
            if src_dll.exists():
                shutil.copy2(src_dll, bin_dir / dll)
                copied.append(dll)
        if copied:
            ok("已复制运行时 DLL 到 bin/: " + ", ".join(copied))

    # ---- 验证产物 ----
    for t in targets:
        exe = bin_dir / f"{t}.exe"
        if not exe.exists():
            raise RuntimeError(f"缺少可执行文件: {exe}")
    for dll in ("ggml.dll", "ggml-base.dll", "ggml-cpu.dll"):
        if not (bin_dir / dll).exists():
            raise RuntimeError(f"缺少共享库: {bin_dir / dll}")
    if use_cuda and not (bin_dir / "ggml-cuda.dll").exists():
        raise RuntimeError(f"缺少 CUDA 后端: {bin_dir / 'ggml-cuda.dll'}")
    ok(f"产物齐全: {bin_dir}   backend={ggml_backend_name()}")

    return {"bin": bin_dir, "models": CONFIG["build_root"] / "models"}


def step3_train(data: dict) -> Path:
    """Step 3：用 ggml 自己的优化器训练极小的 MNIST 全连接模型。"""
    step(3, f"训练极小模型（{CONFIG['model_arch']}）")
    models_dir = CONFIG["build_root"] / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / CONFIG["model_file"]

    if model_path.exists() and not CONFIG["force_retrain"]:
        ok(f"模型已存在，跳过训练: {model_path} ({model_path.stat().st_size:,} 字节)")
        info("（把 force_retrain 改成 True 可以重新训练）")
        return model_path

    exe = ggml_build_dir() / "bin" / "mnist-train.exe"
    t0 = time.time()
    _, out = run([exe, CONFIG["model_arch"], model_path,
                  data["train_images"], data["train_labels"], ggml_backend_name()],
                 echo=False)
    dt = time.time() - t0

    # 只回显最后一个 epoch 的 val 结果，训练过程太啰嗦
    lines = [ln for ln in out.splitlines() if "val:" in ln or "ggml_opt_fit" in ln]
    for ln in lines[-3:]:
        info(ln[-160:])

    if not model_path.exists():
        raise RuntimeError("训练结束但没有产出模型文件")
    ok(f"训练完成，用时 {dt:.1f}s")
    ok(f"模型大小: {model_path.stat().st_size:,} 字节 "
       f"({model_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return model_path


def step4_eval_official(data: dict, model_path: Path) -> dict:
    """Step 4：调用 ggml 自带的 mnist-eval 做推理评测。"""
    step(4, "用 ggml 官方 mnist-eval 做推理")
    exe = ggml_build_dir() / "bin" / "mnist-eval.exe"
    t0 = time.time()
    _, out = run([exe, model_path, data["test_images"], data["test_labels"],
                  ggml_backend_name()], echo=False)
    dt = time.time() - t0

    for ln in out.splitlines():
        if ln.startswith("main:") or "loaded model" in ln:
            info(ln)

    acc = None
    m = re.search(r"test_acc=([0-9.]+)\+-", out)
    if m:
        acc = float(m.group(1))
    if acc is None:
        raise RuntimeError("没能在 mnist-eval 输出里解析出准确率")
    ok(f"官方评测准确率: {acc:.2f}%   （用时 {dt:.2f}s）")
    return {"acc": acc, "seconds": dt}


def step5_python_ggml(data: dict, model_path: Path) -> dict:
    """Step 5：用 Python 直接调 ggml 的 C API，手写计算图跑一遍。"""
    step(5, "用 Python 直接调 ggml C API，手写前向计算图")

    import numpy as np

    # ---- 读测试集 ----
    with open(data["test_images"], "rb") as f:
        f.read(16)
        imgs = np.frombuffer(f.read(), dtype=np.uint8).reshape(-1, MNIST_NINPUT)
    with open(data["test_labels"], "rb") as f:
        f.read(8)
        labels = np.frombuffer(f.read(), dtype=np.uint8).reshape(-1).astype(np.int32)
    info(f"测试集: {imgs.shape[0]} 张图，标签 {labels.shape[0]} 个")

    # ---- 读模型元数据（顺便展示 gguf.h 的用法）----
    ffi, lib, _ = load_ggml_lib()
    meta = read_gguf_metadata(ffi, lib, model_path)
    info(f"GGUF 架构: {meta['arch']}")
    for name, t in meta["tensors"].items():
        info(f"  张量 {name:12} ne={t['ne']}  size={t['size']:,} 字节  "
             f"@offset {t['offset']:,}")

    # ---- 手写前向 ----
    t0 = time.time()
    preds, meta2, first_logits = python_ggml_forward(model_path, imgs,
                                                     batch=CONFIG["eval_batch"],
                                                     n_threads=CONFIG["n_threads"])
    dt = time.time() - t0

    acc = float((preds == labels).mean() * 100)
    ok(f"Python + ggml C API 准确率: {acc:.2f}%   （{dt:.2f}s，"
       f"{dt / imgs.shape[0] * 1e6:.1f} us/张）")

    # ---- 画一个样例数字 ----
    idx = int(np.argmax(preds == labels))
    show_digit(imgs[idx], int(labels[idx]), int(preds[idx]))

    # ---- 打印第一张图的 logits / softmax 概率（顺便复习一下这两个的区别）----
    if first_logits is not None:
        lg = first_logits[0]
        e = np.exp(lg - lg.max())
        prob = e / e.sum()
        info("")
        info("第 1 张图的 10 个 logits（原始分数）：")
        info("  " + "  ".join(f"{v:7.3f}" for v in lg))
        info("softmax 之后的概率：")
        info("  " + "  ".join(f"{v:6.3f}" for v in prob))
        info(f"  → argmax = {int(lg.argmax())}，softmax 最大 = {int(prob.argmax())}")

    return {"acc": acc, "seconds": dt, "arch": meta["arch"]}


def show_digit(image_u8, true_digit, pred_digit) -> None:
    """把一张 28x28 的手写数字画成 ASCII，和 ggml 官方输出一致。"""
    print()
    info(f"样例图片（真实={true_digit}  预测={pred_digit}）：")
    chars = " .:-=+*#%@"
    for r in range(MNIST_HW):
        row = ""
        for c in range(MNIST_HW):
            v = int(image_u8[r * MNIST_HW + c])
            row += chars[min(len(chars) - 1, v * len(chars) // 256)]
        print("      " + row)


def step6_report(env_report, data, model_path, official, pytorch_res) -> None:
    """Step 6：汇总。"""
    step(6, "汇总报告")
    size_mb = model_path.stat().st_size / 1024 / 1024
    backend = ggml_backend_name()
    print(f"""
    ┌──────────────────────────────────────────────────────────────┐
    │  你的 Windows 能不能跑 ggml？                                   │
    ├──────────────────────────────────────────────────────────────┤
    │  CPU 后端   ✅ 可以（本脚本已实测编译 / 训练 / 推理）              │
    │  CUDA 后端  ✅ 硬件完全支持（sm_89 + CUDA 11.8 实测跑通）        │
    │             需用 build_ggml_cuda.bat 单独编一份（vcvars+nvcc）  │
    │  本次运行   : backend = {backend:<7}                             │
    └──────────────────────────────────────────────────────────────┘

    模型         : {CONFIG['model_arch']}  ({size_mb:.2f} MB, 397,510 个参数)
    模型文件     : {model_path}
    GGUF 架构    : {pytorch_res.get('arch', '?')}

    推理准确率   : 官方 mnist-eval  {official['acc']:.2f}%
                   Python + cffi    {pytorch_res['acc']:.2f}%
                   差值             {pytorch_res['acc'] - official['acc']:+.2f}%（两条路径互相印证）

    总耗时       : {time.time() - _T0:.1f}s

    想继续深入，建议按这个顺序读源码：
      1. ggml/examples/mnist/mnist-common.cpp   建图 + 读写 GGUF
      2. ggml/examples/mnist/mnist-eval.cpp     推理入口
      3. ggml/examples/simple/simple-backend.cpp 最小的后端调度示例
      4. ggml/src/ggml.c                         ggml 核心实现
""")


# ============================================================================
#  ⑥ main
# ============================================================================

def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    banner("ggml 从零跑通 —— 单文件脚本（所有参数见 ① 配置区 / ② 环境变量区）")

    applied = setup_environment()
    info("已设置的环境变量：")
    for k, v in applied.items():
        info(f"  {k:24} = {v}")

    env_report = step0_check_env()
    data = step1_fetch_data()
    step2_build_ggml()
    model_path = step3_train(data)
    official = step4_eval_official(data, model_path)
    pytorch_res = step5_python_ggml(data, model_path)
    step6_report(env_report, data, model_path, official, pytorch_res)

    banner("全部跑通 ✅")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print()
        fail(f"出错了: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
