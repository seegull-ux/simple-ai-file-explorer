# simple-ai-file-explorer

一个基于本地大模型的智能文件浏览器，支持代码理解、AI 对话和自动文件创建。  
所有 AI 功能均在本地运行（通过 Ollama），无需联网，保护你的数据隐私。

效果演示

<img width="2560" height="1504" alt="de7378be712453a612bcf4e94c87a7d6" src="https://github.com/user-attachments/assets/5eead5cb-ac82-486f-bd09-22c8a269a043" />

<img width="2560" height="1504" alt="24ea222157c39c2979ca7ee1fed9e15c" src="https://github.com/user-attachments/assets/eb23d6fe-a4d5-4aa1-87d8-054671e39ca4" />

---

##  下载与安装

### 1. 环境要求
- Windows 7/10/11 / Linux / macOS
- Python 3.8 或更高版本（[点此下载](https://www.python.org/downloads/)）
- [Ollama](https://ollama.com) 已安装并运行

### 2. 获取软件

访问仓库：https://github.com/seegull-ux/simple-ai-file-explorer

点击绿色按钮 Code → Download ZIP

解压到任意文件夹（例如 C:\Users\你的用户名\Desktop\my_project）

打开命令提示符，进入该文件夹：

cmd
cd Desktop\my_project

### 3. 安装 Python 依赖
在命令提示符中（确保已进入项目文件夹）执行：

cmd
pip install requests

### 4. 下载 AI 模型

确保 Ollama 已安装并运行（可执行 ollama serve 启动）。

下载推荐模型（约 1.5GB）：

cmd
ollama pull qwen2.5-coder:1.5b

你也可以使用其他模型（如 phi:3.8b、qwen2.5-coder:3b），只要你的电脑能跑动。

运行软件

在项目文件夹中执行：

cmd
python ai_file_explorer.py

软件窗口就会打开。

使用指南

界面布局
顶部地址栏：显示当前路径，可直接输入路径并按回车跳转。

左侧文件树：双击文件打开，显示在右侧文本区。

底部 AI 对话区：输入问题，勾选“包含文件内容”可让 AI 看到当前文件。

基本操作
打开文件
在左侧文件树中双击文件，内容会显示在右侧（仅支持文本文件）。

普通对话
在底部输入框输入问题，不勾选“包含文件内容”，点击“发送”或按回车。AI 直接回答。

基于文件内容提问
打开一个文件，勾选“包含文件内容”。

输入问题（例如“这个文件是做什么的？”），AI 会结合文件内容回答，并知道文件名。

选中代码提问
在右侧文本区选中一段代码，右键 → 发送选中到 AI。

在弹出的对话框中输入问题（如“解释这段代码”），AI 会针对选中代码回答。

AI 修改选中代码
选中代码，右键 → AI 修改选中。

输入修改要求（如“改成列表推导式”），AI 会返回修改后的代码块，并弹出预览窗口。

点击“应用修改”可将新代码替换到原位置（如果有选中区域则替换选中，否则替换整个文件），并自动保存文件。

自动创建文件（自然语言触发）
向 AI 提出创建文件的请求，例如：

“帮我创建一个 hello.txt，内容为 Hello World”

AI 会在回答末尾添加隐藏指令，软件弹出确认框，点击“是”后文件将在当前目录创建，并刷新文件树。

你看到的只有 AI 的自然语言回复（如“好的，已为你创建 hello.txt”），体验流畅。

切换模型
菜单栏 设置 → 设置 Ollama 模型，输入模型名称（例如 qwen2.5-coder:1.5b、phi:3.8b 等），点击保存。后续对话将使用新模型。
