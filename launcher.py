import os
import sys
import traceback


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        # 运行在 PyInstaller 打包后的环境
        return os.path.join(sys._MEIPASS, "ffmpeg")
    else:
        # 运行在开发环境
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")


def setup_environment():
    try:
        # 设置 FFmpeg 路径
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

        print(f"FFmpeg path: {ffmpeg_path}")
        print(f"System PATH: {os.environ['PATH']}")
    except Exception as e:
        print(f"Error setting up environment: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        print("Starting Video2Gif Converter...")
        print(f"Python version: {sys.version}")

        setup_environment()

        from gui import VideoToGifConverter

        app = VideoToGifConverter()
        app.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()

        # 写入错误日志
        with open("error.log", "w") as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())

        # 如果是打包后的程序，等待用户确认
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")
        sys.exit(1)
