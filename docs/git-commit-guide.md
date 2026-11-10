# Git 命令行提交指南（以本仓库为例）

> 面向刚学 Git 的同学。命令以 Windows 11 + PowerShell 为例，Linux/macOS 只需把路径写法换掉。
> 本文用 2026-11-10 这次真实提交作为案例，命令可以直接照着敲。

---

## 0. 先理解四个区域

Git 的日常操作，本质上就是让代码在四个区域之间流动：

```
工作区（你正在编辑的文件）
   │  git add
   ▼
暂存区（这次提交要包含的快照）
   │  git commit
   ▼
本地仓库（.git 目录里的提交历史）
   │  git push
   ▼
远程仓库（GitHub）
```

| 区域 | 常用命令 | 作用 |
| --- | --- | --- |
| 工作区 → 暂存区 | `git add <文件>` | 挑选这次要提交的改动 |
| 暂存区 → 本地仓库 | `git commit -m "说明"` | 生成一个版本快照 |
| 本地仓库 → 远程仓库 | `git push` | 上传提交到 GitHub |
| 远程仓库 → 本地 | `git pull` / `git fetch` | 拉取别人的改动 |

记住一句话：**先 add 再 commit，最后 push**。

---

## 1. 一次性配置（每台电脑只做一次）

```powershell
git config --global user.name "Ethan_Leo"
git config --global user.email "xuesongzhi813@gmail.com"
git config --global init.defaultBranch main
# 让 git status / git log 正常显示中文路径，而不是 \345\255\246 这种转义
git config --global core.quotepath false
```

查看当前配置：

```powershell
git config --global --list
```

### 关于 GitHub 登录（HTTPS 方式）

本仓库的远程地址是 HTTPS：

```powershell
git remote -v
# origin  https://github.com/xuesongzhi813-star/LangChain-LangGraph.git (fetch)
# origin  https://github.com/xuesongzhi813-star/LangChain-LangGraph.git (push)
```

GitHub 已经**不再接受账号密码**。第一次 `git push` 时通常会自动弹出浏览器让授权（Git Credential Manager，Windows 一般已自带）。如果提示输入密码：

1. 打开 GitHub → 右上角头像 → Settings
2. Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token，勾选 `repo` 权限
4. 复制生成的 token，在命令行密码处粘贴（输入时不会显示字符，是正常的）
5. 之后 Windows 凭据管理器会记住它

也可以用 SSH（生成密钥后把公钥加到 GitHub），就不需要每次认证。入门阶段先用 HTTPS 即可。

---

## 2. 每天最常用的命令

### 2.1 看状态

```powershell
git status          # 完整输出
git status -s       # 简短输出，推荐日常使用
```

简短输出的符号含义：

| 符号 | 含义 |
| --- | --- |
| `M` | 已修改（modified） |
| `A` | 新增（added，已暂存） |
| `D` | 删除（deleted） |
| `??` | 未跟踪的新文件（untracked） |
| `M `（M 在左边） | 改动已经 `git add`，进入暂存区 |
| ` M`（M 在右边） | 改动还在工作区，尚未暂存 |

### 2.2 看改了什么

```powershell
git diff                 # 工作区 vs 暂存区：还没 add 的改动
git diff --staged        # 暂存区 vs 上一次提交：即将提交的改动
git diff HEAD            # 工作区 vs 上一次提交：全部改动
```

### 2.3 暂存、提交、推送

```powershell
git add PythonProject/main.py      # 只加一个文件
git add PythonProject/             # 加一个目录
git add .                          # 加当前目录下所有改动（不含被忽略的文件）
git add -A                         # 加整个仓库所有改动（推荐在仓库根目录用）

git commit -m "feat: 新增聊天接口"                  # 一行提交信息
git commit -m "feat: 新增聊天接口" -m "补充说明细节"  # 标题 + 正文
git push                                           # 推到已关联的远程分支
```

提交信息建议用 `类型: 说明` 的格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档
- `chore:` 配置、依赖、忽略规则等杂项
- `refactor:` 重构（不改行为）
- `test:` 测试

---

## 3. 这次提交的完整复盘

下面就是本次实际操作的过程，建议对照着看。

### 3.1 先确认远程和分支

```powershell
git remote -v
git branch -vv
```

当时看到：

```text
* main 39979c6 [origin/main: ahead 3] 初始版本项目
```

意思是：本地 `main` 比远程 `origin/main` **多出 3 个还没推送的提交**。

### 3.2 查看有哪些文件要提交

```powershell
git status
```

发现了 30 项改动。继续检查细节：

```powershell
# 哪些大文件不该进仓库？
Get-ChildItem -Recurse -File |
  Where-Object { $_.Length -gt 5MB } |
  Sort-Object Length -Descending |
  Select-Object FullName, Length

# 有没有 .env 这类敏感文件？
Get-ChildItem -Recurse -Force -File -Filter ".env*"
```

结果发现：

1. `PythonProject/.env` 里有真实的 `DEEPSEEK_API_KEY`，而且**已经被 Git 跟踪**；
2. `LangChain/LangChain/CompleteTool.py` 里有一行硬编码的真实密钥；
3. `PythonProject.zip` 有 66MB，属于不该提交的压缩包。

### 3.3 处理敏感文件：为什么要重写提交

很多人第一步会想到：

```powershell
git rm --cached PythonProject/.env
```

`--cached` 表示“只从 Git 的跟踪列表里移除，磁盘上的文件保留”。这没错，但**还不够**：

> 如果 `.env` 已经存在于**尚未推送**的提交里，仅仅再提交一次“删除 .env”，推送时 Git 仍会把这些历史提交一起上传，密钥依然会出现在 GitHub 上。

所以对“还没推送”的提交，安全的做法是**重写这几个提交**，让它们从一开始就不包含 `.env`。本次操作：

```powershell
# 1) 建一个备份分支，记住原来的提交，随时可以回来
git branch backup/unpushed-20261110

# 2) 把本地 main 退回远程所在的提交
#    默认是 mixed 模式：提交历史回退，但工作区代码原封不动
git reset origin/main

# 3) 确认 .env 变成未跟踪状态，并被 .gitignore 忽略
git status --short
git check-ignore -v PythonProject/.env
```

`git reset` 的三种模式（重要）：

| 命令 | 提交历史 | 暂存区 | 工作区文件 | 使用场景 |
| --- | --- | --- | --- | --- |
| `git reset --soft HEAD~1` | 回退 | 保留 | 保留 | 想重新提交，改动都还在 |
| `git reset HEAD~1`（默认 mixed） | 回退 | 清空 | 保留 | 想重新挑选文件提交 |
| `git reset --hard HEAD~1` | 回退 | 清空 | **删除** | 确定不要这些改动了（危险） |

> 注意：`git reset` 只适合**尚未推送**的提交。已经推送的提交不要随便重写，否则会影响其他人，通常需要 `git push --force`，风险很高。

### 3.4 写 `.gitignore`，把不该提交的东西挡在外面

根目录新增 `.gitignore`，核心内容：

```gitignore
.env
.env.*
!.env.example
!**/.env.example

__pycache__/
*.py[cod]
.venv/
venv/
.idea/
.vscode/
*.iml
*.zip
*.log
```

验证某个文件是否会被忽略：

```powershell
git check-ignore -v PythonProject/.env
# PythonProject/.gitignore:2:.env    PythonProject/.env
```

输出说明：命中 `PythonProject/.gitignore` 第 2 行的 `.env` 规则。

对于**已经被跟踪**的文件，`.gitignore` 不会自动生效，必须手动移出跟踪：

```powershell
git rm --cached PythonProject/.env
git rm -r --cached .idea __pycache__
git commit -m "chore: 停止跟踪 IDE 与缓存文件"
```

本次还清理了 21 个已跟踪的 `.idea` / `__pycache__` / `.pyc` 文件：

```powershell
git ls-files |
  Where-Object { $_ -match '(^|/)\.idea/' -or $_ -match '(^|/)__pycache__/' -or $_ -match '\.pyc$' -or $_ -match '\.iml$' } |
  ForEach-Object { git rm --cached --quiet -- $_ }
```

### 3.5 分多次提交，让历史更清楚

本次代码部分拆成了 3 个提交（这份文档再单独提交一次）：

```powershell
git log --oneline origin/main..HEAD
# 9382bfa feat: 补充 FastAPI/Python 项目、house_agent 工程文件与 LangGraph 分词文件
# 1969593 fix: CompleteTool 改为从环境变量读取 API Key
# e6f24aa chore: 添加根目录 .gitignore，停止跟踪 .env、IDE 配置与 Python 缓存
```

对应命令（简化版）：

```powershell
git add .gitignore .env.example FastAPIProject/.gitignore house_agent/.gitignore
git commit -m "chore: 添加忽略规则，停止跟踪 .env、IDE 配置与 Python 缓存"

git add LangChain/LangChain/CompleteTool.py
git commit -m "fix: CompleteTool 改为从环境变量读取 API Key"

git add -A
git commit -m "feat: 补充项目代码与工程文件"
```

### 3.6 推送前检查

```powershell
# 看看待推送的提交
git log --oneline origin/main..HEAD

# 看看待推送的文件和体积
git diff --stat origin/main..HEAD

# 扫描新提交里有没有疑似密钥
git log origin/main..HEAD -p | Select-String -Pattern 'sk-[0-9a-fA-F]{20,}'
```

### 3.7 推送

```powershell
git push
```

第一次推送新分支时用：

```powershell
git push -u origin main
```

`-u` 表示把本地 `main` 和远程 `origin/main` 建立关联，之后再直接 `git push` 即可。

推送后到 GitHub 网页刷新，确认提交和文件都在，就算完成。

---

## 4. `.gitignore` 规则速成

```gitignore
# 忽略单个文件
config.local.py

# 忽略目录（结尾的 / 表示目录）
__pycache__/
.venv/

# 忽略某种后缀
*.log
*.zip

# 忽略某目录下所有内容，但保留某个文件
logs/*
!logs/keep.md

# 忽略所有 .env，但放行示例模板
.env
.env.*
!.env.example
```

三个容易踩的坑：

1. **规则对已经跟踪的文件无效**：先 `git rm --cached <文件>`，再提交。
2. **`!` 放行要让父目录本身没被忽略**：如果 `logs/` 整个被忽略了，`!logs/keep.md` 不会生效，要写成 `logs/*` + `!logs/keep.md`。
3. **改完 `.gitignore` 用 `git check-ignore -v <文件>` 验证**，比猜快得多。

---

## 5. 分支：改代码前先开分支

```powershell
# 新建并切换到功能分支
git switch -c feature/chat-api

# 在分支上正常 add / commit
git add .
git commit -m "feat: 新增聊天接口"

# 推送到远程（第一次需要 -u）
git push -u origin feature/chat-api

# 回到主分支
git switch main

# 把功能分支合并进 main
git merge feature/chat-api

# 删除已合并的本地分支
git branch -d feature/chat-api
```

团队协作更常用 GitHub 的 Pull Request：推送功能分支后，在网页上发起 PR，让别人 review 再合并。

常用查看命令：

```powershell
git branch              # 本地分支
git branch -a           # 本地 + 远程分支
git log --oneline --graph --all   # 图形化查看所有分支历史
```

---

## 6. 常见问题与排查

### Q1. `Author identity unknown` / 提示设置用户名邮箱

原因：Git 不知道提交作者是谁。

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

邮箱最好和 GitHub 账号一致，这样提交能正确关联到你的头像。

### Q2. `warning: LF will be replaced by CRLF the next time Git touches it`

这是**换行符警告，不是错误**，可以忽略。

- Windows 用 CRLF，Linux/macOS 用 LF，Git 默认会在提交时统一成 LF、检出时转成 CRLF。
- 如果团队要求统一换行符：

```powershell
git config --global core.autocrlf true     # Windows 推荐
# 或跨平台项目常用
git config --global core.autocrlf input
```

### Q3. `nothing to commit, working tree clean`，但明明改了代码

可能原因：

1. 忘记 `git add`：先 `git status` 看文件是不是 `??` 或 ` M`。
2. 文件被 `.gitignore` 忽略了：`git check-ignore -v <文件>` 查看命中了哪条规则。
3. 改的不是这个仓库目录：`git rev-parse --show-toplevel` 确认仓库根目录。
4. 文件已经被跟踪但内容没变化：`git diff` 确认。

### Q4. 改了 `.gitignore`，文件还是出现在 `git status` 里

原因：文件**已经被 Git 跟踪**，忽略规则只对未跟踪文件生效。

```powershell
git rm --cached <文件>        # 保留磁盘文件，只停止跟踪
git commit -m "chore: 停止跟踪 xxx"
```

如果是目录：

```powershell
git rm -r --cached <目录>
```

### Q5. `git push` 报 `failed to push some refs` / `non-fast-forward`

原因：远程有本地没有的新提交，直接推送会被拒绝。

安全做法：

```powershell
git pull --rebase origin main   # 先把远程提交接到本地提交前面
git push
```

不要一上来就 `git push --force`，它可能覆盖别人的提交。只有确认是个人分支、且清楚后果时才用 `--force-with-lease`。

### Q6. `Authentication failed` / `Support for password authentication was removed`

原因：GitHub 不接受账号密码，需要用 Personal Access Token（PAT）或 SSH。

解决：

1. 生成 PAT（Settings → Developer settings → Personal access tokens），勾选 `repo`；
2. 再次 `git push`，密码处粘贴 token；
3. 或检查凭据管理器：Windows 搜索“凭据管理器” → Windows 凭据 → 删除旧的 `git:https://github.com` 条目，再重新 push。

### Q7. `error: src refspec main does not match any`

原因通常是：

1. 这个仓库还没有任何提交：先 `git add` + `git commit`；
2. 当前分支不叫 `main`：`git branch` 看一下，可能是 `master`；
3. 拼写错误：确认 `git push -u origin main` 中的分支名。

### Q8. 提交信息写错了

- **还没推送**：直接修补最近一次提交。

```powershell
git commit --amend -m "正确的提交信息"
```

- **已经推送**：不建议改写历史，直接再提交一次修正，或接受它。公开仓库改写历史需要 force push，容易影响别人。

### Q9. 想撤销操作

```powershell
# 撤销暂存（文件改动还在）
git restore --staged <文件>

# 撤销工作区改动（谨慎：会丢失未提交的修改）
git restore <文件>

# 撤销最近一次提交，但保留改动在暂存区
git reset --soft HEAD~1

# 撤销最近一次提交，改动回到工作区
git reset HEAD~1

# 彻底丢弃最近一次提交和改动（危险）
git reset --hard HEAD~1
```

误操作后想找回提交：

```powershell
git reflog
# 找到之前的 commit hash，然后
git reset --hard <hash>
```

`reflog` 是本地操作的“后悔药”，一般保留 30~90 天。

### Q10. 不小心把密钥提交了（重点）

处理顺序：

1. **立刻去服务商控制台作废/轮换密钥**。只要密钥进过公开仓库，就应当视为已泄露，改代码删不掉别人已经抓取的副本。
2. 把文件移出跟踪并加入 `.gitignore`：

```powershell
git rm --cached .env
# 编辑 .gitignore，加入 .env
git commit -m "chore: 移除 .env"
git push
```

3. 如果提交**还没推送**，可以像本次一样用 `git reset origin/main` 重写，让密钥从未进入远程历史。
4. 如果**已经推送**，普通删除提交无法清除历史。需要 `git filter-repo` 等工具重写全部历史并 force push；个人仓库可做，团队仓库要提前沟通。最根本的仍是**轮换密钥**。
5. 预防：
   - 仓库根目录第一件事就写 `.gitignore`；
   - 只提交 `.env.example`，真实值放 `.env`；
   - 提交前扫一遍：`git diff --staged | Select-String "sk-|api_key|password"`。

### Q11. 文件太大，GitHub 拒绝或警告

- 超过 **100MB** 的单文件会被 GitHub 直接拒绝；超过 **50MB** 会警告。
- 压缩包、模型、数据集、虚拟环境都不该进仓库。
- 解决：加入 `.gitignore`，必要时用 Git LFS：

```powershell
git lfs install
git lfs track "*.psd"
git add .gitattributes
```

如果大文件已经进入历史，需要重写历史或使用 `git filter-repo` 清理。

### Q12. 提示 `detached HEAD`（头指针分离）

原因：你 checkout 到了某个具体提交，而不是分支上。

```powershell
git switch main          # 回到主分支
# 如果在这个分离状态上做了提交，想保留：
git switch -c rescue-branch
```

### Q13. 合并冲突（merge conflict）

现象：`git merge` 或 `git pull` 后提示 `CONFLICT`。

处理：

1. `git status` 查看冲突文件；
2. 打开文件，处理 `<<<<<<<` / `=======` / `>>>>>>>` 标记，保留正确内容；
3. `git add <冲突文件>`；
4. `git commit`（Git 会预填合并提交信息）。

放弃这次合并：

```powershell
git merge --abort
```

### Q14. 中文文件名显示成 `\345\255\246...`

```powershell
git config --global core.quotepath false
```

### Q15. 想回到某个历史版本 / 恢复误删文件

```powershell
git log --oneline                 # 找目标提交
git show <hash>:<文件路径>        # 查看那个版本的文件内容
git restore --source=<hash> <文件>  # 把文件恢复到那个版本
```

只恢复某个文件，不会影响其他代码。

### Q16. `fatal: not a git repository`

原因：当前目录不在 Git 仓库里，或 `.git` 被删了。

```powershell
git rev-parse --show-toplevel   # 查看当前仓库根目录
cd D:\LangChain\LangChain-LangGraph
```

### Q17. `git push` 卡住或超时

1. 检查网络/代理；
2. 用 `git remote -v` 确认地址；
3. 尝试 `git push --verbose` 看卡在哪一步；
4. 公司网络可能限制 HTTPS，改用 SSH 或配置代理。

### Q18. 分支叫 `master`，但教程都写 `main`

GitHub 新仓库默认 `main`，老仓库可能是 `master`。重命名：

```powershell
git branch -m master main
git push -u origin main
# 再到 GitHub 仓库 Settings → Branches 把默认分支改成 main
```

### Q19. `git pull` 提示 `divergent branches` / 要求选择策略

```powershell
# 推荐：变基，历史更线性
git pull --rebase
# 或者允许一次合并提交
git pull --no-rebase
# 设置默认策略
git config --global pull.rebase true
```

### Q20. 推送时提示 `git: 'credential-manager-core' is not a git command`

原因：Git for Windows 升级后，凭据助手的旧名字 `manager-core` 已改为 `manager`。如果本地还缓存着登录凭据，推送可能仍然成功，但每次都会打印这行警告。

```powershell
git config --global credential.helper manager
git push
```

如果改完仍然无法认证，重新安装 Git for Windows（会一并安装 Git Credential Manager），再到“Windows 凭据管理器”里删除旧的 `git:https://github.com` 条目重新登录。

---

## 7. 每次提交前的自检清单

照着做，能避开 90% 的坑：

```powershell
# 1. 看状态
git status -s

# 2. 看即将提交的内容
git diff --staged

# 3. 确认没有敏感信息
git diff --staged | Select-String -Pattern 'sk-|api_key|password|secret|token'

# 4. 确认没有被忽略的大文件混进来
git diff --staged --stat

# 5. 提交
git commit -m "feat: 说明"

# 6. 推送前确认远程有没有新提交
git fetch
git log --oneline HEAD..origin/main    # 有输出说明远程更新了，先 pull --rebase

# 7. 推送
git push

# 8. 到 GitHub 网页确认
```

---

## 8. 命令速查表

| 目的 | 命令 |
| --- | --- |
| 查看状态 | `git status -s` |
| 查看未暂存改动 | `git diff` |
| 查看已暂存改动 | `git diff --staged` |
| 暂存全部 | `git add -A` |
| 提交 | `git commit -m "说明"` |
| 推送 | `git push` |
| 拉取并变基 | `git pull --rebase` |
| 查看历史 | `git log --oneline --graph --all` |
| 查看远程 | `git remote -v` |
| 查看分支 | `git branch -vv` |
| 新建分支 | `git switch -c <名字>` |
| 切换分支 | `git switch <名字>` |
| 合并分支 | `git merge <名字>` |
| 停止跟踪文件 | `git rm --cached <文件>` |
| 检查忽略规则 | `git check-ignore -v <文件>` |
| 撤销暂存 | `git restore --staged <文件>` |
| 撤销工作区修改 | `git restore <文件>` |
| 撤销最近提交（保留改动） | `git reset --soft HEAD~1` |
| 找回误操作 | `git reflog` |
| 查看文件历史 | `git log -p -- <文件>` |

---

## 9. 这次提交总结出的三条经验

1. **先写 `.gitignore`，再开始写代码。** `.env`、`.venv`、`__pycache__`、`.idea`、压缩包默认就不该进仓库。
2. **提交前扫一遍密钥。** 密钥一旦进入公开仓库，就必须轮换，删代码和历史都只是补救。
3. **区分“已推送”和“未推送”的提交。** 未推送的提交可以放心用 `reset` 重写；已推送的提交不要随便改写历史，优先用新的提交来修正。

---

## 附：本次操作涉及的完整命令（可直接复制）

```powershell
# 0) 配置（一次性）
git config --global user.name "Ethan_Leo"
git config --global user.email "xuesongzhi813@gmail.com"
git config --global core.quotepath false

# 1) 检查
git remote -v
git status
git branch -vv

# 2) 备份 + 重写未推送提交
git branch backup/unpushed-20261110
git reset origin/main

# 3) 停止跟踪不该提交的文件
git ls-files |
  Where-Object { $_ -match '(^|/)\.idea/' -or $_ -match '(^|/)__pycache__/' -or $_ -match '\.pyc$' -or $_ -match '\.iml$' } |
  ForEach-Object { git rm --cached --quiet -- $_ }

# 4) 分提交
git add .gitignore .env.example FastAPIProject/.gitignore house_agent/.gitignore
git commit -m "chore: 添加根目录 .gitignore，停止跟踪 .env、IDE 配置与 Python 缓存"

git add LangChain/LangChain/CompleteTool.py
git commit -m "fix: CompleteTool 改为从环境变量读取 API Key"

git add -A
git commit -m "feat: 补充项目代码与工程文件"

# 5) 推送前审计
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD
git log origin/main..HEAD -p | Select-String -Pattern 'sk-[0-9a-fA-F]{20,}'

# 6) 推送
git push
```
