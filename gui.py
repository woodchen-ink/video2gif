import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import platform
import os
import webbrowser
from threading import Thread
import traceback

# 在类定义前添加 FFmpeg 路径设置
if getattr(sys, "frozen", False):
    # 运行在 PyInstaller 打包后的环境
    ffmpeg_path = os.path.join(
        sys._MEIPASS,
        "ffmpeg",
        "ffmpeg.exe" if platform.system().lower() == "windows" else "ffmpeg",
    )
    ffprobe_path = os.path.join(
        sys._MEIPASS,
        "ffmpeg",
        "ffprobe.exe" if platform.system().lower() == "windows" else "ffprobe",
    )
else:
    # 运行在开发环境
    ffmpeg_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "ffmpeg",
        "ffmpeg.exe" if platform.system().lower() == "windows" else "ffmpeg",
    )
    ffprobe_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "ffmpeg",
        "ffprobe.exe" if platform.system().lower() == "windows" else "ffprobe",
    )

# 设置 ffmpeg-python 包使用的 FFmpeg 路径
import ffmpeg

ffmpeg._run.DEFAULT_FFMPEG_PATH = ffmpeg_path
ffmpeg._run.DEFAULT_FFPROBE_PATH = ffprobe_path

# 添加到系统 PATH
if os.path.dirname(ffmpeg_path) not in os.environ["PATH"]:
    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]


class VideoToGifConverter:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("视频转GIF工具")

        # 设置窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 设置窗口样式
        self.root.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabelframe", background="#f0f0f0")

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        # 文件选择框
        self.file_frame = ttk.LabelFrame(self.root, text="选择文件")
        self.file_frame.pack(padx=10, pady=5, fill="x")

        self.files_list = tk.Listbox(self.file_frame, height=5)
        self.files_list.pack(padx=5, pady=5, fill="x")

        # 为文件列表添加右键菜单
        self.files_list_menu = tk.Menu(self.root, tearoff=0)
        self.files_list_menu.add_command(label="删除选中", command=self.delete_selected)
        self.files_list_menu.add_command(
            label="清空列表", command=lambda: self.files_list.delete(0, tk.END)
        )

        self.files_list.bind("<Button-3>", self.show_context_menu)

        btn_frame = ttk.Frame(self.file_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        self.select_btn = ttk.Button(
            btn_frame, text="选择视频", command=self.select_files
        )
        self.select_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(
            btn_frame,
            text="清空列表",
            command=lambda: self.files_list.delete(0, tk.END),
        )
        self.clear_btn.pack(side="left", padx=5)

        # 转换设置框
        self.settings_frame = ttk.LabelFrame(self.root, text="转换设置")
        self.settings_frame.pack(padx=10, pady=5, fill="x")

        # 尺寸设置
        size_frame = ttk.Frame(self.settings_frame)
        size_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(size_frame, text="尺寸设置:").pack(side="left", padx=5)
        self.size_var = tk.StringVar(value="original")
        ttk.Radiobutton(
            size_frame, text="保持原始尺寸", variable=self.size_var, value="original"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            size_frame, text="自定义尺寸", variable=self.size_var, value="custom"
        ).pack(side="left", padx=5)

        # 自定义尺寸输入框
        custom_size_frame = ttk.Frame(self.settings_frame)
        custom_size_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(custom_size_frame, text="宽度:").pack(side="left", padx=5)
        self.width_var = tk.StringVar(value="480")
        self.width_entry = ttk.Entry(
            custom_size_frame, textvariable=self.width_var, width=8
        )
        self.width_entry.pack(side="left", padx=5)

        ttk.Label(custom_size_frame, text="高度:").pack(side="left", padx=5)
        self.height_var = tk.StringVar(value="auto")
        self.height_entry = ttk.Entry(
            custom_size_frame, textvariable=self.height_var, width=8
        )
        self.height_entry.pack(side="left", padx=5)

        # FPS设置
        fps_frame = ttk.Frame(self.settings_frame)
        fps_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(fps_frame, text="FPS:").pack(side="left", padx=5)
        self.fps_var = tk.StringVar(value="10")
        self.fps_entry = ttk.Entry(fps_frame, textvariable=self.fps_var, width=8)
        self.fps_entry.pack(side="left", padx=5)

        # 时长控制
        duration_frame = ttk.Frame(self.settings_frame)
        duration_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(duration_frame, text="时长控制(秒):").pack(side="left", padx=5)
        ttk.Label(duration_frame, text="开始时间:").pack(side="left", padx=5)
        self.start_time_var = tk.StringVar(value="0")
        self.start_time_entry = ttk.Entry(
            duration_frame, textvariable=self.start_time_var, width=8
        )
        self.start_time_entry.pack(side="left", padx=5)

        ttk.Label(duration_frame, text="持续时间:").pack(side="left", padx=5)
        self.duration_var = tk.StringVar(value="")
        self.duration_entry = ttk.Entry(
            duration_frame, textvariable=self.duration_var, width=8
        )
        self.duration_entry.pack(side="left", padx=5)
        ttk.Label(duration_frame, text="(留空表示全部)").pack(side="left", padx=5)

        # 质量设置
        quality_frame = ttk.Frame(self.settings_frame)
        quality_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(quality_frame, text="质量设置:").pack(side="left", padx=5)
        self.quality_var = tk.StringVar(value="medium")
        ttk.Radiobutton(
            quality_frame, text="高质量", variable=self.quality_var, value="high"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            quality_frame, text="中等", variable=self.quality_var, value="medium"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            quality_frame, text="低质量", variable=self.quality_var, value="low"
        ).pack(side="left", padx=5)

        # 输出设置
        output_frame = ttk.Frame(self.settings_frame)
        output_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(output_frame, text="输出位置:").pack(side="left", padx=5)
        self.output_var = tk.StringVar(value="same")
        ttk.Radiobutton(
            output_frame, text="与视频相同目录", variable=self.output_var, value="same"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            output_frame, text="自定义目录", variable=self.output_var, value="custom"
        ).pack(side="left", padx=5)

        self.output_path_var = tk.StringVar()
        self.output_path_entry = ttk.Entry(
            output_frame, textvariable=self.output_path_var, width=30
        )
        self.output_path_entry.pack(side="left", padx=5)

        self.browse_btn = ttk.Button(
            output_frame, text="浏览", command=self.browse_output
        )
        self.browse_btn.pack(side="left", padx=5)

        # 转换按钮
        self.convert_btn = ttk.Button(
            self.root, text="开始转换", command=self.start_conversion
        )
        self.convert_btn.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # 状态标签
        self.status_label = ttk.Label(self.root, text="就绪")
        self.status_label.pack(pady=5)

    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.files_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.files_list_menu.grab_release()

    def delete_selected(self):
        """删除选中的文件"""
        selection = self.files_list.curselection()
        for index in reversed(selection):
            self.files_list.delete(index)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path_var.set(directory)

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        self.files_list.delete(0, tk.END)
        for file in files:
            self.files_list.insert(tk.END, file)

    def get_quality_settings(self):
        """根据质量设置返回 FFmpeg 参数"""
        quality = self.quality_var.get()
        if quality == "high":
            return ["-quality", "100"]
        elif quality == "medium":
            return ["-quality", "75"]
        else:
            return ["-quality", "50"]

    def validate_inputs(self):
        """验证输入参数"""
        try:
            # 验证FPS
            fps = int(self.fps_var.get())
            if fps <= 0:
                raise ValueError("FPS必须大于0")

            # 验证时间设置
            start_time = float(self.start_time_var.get() or 0)
            if start_time < 0:
                raise ValueError("开始时间不能为负数")

            if self.duration_var.get():
                duration = float(self.duration_var.get())
                if duration <= 0:
                    raise ValueError("持续时间必须大于0")

            # 验证自定义尺寸
            if self.size_var.get() == "custom":
                width = int(self.width_var.get())
                if width <= 0:
                    raise ValueError("宽度必须大于0")

                height = self.height_var.get()
                if height != "auto":
                    height = int(height)
                    if height <= 0:
                        raise ValueError("高度必须大于0")

            return True
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False

    def convert_video_to_gif(self, video_path):
        try:
            # 打印环境信息
            print(f"FFmpeg path: {ffmpeg_path}")
            print(f"FFprobe path: {ffprobe_path}")
            print(f"System PATH: {os.environ['PATH']}")
            # 验证 FFmpeg 是否可用
            try:
                version_info = ffmpeg.probe(ffmpeg._run.DEFAULT_FFMPEG_PATH)
                print(f"FFmpeg version info: {version_info}")
            except Exception as e:
                print(f"FFmpeg probe error: {e}")
            # 验证输入
            if not self.validate_inputs():
                return False
            # 确定输出路径
            if self.output_var.get() == "same":
                output_dir = os.path.dirname(video_path)
            else:
                output_dir = self.output_path_var.get()
                if not output_dir:
                    raise ValueError("请选择输出目录")

            output_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(video_path))[0] + ".gif"
            )

            # 获取设置值
            start_time = float(self.start_time_var.get() or 0)
            duration = self.duration_var.get()
            fps = int(self.fps_var.get())

            # 设置调色板生成
            palette_path = os.path.join(output_dir, "palette.png")

            # 获取CPU核心数
            cpu_count = os.cpu_count() or 1
            threads = max(1, min(cpu_count - 1, 8))  # 留一个核心给系统用

            # 更新状态显示
            self.status_label.config(
                text=f"正在生成调色板... {os.path.basename(video_path)}"
            )
            self.root.update()
            # 第一步：生成调色板（添加线程参数）
            stream = ffmpeg.input(video_path)

            if start_time > 0:
                stream = ffmpeg.filter(stream, "setpts", f"PTS-{start_time}/TB")

            if duration:
                stream = ffmpeg.filter(stream, "t", duration=float(duration))

            stream = ffmpeg.filter(stream, "fps", fps=fps)

            if self.size_var.get() == "custom":
                width = int(self.width_var.get())
                height = self.height_var.get()
                height = -1 if height == "auto" else int(height)
                stream = ffmpeg.filter(stream, "scale", width=width, height=height)

            stream = ffmpeg.filter(stream, "palettegen")
            # 添加线程参数
            ffmpeg.run(
                ffmpeg.output(stream, palette_path, threads=threads),
                overwrite_output=True,
            )

            # 更新状态显示
            self.status_label.config(
                text=f"正在生成GIF... {os.path.basename(video_path)}"
            )
            self.root.update()
            # 第二步：使用调色板生成GIF（添加线程参数）
            stream = ffmpeg.input(video_path)
            palette = ffmpeg.input(palette_path)

            if start_time > 0:
                stream = ffmpeg.filter(stream, "setpts", f"PTS-{start_time}/TB")

            if duration:
                stream = ffmpeg.filter(stream, "t", duration=float(duration))

            stream = ffmpeg.filter(stream, "fps", fps=fps)

            if self.size_var.get() == "custom":
                width = int(self.width_var.get())
                height = self.height_var.get()
                height = -1 if height == "auto" else int(height)
                stream = ffmpeg.filter(stream, "scale", width=width, height=height)

            stream = ffmpeg.filter([stream, palette], "paletteuse")
            # 添加线程参数
            ffmpeg.run(
                ffmpeg.output(stream, output_path, threads=threads),
                overwrite_output=True,
            )

            # 删除临时调色板文件
            if os.path.exists(palette_path):
                os.remove(palette_path)

            return True

        except Exception as e:
            error_msg = str(e)
            print(f"Conversion error: {error_msg}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()
            messagebox.showerror("错误", f"转换失败:\n{error_msg}")
            return False

    def start_conversion(self):
        def convert():
            try:
                files = self.files_list.get(0, tk.END)
                if not files:
                    messagebox.showwarning("警告", "请先选择要转换的视频文件")
                    return

                total = len(files)
                success_count = 0

                for i, file in enumerate(files):
                    current = i + 1
                    self.status_label.config(
                        text=f"正在转换: {os.path.basename(file)} ({current}/{total})"
                    )
                    if self.convert_video_to_gif(file):
                        success_count += 1
                    progress = current / total * 100
                    self.progress["value"] = progress

                self.status_label.config(text=f"转换完成 ({success_count}/{total})")
                self.convert_btn["state"] = "normal"

                if success_count == total:
                    messagebox.showinfo(
                        "完成", f"所有文件转换完成！\n成功转换 {total} 个文件"
                    )
                else:
                    messagebox.showwarning(
                        "完成",
                        f"转换完成，但有部分失败。\n成功：{success_count}/{total}",
                    )

            except Exception as e:
                print(f"Conversion error: {str(e)}")
                traceback.print_exc()
                messagebox.showerror("错误", f"转换过程出错：\n{str(e)}")
            finally:
                self.convert_btn["state"] = "normal"

        self.convert_btn["state"] = "disabled"
        self.progress["value"] = 0
        Thread(target=convert).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        print("程序启动...")

        app = VideoToGifConverter()
        app.run()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback

        traceback.print_exc()  # 打印详细错误信息
        sys.exit(1)
