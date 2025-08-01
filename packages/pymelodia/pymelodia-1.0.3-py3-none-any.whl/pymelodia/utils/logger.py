# -*- coding: utf-8 -*-
"""日志记录器模块"""

from typing import Optional, Any


class Logger:
    """统一的日志记录器"""
    
    def __init__(self):
        self.progress_display: Optional[Any] = None
        self.fallback_enabled = True
    
    def set_progress_display(self, progress_display: Any):
        """设置进度显示器"""
        self.progress_display = progress_display
    
    def info(self, message: str):
        """信息日志"""
        if self.progress_display:
            self.progress_display.info(message)
        elif self.fallback_enabled:
            print(f"[INFO] {message}")
    
    def success(self, message: str):
        """成功日志"""
        if self.progress_display:
            self.progress_display.success(message)
        elif self.fallback_enabled:
            print(f"[SUCCESS] {message}")
    
    def warning(self, message: str):
        """警告日志"""
        if self.progress_display:
            self.progress_display.warning(message)
        elif self.fallback_enabled:
            print(f"[WARNING] {message}")
    
    def error(self, message: str):
        """错误日志"""
        if self.progress_display:
            self.progress_display.error(message)
        elif self.fallback_enabled:
            print(f"[ERROR] {message}")
    
    def debug(self, message: str):
        """调试日志"""
        if self.progress_display:
            self.progress_display.debug(message)
        elif self.fallback_enabled:
            print(f"[DEBUG] {message}")
    
    def disable_fallback(self):
        """禁用fallback模式（不输出到控制台）"""
        self.fallback_enabled = False
    
    def enable_fallback(self):
        """启用fallback模式"""
        self.fallback_enabled = True


# 全局日志记录器实例
logger = Logger()
