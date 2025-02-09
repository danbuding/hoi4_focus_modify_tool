import re
import os
from tkinter import Tk, Menu, Button, Label, filedialog, messagebox, Frame, Listbox, Scrollbar, END

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    messagebox.showerror("错误", "需要 tkinterdnd2 库支持拖放功能\n请执行: pip install tkinterdnd2")
    exit()

class FileModifierApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("国策：时间及科研槽修改工具 v0.1")
        self.geometry("800x500")
        self.selected_files = []
        self.create_menu()
        self.create_widgets()
        self.configure_drag_drop()

    def create_menu(self):
        menubar = Menu(self)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.open_files)
        file_menu.add_command(label="关闭文件", command=self.close_files)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        main_frame = Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        Label(main_frame, text="拖放文件到这里或使用菜单选择:\n 本软件仅支持将国策大于14天的项目设置为14天\n 以及将添加1个科研槽的国策修改为添加2个科研槽").pack(anchor="w")
        
        list_frame = Frame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        # 水平滚动条
        xscrollbar = Scrollbar(list_frame, orient="horizontal")
        xscrollbar.pack(side="bottom", fill="x")

        # 垂直滚动条
        yscrollbar = Scrollbar(list_frame)
        yscrollbar.pack(side="right", fill="y")

        self.file_listbox = Listbox(
            list_frame,
            xscrollcommand=xscrollbar.set,
            yscrollcommand=yscrollbar.set,
            selectmode="extended",
            height=12,
            width=80
        )
        self.file_listbox.pack(fill="both", expand=True)
        
        xscrollbar.config(command=self.file_listbox.xview)
        yscrollbar.config(command=self.file_listbox.yview)

        btn_frame = Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        Button(btn_frame, text="修改文件", command=self.modify_files).pack(side="left", padx=5)
        Button(btn_frame, text="清除列表", command=self.close_files).pack(side="left", padx=5)
        Button(btn_frame, text="退出程序", command=self.quit).pack(side="right", padx=5)

        self.status_label = Label(main_frame, text="就绪", bd=1, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", pady=(5,0))

    def configure_drag_drop(self):
        """配置拖放支持"""
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """处理拖放事件"""
        files = self.parse_dropped_files(event.data)
        if files:
            self.add_files(files)
            self.update_status(f"拖放添加 {len(files)} 个文件")

    def parse_dropped_files(self, data):
        """解析拖放的文件路径"""
        files = []
        # Windows路径处理
        if data.startswith('{') and data.endswith('}'):
            files = [f.strip('{} ') for f in data.split('} {')]
        # Linux/Mac路径处理
        else:
            files = data.split()
        
        # 验证文件是否存在
        valid_files = []
        for f in files:
            if os.path.exists(f):
                if os.path.isfile(f):
                    valid_files.append(f)
                else:
                    self.update_status(f"忽略文件夹: {f}")
        return valid_files

    def add_files(self, files):
        """添加文件到列表（去重）"""
        new_files = [f for f in files if f not in self.selected_files]
        self.selected_files.extend(new_files)
        self.update_file_list()

    def open_files(self):
        filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(
            title="选择要修改的文件",
            initialdir=os.getcwd(),
            filetypes=filetypes
        )
        if files:
            self.add_files(files)
            self.update_status(f"添加 {len(files)} 个文件")

    def close_files(self):
        self.selected_files.clear()
        self.file_listbox.delete(0, END)
        self.update_status("文件列表已清空")

    def modify_files(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要修改的文件！")
            return

        success = 0
        total = len(self.selected_files)
        
        for idx, filepath in enumerate(self.selected_files, 1):
            try:
                with open(filepath, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 修改 cost 值
                    content = re.sub(
                        r'(cost\s*=\s*)(\d+)',
                        lambda m: f'{m.group(1)}2' if int(m.group(2)) > 2 else m.group(0),
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    # 修改 research_slot 值
                    content = re.sub(
                        r'(add_research_slot\s*=\s*)(1)(\D|$)',
                        r'\g<1>2\g<3>',
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    f.seek(0)
                    f.write(content)
                    f.truncate()
                
                success += 1
                self.update_status(f"处理中 ({idx}/{total}): {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"文件 {filepath} 修改失败:\n{str(e)}")

        result_msg = f"成功修改 {success}/{total} 个文件"
        messagebox.showinfo("完成", result_msg)
        self.update_status(result_msg)
        self.close_files()

    def update_file_list(self):
        self.file_listbox.delete(0, END)
        for path in self.selected_files:
            self.file_listbox.insert(END, path)  # 显示完整路径

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()

    def show_about(self):
        about_msg = ("国策：时间及科研槽修改工具 v0.1\n\n"
                    "新增功能：\n"
                    "- 支持拖放文件操作\n"
                    "- 显示完整文件路径\n"
                    "- 自动滚动长路径\n"
                    "- 改进的错误处理机制")
        messagebox.showinfo("关于", about_msg)

if __name__ == "__main__":
    app = FileModifierApp()
    app.mainloop()
