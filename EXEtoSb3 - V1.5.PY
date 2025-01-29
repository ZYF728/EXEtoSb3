import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from os import makedirs, remove, rmdir, walk
from os.path import join, splitext, exists
from zipfile import ZipFile


def custom_relpath(path, start):
    # 将路径转换为绝对路径并规范化
    path = os.path.abspath(os.path.normpath(path))
    start = os.path.abspath(os.path.normpath(start))
    if start not in path:
        return path
    common = os.path.commonprefix([path, start])
    rel_path = path[len(common):].lstrip(os.sep)
    parts = rel_path.split(os.sep)
    rel = []
    for part in parts:
        if part == '..':
            rel.pop()
        elif part!= '.':
            rel.append(part)
    return os.sep.join(rel)


def convert_exe_to_sb3(zip_file_name, output_dir):
    file_name = os.path.basename(zip_file_name)
    target_zip_name = join(output_dir, splitext(file_name)[0] + ".sb3")
    # 构建临时解压目录路径
    temp_dir = join(output_dir, "temp_extract")
    makedirs(temp_dir, exist_ok=True)
    print(f"正在解压 {zip_file_name} 到 {temp_dir}...")
    # 解压主程序压缩包
    try:
        with ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except ZipFile.BadZipFile:
        print(f"错误: {zip_file_name} 不是有效的压缩文件。")
        return

    # 找到 resources\app 目录并压缩其下所有文件为 sb3 格式
    app_dir = join(temp_dir, "resources", "app")
    if not exists(app_dir):
        print(f"错误: 在解压文件中未找到 {app_dir}。")
        return

    print(f"正在从 {app_dir} 创建 {target_zip_name}...")
    with ZipFile(target_zip_name, 'w') as new_zip:
        for root, dirs, files in walk(app_dir):
            for file in files:
                file_path = join(root, file)
                # 计算文件在压缩包中的相对路径
                arcname = join(custom_relpath(root, app_dir), file)
                new_zip.write(file_path, arcname=arcname)

    # 删除临时目录及其中文件
    print(f"正在清理 {temp_dir}...")
    for root, dirs, files in walk(temp_dir, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            rmdir(join(root, name))
    rmdir(temp_dir)
    print(f"转换完成。生成 {target_zip_name}")


def select_input_file():
    global input_file_path
    input_file_path = filedialog.askopenfilename(filetypes=[("ZIP文件", "*.zip")])
    input_file_label.config(text=f"选择的文件: {input_file_path}")


def select_output_dir():
    global output_dir_path
    output_dir_path = filedialog.askdirectory()
    output_dir_label.config(text=f"选择的输出目录: {output_dir_path}")


def gui_convert():
    if not input_file_path or not output_dir_path:
        messagebox.showwarning("警告", "请选择输入文件和输出目录。")
        return
    convert_exe_to_sb3(input_file_path, output_dir_path)


def show_author_link():
    messagebox.showinfo("关于作者", "作者链接: https://space.bilibili.com/3546607349926754")


if __name__ == "__main__":
    print("Author's link: https://space.bilibili.com/3546607349926754")
    input_file_path = ""
    output_dir_path = ""
    if len(sys.argv) == 3:
        convert_exe_to_sb3(sys.argv[1], sys.argv[2])
    else:
        root = tk.Tk()
        root.title("EXE转SB3转换器")
        root.geometry("600x350")
        root.resizable(False, False)
        root.configure(bg='#f0f0f5')

        input_button = tk.Button(root, text="选择ZIP文件", command=select_input_file, bg='#4CAF50', fg='white')
        input_button.pack(pady=10)

        input_file_label = tk.Label(root, text="选择的文件: ", bg='#f0f0f5')
        input_file_label.pack(pady=5)

        output_button = tk.Button(root, text="选择输出目录", command=select_output_dir, bg='#2196F3', fg='white')
        output_button.pack(pady=10)

        output_dir_label = tk.Label(root, text="选择的输出目录: ", bg='#f0f0f5')
        output_dir_label.pack(pady=5)

        convert_button = tk.Button(root, text="执行转换", command=gui_convert, bg='#FF9800', fg='white')
        convert_button.pack(pady=20)

        about_author_button = tk.Button(root, text="关于作者", command=show_author_link, bg='#9C27B0', fg='white')
        about_author_button.pack(pady=10)

        root.mainloop()