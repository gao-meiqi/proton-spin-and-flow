# Ji's Sum Rule 与质子角动量分解笔记

---

## 核心物理结论（TL;DR）

1. **Ji's Sum Rule 给出的是总角动量 $J_X$（Total Angular Momentum），而不是纯 Spin ($S_X$)**：
   $$J_X = \frac{1}{2}\left[ A_X(0) + B_X(0) \right] = L_X + S_X \quad (X = q, g)$$
2. **为什么总角动量加起来是 $\frac{1}{2}$？**
   质子作为一个整体，是极化为自旋 $\frac{1}{2}$ 的费米子。由于 QCD 组分的完备性与时空转动对称性守恒（能动量张量 $T^{\mu\nu}$ 守恒）：
   $$J_{\text{total}} = J_q + J_g = \frac{1}{2} \left[ (A_q(0)+A_g(0)) + (B_q(0)+B_g(0)) \right] = \frac{1}{2}(1 + 0) = \frac{1}{2}$$
3. **复合粒子的自旋 $\neq$ 基本粒子内禀自旋的简单相加**：
   纯夸克自旋 $\frac{1}{2}\Delta\Sigma \approx 0.15$（只占总自旋的 $\sim 30\%$），纯胶子自旋 $\Delta G \approx 0.23$。两者相加并不等于 $\frac{1}{2}$！剩余的大头（$>60\%$）来自夸克和胶子接近光速运动产生的**轨道角动量（Orbital Angular Momentum, OAM）**。

---

## 一、 能动量张量（EMT）与角动量算符

在 QCD 场论中，质子的总角动量算符由 Belinfante 对称能动量张量 $T^{\mu\nu}$ 构造：
$$J^3 = \int d^3x \left( x^1 T^{02}(x) - x^2 T^{01}(x) \right)$$

对于自旋 $1/2$ 质子态，非前向 EMT 矩阵元参数化为三个**引力形状因子（Gravitational Form Factors）** $A(t), B(t), C(t)$：
$$\langle P' | T_X^{\mu\nu} | P \rangle = \bar{u}(P') \left[ A_X(t) \frac{\gamma^\mu \bar{P}^\nu + \gamma^\nu \bar{P}^\mu}{2} + B_X(t) \frac{i \sigma^{\mu\alpha} \Delta_\alpha \bar{P}^\nu + i \sigma^{\nu\alpha} \Delta_\alpha \bar{P}^\mu}{4M} + C_X(t) \frac{\Delta^\mu \Delta^\nu - g^{\mu\nu}\Delta^2}{M} \right] u(P)$$

其中 $\bar{P} = \frac{P'+P}{2}$，$\Delta = P' - P$，$t = \Delta^2$。

### 提取 $J^3$ 期望值（前向极限 $\Delta \to 0$）：
通过在波包态下取动量导数 $x^j \to i \frac{\partial}{\partial \Delta_j}$，在前向极限 $\Delta \to 0$ 下：
* $A_X(0)$：吸收了动量流分布（即夸克/胶子携带的**纵向动量份额** $\langle x \rangle_X$）。
* $B_X(0)$：类似于“引力反常磁矩”（Gravitomagnetic moment），捕捉到了转动诱导的对称性响应。

经过旋量缩合计算后，得：
$$\langle J^3_X \rangle = \frac{1}{2} \left[ A_X(0) + B_X(0) \right] \cdot 2S^3 \implies J_X = \frac{1}{2}[A_X(0) + B_X(0)]$$

这说明 $A_X(0) + B_X(0)$ 的组合**天然吸干了组分 $X$ 对总角动量 $J$ 的全部贡献**。

---

## 二、 两种角动量分解方案对比

为了厘清“为什么自旋不是简单加和”，需对比物理学中两种最主流的分解方案：

| 维度 | **Ji's Decomposition** | **Jaffe-Manohar Decomposition** |
| :--- | :--- | :--- |
| **分解公式** | $J_{\text{total}} = J_q + J_g$ | $\frac{1}{2} = \frac{1}{2}\Delta\Sigma + \Delta G + L_q + L_g$ |
| **夸克项** | $J_q = \frac{1}{2}\Delta\Sigma + L_q^{\text{kin}}$ | $\text{Spin: } \frac{1}{2}\Delta\Sigma \quad \text{OAM: } L_q^{\text{can}}$ |
| **胶子项** | $J_g$ (自旋与轨道包含在一起) | $\text{Spin: } \Delta G \quad \text{OAM: } L_g^{\text{can}}$ |
| **规范不变性** | 每一项在局域上都严格**规范不变** | 需固定规范（如光锥规范），包含非局域 Wilson Line |
| **实验/格点测定** | 与 GPDs 二次矩直接联系，适合**格点 QCD** 计算 | 适合**高能散射实验**（如 DIS、RHIC 极化对撞） |

> **关键注记**：Ji 分解中的 $J_q$ 已经把“纯夸克自旋 $\frac{1}{2}\Delta\Sigma$”与“运动学轨道角动量 $L_q^{\text{kin}}$”合并在了一起。

---

## 三、 为什么复合粒子的自旋不等于基础粒子自旋的简单叠加？

### 1. 非相对论量子力学 vs. 相对论 QCD

* **非相对论夸克模型（SU(6) 图像）**：
  假定夸克在质子内近乎静止（$L=0$），没有胶子场（$\Delta G = 0, L_g = 0$）。此时：
  $$S_{\text{proton}} = s_1 + s_2 + s_3 = \frac{1}{2}$$
  这是非相对论系统中的 Clebsch-Gordan 系数矢量叠加。

* **相对论 QCD（现实世界）**：
  * **狭义相对论+海森堡不确定性原理**：夸克被禁闭在 $\sim 1\text{ fm}$ 的强子空间中，动量非常大，以接近光速旋转狂飙，产生**巨大的空间轨道角动量 $L$**。
  * **量子涨落与海粒子**：存在无限多的虚夸克对和强极化胶子场，胶子带自旋（$s=1$）并参与旋转。

### 2. 质子自旋“账单”实际分布（以标度 $\mu^2 \sim 2\text{ GeV}^2$ 为例）

$$
\underbrace{S_{\text{proton}} = \frac{1}{2}}_{\text{质子整体量子数}} = \underbrace{\frac{1}{2}\Delta\Sigma}_{\approx 0.15 \text{ (夸克自旋)}} + \underbrace{\Delta G}_{\approx 0.23 \text{ (胶子自旋)}} + \underbrace{L_q + L_g}_{\approx 0.12 \text{ (轨道角动量总和)}}
$$

* 纯自旋贡献（夸克自旋 + 胶子自旋）加起来只有大约 **$0.38$**（占 $\sim 75\%$ 左右，视标度而定），**并不等于 $\frac{1}{2}$**。
* 真正锁定在 $\frac{1}{2}$ 的，是包含轨道角动量后的**全系统总角动量求和规则**（Sum Rule）。