import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("简易文件浏览器")
        self.root.geometry("900x600")

        # ========== 顶部地址栏 ==========
        top_frame = ttk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(top_frame, text="地址:").pack(side=tk.LEFT)
        self.address_entry = ttk.Entry(top_frame)
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.address_entry.bind("<Return>", self.go_to_path)  # 回车触发前往
        self.go_button = ttk.Button(top_frame, text="前往", command=self.go_to_path)
        self.go_button.pack(side=tk.LEFT)

        # ========== 主框架 ==========
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ----- 左侧文件树 -----
        tree_frame = ttk.Frame(main_frame, width=250)
        tree_frame.pack(side=tk.LEFT, fill=tk.Y)
        tree_frame.pack_propagate(False)  # 固定宽度

        ttk.Label(tree_frame, text="文件浏览器", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, selectmode=tk.BROWSE)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # ----- 右侧文本显示 -----
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(text_frame, text="文件内容", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        self.text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(yscrollcommand=text_scroll.set)

        # ========== 菜单栏 ==========
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开文件夹...", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        root.config(menu=menubar)

        # ========== 初始化：显示当前工作目录 ==========
        self.current_path = os.getcwd()
        self.load_directory(self.current_path)
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, self.current_path)

    def open_folder(self):
        """打开文件夹选择对话框"""
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self.current_path = folder
            self.load_directory(folder)
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, folder)

    def load_directory(self, path):
        """加载文件夹到树"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加根节点
        root_node = self.tree.insert("", tk.END, text=os.path.basename(path), open=True, values=[path])
        self.populate_tree(root_node, path)

    def populate_tree(self, parent, path):
        """递归填充目录内容"""
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    folder_node = self.tree.insert(parent, tk.END, text=item, open=False, values=[item_path])
                    # 插入占位节点，实现懒加载
                    self.tree.insert(folder_node, tk.END, text="loading...")
                else:
                    self.tree.insert(parent, tk.END, text=item, values=[item_path])
        except PermissionError:
            pass  # 跳过无权限访问的文件夹

    def on_tree_double_click(self, event):
        """双击树节点"""
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        item_path = self.tree.item(item, "values")
        if not item_path:
            return
        path = item_path[0]

        # 更新地址栏
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, path)

        if os.path.isdir(path):
            # 如果是文件夹，检查是否需要展开（懒加载）
            children = self.tree.get_children(item)
            if len(children) == 1 and self.tree.item(children[0], "text") == "loading...":
                self.tree.delete(children[0])
                self.populate_tree(item, path)
        else:
            # 如果是文件，读取并显示内容
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
        """地址栏前往功能"""
        path = self.address_entry.get().strip()
        if not path:
            return
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在")
            return

        if os.path.isdir(path):
            # 如果是文件夹，加载到树
            self.current_path = path
            self.load_directory(path)
            # 地址栏可能保持不变，但为了保险再设置一次
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, path)
        else:
            # 如果是文件，直接显示内容
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                # 地址栏显示文件路径（已经是路径，不需要改）
            except UnicodeDecodeError:
                messagebox.showerror("错误", "无法以文本方式打开此文件（可能为二进制文件）")
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
