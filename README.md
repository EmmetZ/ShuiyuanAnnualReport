# 水源社区个人年度报告脚本

用于生成SJTU[水源社区](https://shuiyuan.sjtu.edu.cn)个人年度总结

数据量较大的情况请谨慎使用（

## 使用方法

**请将 cookie `_t` 的值填入`cookie.txt`中**

### 1. 使用 [uv](https://github.com/astral-sh/uv)

```sh
uv sync
source .venv/bin/activate
python main.py
```

### 2. 使用 pip

```sh
python -m venv venv # 创建虚拟环境
source venv/bin/activate
pip install -r requirements.txt
python main.py
```


## 致谢

部分代码参考和思路来源：

https://github.com/UNIkeEN/Little-UNIkeEN-Bot

https://shuiyuan.sjtu.edu.cn/t/topic/202121

https://shuiyuan.sjtu.edu.cn/t/topic/202653

https://shuiyuan.sjtu.edu.cn/t/topic/205568

https://shuiyuan.sjtu.edu.cn/t/topic/48095

https://shuiyuan.sjtu.edu.cn/t/topic/123808

api参考

https://docs.discourse.org/
