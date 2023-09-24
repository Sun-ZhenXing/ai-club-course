# 第 1 章：图片超分辨率服务

## 1. 环境搭建

环境：

- Python >= 3.9

工作之前先切换到当前文件夹下，然后安装依赖：

```bash
cd chapter-01
pip install -U -r requirements.txt
```

下面到 [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0) 项目下载最新的 Releases，然后解压到 `./libs/` 目录下。

运行开发环境：

```bash
sanic server.app --host 127.0.0.1 --port 8000 --dev -R static
```

## 2. 生产环境

请在 Linux/Unix 环境下运行，目前 Windows 不能进行生产环境的部署。

```bash
sanic server.app --host 0.0.0.0 --port 8000
```
