#!/usr/bin/env python3
"""
KRenamer GUI - Korean Advanced file renaming with real-time preview
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
from datetime import datetime
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

try:
    from .core import RenameEngine
except ImportError:
    from core import RenameEngine


class RenamerGUI:
    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        
        self.engine = RenameEngine()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.setup_drag_drop()
        self.setup_bindings()
    
    def setup_window(self):
        self.root.title("KRenamer - Korean Advanced File Renaming Tool")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1000x600+{x}+{y}")
    
    def setup_variables(self):
        # Filter variables
        self.display_filter = tk.StringVar(value="모든 파일")
        self.custom_extension = tk.StringVar()
        
        # Basic rename variables
        self.basic_method = tk.StringVar(value="prefix")
        self.basic_text = tk.StringVar()
        self.basic_start_num = tk.StringVar(value="1")
        self.basic_find = tk.StringVar()
        self.basic_replace = tk.StringVar()
        
        # Pattern variables
        self.use_regex = tk.BooleanVar()
        self.pattern = tk.StringVar()
        self.replacement = tk.StringVar()
        
        # Conditional variables
        self.use_size_condition = tk.BooleanVar()
        self.size_operator = tk.StringVar(value=">")
        self.size_value = tk.StringVar(value="1")
        self.size_unit = tk.StringVar(value="MB")
        
        self.use_date_condition = tk.BooleanVar()
        self.date_operator = tk.StringVar(value="after")
        self.date_value = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        self.use_ext_condition = tk.BooleanVar()
        self.ext_list = tk.StringVar(value=".jpg,.png,.gif")
        
        # Batch variables
        self.case_method = tk.StringVar(value="none")
        self.remove_special = tk.BooleanVar()
        self.replace_space = tk.BooleanVar()
        self.handle_duplicate = tk.BooleanVar(value=True)
        
        # Status
        self.status_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.status_var.set("파일을 추가하고 이름 변경 조건을 설정하세요")
        self.count_var.set("파일 개수: 0")
    
    def setup_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 좌측: 파일 리스트 및 옵션
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 우측: 미리보기
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.setup_file_list_section(left_frame)
        self.setup_options_section(left_frame)
        self.setup_buttons_section(left_frame)
        self.setup_preview_section(right_frame)
        
        # 상태바
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 그리드 설정 - 반응형 레이아웃
        # 루트 윈도우 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 메인 프레임 설정 - 좌우 1:1 비율
        main_frame.columnconfigure(0, weight=1)  # 좌측 패널
        main_frame.columnconfigure(1, weight=1)  # 우측 패널
        main_frame.rowconfigure(0, weight=1)     # 주요 컨텐츠 영역
        
        # 좌측 프레임 내부 설정
        left_frame.rowconfigure(0, weight=0)     # 파일 리스트 (고정 높이)
        left_frame.rowconfigure(1, weight=1)     # 옵션 탭 (확장 가능)
        left_frame.rowconfigure(2, weight=0)     # 버튼 (고정 높이)
        left_frame.columnconfigure(0, weight=1)
        
        # 우측 프레임 설정
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
    
    def setup_file_list_section(self, parent):
        # 파일 목록 프레임
        files_frame = ttk.LabelFrame(parent, text="파일 목록", padding="5")
        files_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 파일 필터
        filter_frame = ttk.Frame(files_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(filter_frame, text="파일 필터:").pack(side=tk.LEFT)
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.display_filter, width=13)
        filter_combo['values'] = ('모든 파일', '이미지 파일', '문서 파일', '텍스트 파일', '사용자 정의')
        filter_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(filter_frame, text="확장자:").pack(side=tk.LEFT)
        custom_filter_entry = ttk.Entry(filter_frame, textvariable=self.custom_extension, width=10)
        custom_filter_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 파일 개수
        count_label = ttk.Label(filter_frame, textvariable=self.count_var)
        count_label.pack(side=tk.RIGHT)
        
        # 리스트박스 (드래그 앤 드롭 텍스트 제거, 리스트박스만 유지)
        listbox_frame = ttk.Frame(files_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.files_listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 그리드 설정
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
    
    def setup_options_section(self, parent):
        # 노트북 위젯으로 탭 구성
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 기본 이름 변경 탭
        self.setup_basic_tab()
        
        # 패턴 기반 탭
        self.setup_pattern_tab()
        
        # 조건부 변경 탭
        self.setup_conditional_tab()
        
        # 일괄 작업 탭
        self.setup_batch_tab()
    
    def setup_basic_tab(self):
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="기본 변경")
        
        # 기본 이름 변경 방식
        method_frame = ttk.Frame(basic_frame)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(method_frame, text="접두사", variable=self.basic_method, value="prefix", 
                       command=self.update_basic_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="접미사", variable=self.basic_method, value="suffix",
                       command=self.update_basic_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="순번", variable=self.basic_method, value="number",
                       command=self.update_basic_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="찾기/바꾸기", variable=self.basic_method, value="replace",
                       command=self.update_basic_fields).pack(side=tk.LEFT)
        
        # 입력 필드들 저장을 위한 딕셔너리
        self.basic_widgets = {}
        
        # 텍스트 필드 (접두사/접미사용)
        self.basic_widgets['text_label'] = ttk.Label(basic_frame, text="텍스트:")
        self.basic_widgets['text_label'].grid(row=1, column=0, sticky=tk.W, pady=2)
        self.basic_widgets['text_entry'] = ttk.Entry(basic_frame, textvariable=self.basic_text, width=30)
        self.basic_widgets['text_entry'].grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 시작 번호 필드 (순번용)
        self.basic_widgets['number_label'] = ttk.Label(basic_frame, text="시작 번호:")
        self.basic_widgets['number_label'].grid(row=2, column=0, sticky=tk.W, pady=2)
        self.basic_widgets['number_entry'] = ttk.Entry(basic_frame, textvariable=self.basic_start_num, width=10)
        self.basic_widgets['number_entry'].grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 찾을 텍스트 필드 (찾기/바꾸기용)
        self.basic_widgets['find_label'] = ttk.Label(basic_frame, text="찾을 텍스트:")
        self.basic_widgets['find_label'].grid(row=3, column=0, sticky=tk.W, pady=2)
        self.basic_widgets['find_entry'] = ttk.Entry(basic_frame, textvariable=self.basic_find, width=30)
        self.basic_widgets['find_entry'].grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 바꿀 텍스트 필드 (찾기/바꾸기용)
        self.basic_widgets['replace_label'] = ttk.Label(basic_frame, text="바꿀 텍스트:")
        self.basic_widgets['replace_label'].grid(row=4, column=0, sticky=tk.W, pady=2)
        self.basic_widgets['replace_entry'] = ttk.Entry(basic_frame, textvariable=self.basic_replace, width=30)
        self.basic_widgets['replace_entry'].grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        basic_frame.columnconfigure(1, weight=1)
        
        # 초기 필드 상태 설정
        self.update_basic_fields()
    
    def setup_pattern_tab(self):
        pattern_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(pattern_frame, text="패턴 기반")
        
        # 정규식 사용 여부
        ttk.Checkbutton(pattern_frame, text="정규식 사용", variable=self.use_regex).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 패턴 입력
        ttk.Label(pattern_frame, text="검색 패턴:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(pattern_frame, textvariable=self.pattern, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(pattern_frame, text="치환 패턴:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(pattern_frame, textvariable=self.replacement, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        pattern_frame.columnconfigure(1, weight=1)
    
    def setup_conditional_tab(self):
        conditional_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(conditional_frame, text="조건부 변경")
        
        # 파일 크기 조건
        size_frame = ttk.LabelFrame(conditional_frame, text="파일 크기 조건", padding="5")
        size_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(size_frame, text="파일 크기 조건 사용", variable=self.use_size_condition).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        ttk.Combobox(size_frame, textvariable=self.size_operator, values=["<", "<=", "=", ">=", ">"], width=5).grid(row=1, column=0, padx=(20, 5))
        ttk.Entry(size_frame, textvariable=self.size_value, width=10).grid(row=1, column=1, padx=5)
        ttk.Combobox(size_frame, textvariable=self.size_unit, values=["Bytes", "KB", "MB", "GB"], width=8).grid(row=1, column=2, padx=5)
        
        # 날짜 조건
        date_frame = ttk.LabelFrame(conditional_frame, text="수정 날짜 조건", padding="5")
        date_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(date_frame, text="수정 날짜 조건 사용", variable=self.use_date_condition).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(date_frame, text="이후", variable=self.date_operator, value="after").grid(row=1, column=0, padx=(20, 0), sticky=tk.W)
        ttk.Radiobutton(date_frame, text="이전", variable=self.date_operator, value="before").grid(row=1, column=1, sticky=tk.W)
        ttk.Entry(date_frame, textvariable=self.date_value, width=15).grid(row=2, column=0, columnspan=2, padx=(20, 0), sticky=tk.W)
        
        # 확장자 조건
        ext_frame = ttk.LabelFrame(conditional_frame, text="확장자 조건", padding="5")
        ext_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(ext_frame, text="특정 확장자만", variable=self.use_ext_condition).grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(ext_frame, textvariable=self.ext_list, width=30).grid(row=1, column=0, padx=(20, 0), sticky=(tk.W, tk.E))
        
        conditional_frame.columnconfigure(0, weight=1)
    
    def setup_batch_tab(self):
        batch_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(batch_frame, text="일괄 작업")
        
        # 대소문자 변환
        case_frame = ttk.LabelFrame(batch_frame, text="대소문자 변환", padding="5")
        case_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(case_frame, text="변경 안함", variable=self.case_method, value="none").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(case_frame, text="모두 대문자", variable=self.case_method, value="upper").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(case_frame, text="모두 소문자", variable=self.case_method, value="lower").grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(case_frame, text="첫글자만 대문자", variable=self.case_method, value="title").grid(row=1, column=0, sticky=tk.W)
        
        # 특수문자 처리
        special_frame = ttk.LabelFrame(batch_frame, text="특수문자 처리", padding="5")
        special_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(special_frame, text="특수문자 제거", variable=self.remove_special).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(special_frame, text="공백을 언더스코어로", variable=self.replace_space).grid(row=1, column=0, sticky=tk.W)
        
        # 중복 제거
        duplicate_frame = ttk.LabelFrame(batch_frame, text="중복 처리", padding="5")
        duplicate_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Checkbutton(duplicate_frame, text="중복 파일명에 번호 추가", variable=self.handle_duplicate).grid(row=0, column=0, sticky=tk.W)
        
        batch_frame.columnconfigure(0, weight=1)
    
    def setup_buttons_section(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=10)
        
        # 파일 관리 버튼
        ttk.Button(button_frame, text="파일 추가", command=self.add_files_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="선택 제거", command=self.remove_selected_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="모두 제거", command=self.clear_all_files).pack(side=tk.LEFT, padx=(0, 20))
        
        # 이름 변경 버튼
        ttk.Button(button_frame, text="실행", command=self.execute_rename).pack(side=tk.LEFT)
    
    def setup_preview_section(self, parent):
        # 미리보기 프레임
        preview_frame = ttk.LabelFrame(parent, text="실시간 미리보기", padding="5")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 트리뷰로 미리보기 표시
        columns = ("original", "new", "status")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="tree headings")
        
        self.preview_tree.heading("#0", text="순번")
        self.preview_tree.heading("original", text="원본 파일명")
        self.preview_tree.heading("new", text="새 파일명")
        self.preview_tree.heading("status", text="상태")
        
        # 컬럼 너비를 더 유연하게 설정
        self.preview_tree.column("#0", width=50, minwidth=50)
        self.preview_tree.column("original", width=200, minwidth=150)
        self.preview_tree.column("new", width=200, minwidth=150)
        self.preview_tree.column("status", width=80, minwidth=60)
        
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.config(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
    
    def setup_drag_drop(self):
        if DND_AVAILABLE:
            # 리스트박스에만 드래그 앤 드롭 등록
            self.files_listbox.drop_target_register(DND_FILES)
            self.files_listbox.dnd_bind('<<Drop>>', self.on_drop)
    
    def setup_bindings(self):
        # 실시간 미리보기를 위한 변수 바인딩
        variables_to_trace = [
            self.basic_method, self.basic_text, self.basic_start_num, 
            self.basic_find, self.basic_replace, self.use_regex, 
            self.pattern, self.replacement, self.use_size_condition,
            self.size_operator, self.size_value, self.size_unit,
            self.use_date_condition, self.date_operator, self.date_value,
            self.use_ext_condition, self.ext_list, self.case_method,
            self.remove_special, self.replace_space, self.handle_duplicate
        ]
        
        for var in variables_to_trace:
            var.trace('w', self.update_preview)
    
    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.add_files(files)
    
    def add_files_dialog(self):
        files = filedialog.askopenfilenames(title="파일 선택")
        if files:
            self.add_files(files)
    
    def add_files(self, file_paths):
        added_count = self.engine.add_files(file_paths)
        self.refresh_file_list()
        if added_count > 0:
            self.status_var.set(f"{added_count}개 파일이 추가되었습니다")
            self.update_preview()
    
    def remove_selected_files(self):
        selection = self.files_listbox.curselection()
        if selection:
            indices = list(selection)
            self.engine.remove_files_by_indices(indices)
            self.refresh_file_list()
            self.status_var.set(f"{len(selection)}개 파일이 제거되었습니다")
            self.update_preview()
    
    def clear_all_files(self):
        count = len(self.engine.files)
        self.engine.clear_files()
        self.refresh_file_list()
        self.status_var.set(f"모든 파일({count}개)이 제거되었습니다")
        self.update_preview()
    
    def update_basic_fields(self):
        """선택된 기본 변경 방식에 따라 관련 필드만 표시"""
        method = self.basic_method.get()
        
        # 모든 필드 초기화 (숨김)
        for widget in self.basic_widgets.values():
            widget.grid_remove()
        
        # 선택된 방식에 따라 해당 필드만 표시
        if method == "prefix":
            # 접두사: 텍스트 필드만 표시
            self.basic_widgets['text_label'].grid()
            self.basic_widgets['text_entry'].grid()
            self.basic_widgets['text_label'].config(text="접두사 텍스트:")
            
        elif method == "suffix":
            # 접미사: 텍스트 필드만 표시
            self.basic_widgets['text_label'].grid()
            self.basic_widgets['text_entry'].grid()
            self.basic_widgets['text_label'].config(text="접미사 텍스트:")
            
        elif method == "number":
            # 순번: 시작 번호 필드만 표시
            self.basic_widgets['number_label'].grid()
            self.basic_widgets['number_entry'].grid()
            
        elif method == "replace":
            # 찾기/바꾸기: 찾을 텍스트와 바꿀 텍스트 필드 표시
            self.basic_widgets['find_label'].grid()
            self.basic_widgets['find_entry'].grid()
            self.basic_widgets['replace_label'].grid()
            self.basic_widgets['replace_entry'].grid()
        
        # 필드 변경 후 미리보기 업데이트 (preview_tree가 있는 경우에만)
        if hasattr(self, 'preview_tree'):
            self.update_preview()
    
    def refresh_file_list(self):
        """파일 리스트 새로고침"""
        self.files_listbox.delete(0, tk.END)
        
        for file_path in self.engine.files:
            file_name = os.path.basename(file_path)
            self.files_listbox.insert(tk.END, file_name)
        
        self.count_var.set(f"파일 개수: {len(self.engine.files)}")
    
    def update_preview(self, *args):
        """실시간 미리보기 업데이트"""
        # preview_tree가 아직 생성되지 않은 경우 리턴
        if not hasattr(self, 'preview_tree'):
            return
            
        # 기존 미리보기 항목 제거
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        if not self.engine.files:
            return
        
        # Engine에 현재 설정 적용
        self.apply_settings_to_engine()
        
        # 미리보기 생성
        rename_plan = self.engine.generate_rename_plan()
        
        for i, (original_path, new_name, matches) in enumerate(rename_plan):
            original_name = os.path.basename(original_path)
            status = "변경" if matches else "제외"
            
            # 색상 구분
            tags = ("change",) if matches else ("skip",)
            
            self.preview_tree.insert("", tk.END, text=str(i+1), 
                                   values=(original_name, new_name if matches else "", status),
                                   tags=tags)
        
        # 트리뷰 태그 설정
        self.preview_tree.tag_configure("change", foreground="blue")
        self.preview_tree.tag_configure("skip", foreground="gray")
    
    def apply_settings_to_engine(self):
        """GUI 설정을 엔진에 적용"""
        # 기본 설정
        self.engine.method = self.basic_method.get()
        self.engine.prefix_text = self.basic_text.get()
        self.engine.suffix_text = self.basic_text.get()
        self.engine.start_number = int(self.basic_start_num.get()) if self.basic_start_num.get().isdigit() else 1
        self.engine.find_text = self.basic_find.get()
        self.engine.replace_text = self.basic_replace.get()
        
        # 패턴 설정
        self.engine.use_regex = self.use_regex.get()
        self.engine.pattern = self.pattern.get()
        self.engine.replacement = self.replacement.get()
        
        # 조건 설정
        self.engine.use_size_condition = self.use_size_condition.get()
        self.engine.size_operator = self.size_operator.get()
        self.engine.size_value = float(self.size_value.get()) if self.size_value.get().replace('.', '').isdigit() else 1.0
        self.engine.size_unit = self.size_unit.get()
        
        self.engine.use_date_condition = self.use_date_condition.get()
        self.engine.date_operator = self.date_operator.get()
        self.engine.date_value = self.date_value.get()
        
        self.engine.use_ext_condition = self.use_ext_condition.get()
        self.engine.allowed_extensions = self.ext_list.get()
        
        # 배치 설정
        self.engine.case_method = self.case_method.get()
        self.engine.remove_special_chars = self.remove_special.get()
        self.engine.replace_spaces = self.replace_space.get()
        self.engine.handle_duplicates = self.handle_duplicate.get()
    
    def execute_rename(self):
        """이름 변경 실행"""
        if not self.engine.files:
            self.status_var.set("변경할 파일이 없습니다")
            return
        
        self.apply_settings_to_engine()
        rename_plan = self.engine.generate_rename_plan()
        
        # 실제 변경될 파일 수 계산
        change_count = sum(1 for _, _, matches in rename_plan if matches)
        
        if change_count == 0:
            self.status_var.set("조건에 맞는 파일이 없습니다")
            return
        
        if not messagebox.askyesno("확인", f"{change_count}개 파일의 이름을 변경하시겠습니까?"):
            return
        
        # 실행
        success_count, errors = self.engine.execute_rename()
        
        # 결과 처리
        if errors:
            error_msg = f"{success_count}개 파일 변경 완료.\n오류:\n" + "\n".join(errors[:3])
            if len(errors) > 3:
                error_msg += f"\n... 외 {len(errors)-3}개"
            messagebox.showwarning("완료", error_msg)
        else:
            messagebox.showinfo("완료", f"{success_count}개 파일의 이름이 변경되었습니다")
        
        self.status_var.set(f"변경 완료: {success_count}개 성공, {len(errors)}개 오류")
        
        # 파일 리스트 새로고침 (경로가 변경되었을 수 있으므로)
        self.refresh_file_list()
        self.update_preview()
    
    def run(self):
        self.root.mainloop()