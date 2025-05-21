import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
from datetime import datetime

SERVER_HOST = 'localhost'
SERVER_PORT = 2540


class ModernATMClient:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.configure_styles()
        self.current_user = None

        # 主界面架构
        self.main_container = ttk.Frame(root)  # 动态内容容器
        self.main_container.pack(expand=True, fill=tk.BOTH)

        self.status_container = ttk.Frame(root)  # 固定状态栏容器
        self.status_container.pack(side=tk.BOTTOM, fill=tk.X)

        # 初始化网络和界面
        self.setup_status_bar()
        self.connect_server()
        self.show_login_ui()

    def configure_styles(self):
        """配置全局样式"""
        self.style.theme_use('clam')
        # 主界面样式
        self.style.configure('TFrame', background='#F5F6FA')
        self.style.configure('TLabel', font=('Arial', 10), background='#F5F6FA')
        self.style.configure('Primary.TButton',
                             foreground='white',
                             background='#2D89EF',
                             font=('Arial', 12, 'bold'),
                             padding=8)
        self.style.map('Primary.TButton',
                       background=[('active', '#2B5797')])
        self.style.configure('TEntry',
                             font=('Arial', 12),
                             padding=5,
                             fieldbackground='white')
        # 状态栏样式
        self.style.configure('Status.TFrame', background='#e0e0e0')
        self.style.configure('Status.TLabel',
                             font=('Consolas', 10),
                             background='#e0e0e0')

    def setup_status_bar(self):
        """初始化状态栏"""
        status_frame = ttk.Frame(self.status_container, style='Status.TFrame')
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(status_frame,
                  text="通信状态监控：",
                  style='Status.TLabel').pack(anchor='w')

        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            wrap=tk.WORD,
            height=8,
            font=('Consolas', 9),
            state='disabled'
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        # 配置颜色标签
        self.status_text.tag_config('send', foreground='blue')
        self.status_text.tag_config('recv', foreground='green')
        self.status_text.tag_config('error', foreground='red')
        self.status_text.tag_config('sys', foreground='#666666')

    def update_status(self, message, tag=None):
        """更新状态信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.configure(state='normal')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.status_text.see(tk.END)
        self.status_text.configure(state='disabled')

    def connect_server(self):
        """连接服务器"""
        try:
            self.update_status("正在连接服务器...", 'sys')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.update_status(f"已连接到服务器 {SERVER_HOST}:{SERVER_PORT}", 'sys')
        except Exception as e:
            self.update_status(f"连接失败: {str(e)}", 'error')
            messagebox.showerror("连接错误", "无法连接到服务器")
            self.root.destroy()

    def clear_main_container(self):
        """清空主容器内容"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_login_ui(self):
        """显示登录界面"""
        self.clear_main_container()
        self.update_status("进入登录界面", 'sys')

        login_frame = ttk.Frame(self.main_container, padding=20)
        login_frame.pack(expand=True, fill=tk.BOTH)

        # 标题
        ttk.Label(login_frame,
                  text="ATM取款机",
                  font=('Arial', 24, 'bold'),
                  foreground='#1F3A93').pack(pady=20)

        # 输入区域
        input_frame = ttk.Frame(login_frame)
        input_frame.pack(pady=20)

        ttk.Label(input_frame, text="账号：").grid(row=0, column=0, padx=5, pady=10, sticky='e')
        self.username_entry = ttk.Entry(input_frame, width=20)
        self.username_entry.grid(row=0, column=1, padx=5, pady=10)
        self.username_entry.focus()

        ttk.Label(input_frame, text="密码：").grid(row=1, column=0, padx=5, pady=10, sticky='e')
        self.password_entry = ttk.Entry(input_frame, show="•", width=20)
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)

        # 操作按钮
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame,
                   text="登  录",
                   style='Primary.TButton',
                   command=self.login).pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame,
                   text="退  出",
                   style='Primary.TButton',
                   command=self.on_closing).pack(side=tk.LEFT, padx=10)

    def show_main_ui(self):
        """显示主操作界面"""
        self.clear_main_container()
        self.update_status(f"用户 {self.current_user} 登录成功", 'sys')

        main_frame = ttk.Frame(self.main_container, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 用户信息栏
        user_bar = ttk.Frame(main_frame)
        user_bar.pack(fill=tk.X, pady=10)

        ttk.Label(user_bar,
                  text=f"欢迎您，{self.current_user}",
                  font=('Arial', 16, 'bold'),
                  foreground='#1F3A93').pack(side=tk.LEFT)

        ttk.Button(user_bar,
                   text="注销登录",
                   style='Primary.TButton',
                   command=self.logout).pack(side=tk.RIGHT)

        # 功能按钮区
        func_grid = ttk.Frame(main_frame)
        func_grid.pack(pady=30)

        ttk.Button(func_grid,
                   text="查询余额",
                   style='Primary.TButton',
                   command=self.check_balance,
                   width=15).grid(row=0, column=0, padx=15, pady=15)

        ttk.Button(func_grid,
                   text="取款操作",
                   style='Primary.TButton',
                   command=self.show_withdraw_panel,
                   width=15).grid(row=0, column=1, padx=15, pady=15)

    def show_withdraw_panel(self):
        """显示取款面板"""
        self.update_status("进入取款界面", 'sys')
        withdraw_frame = ttk.Frame(self.main_container)
        withdraw_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        ttk.Label(withdraw_frame, text="取款金额：").pack(side=tk.LEFT)
        self.amount_entry = ttk.Entry(withdraw_frame, width=15)
        self.amount_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(withdraw_frame,
                   text="确认取款",
                   style='Primary.TButton',
                   command=self.withdraw).pack(side=tk.LEFT)

    def login(self):
        """处理登录逻辑"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.update_status(f"尝试登录用户: {username}", 'sys')
        response = self.send_command(f"HELO {username}")
        if "500 AUTH REQUIRE" in response:
            auth_res = self.send_command(f"PASS {password}")
            if "525 OK!" in auth_res:
                self.current_user = username
                self.show_main_ui()  # 切换至主界面
            else:
                self.update_status("密码验证失败", 'error')
                self.show_error("认证失败", "密码错误")
        else:
            self.update_status("无效的用户名", 'error')
            self.show_error("认证失败", "无效的用户名")

    def check_balance(self):
        """查询余额"""
        self.update_status("正在查询余额...", 'sys')
        response = self.send_command("BALA")
        if response.startswith("AMNT:"):
            balance = response.split(":")[1]
            self.show_info("账户余额", f"当前余额：¥{float(balance):.2f}")
            self.update_status("余额查询成功", 'recv')
        else:
            self.update_status("余额查询失败", 'error')

    def withdraw(self):
        """处理取款操作"""
        amount = self.amount_entry.get()
        try:
            float(amount)
            self.update_status(f"尝试取款 ¥{amount}", 'send')
            response = self.send_command(f"WDRA {amount}")
            if "525 OK!" in response:
                self.show_info("操作成功", f"成功取款 ¥{float(amount):.2f}")
                self.update_status("取款操作成功", 'recv')
            else:
                self.update_status("取款请求被拒绝", 'error')
                self.show_error("操作失败", "取款失败，请检查余额")
        except ValueError:
            self.update_status("无效的金额输入", 'error')
            self.show_error("输入错误", "请输入有效的金额")

    def logout(self):
        """注销登录"""
        self.update_status("用户注销登录", 'sys')
        self.send_command("BYE")
        self.current_user = None
        self.show_login_ui()  # 返回登录界面

    def send_command(self, cmd):
        """发送命令到服务器"""
        try:
            self.sock.sendall(cmd.encode())
            response = self.sock.recv(1024).decode()
            self.update_status(f"发送: {cmd}", 'send')
            self.update_status(f"接收: {response}", 'recv')
            return response
        except Exception as e:
            self.update_status(f"通信错误: {str(e)}", 'error')
            self.show_error("连接错误", "服务器连接已中断")
            self.root.destroy()
            return ""

    def show_info(self, title, message):
        """显示信息提示"""
        messagebox.showinfo(title, message, parent=self.root)

    def show_error(self, title, message):
        """显示错误提示"""
        messagebox.showerror(title, message, parent=self.root)

    def on_closing(self):
        """关闭窗口时的处理"""
        self.update_status("正在关闭连接...", 'sys')
        if self.sock:
            self.sock.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ATM客户端")
    root.geometry("800x680")
    root.configure(bg='#F5F6FA')

    try:
        root.iconbitmap('bank.ico')
    except:
        pass

    app = ModernATMClient(root)
    root.mainloop()