import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import re

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 文件浏览器 (代码助手)")
        self.root.geometry("1000x700")

        # ========== 顶部地址栏 ==========
        top_frame = ttk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(top_frame, text="地址:").pack(side=tk.LEFT)
        self.address_entry = ttk.Entry(top_frame)
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.address_entry.bind("<Return>", self.go_to_path)
        self.go_button = ttk.Button(top_frame, text="前往", command=self.go_to_path)
        self.go_button.pack(side=tk.LEFT)

        # ========== 主区域（左右分割） ==========
        main_pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ----- 左侧文件树 -----
        tree_frame = ttk.Frame(main_pane, width=250)
        main_pane.add(tree_frame, weight=1)

        ttk.Label(tree_frame, text="文件浏览器", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, selectmode=tk.BROWSE)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # ----- 右侧内容区域（垂直分割）-----
        right_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane, weight=3)

        # 上半部分：文件内容显示（带右键菜单）
        text_frame = ttk.Frame(right_pane)
        right_pane.add(text_frame, weight=2)

        ttk.Label(text_frame, text="文件内容", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        self.text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(yscrollcommand=text_scroll.set)

        # 为文本区域添加右键菜单
        self.text_menu = tk.Menu(self.root, tearoff=0)
        self.text_menu.add_command(label="发送选中到 AI", command=self.send_selection_to_ai)
        self.text_menu.add_command(label="AI 修改选中", command=self.ai_modify_selection)
        self.text_area.bind("<Button-3>", self.show_text_menu)

        # 下半部分：AI 对话面板
        ai_frame = ttk.Frame(right_pane)
        right_pane.add(ai_frame, weight=1)

        ttk.Label(ai_frame, text="AI 助手", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)

        # 对话历史显示框
        self.chat_display = tk.Text(ai_frame, wrap=tk.WORD, font=("Consolas", 10), height=10)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        chat_scroll = ttk.Scrollbar(ai_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.configure(yscrollcommand=chat_scroll.set)
        self.chat_display.config(state=tk.DISABLED)

        # 输入区域
        input_frame = ttk.Frame(ai_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_entry.bind("<Return>", self.send_to_ai)

        self.send_button = ttk.Button(input_frame, text="发送", command=self.send_to_ai)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # 选项：是否包含当前文件内容
        self.include_file_var = tk.BooleanVar(value=True)
        self.include_file_check = ttk.Checkbutton(input_frame, text="包含文件内容", variable=self.include_file_var)
        self.include_file_check.pack(side=tk.LEFT, padx=5)

        # ========== 菜单栏 ==========
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开文件夹...", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="设置 Ollama 模型", command=self.set_model)
        menubar.add_cascade(label="设置", menu=settings_menu)

        root.config(menu=menubar)

        # ========== Ollama 配置 ==========
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5-coder:1.5b"  # 默认使用轻量代码模型

        # ========== 初始化：显示当前工作目录 ==========
        self.current_path = os.getcwd()
        self.load_directory(self.current_path)
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, self.current_path)

        self.append_to_chat("系统", "AI 助手已就绪（代码模型）。你可以选中代码后右键操作。")

    # ------------------ 文件浏览方法 ------------------
    def open_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self.current_path = folder
            self.load_directory(folder)
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, folder)

    def load_directory(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)
        root_node = self.tree.insert("", tk.END, text=os.path.basename(path), open=True, values=[path])
        self.populate_tree(root_node, path)

    def populate_tree(self, parent, path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    folder_node = self.tree.insert(parent, tk.END, text=item, open=False, values=[item_path])
                    self.tree.insert(folder_node, tk.END, text="loading...")
                else:
                    self.tree.insert(parent, tk.END, text=item, values=[item_path])
        except PermissionError:
            pass

    def on_tree_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        item_path = self.tree.item(item, "values")
        if not item_path:
            return
        path = item_path[0]

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, path)

        if os.path.isdir(path):
            children = self.tree.get_children(item)
            if len(children) == 1 and self.tree.item(children[0], "text") == "loading...":
                self.tree.delete(children[0])
                self.populate_tree(item, path)
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            except UnicodeDecodeError:
                messagebox.showerror("错误", "无法以文本方式打开此文件（可能为二进制文件）")
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败：{str(e)}")

    def go_to_path(self, event=None):
        path = self.address_entry.get().strip()
        if not path:
            return
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在")
            return
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory(path)
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, path)
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            except UnicodeDecodeError:
                messagebox.showerror("错误", "无法以文本方式打开此文件（可能为二进制文件）")
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败：{str(e)}")

    # ------------------ AI 相关方法 ------------------
    def set_model(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("设置模型")
        dialog.geometry("300x100")
        ttk.Label(dialog, text="模型名称:").pack(pady=5)
        model_entry = ttk.Entry(dialog)
        model_entry.pack(pady=5)
        model_entry.insert(0, self.model_name)
        def save():
            self.model_name = model_entry.get().strip()
            dialog.destroy()
        ttk.Button(dialog, text="保存", command=save).pack()

    def append_to_chat(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_to_ai(self, event=None):
        user_input = self.chat_entry.get().strip()
        if not user_input:
            return
        self.chat_entry.delete(0, tk.END)
        self.append_to_chat("你", user_input)

        # 获取当前文件内容（如果勾选）
        file_content = ""
        filename = "未知文件"
        if self.include_file_var.get():
            file_content = self.text_area.get(1.0, tk.END).strip()
            # 获取当前打开的文件名
            current_path = self.address_entry.get().strip()
            if os.path.isfile(current_path):
                filename = os.path.basename(current_path)
            
            if not file_content:
                file_content = "[当前没有打开文件或文件为空]"
            else:
                # 限制文件长度，防止风扇狂转
                if len(file_content) > 1000:
                    file_content = file_content[:1000] + "\n\n[文件太长，已截断至前1000字符]"

        # 构造提示词（优化版）
        system_prompt = "你是一个智能助手，请直接回答用户的问题。"
        if file_content:
            prompt = f"{system_prompt}\n\n文件名称：{filename}\n文件内容：\n```\n{file_content}\n```\n\n用户问题：{user_input}"
        else:
            prompt = f"{system_prompt}\n\n用户问题：{user_input}"

        # 额外：如果用户要求创建文件，AI可以在回答末尾添加【CREATE】指令（我们会隐藏它）
        # 我们不在提示词中强制说明，让AI自然生成即可（如果有指令我们会处理）

        threading.Thread(target=self.call_ollama, args=(prompt,), daemon=True).start()

    def call_ollama(self, prompt):
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "无响应内容")
            else:
                answer = f"请求失败，状态码: {response.status_code}"
        except Exception as e:
            answer = f"调用 Ollama 时出错: {str(e)}"

        # 在主线程中处理回答
        self.root.after(0, self.handle_ai_response, answer)

    def handle_ai_response(self, answer):
        """处理AI回答：提取指令，显示无指令的回答，执行指令"""
        lines = answer.strip().split('\n')
        display_lines = []
        command_line = None

        # 遍历每一行，寻找指令行
        for line in lines:
            if re.match(r'^【CREATE】.+?\|.+', line.strip()):
                command_line = line.strip()
                # 不将此行加入显示
            else:
                display_lines.append(line)

        # 显示无指令的回答
        display_answer = '\n'.join(display_lines).strip()
        if display_answer:
            self.append_to_chat("AI", display_answer)
        else:
            # 如果所有行都是指令（不太可能），至少显示一个提示
            self.append_to_chat("AI", "（无文本回复）")

        # 如果存在指令行，解析并执行
        if command_line:
            match = re.match(r'【CREATE】(.+?)\|(.+)', command_line)
            if match:
                filename = match.group(1).strip()
                content = match.group(2).strip()
                # 询问用户是否创建
                if messagebox.askyesno("创建文件", f"AI 建议创建文件：{filename}\n内容：\n{content}\n\n是否创建？"):
                    try:
                        # 获取当前目录
                        target_dir = self.address_entry.get().strip()
                        if os.path.isfile(target_dir):
                            target_dir = os.path.dirname(target_dir)
                        elif not os.path.isdir(target_dir):
                            target_dir = self.current_path
                        full_path = os.path.join(target_dir, filename)
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        messagebox.showinfo("成功", f"文件已创建：{full_path}")
                        # 刷新文件树
                        self.load_directory(target_dir)
                    except Exception as e:
                        messagebox.showerror("错误", f"创建文件失败：{str(e)}")

    # ------------------ 右键菜单功能 ------------------
    def show_text_menu(self, event):
        try:
            self.text_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_menu.grab_release()

    def send_selection_to_ai(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            messagebox.showwarning("提示", "请先选中要发送的代码")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("向 AI 提问")
        dialog.geometry("400x150")
        ttk.Label(dialog, text="你的问题（关于选中代码）:").pack(pady=5)
        entry = ttk.Entry(dialog, width=50)
        entry.pack(pady=5)
        entry.focus()

        def on_submit():
            question = entry.get().strip()
            if question:
                system_prompt = "你是一个智能助手，请直接回答用户的问题。"
                prompt = f"{system_prompt}\n\n选中代码：\n```\n{selected}\n```\n\n用户问题：{question}"
                self.append_to_chat("你", f"（针对选中代码）{question}")
                threading.Thread(target=self.call_ollama, args=(prompt,), daemon=True).start()
            dialog.destroy()

        ttk.Button(dialog, text="发送", command=on_submit).pack(pady=5)

    def ai_modify_selection(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            messagebox.showwarning("提示", "请先选中要修改的代码")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("AI 修改代码")
        dialog.geometry("400x150")
        ttk.Label(dialog, text="修改要求:").pack(pady=5)
        entry = ttk.Entry(dialog, width=50)
        entry.pack(pady=5)
        entry.focus()

        def on_submit():
            requirement = entry.get().strip()
            if requirement:
                prompt = f"以下是需要修改的代码：\n```\n{selected}\n```\n\n修改要求：{requirement}\n请直接输出修改后的完整代码，不要额外解释，只输出代码块。"
                self.append_to_chat("你", f"（修改选中代码）{requirement}")
                threading.Thread(target=self.call_ollama_with_modify, args=(prompt, selected), daemon=True).start()
            dialog.destroy()

        ttk.Button(dialog, text="发送", command=on_submit).pack(pady=5)

    def call_ollama_with_modify(self, prompt, original_code):
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")
            else:
                answer = f"请求失败，状态码: {response.status_code}"
        except Exception as e:
            answer = f"调用 Ollama 时出错: {str(e)}"

        self.root.after(0, self.display_ai_modify_result, answer, original_code)

    def display_ai_modify_result(self, answer, original_code):
        self.append_to_chat("AI", answer)

        code_blocks = re.findall(r'```(?:\w*)\n(.*?)```', answer, re.DOTALL)
        if not code_blocks:
            return

        modified_code = code_blocks[0]

        preview = tk.Toplevel(self.root)
        preview.title("代码修改预览")
        preview.geometry("600x400")

        text_preview = tk.Text(preview, wrap=tk.NONE, font=("Consolas", 10))
        text_preview.pack(fill=tk.BOTH, expand=True)
        text_preview.insert(tk.END, modified_code)

        def apply_modification():
            try:
                sel_start = self.text_area.index(tk.SEL_FIRST)
                sel_end = self.text_area.index(tk.SEL_LAST)
                has_selection = True
            except tk.TclError:
                has_selection = False

            if has_selection:
                self.text_area.delete(sel_start, sel_end)
                self.text_area.insert(sel_start, modified_code)
            else:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, modified_code)

            current_path = self.address_entry.get().strip()
            if os.path.isfile(current_path):
                try:
                    with open(current_path, 'w', encoding='utf-8') as f:
                        f.write(self.text_area.get(1.0, tk.END).strip())
                    messagebox.showinfo("成功", "文件已保存")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
            else:
                messagebox.showinfo("提示", "修改已应用，请手动保存文件")

            preview.destroy()

        ttk.Button(preview, text="应用修改", command=apply_modification).pack(pady=5)
        ttk.Button(preview, text="取消", command=preview.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
