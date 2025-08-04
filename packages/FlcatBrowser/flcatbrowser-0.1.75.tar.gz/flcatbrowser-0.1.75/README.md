# 如何发布
修改 pyproject.toml和FlcatBrowser/version.py中的版本号，提交代码
在github中进行release，然后在actions中观察发布情况
# 发布后如何安装最新的包
因为包缓存的原因，刚刚发布的包无法立刻安装通过以下命令指定源进行安装
```
pip install FlcatBrowser== -i https://pypi.org/simple
```