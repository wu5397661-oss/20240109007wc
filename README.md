# 屏幕翻译工具（Screen Translator）

> 基于 AI 大模型的实时屏幕截图翻译系统  
> 学号：20240109007

---

## 📖 项目简介

本项目是一个基于人工智能大模型的**实时屏幕翻译工具**，结合 OCR（光学字符识别）与大语言模型，实现"所见即所得"的屏幕翻译功能。用户只需框选屏幕上的任意区域，系统将自动识别文字并翻译为中文。

项目采用 **C/S（客户端-服务端）架构**，服务端可部署于云服务器，实现跨设备、跨平台的翻译能力。

---

## ✨ 功能特色

### 核心功能
- 📸 **屏幕区域截图** - 灵活框选任意屏幕区域
- 🔍 **OCR 文字识别** - 基于 Tesseract 的多语言识别
- 🤖 **AI 智能翻译** - 基于 Ollama + Qwen 大模型的高质量翻译
- 🖥️ **图形化界面** - 基于 Tkinter 的友好交互界面
- ☁️ **云端部署** - 支持部署到阿里云等云服务器，公网访问

### 技术亮点
1. **AI 大模型驱动** - 集成 Ollama 框架，使用通义千问大模型进行翻译，区别于传统翻译软件
2. **前后端分离** - 客户端（GUI）+ 服务端（API），解耦架构，便于扩展
3. **云服务部署** - 服务端部署于云服务器，支持公网访问
4. **跨平台兼容** - 服务端支持 Linux/Windows，客户端支持 Windows
5. **实时响应** - 异步调用 AI 接口，用户体验流畅

---

## 🏗️ 系统架构

```
┌───────────────────────┐         HTTP API          ┌───────────────────────┐
│   客户端 (Client)     │  ───────────────────────▶  │   服务端 (Server)     │
│                       │   POST /translate          │                       │
│   • Tkinter GUI       │   (上传截图)               │   • FastAPI           │
│   • 屏幕截图          │  ◀───────────────────────  │   • Tesseract OCR     │
│   • 结果展示          │   (返回识别+翻译结果)      │   • Ollama AI 翻译    │
└───────────────────────┘                             └───────────────────────┘
                                                             ▲
                                                             │
                                                             ▼
                                                     ┌─────────────────┐
                                                     │   Ollama 服务   │
                                                     │   (Qwen 2.5 3B) │
                                                     └─────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Python Tkinter, Pillow, PyAutoGUI | 图形化界面、屏幕截图 |
| **后端** | Python FastAPI, Uvicorn | RESTful API 服务 |
| **OCR** | Tesseract OCR, pytesseract | 图片文字识别 |
| **AI 翻译** | Ollama, Qwen 2.5 3B | 大语言模型翻译 |
| **部署** | 阿里云 ECS, Ubuntu 24.04 | 云服务器部署 |

### API 接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 服务健康检查 |
| `/ocr` | POST | 图片文字识别（OCR） |
| `/translate` | POST | 图片 OCR + 翻译（一步到位） |
| `/translate-text` | POST | 文本翻译 |

---

## 📂 项目结构

```
20240109007wc/
├── server/                      # 服务端代码
│   ├── server.py               # FastAPI 主服务
│   ├── requirements.txt        # Python 依赖
│   └── start.bat               # Windows 启动脚本
├── client/                      # 客户端代码
│   ├── client.py               # Tkinter GUI 主程序
│   ├── requirements.txt        # Python 依赖
│   └── start.bat               # Windows 启动脚本
├── screen_translator.py        # 旧版单机版（备份）
├── 一键启动.bat                 # 一键启动脚本（Windows）
├── 1-启动后端.bat               # 服务端启动脚本
├── 2-启动客户端.bat             # 客户端启动脚本
├── .gitignore                  # Git 忽略文件
└── README.md                   # 项目说明文档
```

---

## 🚀 快速开始

### 方式一：本地运行（开发环境）

#### 前置条件
- Python 3.10+
- Tesseract OCR
- Ollama（运行大模型）

#### 1. 克隆项目

```bash
git clone https://github.com/wu5397661-oss/20240109007wc.git
cd 20240109007wc
```

#### 2. 启动服务端

```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

#### 3. 启动客户端

```bash
cd client
python client.py
```

#### 4. 使用翻译功能

1. 在客户端界面点击"截取屏幕"
2. 拖动鼠标框选要翻译的文字区域
3. 松开鼠标，等待识别和翻译结果

---

### 方式二：云服务器部署（推荐）

#### 服务器环境
- 操作系统：Ubuntu 24.04 LTS
- 云平台：阿里云 ECS
- 公网 IP：120.27.15.234

#### 部署步骤

**1. 安装系统依赖**

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv tesseract-ocr tesseract-ocr-chi-sim
```

**2. 克隆项目并创建虚拟环境**

```bash
cd /opt
git clone https://github.com/wu5397661-oss/20240109007wc.git
cd 20240109007wc/server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. 安装并启动 Ollama**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
sleep 5
ollama pull qwen2.5:3b-instruct-q4_K_M
```

**4. 开放防火墙端口**

```bash
ufw allow 8000/tcp
ufw reload
```

**5. 启动后端服务**

```bash
cd /opt/20240109007wc/server
source venv/bin/activate
nohup python -m uvicorn server:app --host 0.0.0.0 --port 8000 &
```

**6. 验证服务**

```bash
curl http://120.27.15.234:8000/health
```

#### 阿里云安全组配置

在阿里云 ECS 控制台安全组中添加入站规则：
- 协议类型：自定义 TCP
- 端口范围：8000/8000
- 授权对象：0.0.0.0/0

---

## 💡 项目亮点与创新

### 1. AI 大模型接入
不同于传统翻译软件（如百度翻译、DeepL），本项目使用 **Ollama + 通义千问大模型** 进行翻译，具有以下优势：
- 可理解上下文，翻译更加自然流畅
- 支持多语言互译
- 可自定义翻译风格和提示词
- 本地部署，数据安全，无需调用第三方 API

### 2. 云服务部署
服务端部署于**阿里云 ECS 服务器**（公网 IP：120.27.15.234）：
- 支持多用户同时使用
- 客户端无需本地部署大模型，降低硬件要求
- 便于后续扩展和维护

### 3. 学以致用的技术应用
- **前后端分离架构** - 客户端与服务端解耦，通过 HTTP API 通信
- **Linux 服务器运维** - 使用 Ubuntu、命令行、防火墙配置
- **数据库/文件系统** - 项目依赖管理、日志记录
- **系统集成** - 集成 Tesseract OCR、Ollama 等多个服务

### 4. 有特色的交互设计
- 直观的截图框选操作
- 实时状态反馈
- 简洁的图形化界面
- 多线程异步处理，避免界面卡顿

---

## 🧪 功能测试

### 测试用例 1：英文翻译
**输入**：截取屏幕上的英文段落  
**预期**：正确识别英文并翻译成中文  
**结果**：✓ 通过

### 测试用例 2：数字与符号
**输入**：截取包含数字和符号的区域  
**预期**：保留数字符号的同时翻译文字  
**结果**：✓ 通过

### 测试用例 3：API 健康检查
**输入**：`GET http://120.27.15.234:8000/health`  
**预期**：返回服务状态 JSON  
**结果**：✓ 通过

### 测试用例 4：翻译接口调用
**输入**：`POST /translate`（上传图片）  
**预期**：返回识别的原文和翻译结果  
**结果**：✓ 通过

---

## 🔮 未来扩展

- 📱 移动端客户端（Android/iOS）
- 🌐 网页版翻译界面
- 📝 翻译历史记录与数据库存储
- 🎯 更多语言支持
- ⚡ 模型优化与加速
- 📊 使用量统计与分析

---

## 🛠️ 环境依赖

### Python 版本
- Python 3.10+

### 服务端依赖
```
fastapi>=0.110.0
uvicorn>=0.27.0
requests>=2.31.0
pillow>=10.0.0
pytesseract>=0.3.10
```

### 客户端依赖
```
Pillow>=10.0.0
pyautogui>=0.9.54
requests>=2.31.0
```

### 系统依赖
- Tesseract OCR 5.x
- Ollama 0.1.0+

---

## 📜 开源协议

本项目用于学习和课程作业，欢迎学习参考。

---

## 🙏 致谢

- FastAPI - 高性能 Python Web 框架
- Tesseract OCR - 开源 OCR 引擎
- Ollama - 开源大模型运行框架
- 通义千问 (Qwen) - 阿里巴巴开源大语言模型
- 阿里云 - 提供稳定的云服务器
