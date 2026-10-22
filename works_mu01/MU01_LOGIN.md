# mu01 登录说明与故障复盘

最后成功验证：2026-10-21。本文不保存密码、私钥或一次性验证码。

## 正确连接路径

```text
Windows PowerShell
  → WSL Ubuntu-22.04 的 SSH
  → snsc（gaomq@222.200.137.16:10023）
  → 在 snsc 上运行 SSH 连接 mu01
  → mu01（gaomeiqi）
```

**必须从 snsc 发起第二段 SSH。** 不使用 Windows 原生 SSH，也不在本机 WSL Ubuntu 直接执行 `ssh mu01`。本机 Ubuntu 没有 mu01 所需的私钥。

现有配置已经可用，不修改 SSH 配置或密钥。snsc 的 `/public/home/gaomq/.ssh/config` 中已配置：

```sshconfig
Host mu01
    HostName localhost
    Port 6439
    User gaomeiqi
    ControlMaster auto
    ControlPath ~/.ssh/%r@%h:%p.sock
    ControlPersist 12h
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

这里的 `localhost:6439` 是 **snsc 上访问的地址**，不是 Windows 或 WSL 本机的地址。

## 下次登录的操作步骤

### 1. 检查连接复用并验证身份

通过 `exec_command` 执行以下 PowerShell 命令：

```powershell
wsl -d Ubuntu-22.04 -- ssh -o BatchMode=yes -o ConnectTimeout=15 snsc "ssh -O check mu01 && ssh -o BatchMode=yes -o ConnectTimeout=15 mu01 'hostname; whoami'"
```

成功输出包含以下内容，PID 会变化：

```text
Master running (pid=...)
mu01
gaomeiqi
```

`ssh -O check` 检查 snsc 上的 mu01 主连接，后面的命令实际验证远端主机与用户。不能仅凭存在 socket 文件判断连接仍然有效。

### 2. 建立并保持自己的交互会话

不论复用检查是否成功，需要持续操作时都使用下面的命令。有效主连接会被自动复用；失效时可能需要重新认证。

```powershell
wsl -d Ubuntu-22.04 -- ssh -tt -o ConnectTimeout=15 snsc "ssh -tt -o ConnectTimeout=15 mu01"
```

- `exec_command` 设置 `tty=true`，保留工具返回的 `session_id`。
- 命令仍在运行且返回 `session_id`，通常表示交互会话仍存活，不代表失败。
- 用 `write_stdin` 读取后续输出并发送命令。
- 如果出现 `Verification code:`，向用户索取**当前一次性验证码**，然后通过 `write_stdin` 输入验证码和换行。
- 不使用历史验证码，不把验证码写入文件；等待验证码时不要关闭会话。
- 如需其他交互认证，按实际提示让用户协助，不猜测凭据。

### 3. 登录后确认身份，再进入工作目录

通过同一会话的 `write_stdin` 发送：

```bash
hostname
whoami
pwd
```

本次验证结果：

```text
mu01
gaomeiqi
/home/gaomeiqi
```

确认身份后进入目标目录：

```bash
cd /home/gaomeiqi/T00_new
pwd
find . -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
```

后续继续通过 `write_stdin` 操作这个交互会话。没有结束会话的需要时，不主动发送 `exit` 或终止 SSH。

## 之前为什么失败

| 尝试或现象 | 原因与教训 |
|---|---|
| 使用 Windows 原生 `ssh mu01` | 用错了连接环境，读取的是 Windows 的 SSH 配置和认证信息。Windows 原生连接的首次尝试被沙箱阻止，沙箱外尝试出现握手超时；后续检查还确认 Windows 的密钥未通过 snsc 认证。应直接使用指定的 WSL 路径。 |
| 在本机 WSL 直接 `ssh mu01`，通过 `ProxyJump snsc` 跳转 | 本机 SSH 客户端仍负责向 mu01 认证，本机 Ubuntu 缺少所需私钥，因此出现 `Permission denied (publickey)`。ProxyJump 不等于登录 snsc 后运行第二段 SSH。 |
| 在 snsc 上直接执行 `ssh -p 6439 gaomeiqi@localhost` | 没有使用已配置的 `mu01` 别名，不能假定会应用该别名下的连接复用设置。本次返回 `Permission denied (keyboard-interactive)`；应使用 `ssh mu01`，必要时按交互提示重新认证。 |
| 把 `BatchMode=yes` 当成完整登录办法 | BatchMode 适合检查已有认证或复用连接，无法完成交互式验证码认证。失败后应建立带 TTY 的交互会话。 |
| `Wsl/E_ACCESSDENIED` 或沙箱中的网络 `Permission denied` | 这是本地工具权限限制，不足以证明服务器故障。按工具要求申请沙箱外执行，再重试原命令。 |

最终成功方式是：使用 WSL SSH 登录 snsc，在 snsc 上以 `mu01` 别名复用已有主连接，验证身份后建立独立交互会话。

## 注意事项

- **配置和密钥不需修改。** 不因连接失败而生成、复制或替换密钥，也不改动现有 SSH 配置。
- snsc 登录可能提示缺少 GCC、CUDA、CMake、libxml2、hpcx、openblas 模块。本次这些警告没有阻止 SSH 登录，应以实际认证结果和主机身份为准。
- WSL 可能提示 localhost 代理未镜像到 NAT 模式。本次该提示没有阻止连接，不要仅凭这个提示修改网络配置。
- 已有 SSH 主连接可能到期或失效，不能保证下一次免验证码。`ControlPersist 12h` 也不保证连接始终可用。
- 其他聊天的 `session_id` 不能直接使用；每次需要建立自己的工具会话，但可以复用 snsc 上仍有效的 SSH 主连接。
- 不硬编码本次的 session ID 或主连接 PID。后续只使用当前工具实际返回的值。
- 查看 `T00_new` 时先做只读操作；不要把登录或查看目录理解成修改、删除文件的授权。

## 可直接用于下次聊天的提示

> 请先阅读工作目录中的 `MU01_LOGIN.md`，按 Windows → WSL Ubuntu-22.04 → snsc → mu01 的路径连接。必须从 snsc 发起第二段 `ssh mu01`，不要使用 Windows 原生 SSH，也不要在本机 Ubuntu 直接 `ssh mu01`。先检查连接复用，再建立并保留自己的交互会话；需要验证码时向我索取当前验证码。不要修改配置或密钥。目标目录是 `/home/gaomeiqi/T00_new`。
