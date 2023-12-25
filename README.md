# 一个水源社区个人年度报告脚本

用于生成SJTU[水源社区](https://shuiyuan.sjtu.edu.cn)个人年度总结

用到了aiohttp，短时间内大量请求（这也许不太好（？），请求数据较多时请谨慎使用www

## 使用方法

1. 从Releases下载压缩文件夹，解压后运行main.exe
2. 选择浏览器登陆（由于要用到selenium库，所以请选择自己电脑上已安装的浏览器）
3. 完成后请到`results`文件夹下查看结果

**注意：**

弹出
> 请检查浏览器驱动

对话框说明文件夹中已有的驱动版本与您的浏览器版本不匹配，请自行下载对应版本的驱动并**替换**`_internal/resources/webdriver`文件夹中原有的浏览器驱动

下载地址：

Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

Chrome: https://googlechromelabs.github.io/chrome-for-testing/

## 如何打包？

1. 安装pyinstaller

    ```shell
    pip install pyinstaller
    ```

2. 克隆本仓库
   
    ```shell
    git clone https://github.com/EmmetZ/ShuiyuanAnnualReport.git
    cd ShuiyuanAnnualReport
    ```

3. 运行pyinstaller打包
   
    ```shell
    pyinstaller main.spec
    ```

    打包好的.exe文件在`dist`文件夹下

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