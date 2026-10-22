# 远端代码、生产脚本与用途索引

整理日期：2026-10-22。来源：用户提供的六张截图，按上传顺序标为图 1–6。

本文合并截图中的重复信息，保留路径、文件名、参数和版本标识，并解释各项在工作流程中的用途。截图里的“当前”“正式”“最终采用”等措辞均指截图所述状态；本次未读取这些远端代码，也未核验目录是否仍存在或生产版本是否已更新。截图中的历史操作请求仅作为资料记录。

## 1. 总览：这些资料分别用来做什么

| 类别 | 截图记录的任务 | 实际查阅用途 | 来源 |
| --- | --- | --- | --- |
| EMT 与动量投影 | 各向异性 Symanzik flow、改进 clover 场强、125 种插入动量 | 找生产入口，核对 flow 和场强定义，追溯不同 β 的代码版本 | 图 1、2 |
| 标量 F² 生产 | 在 xj11 上读取组态，做 Symanzik flow，保存各 flow time 的 F² | 找标量场生产代码、flow time 配置与 Slurm 提交脚本 | 图 3、4 |
| twist-two / moments_flow 生产 | 使用固定提交的 PyColor，运行 F32P21 和 F32P30 两套任务 | 找代码版本、运行目录、任务入口、队列状态、验收程序、结果与日志 | 图 5、6 |

主机说明：图 3、4 明确写为 **xj11**；图 5、6 分别写为 **SNSC** 和 **mgmt04**；图 1、2 没有明确写出主机。因此不能仅因本聊天已连接 mu01，就认定全部路径位于 mu01。

## 2. EMT：Symanzik flow 与改进场强

### 2.1 主代码目录

来源：图 1。主机未在截图中明确标注。

```text
/home/jliang/vibe_coding_3_glueball_wavefunction/EMT/
```

截图说明：正式数据采用各向异性、树级 Symanzik flow，各向异性参数为 ξ = 5；EMT 使用 Symanzik 改进的 clover 场强构造。

以下文件均位于上述主代码目录：

| 文件 | 截图记录的功能 | 查阅它的用途 |
| --- | --- | --- |
| `produce_symanzik_momentum_emt.py` | 生产入口，计算 125 种插入动量 | 从这里了解 EMT 生产任务如何组织和调用其他模块 |
| `pyquda_symanzik_flow.py` | 调用 PyQUDA 的 `symanzikFlow`，传入各向异性 | 核对 flow 的调用方式与各向异性参数传递 |
| `symanzik_field_strength_cuda.py` | 生产使用的改进场强 CUDA 实现 | 查看实际生产所用的场强计算实现 |
| `symanzik_field_strength.py` | 同一场强的参考实现 | 对照 CUDA 实现，理解和核查场强计算 |
| `symanzik_momentum_emt.py` | 构造 EMT 的 10 个对称无迹分量并做动量投影 | 查看张量分量如何构造、如何投影到插入动量 |

“10 个对称无迹分量”为截图原述；截图没有展示分量列表及约束实现，不能据此认定有 10 个独立自由度。

### 2.2 截图中的定义与系数

Flow 作用量系数：

- plaquette：`5/3`。
- rectangle：`−1/12`。

EMT 改进场强：

$$
F_{\mu\nu}^{\mathrm{imp}}
= \frac{5}{3} C_{11}
- \frac{1}{6}\left(C_{12}+C_{21}\right).
$$

截图特别说明：这里的 $C_{mn}$ **未除以环面积**。

这些信息用于核对生产所用的离散化定义。Flow 作用量的系数与场强组合的系数应分别记录；比较不同实现时还需要保持 $C_{mn}$ 的归一化约定一致。

### 2.3 不同 β 对应的生产代码目录

来源：图 2。主机未在截图中明确标注。

β = 2.4、2.8：

```text
/home/jliang/works/glueball_wave_functions/EMT/symanzik_mom125_run_20260909/code/
```

β = 3.0，截图称最终采用的 `step8` 版本：

```text
/home/jliang/works/glueball_wave_functions/EMT/symanzik_mom125_beta3_step8_20260909/code/
```

用途：按 β 查找对应生产代码，追溯数据生成时使用的版本。截图未解释 `step8` 的具体含义，不宜仅凭目录名推断其参数。

图 2 原有核验说明：当时已按本地代码和生产记录核对，但远程连接仍关闭，未能重新在线确认目录。本次整理保留这一限制。

## 3. xj11：标量 F² 的 flow 生产

### 3.1 代码目录与各文件用途

来源：图 3、4。主机：**xj11**。

```text
/home/jliang/works/scalar_current_4pts/code/flow_production/
```

| 文件 | 截图记录的功能 | 查阅它的用途 |
| --- | --- | --- |
| `produce_f2_641_3296.py` | 主程序：读取组态、做 Symanzik flow、保存各 flow time 的 $F^2(x,y,z,t)$ | 了解从输入组态到标量场输出的生产流程 |
| `clover_scalar.py` | 计算 clover $F^2$，包含两卡分块的边界处理 | 查看标量算符的实现及多卡分块边界处理 |
| `submit_f2.slurm` | 提交脚本：两张 P100、两个 MPI ranks | 查看资源申请及主程序启动方式 |
| `flow_plan_20pts.json` | 20 个 flow time 的设置 | 查看保存哪些流时间点及其配置 |

这里沿用截图的 $F^2(x,y,z,t)$ 写法；具体坐标与 flow time 在代码中的变量名、轴顺序及输出格式仍需读代码确认。

### 3.2 提交脚本和主程序完整路径

提交脚本：

```text
/home/jliang/works/scalar_current_4pts/code/flow_production/submit_f2.slurm
```

该脚本调用的主程序：

```text
/home/jliang/works/scalar_current_4pts/code/flow_production/produce_f2_641_3296.py
```

### 3.3 PyQUDA 依赖

截图记录的 PyQUDA 库目录：

```text
/home/jliang/vibe_coding_3_glueball_wavefunction/EMT/PyQUDA/
```

用途：追溯生产任务调用的 PyQUDA 来源，在排查 flow 调用、依赖版本或运行环境问题时定位库代码。

图 3 还提到，本地 Git 中对应代码为 `flow_production`，但没有提供本地绝对路径或仓库地址。

## 4. twist-two / moments_flow：PyColor 与批量生产任务

### 4.1 固定的生产代码版本

来源：图 5。截图标题为 `twist-two ops`，正文给出了 PyColor 与 `moments_flow` 的生产路径。

截图记录：生产任务使用的 PyColor 固定在提交 **`b302ebe`**。

```text
/public/home/liangj/works/vibe_codings/moments_flow/releases/b302ebe/pycolor/
```

用途：定位生产所用的代码发布版本，便于追溯结果和比较版本变化。截图没有给出该代码目录所在主机、具体算符定义或完整提交哈希。

### 4.2 F32P21（SNSC）

运行目录：

```text
/public/home/liangj/works/vibe_codings/moments_flow/campaigns/F32P21/snsc_v100_20260925/
```

占位及任务入口脚本目录：

```text
/public/home/liangj/works/vibe_codings/hyperon_FF/sbatch_pool_v100/scripts8/
```

用途：运行目录用于查找 F32P21 的任务配置、状态、结果和日志；脚本目录用于查找该任务对应的占位及启动入口。

### 4.3 F32P30（mgmt04）

来源：图 5、6，具体路径由图 6 补全。

运行目录：

```text
/public/home/liangj/works/vibe_codings/moments_flow/campaigns/F32P30/ensemble_gpu030_20260923/
```

占位及任务入口脚本目录：

```text
/public/home/liangj/works/vibe_codings/moments_flow/campaigns/F32P30/ensemble_gpu030_20260923/pool/scripts8/
```

用途：运行目录用于查找 F32P30 的任务配置、状态、结果和日志；`pool/scripts8/` 用于查找这套任务的占位及启动入口。截图中换行显示的 `p` 与 `ool/scripts8/` 已合并为 `pool/scripts8/`。

### 4.4 两个运行目录共有的文件与子目录

以下路径均相对于各自运行目录：

| 文件或目录 | 截图记录的功能 | 查阅它的用途 |
| --- | --- | --- |
| `worker.sh` | 计算流程及容器环境 | 查看实际执行步骤和容器环境设置 |
| `queue.py` | 组态领取、完成与失败记录 | 查看组态如何分配以及任务状态如何记录 |
| `verify.py` | 结果验收 | 查看输出需要满足哪些验收条件 |
| `work/inputs/` | 逐组态 YAML | 查找单个组态的输入参数 |
| `work/output/` | 结果 | 定位生产输出 |
| `work/logs/` | 日志 | 查看运行记录、定位报错 |

占位及任务入口脚本的命名模式：

| 名称模式 | 截图说明 |
| --- | --- |
| `place_holder_batch_XXX.sh` | 占位脚本 |
| `batch_XXX.sh` | 任务入口脚本 |

`XXX` 是截图中给出的占位符；实际脚本编号、调用参数和占位机制未展示，需要读取对应目录及脚本确认。

## 5. 按需求查找

| 想完成的事情 | 优先查看 |
| --- | --- |
| 找 EMT 生产入口和 125 种动量的处理 | `produce_symanzik_momentum_emt.py`、`symanzik_momentum_emt.py` |
| 核对各向异性 flow 与参数 ξ | `pyquda_symanzik_flow.py` 及生产配置 |
| 核对改进场强定义和 CUDA 实现 | `symanzik_field_strength.py`、`symanzik_field_strength_cuda.py`，注意环面积约定 |
| 追溯某个 β 的 EMT 数据生产代码 | 第 2.3 节对应的 `code/` 目录 |
| 找标量 F² 的生产入口和流时间设置 | `produce_f2_641_3296.py`、`flow_plan_20pts.json` |
| 了解 xj11 上 F² 任务如何启动 | `submit_f2.slurm` |
| 追溯 moments_flow 使用的 PyColor 版本 | `releases/b302ebe/pycolor/` |
| 查看 F32P21 / F32P30 的执行环境和任务状态 | 相应运行目录中的 `worker.sh`、`queue.py` |
| 查结果是否通过验收或定位失败原因 | `verify.py`、`work/output/`、`work/logs/` |
| 查单个组态的输入参数 | `work/inputs/` 中对应的 YAML |

这份索引用于定位与理解截图中的资料；不包含实际脚本正文、完整运行命令或远端在线核验结果。

## 6. 截图来源对应

| 图片 | 原文件名 | 内容 |
| --- | --- | --- |
| 图 1 | `40847fd9da5fdccc6119a117ee3ff82b.png` | EMT 主代码、模块职责、ξ 与改进系数 |
| 图 2 | `e5b767371853e5c6e4c3cfff150ed0fd.png` | 不同 β 的生产代码目录与原有核验限制 |
| 图 3 | `45d27ca209a7776b5a0922ed88ef5690.png` | xj11 标量 F² 代码、配置和 PyQUDA 依赖 |
| 图 4 | `ea5f5076fc539ff5a3d2e5965ac2225c.png` | F² 提交脚本与主程序完整路径 |
| 图 5 | `47e2059629c3fc7e3415dea63db88851.png` | PyColor 固定提交、F32P21 目录与脚本位置 |
| 图 6 | `3d9cd84af023779e53c1a2eb5d7b5ee5.png` | F32P30 目录、两套任务的公共文件和脚本命名 |
