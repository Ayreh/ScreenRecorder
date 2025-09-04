#!/usr/bin/env python3
"""
PyInstaller build script for Gaming Screen Recorder
This script bundles FFmpeg (from ffmpeg/bin) with the executable
"""

import PyInstaller.__main__
import os
import sys
import shutil


def build_exe():
    """Build the executable with bundled FFmpeg (from ffmpeg/bin)"""

    # 检查 ffmpeg.exe 是否存在（路径：ffmpeg/bin/ffmpeg.exe）
    ffmpeg_path = os.path.join('ffmpeg', 'bin', 'ffmpeg.exe')
    if not os.path.exists(ffmpeg_path):
        print("❌ Error: ffmpeg.exe not found!")
        print("请确认 FFmpeg 的 bin 文件夹已放入项目的 ffmpeg 目录中")
        print("正确路径应为：ffmpeg/bin/ffmpeg.exe")
        print("下载 FFmpeg: https://www.gyan.dev/ffmpeg/builds/")
        return False

    print("✅ Found ffmpeg.exe")
    print(f"📁 FFmpeg 路径: {os.path.abspath(ffmpeg_path)}")

    # PyInstaller 参数（关键调整：--add-data=ffmpeg/bin;ffmpeg/bin）
    args = [
        'fps_screen_recorder.py',  # 主脚本名称
        '--onefile',  # 生成单个 EXE
        '--windowed',  # 无控制台窗口
        '--name=GamingScreenRecorder',  # 生成的 EXE 名称
        '--add-data=ffmpeg/bin;ffmpeg/bin',  # 打包 ffmpeg/bin 下的所有文件
        #'--icon=icon.ico',  # 可选：添加图标（如果有）
        '--clean',  # 清理缓存
        '--noconfirm',  # 不提示确认
        # pynput 的隐藏导入
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
        # 排除不必要的大模块以减小体积
        '--exclude-module=matplotlib',
        '--exclude-module=numpy.distutils',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
    ]

    print("🔨 正在构建可执行文件...")
    print("这可能需要几分钟...")

    # 运行 PyInstaller
    PyInstaller.__main__.run(args)

    # 检查构建是否成功
    exe_path = os.path.join('dist', 'GamingScreenRecorder.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # 转换为 MB
        print(f"✅ 构建成功!")
        print(f"📦 可执行文件: {exe_path}")
        print(f"📏 大小: {file_size:.1f} MB")

        # 创建简单的安装包文件夹
        installer_dir = 'installer'
        if os.path.exists(installer_dir):
            shutil.rmtree(installer_dir)
        os.makedirs(installer_dir)

        # 复制 EXE 到安装包文件夹
        shutil.copy2(exe_path, installer_dir)

        # 创建简单的 README
        readme_content = """# Gaming Screen Recorder

## 使用方法:
1. 运行 GamingScreenRecorder.exe
2. 选择保存目录
3. 选择录制设置（帧率和画质）
4. 点击 "开始录制"
5. 按 F10 停止录制

## 输出文件:
- screen_recording_YYYYMMDD_HHMMSS.mp4（视频）
- input_log_YYYYMMDD_HHMMSS.jsonl（鼠标/键盘事件）

## 功能:
- 使用内置 FFmpeg 进行高质量屏幕录制
- 鼠标移动追踪（适合 FPS 游戏）
- 键盘事件记录
- 无外部依赖

## 系统要求:
- Windows 10/11
- 建议至少 4GB 内存
- 足够的磁盘空间用于录制

如需支持或反馈问题，请联系开发者。
"""

        with open(os.path.join(installer_dir, 'README.txt'), 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"📁 安装包已创建: {installer_dir}/")
        print("📝 已创建 README.txt（含使用说明）")

    else:
        print("❌ 构建失败!")
        return False

    return True


if __name__ == "__main__":
    print("🚀 Gaming Screen Recorder - 构建脚本")
    print("=" * 50)

    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller

        print("✅ PyInstaller 已找到")
    except ImportError:
        print("❌ PyInstaller 未找到。请用以下命令安装: pip install pyinstaller")
        sys.exit(1)

    # 执行构建
    success = build_exe()

    if success:
        print("\n🎉 构建成功完成!")
        print("可执行文件已准备好分发。")
    else:
        print("\n💥 构建失败!")
        sys.exit(1)