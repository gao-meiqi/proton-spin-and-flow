# F32P21 的 T00 生成方法与老师 EMT 代码的对比

核查日期：2026-10-22。此次已通过既定连接路径读取 mu01 上的实际代码、目录、部分生产日志和数据头；不再仅依据截图。

## 1. 结论

你的 F32P21 和老师的 EMT 都调用 Symanzik flow。主要区别在于 **flow 后如何定义场强、保存哪些算符与动量，以及系综和各向异性不同**。

你的程序使用普通 1×1 clover，保存零空间动量的电、磁平方和；老师使用含矩形环的 Symanzik 改进且颜色无迹的场强，构造作用量密度及对称无迹张量的 10 个存储分量，并投影到 125 个空间动量。现有两个电磁总和文件不能通过乘一个系数变成老师的完整输出。

这里比较的是生产层。两边的这些输出都不是在生产程序中完成 matching/重整化后的完整物理 EMT；本次没有逐一追踪你的全部后处理笔记本。

## 2. 找到的实际位置

### 你的代码和数据（mu01）

- 生成主程序：`/workspace/gaomeiqi/T00_F32P21/t00_F32P21.py`
- 提交脚本：`/workspace/gaomeiqi/T00_F32P21/t00_F32P21_fix.sh`
- 场强路径实现：`/workspace/gaomeiqi/T00_F32P21/fmunu_torch.py`
- 实际调用的兼容层：`/workspace/gaomeiqi/T00_F32P21/fmunu_shim.py`
- 补数据调度程序：`/workspace/gaomeiqi/T00_F32P21/fill_missing.py`
- 生产日志：`/workspace/gaomeiqi/T00_F32P21/log/`
- 数据：`/home/gaomeiqi/T00_new/F32P21/data_T00_flow*/`
- 已有质检记录：`/home/gaomeiqi/T00_new/qc_20261013/qc_report.md`

本地 Windows 工作区原本只有 Markdown 资料；生成代码位于 mu01 的 `/workspace`，输出位于 `/home/gaomeiqi/T00_new`。你说的 FP21 对应这里的 **F32P21**。

日志和数据目录的更新时间与 10 月 6–7 日这批生产吻合。当前脚本按输出是否已存在来跳过组态，因此仅靠当前源码和日志，不能证明每个历史文件都由完全相同的源码版本生成。

### 老师的代码（mu01）

本次实际读取并用于逐项比较的是生产快照：

```text
/home/jliang/works/glueball_wave_functions/EMT/symanzik_mom125_run_20260909/code/
```

主要文件：`produce_symanzik_momentum_emt.py`、`pyquda_symanzik_flow.py`、`symanzik_field_strength.py`、`symanzik_field_strength_cuda.py`、`symanzik_momentum_emt.py`。

β=3 的 step8 运行目录也存在，并已读取其 `plan.json`：

```text
/home/jliang/works/glueball_wave_functions/EMT/symanzik_mom125_beta3_step8_20260909/
```

截图中的主目录 `/home/jliang/vibe_coding_3_glueball_wavefunction/EMT/` 存在，但本次该目录中未找到截图所列的 `*symanzik*.py`；上述生产快照保留了这些文件。本报告的算法结论以实际读到的快照为准。

## 3. 逐项差异

| 项目 | 你的 F32P21 | 老师的 EMT |
| --- | --- | --- |
| 输入系综 | `CLOVER/beta6.41_mu-0.2320_ms-0.2050_L32x64`，32³×64 | `purgauge` 下 β=2.4、2.8、3.0；12³×192 或 16³×192 |
| 各向异性 | `xi_0=nu=1`，即 ξ=1 | 显式 ξ=5，并向 flow 传入 `smear_anisotropy` |
| flow 类型 | `gauge_m.symanzikFlow(itf, 0.01)`；底层明确选择 `QUDA_GAUGE_SMEAR_SYMANZIK_FLOW` | 各向异性 Symanzik flow |
| 测量场强 | 四个 1×1 环平均后取反厄米部分 | 1×1、1×2、2×1 clover 组合，取反厄米并去颜色迹 |
| 场强改进 | 未包含矩形环项 | `5/3 C11 − (C12+C21)/6`，Cmn 不除环面积 |
| 保存算符 | 电平方和、磁平方和各一份 | 作用量密度 `E`、10 个 `U` 存储分量，以及分方向电磁诊断量 |
| 动量 | 对整个空间直接求和，即 q=0 | q 的三个整数分量各取 −2…2，共 125 个模式 |
| 空间归一化 | 空间和，不除体积 | 空间 Fourier 和，不除体积 |
| 时间分量标签 | `get_field(3,i)` 为时间–空间面 | 同样时间索引为 3；时间对角分量是 `U[...,9]`，标签 `33` |
| 输出格式 | 每组态、每 flow 两个 `.npy`；抽查为 `(1,64)`、complex128 | 每组态一个 `.npz`，含全部 flow、动量、分量及元数据；默认 `U` 为 `(26,125,192,10)` |
| 测量执行位置 | flow 用 MPI/GPU；全格 gather 到 rank 0 后，当前 shim 在 CPU Torch 上计算场强 | 改进场强用融合 CUDA kernel，收缩及 FFT 也在 GPU 上 |
| 多 flow 工作组织 | 每个 itf 单独读取原组态，从头 flow 至该时刻 | 每组态逐段推进 flow，并依次测量多个时刻 |

老师的 10 个对称张量存储分量满足总迹为零，因此不能称为 10 个独立自由度。“颜色无迹”和“时空张量无迹”是两件不同的事。

## 4. 你的数据究竟保存了什么

记四个定向 plaquette 的和为 Q。由你的 `get_field` 和四叶平均可直接读出：

$$
F_{\mu\nu}^{\rm yours}=\frac{Q_{\mu\nu}-Q_{\mu\nu}^{\dagger}}8.
$$

它是反厄米矩阵，但代码没有再执行颜色迹减除。定义时间片上的两个已保存量：

$$
\mathcal E(\tau)=-\sum_{\mathbf x,i}\operatorname{Tr}[F_{3i}(\tau,\mathbf x)^2],
\qquad
\mathcal B(\tau)=-\sum_{\mathbf x,i<j<3}\operatorname{Tr}[F_{ij}(\tau,\mathbf x)^2].
$$

则 `E_temporal_local_F_...npy` 保存的是 $\mathcal E$，`E_spatial_local_F_...npy` 保存的是 $\mathcal B$。尽管文件名有 `local`，`einsum('tzyxab,tzyxba->t',...)` 已经对 x、y、z 和颜色求和，空间位置并未保留。

在老师代码的收缩与张量归一化约定下，若使用同一组场强并令 ξ=1，可构造：

$$
E_{\rm action}(q=0,\tau)=\mathcal E+\mathcal B,
\qquad
U_{33}(q=0,\tau)=\mathcal E-\mathcal B.
$$

这只是两个程序的**裸算符结构对应关系**。你的 F 与老师的 F 定义不同，因此不能据此宣称现有数据与老师的数值相等，也不能直接把差值等同于已重整化的 Minkowski 能量密度。

老师 ξ=5 时的同类公式为：

$$
U_{33}(q=0,\tau)=\xi^2\mathcal E_{\rm raw}^{\rm imp}(\tau)-\mathcal B_{\rm raw}^{\rm imp}(\tau).
$$

不要把老师的“第 0 个 U 分量”当作你的 T00：他的方向编号为 x,y,z,t，第 0 项是空间 xx，第 9 项才是时间 tt（常称 U44）。

## 5. 为什么普通 clover 不能用总系数变成改进 clover

老师首先对每种环组合执行颜色无迹投影：

$$
C_{mn}=\frac{Q_{mn}-Q_{mn}^{\dagger}}8
-\frac13\operatorname{Tr}\!\left(\frac{Q_{mn}-Q_{mn}^{\dagger}}8\right)I,
$$

然后构造：

$$
F^{\rm imp}=\frac53C_{11}-\frac16(C_{12}+C_{21}).
$$

平方收缩后不仅有 $C_{11}^2$，还有矩形环平方与不同环之间的交叉项。你保存的 $\mathcal E$、$\mathcal B$ 没有这些信息，也没有保存逐点颜色迹，无法事后精确补出它们。

因此 **使用了 Symanzik flow，不代表测量算符也使用了 Symanzik 改进场强**。你的 flow 已是 Symanzik；要复现老师的测量定义，需要改的是测量部分，并重新从规范场测量。此次没有对同一组态做两套测量，差异的数值大小仍未知。

## 6. flow 时间和重整化约定

你的脚本步长为 0.01 个格子流时单位，`flow300` 对应脚本约定的 $t_f/a^2=3$。本次找到 25 个输出时刻：

```text
2, 6, 10, 14, 18, 22,
30, 45, 60, 75, 90, 105, 120, 135, 150, 165,
180, 195, 210, 225, 240, 255, 270, 285, 300
```

已有质检文档采用 a=0.07746 fm；按这个标尺，最大流时约 0.018 fm²。这里引用其格距，未重新做尺度标定。

老师的程序按物理流时生成 0、0.001、…、0.025 fm²，共 26 点。普通快照默认每间隔 4 步；β=3 的 step8 `plan.json` 明确为每间隔 8 步。比较时应对齐物理流时，不能直接对齐步数或目录后缀。

你的程序中的 `coeff_t`、`coeff_r` 虽然定义为 1.1408845194，但后续测量和保存并未使用它们。主程序没有施加 EMT matching 系数、真空减除或物理单位换算。老师此生产入口也只保存流后的裸 `E/U`，没有在输出前完成这些后处理。

老师这里使用的是 `purgauge` 系综，你使用的是带夸克质量标识的 CLOVER 系综；不能把老师纯规范场分析所用的匹配系数不加核对地移植到你的分析。是否及如何处理夸克–胶子算符混合，需要结合你最终要提取的物理量和后处理方案另行核查。

## 7. 现有数据能做什么、不能恢复什么

- 可以使用现有电磁两份数据构造其自身定义下的 q=0 和与差，继续与已有分析的约定对接。
- 不能从两个空间总和恢复 q≠0 模式，因为逐空间位置的信息已求和消失。
- 不能从两个总和恢复非对角 EMT 分量，因为相应场强交叉收缩未保存。
- 不能从两个总和精确恢复改进 clover，因为缺少矩形环、交叉项和颜色迹信息。
- 若要采用老师的测量方法，应在你的 F32P21 组态上保留 ξ=1，并使用改进场强重新测量；不要照搬他的 ξ=5 和纯规范场输入目录。若只需要 q=0 时间对角量，可只输出所需通道。

先对同一组态、相同 flow 后规范场比较“现有 clover → 仅去颜色迹 → 改进 clover”，能分别识别两项定义变化的影响；当前尚未运行该数值对照。

## 8. 本次核实的数据完整性

仅做目录计数、E/B 文件配对和一个样本头部读取，未重跑全量数值质检：

- 25 个 flow 目录中，24 个各有 459 对电/磁文件。
- `flow255` 有 417 对，比其他流时少 42 对。
- 各 flow 内电/磁组态编号集合一致。
- 抽查 `flow300/E_temporal_local_F_cfg_29000_flow300.npy`：形状 `(1,64)`，类型 `<c16`（complex128）。

这与 2026-10-13 质检记录的缺口一致。旧质检文档中的统计与物理解释没有在本次重新验证，也不作为两种算符数值等价的证据。

## 9. 本地证据副本

为方便复查，在当前工作区保存了源码文本副本（UTF-8，换行可能被规范化，不作字节哈希证明）：

| 本地文件（位于 `comparison_sources/`） | 远端来源 |
| --- | --- |
| `user_t00_F32P21.py` | `/workspace/gaomeiqi/T00_F32P21/t00_F32P21.py` |
| `user_fmunu_torch.py` | `/workspace/gaomeiqi/T00_F32P21/fmunu_torch.py` |
| `user_fmunu_shim.py` | `/workspace/gaomeiqi/T00_F32P21/fmunu_shim.py` |
| `user_t00_F32P21_fix.sh` | `/workspace/gaomeiqi/T00_F32P21/t00_F32P21_fix.sh` |
| `teacher_symanzik_field_strength.py` | 老师上述生产快照中同名文件 |
| `teacher_symanzik_momentum_emt.py` | 老师上述生产快照中同名文件 |
| `teacher_produce_symanzik_momentum_emt.py` | 老师上述生产快照中同名文件 |
| `teacher_pyquda_symanzik_flow.py` | 老师上述生产快照中同名文件 |

老师普通快照的 `plan.json` 记录 `source_commit=c1767f2b4fd10091257a916f09e0121ccb400522`、`pyquda_commit=8857743f50f65c8f0d1da5f563a3ecf96a6a2932`。这是计划记录值，本次没有重新校验仓库提交及全部源文件哈希。
