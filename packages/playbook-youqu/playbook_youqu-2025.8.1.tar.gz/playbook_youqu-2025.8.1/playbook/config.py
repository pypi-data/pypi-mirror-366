import os


class _Config:
    PASSWORD = os.getenv("YOUQU_PASSWORD") or "Autotest12#$"
    PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
    WORKDIR = os.path.abspath(".")

config = _Config()
