from setuptools import setup, find_packages

setup(
    name="video-to-gif-converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ffmpeg-python>=0.2.0",
        "Pillow>=9.0.0",
    ],
    extras_require={
        'gui': [
            'ttkthemes>=3.2.0',
            'ttkwidgets>=0.12.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
    },
    python_requires='>=3.7',
    
    # 元数据
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple video to GIF converter with GUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="video, gif, converter, ffmpeg, gui",
    url="https://github.com/yourusername/video-to-gif-converter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
