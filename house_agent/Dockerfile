# =============================================================================
#  LangGraph 应用镜像
#  ─────────────────────────────────────────────────────────────────────────────
#  放哪里：你项目根目录（和 requirements.txt / pyproject.toml 同一层），文件名就叫 Dockerfile
#  它是什么：一份"菜谱"。docker build 按这份菜谱在服务器上做出一个"镜像"，
#           镜像里包含：Linux + Python + 你的全部依赖 + 你的代码。
#           所以服务器上根本不需要装 Python。
#  为什么能和本地环境一样：Python 小版本 + 依赖的精确版本都被写死在镜像里了。
# =============================================================================

# ① 基础镜像：必须和本地虚拟环境的 Python 版本一致（你本地是 Python 3.13.16）
#    ⚠️ 只能写【官方镜像名】，小写、中间是冒号：
#       FROM python:3.13-slim   ✅
#       FROM Python 3.13.16     ❌（invalid reference format: must be lowercase）
#       FROM python 3.13-slim   ❌（空格会被当成阶段名）
FROM python:3.13-slim

# ② 全局环境变量
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# ③ 换国内 apt 源 + 装系统依赖
#    ⚠️ 不换源的话，deb.debian.org 在国内会慢到"一小时都装不完"。
#    build-essential 是编译器（约 88MB 带依赖）。留着最保险：万一某个包没有现成的
#    Linux 轮子、需要现场编译，没它就会报 "command 'gcc' failed"。
#    以后想瘦身，可以把它删掉再试（多数项目其实用不上）。
RUN set -eux; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/debian.sources; do \
        if [ -f "$f" ]; then \
            sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' "$f"; \
        fi; \
    done; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates tzdata; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime; \
    rm -rf /var/lib/apt/lists/*

# ④ 工作目录：容器里的 /app 就是你项目根目录的位置
WORKDIR /app

# ⑤ 把项目拷进镜像（.dockerignore 会排除 .venv / __pycache__ / .git / .langgraph_api 等）
COPY . .

# ⑥ 装依赖。优先级从上到下，谁先存在用谁：
#    1) requirements.lock.txt —— 本地 pip freeze 导出的精确版本清单（推荐，环境最一致）
#    2) requirements.txt
#    3) uv.lock / poetry.lock / pyproject.toml
RUN pip install --upgrade pip && \
    if [ -f requirements.lock.txt ]; then \
        echo ">>> 使用精确版本清单 requirements.lock.txt"; pip install -r requirements.lock.txt; \
    elif [ -f requirements.txt ]; then \
        echo ">>> 使用 requirements.txt"; pip install -r requirements.txt; \
    elif [ -f uv.lock ]; then \
        echo ">>> 使用 uv.lock"; pip install uv && uv sync --frozen; \
    elif [ -f poetry.lock ]; then \
        echo ">>> 使用 poetry.lock"; pip install poetry && poetry config virtualenvs.create false && poetry install --no-root; \
    elif [ -f pyproject.toml ]; then \
        echo ">>> 使用 pyproject.toml"; pip install .; \
    else \
        echo "!!!! 项目根目录没有找到任何依赖清单文件"; exit 1; \
    fi

# ⑦ uv 会把依赖装在 /app/.venv，加进 PATH 才能直接调用；不用 uv 的项目这行无副作用
ENV PATH="/app/.venv/bin:${PATH}"

# ⑧ 安装项目自身（关键，千万别漏！）
#    本地 pip freeze 里有这样一行：
#       -e git+https://github.com/xuesongzhi813-star/LangChain-LangGraph.git@9aed...#egg=agent&subdirectory=house_agent
#    这种「可编辑安装 / 本地路径」的行会被打包脚本自动剔除（服务器上装不上），
#    所以必须在这里用已经 COPY 进来的源码补装一次。
#    --no-deps：依赖已按精确版本装好，不要让 pip 再去解析/升级依赖。
RUN pip install --no-deps -e .

# ⑨ 兜底清理：把「本地开发状态文件」从镜像里彻底删掉 ★重要★
#    症状：容器启动就崩，日志最后一行是
#       RuntimeError: Unexpected error loading store data from
#       .langgraph_api/store.pckl: No module named 'agent'
#    原因：.langgraph_api/ 是你本地跑 langgraph dev 生成的状态目录，里面的 *.pckl 是
#          pickle 序列化数据，记录着【本地】的模块路径。它一旦被打进镜像，容器启动时
#          会尝试"恢复上次的状态"，反序列化就炸。
#    .dockerignore 已经排除它了，这里再加一道保险：即使哪天漏了也能救回来。
RUN set -eux; \
    find /app -name '.langgraph_api' -type d -prune -exec rm -rf {} + || true; \
    find /app -name '.langgraph' -type d -prune -exec rm -rf {} + || true; \
    find /app -name '*.pckl' -delete || true; \
    find /app -name '__pycache__' -type d -prune -exec rm -rf {} + || true

# ⑩ 用非 root 账号运行容器（更安全，被入侵时损失更小）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ⑪ 声明容器对外提供 8000 端口（要和 docker run -p 8000:8000 保持一致）
EXPOSE 8000

# =============================================================================
# ⑫ 启动命令（唯一需要你按项目实际情况确认的一行）
# ─────────────────────────────────────────────────────────────────────────────
#  怎么确定？就看你在本地激活虚拟环境之后敲的那条启动命令，原样搬过来，
#  只把「监听地址」改成 0.0.0.0（否则容器外访问不到）。常见四种：
#
#   FastAPI 项目，入口是 app/main.py 里的 app 对象：
#       CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#   FastAPI 项目，入口是根目录 main.py：
#       CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#   LangGraph 官方 CLI（项目里有 langgraph.json）：
#       CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8000"]
#   普通脚本：
#       CMD ["python", "main.py"]
#
#  容器里不需要"激活虚拟环境"这一步：镜像本身就是那个环境，python/langgraph 直接可用。
# =============================================================================
CMD ["langgraph","dev","--host","0.0.0.0","--port","8000"]
