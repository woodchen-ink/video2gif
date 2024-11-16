import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import platform
import os
import webbrowser
from threading import Thread
import ffmpeg
import traceback  # 用于打印详细错误信息

# 根据平台选择拖放实现
PLATFORM = platform.system().lower()

if PLATFORM == "windows":
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD

        SUPPORT_DND = "tkdnd"
    except ImportError:
        SUPPORT_DND = None
elif PLATFORM == "darwin":  # macOS
    SUPPORT_DND = "macos"
else:  # Linux or others
    SUPPORT_DND = None


class FFmpegInstaller:
    @staticmethod
    def get_ffmpeg_path():
        """获取FFmpeg可执行文件路径"""
        try:
            # 获取程序运行路径
            if getattr(sys, "frozen", False):
                # PyInstaller打包后的路径
                base_path = sys._MEIPASS
            else:
                # 开发环境路径
                base_path = os.path.dirname(os.path.abspath(__file__))

            # FFmpeg路径
            ffmpeg_dir = os.path.join(base_path, "ffmpeg")
            if platform.system().lower() == "windows":
                ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
            else:
                ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg")

            return ffmpeg_path
        except Exception as e:
            print(f"Error getting FFmpeg path: {e}")
            return None

    @staticmethod
    def check_ffmpeg():
        """检查是否可以使用FFmpeg"""
        try:
            ffmpeg_path = FFmpegInstaller.get_ffmpeg_path()
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                # 使用打包的FFmpeg
                if platform.system().lower() == "windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    result = subprocess.run(
                        [ffmpeg_path, "-version"],
                        capture_output=True,
                        startupinfo=startupinfo,
                    )
                else:
                    result = subprocess.run(
                        [ffmpeg_path, "-version"], capture_output=True
                    )
                return result.returncode == 0

            # 尝试系统PATH中的FFmpeg
            if platform.system().lower() == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(
                    ["ffmpeg", "-version"], capture_output=True, startupinfo=startupinfo
                )
            else:
                result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
            return result.returncode == 0

        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"FFmpeg检测出错: {str(e)}")
            return False

    @staticmethod
    def get_system_info():
        """获取系统信息"""
        system = platform.system().lower()
        is_64bits = sys.maxsize > 2**32
        return system, is_64bits

    def show_installation_dialog(self):
        """显示安装向导对话框"""
        system, is_64bits = self.get_system_info()

        dialog = tk.Toplevel()
        dialog.title("FFmpeg 安装向导")
        dialog.geometry("500x400")
        dialog.transient()  # 设置为模态窗口

        # 添加说明文本
        ttk.Label(
            dialog,
            text="未检测到 FFmpeg，需要先安装 FFmpeg 才能继续使用。",
            wraplength=450,
        ).pack(padx=20, pady=10)

        if system == "windows":
            self._setup_windows_installer(dialog)
        elif system == "darwin":  # macOS
            self._setup_macos_installer(dialog)
        elif system == "linux":
            self._setup_linux_installer(dialog)
        else:
            self._setup_manual_installer(dialog)

        dialog.focus_set()
        return dialog

    def _setup_windows_installer(self, dialog):
        """Windows安装方式"""
        ttk.Label(dialog, text="Windows 安装方式：", font=("", 10, "bold")).pack(
            padx=20, pady=5
        )

        # 方式1: Chocolatey
        choco_frame = ttk.LabelFrame(dialog, text="方式1：使用 Chocolatey（推荐）")
        choco_frame.pack(padx=20, pady=5, fill="x")

        ttk.Label(
            choco_frame,
            text="1. 首先安装 Chocolatey，在管理员权限的 PowerShell 中运行：",
            wraplength=450,
        ).pack(padx=5, pady=5)

        choco_cmd = """Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"""
        cmd_text = ttk.Entry(choco_frame, width=50)
        cmd_text.insert(0, choco_cmd)
        cmd_text.pack(padx=5, pady=5)

        ttk.Button(
            choco_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(choco_cmd),
        ).pack(pady=5)

        ttk.Label(choco_frame, text="2. 然后安装 FFmpeg，运行：").pack(padx=5, pady=5)

        ffmpeg_cmd = "choco install ffmpeg"
        cmd_text2 = ttk.Entry(choco_frame, width=50)
        cmd_text2.insert(0, ffmpeg_cmd)
        cmd_text2.pack(padx=5, pady=5)

        ttk.Button(
            choco_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(ffmpeg_cmd),
        ).pack(pady=5)

        # 方式2: 直接下载
        direct_frame = ttk.LabelFrame(dialog, text="方式2：直接下载")
        direct_frame.pack(padx=20, pady=5, fill="x")

        ttk.Label(direct_frame, text="从官方网站下载并手动配置环境变量：").pack(
            padx=5, pady=5
        )

        ttk.Button(
            direct_frame,
            text="打开下载页面",
            command=lambda: webbrowser.open("https://ffmpeg.org/download.html"),
        ).pack(pady=5)

    def _setup_macos_installer(self, dialog):
        """macOS安装方式"""
        ttk.Label(dialog, text="macOS 安装方式：", font=("", 10, "bold")).pack(
            padx=20, pady=5
        )

        # 方式1: Homebrew
        brew_frame = ttk.LabelFrame(dialog, text="方式1：使用 Homebrew（推荐）")
        brew_frame.pack(padx=20, pady=5, fill="x")

        ttk.Label(
            brew_frame, text="1. 首先安装 Homebrew，在终端运行：", wraplength=450
        ).pack(padx=5, pady=5)

        brew_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        cmd_text = ttk.Entry(brew_frame, width=50)
        cmd_text.insert(0, brew_cmd)
        cmd_text.pack(padx=5, pady=5)

        ttk.Button(
            brew_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(brew_cmd),
        ).pack(pady=5)

        ttk.Label(brew_frame, text="2. 然后安装 FFmpeg，运行：").pack(padx=5, pady=5)

        ffmpeg_cmd = "brew install ffmpeg"
        cmd_text2 = ttk.Entry(brew_frame, width=50)
        cmd_text2.insert(0, ffmpeg_cmd)
        cmd_text2.pack(padx=5, pady=5)

        ttk.Button(
            brew_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(ffmpeg_cmd),
        ).pack(pady=5)

    def _setup_linux_installer(self, dialog):
        """Linux安装方式"""
        ttk.Label(dialog, text="Linux 安装方式：", font=("", 10, "bold")).pack(
            padx=20, pady=5
        )

        # Ubuntu/Debian
        ubuntu_frame = ttk.LabelFrame(dialog, text="Ubuntu/Debian")
        ubuntu_frame.pack(padx=20, pady=5, fill="x")

        ubuntu_cmd = "sudo apt update && sudo apt install ffmpeg"
        cmd_text = ttk.Entry(ubuntu_frame, width=50)
        cmd_text.insert(0, ubuntu_cmd)
        cmd_text.pack(padx=5, pady=5)

        ttk.Button(
            ubuntu_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(ubuntu_cmd),
        ).pack(pady=5)

        # CentOS/RHEL
        centos_frame = ttk.LabelFrame(dialog, text="CentOS/RHEL")
        centos_frame.pack(padx=20, pady=5, fill="x")

        centos_cmd = "sudo yum install epel-release && sudo yum install ffmpeg"
        cmd_text2 = ttk.Entry(centos_frame, width=50)
        cmd_text2.insert(0, centos_cmd)
        cmd_text2.pack(padx=5, pady=5)

        ttk.Button(
            centos_frame,
            text="复制命令",
            command=lambda: self._copy_to_clipboard(centos_cmd),
        ).pack(pady=5)

    def _setup_manual_installer(self, dialog):
        """手动安装说明"""
        ttk.Label(
            dialog, text="请访问 FFmpeg 官方网站下载并安装：", wraplength=450
        ).pack(padx=20, pady=10)

        ttk.Button(
            dialog,
            text="打开 FFmpeg 官方网站",
            command=lambda: webbrowser.open("https://ffmpeg.org/download.html"),
        ).pack(pady=10)

    def _copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        dialog = tk.Toplevel()
        dialog.withdraw()
        dialog.clipboard_clear()
        dialog.clipboard_append(text)
        dialog.update()
        dialog.destroy()
        messagebox.showinfo("提示", "命令已复制到剪贴板！")


class VideoToGifConverter:
    def __init__(self):
        self.check_ffmpeg_installation()

        # 创建主窗口
        if SUPPORT_DND == "tkdnd":
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("视频转GIF工具")

        # 设置拖放支持
        self.setup_dnd()

        # 设置UI
        self.setup_ui()

    def setup_dnd(self):
        """设置拖放支持"""
        if SUPPORT_DND == "tkdnd":
            # Windows with tkinterdnd2
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self.handle_drop)
        elif SUPPORT_DND == "macos":
            # macOS native drag and drop
            self.root.bind("<<MacDropFiles>>", self.handle_macos_drop)
            # 启用macOS拖放
            self.root.tk.call("tk_getOpenFile", "-setup")
        else:
            print("Drag and drop not supported on this platform")

    def handle_drop(self, event):
        """处理Windows下的文件拖放"""
        files = self.root.tk.splitlist(event.data)
        self.process_dropped_files(files)

    def handle_macos_drop(self, event):
        """处理macOS下的文件拖放"""
        # macOS下获取拖放的文件路径
        files = self.root.tk.splitlist(self.root.tk.call("::tk::mac::GetDroppedFiles"))
        self.process_dropped_files(files)

    def process_dropped_files(self, files):
        """处理拖放的文件"""
        # 过滤出视频文件
        valid_extensions = (".mp4", ".avi", ".mov", ".mkv")
        valid_files = [f for f in files if f.lower().endswith(valid_extensions)]

        if valid_files:
            self.files_list.delete(0, tk.END)
            for file in valid_files:
                self.files_list.insert(tk.END, file)
        else:
            messagebox.showwarning(
                "警告", "请拖入视频文件（支持mp4, avi, mov, mkv格式）"
            )

    # 添加拖放处理方法
    def handle_drop(self, event):
        """处理文件拖放"""
        files = self.root.tk.splitlist(event.data)
        # 过滤出视频文件
        valid_extensions = (".mp4", ".avi", ".mov", ".mkv")
        valid_files = [f for f in files if f.lower().endswith(valid_extensions)]

        if valid_files:
            self.files_list.delete(0, tk.END)
            for file in valid_files:
                self.files_list.insert(tk.END, file)
        else:
            messagebox.showwarning(
                "警告", "请拖入视频文件（支持mp4, avi, mov, mkv格式）"
            )

    def check_ffmpeg_installation(self):
        """检查FFmpeg是否已安装"""
        installer = FFmpegInstaller()
        if not installer.check_ffmpeg():
            # 创建一个临时的root窗口来显示消息框
            temp_root = tk.Tk()
            temp_root.withdraw()  # 隐藏临时窗口

            response = messagebox.askquestion(
                "FFmpeg未安装", "需要安装FFmpeg才能使用本工具。是否查看安装指南？"
            )

            if response == "yes":
                dialog = installer.show_installation_dialog()
                temp_root.wait_window(dialog)  # 等待安装向导窗口关闭

                # 再次检查安装
                if not installer.check_ffmpeg():
                    if (
                        messagebox.askquestion(
                            "提示", "请安装完FFmpeg后再运行程序。是否退出程序？"
                        )
                        == "yes"
                    ):
                        temp_root.destroy()
                        sys.exit()
            else:
                temp_root.destroy()
                sys.exit()

            temp_root.destroy()

    def setup_ui(self):
        # 文件选择框
        self.file_frame = ttk.LabelFrame(self.root, text="选择文件")
        self.file_frame.pack(padx=10, pady=5, fill="x")

        # 添加拖放提示
        if SUPPORT_DND:
            ttk.Label(
                self.file_frame, text="可以直接拖放视频文件到此处", foreground="blue"
            ).pack(pady=5)

        self.files_list = tk.Listbox(self.file_frame, height=5)
        self.files_list.pack(padx=5, pady=5, fill="x")

        # 如果是macOS，为Listbox添加拖放支持
        if SUPPORT_DND == "macos":
            self.files_list.bind("<<MacDropFiles>>", self.handle_macos_drop)

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
        # 如果不支持拖放，添加提示
        if not SUPPORT_DND:
            ttk.Label(
                self.file_frame,
                text="注意：当前版本不支持拖放功能，请使用'选择视频'按钮",
                wraplength=300,
                foreground="red",
            ).pack(pady=5)

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

    # 修改 convert_video_to_gif 方法
    def convert_video_to_gif(self, video_path):
        try:
            ffmpeg_path = FFmpegInstaller.get_ffmpeg_path()
            if ffmpeg_path:
                # 设置FFmpeg路径
                ffmpeg.input.DEFAULT_FFMPEG_PATH = ffmpeg_path
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
            messagebox.showerror("错误", f"转换失败:\n{error_msg}")
            return False

    def start_conversion(self):
        def convert():
            files = self.files_list.get(0, tk.END)
            if not files:
                messagebox.showwarning("警告", "请先选择要转换的视频文件")
                return

            total = len(files)

            for i, file in enumerate(files):
                current = i + 1
                self.status_label.config(
                    text=f"正在转换: {os.path.basename(file)} ({current}/{total})"
                )
                success = self.convert_video_to_gif(file)
                progress = current / total * 100
                self.progress["value"] = progress

            self.status_label.config(text=f"转换完成 ({total}/{total})")
            self.convert_btn["state"] = "normal"
            messagebox.showinfo("完成", f"所有文件转换完成！\n成功转换 {total} 个文件")

        self.convert_btn["state"] = "disabled"
        self.progress["value"] = 0
        Thread(target=convert).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        print("程序启动...")
        # 先单独测试 FFmpeg
        installer = FFmpegInstaller()
        ffmpeg_installed = installer.check_ffmpeg()
        print(f"FFmpeg 检测结果: {ffmpeg_installed}")

        if not ffmpeg_installed:
            print("FFmpeg 未安装，将显示安装向导...")

        app = VideoToGifConverter()
        app.run()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback

        traceback.print_exc()  # 打印详细错误信息
        sys.exit(1)
