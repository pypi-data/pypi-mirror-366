def gui_error(message):
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showerror("错误", message)
    root.destroy()  # 销毁主窗口
