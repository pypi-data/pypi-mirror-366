#!/usr/bin/env python3
"""
KRenamer - Korean Advanced File Renaming Tool
Main application entry point
"""

import sys
import tkinter as tk
from tkinter import messagebox

try:
    from .gui import RenamerGUI
except ImportError:
    # 직접 실행되는 경우
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gui import RenamerGUI


def main():
    """메인 함수"""
    try:
        app = RenamerGUI()
        app.run()
    except Exception as e:
        # GUI 초기화 실패 시 에러 메시지 표시
        root = tk.Tk()
        root.withdraw()  # 메인 창 숨기기
        messagebox.showerror(
            "오류", 
            f"애플리케이션을 시작할 수 없습니다:\n{str(e)}\n\n"
            "tkinterdnd2 패키지가 설치되어 있는지 확인하세요.\n"
            "설치 명령: pip install tkinterdnd2"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()