# -*- coding: utf-8 -*-
"""进度条和日志美化模块"""

import sys
import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ProgressInfo:
    """进度信息"""
    current: int = 0
    total: int = 0
    label: str = ""
    percentage: float = 0.0


class Colors:
    """终端颜色常量"""
    # 重置
    RESET = '\033[0m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'


class ProgressDisplay:
    """美观的进度显示器 - 线程安全版本"""
    
    def __init__(self):
        self.progress_bars: Dict[str, ProgressInfo] = {}
        self.log_lines = []
        self.max_log_history = 100  # 保存更多日志历史
        self.terminal_width = 80
        self.terminal_height = 24
        self.is_initialized = False
        self.lock = threading.RLock()  # 使用递归锁支持多线程
        try:
            import shutil
            size = shutil.get_terminal_size()
            self.terminal_width = size.columns
            self.terminal_height = size.lines
            # 确保最小尺寸
            self.terminal_width = max(80, self.terminal_width)
            self.terminal_height = max(20, self.terminal_height)
        except:
            pass
    
    def add_progress_bar(self, name: str, total: int, label: str = ""):
        """添加进度条 - 线程安全"""
        with self.lock:
            self.progress_bars[name] = ProgressInfo(0, total, label or name)
    
    def update_progress(self, name: str, current: int, additional_info: str = ""):
        """更新进度条 - 线程安全"""
        with self.lock:
            if name in self.progress_bars:
                bar = self.progress_bars[name]
                old_percentage = bar.percentage
                bar.current = current
                bar.percentage = (current / bar.total * 100) if bar.total > 0 else 0
                if additional_info:
                    bar.label = f"{name} - {additional_info}"
                
                # 只在进度有明显变化时刷新显示（避免过度刷新）
                if abs(bar.percentage - old_percentage) >= 1.0 or current == bar.total:
                    self._render_complete_ui()
    
    def increment_progress(self, name: str, additional_info: str = ""):
        """递增进度条 - 线程安全"""
        with self.lock:
            if name in self.progress_bars:
                bar = self.progress_bars[name]
                self.update_progress(name, bar.current + 1, additional_info)
    
    def remove_progress_bar(self, name: str):
        """移除进度条 - 线程安全"""
        with self.lock:
            if name in self.progress_bars:
                del self.progress_bars[name]
    
    def add_log(self, message: str, level: str = "INFO"):
        """添加日志消息 - 线程安全"""
        with self.lock:
            timestamp = time.strftime("%H:%M:%S")
            color = Colors.WHITE
            
            if level == "SUCCESS":
                color = Colors.BRIGHT_GREEN
            elif level == "WARNING":
                color = Colors.BRIGHT_YELLOW
            elif level == "ERROR":
                color = Colors.BRIGHT_RED
            elif level == "INFO":
                color = Colors.BRIGHT_CYAN
            elif level == "DEBUG":
                color = Colors.BRIGHT_BLACK
            
            # 截断过长的消息以防止换行
            max_message_length = self.terminal_width - 20  # 留出时间戳和标签的空间
            if len(message) > max_message_length:
                message = message[:max_message_length-3] + "..."
            
            formatted_msg = f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{level}]{Colors.RESET} {message}"
            self.log_lines.append(formatted_msg)
            
            # 保持日志行数在限制内
            if len(self.log_lines) > self.max_log_history:
                self.log_lines.pop(0)
            
            # 触发完整重新渲染
            self._render_complete_ui()
    
    def _draw_progress_bar(self, bar: ProgressInfo, width: int = 50) -> str:
        """绘制单个进度条"""
        filled = int(width * bar.percentage / 100)
        empty = width - filled
        
        # 进度条样式
        bar_filled = "█" * filled
        bar_empty = "░" * empty
        
        # 颜色选择
        if bar.percentage >= 100:
            bar_color = Colors.BRIGHT_GREEN
        elif bar.percentage >= 75:
            bar_color = Colors.GREEN
        elif bar.percentage >= 50:
            bar_color = Colors.YELLOW
        elif bar.percentage >= 25:
            bar_color = Colors.CYAN
        else:
            bar_color = Colors.RED
        
        percentage_str = f"{bar.percentage:5.1f}%"
        count_str = f"{bar.current}/{bar.total}"
        
        # 计算中文字符的实际显示宽度
        def get_display_width(text):
            """计算字符串的实际显示宽度（考虑中文字符）"""
            width = 0
            for char in text:
                if ord(char) > 127:  # 中文或其他宽字符
                    width += 2
                else:  # ASCII字符
                    width += 1
            return width
        
        # 使用固定显示宽度对齐标题
        label_display_width = 30  # 固定显示宽度
        current_width = get_display_width(bar.label)
        
        if current_width > label_display_width:
            # 标题太长，需要截断
            truncated_label = ""
            current_len = 0
            for char in bar.label:
                char_width = 2 if ord(char) > 127 else 1
                if current_len + char_width > label_display_width - 3:  # 留3位给...
                    truncated_label += "..."
                    break
                truncated_label += char
                current_len += char_width
            aligned_label = truncated_label
        else:
            # 标题合适，补充空格对齐
            padding = label_display_width - current_width
            aligned_label = bar.label + " " * padding
        
        return (f"{Colors.BOLD}{aligned_label}{Colors.RESET} "
                f"[{bar_color}{bar_filled}{Colors.BRIGHT_BLACK}{bar_empty}{Colors.RESET}] "
                f"{Colors.BRIGHT_WHITE}{percentage_str}{Colors.RESET} "
                f"{Colors.BRIGHT_BLACK}({count_str}){Colors.RESET}")
    
    def _calculate_layout(self):
        """计算布局：返回各部分的行数分配"""
        # 标题部分：2行（标题+分隔线）
        title_lines = 2
        
        # 进度条部分：每个进度条1行，加1行空白分隔
        progress_lines = len(self.progress_bars) + (1 if self.progress_bars else 0)
        
        # 日志头部：2行（标题+分隔线）
        log_header_lines = 2
        
        # 计算可用于日志内容的行数
        used_lines = title_lines + progress_lines + log_header_lines + 2  # 留2行底部边距
        available_log_lines = max(1, self.terminal_height - used_lines)
        
        return {
            'title_lines': title_lines,
            'progress_lines': progress_lines,
            'log_header_lines': log_header_lines,
            'available_log_lines': available_log_lines,
            'log_start_line': title_lines + progress_lines + 1
        }
    
    def _render_complete_ui(self):
        """完整重新渲染整个UI - 线程安全"""
        with self.lock:
            if not self.is_initialized:
                self.clear_screen()
                self.hide_cursor()
                self.is_initialized = True
            
            # 移动到顶部开始渲染
            self.move_cursor(1, 1)
            
            # 计算布局
            layout = self._calculate_layout()
            
            # 1. 渲染标题
            title = f"{Colors.BOLD}{Colors.BRIGHT_CYAN}🎵 Melodia 🎵{Colors.RESET}"
            print(f"\033[2K{title:^{self.terminal_width}}", flush=True)
            print(f"\033[2K{Colors.BRIGHT_BLACK}{'═' * self.terminal_width}{Colors.RESET}", flush=True)
            
            # 2. 渲染进度条
            if self.progress_bars:
                for name, bar in self.progress_bars.items():
                    progress_line = self._draw_progress_bar(bar, min(50, self.terminal_width // 2))
                    print(f"\033[2K{progress_line}", flush=True)
                print("\033[2K", flush=True)  # 空行分隔
            
            # 3. 渲染日志头部
            print(f"\033[2K{Colors.BOLD}{Colors.BRIGHT_WHITE}📝 实时日志{Colors.RESET}", flush=True)
            print(f"\033[2K{Colors.BRIGHT_BLACK}{'─' * self.terminal_width}{Colors.RESET}", flush=True)
            
            # 4. 渲染日志内容
            if self.log_lines:
                # 显示最新的日志，数量由可用空间决定
                display_count = min(len(self.log_lines), layout['available_log_lines'])
                display_logs = self.log_lines[-display_count:] if display_count > 0 else []
                
                for log_line in display_logs:
                    print(f"\033[2K{log_line}", flush=True)
            
            # 5. 清除剩余行到屏幕底部
            current_line = self.move_cursor_get_current()
            while current_line < self.terminal_height:
                print("\033[2K", flush=True)
                current_line += 1
            
            # 强制刷新输出
            sys.stdout.flush()
    
    def move_cursor_get_current(self):
        """获取当前光标行位置的辅助方法"""
        # 这是一个简化版本，实际中我们通过计算得出
        layout = self._calculate_layout()
        used_lines = 2 + layout['progress_lines'] + 2  # 标题+进度+日志头
        if self.log_lines:
            display_count = min(len(self.log_lines), layout['available_log_lines'])
            used_lines += display_count
        return used_lines + 1
    
    def clear_screen(self):
        """清除屏幕"""
        print("\033[2J\033[H", end="")
    
    def move_cursor(self, row: int, col: int = 1):
        """移动光标到指定位置"""
        print(f"\033[{row};{col}H", end="")
    
    def clear_from_cursor(self):
        """从光标位置清除到屏幕底部"""
        print("\033[0J", end="")
    
    def save_cursor_position(self):
        """保存光标位置"""
        print("\033[s", end="")
    
    def restore_cursor_position(self):
        """恢复光标位置"""
        print("\033[u", end="")
    
    def hide_cursor(self):
        """隐藏光标"""
        print("\033[?25l", end="")
    
    def show_cursor(self):
        """显示光标"""
        print("\033[?25h", end="")
    
    def display(self):
        """显示UI（兼容性方法）"""
        self._render_complete_ui()
    
    def display_initial(self):
        """首次显示"""
        self._render_complete_ui()
    
    def display_update(self):
        """更新显示"""
        self._render_complete_ui()
    
    def success(self, message: str):
        """成功消息"""
        self.add_log(f"✅ {message}", "SUCCESS")
    
    def warning(self, message: str):
        """警告消息"""
        self.add_log(f"⚠️ {message}", "WARNING")
    
    def error(self, message: str):
        """错误消息"""
        self.add_log(f"❌ {message}", "ERROR")
    
    def info(self, message: str):
        """信息消息"""
        self.add_log(f"ℹ️ {message}", "INFO")
    
    def debug(self, message: str):
        """调试消息"""
        self.add_log(f"🔍 {message}", "DEBUG")


# 全局进度显示器实例
progress_display = ProgressDisplay()
