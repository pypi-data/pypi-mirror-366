# -*- coding: utf-8 -*-
"""多线程管理模块"""

import threading
import time
import uuid
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Callable, Any, Dict, Tuple
from queue import Queue
from ..config import config
from ..utils.logger import logger


class ThreadSafeProgress:
    """线程安全的进度管理器"""
    
    def __init__(self, progress_display):
        self.progress_display = progress_display
        self.lock = threading.Lock()
        self.thread_progresses: Dict[str, dict] = {}
    
    def add_thread_progress(self, thread_id: str, total: int, description: str = ""):
        """添加线程进度条"""
        with self.lock:
            self.thread_progresses[thread_id] = {
                'current': 0,
                'total': total,
                'description': description
            }
            self.progress_display.add_progress_bar(thread_id, total, description)
    
    def update_thread_progress(self, thread_id: str, current: int, description: str = ""):
        """更新线程进度"""
        with self.lock:
            if thread_id in self.thread_progresses:
                self.thread_progresses[thread_id]['current'] = current
                if description:
                    self.thread_progresses[thread_id]['description'] = description
                self.progress_display.update_progress(thread_id, current, description)
    
    def remove_thread_progress(self, thread_id: str):
        """移除线程进度条"""
        with self.lock:
            if thread_id in self.thread_progresses:
                del self.thread_progresses[thread_id]
                self.progress_display.remove_progress_bar(thread_id)
    
    def log_message(self, message: str, level: str = "INFO"):
        """线程安全的日志输出"""
        with self.lock:
            if level == "SUCCESS":
                self.progress_display.success(message)
            elif level == "WARNING":
                self.progress_display.warning(message)
            elif level == "ERROR":
                self.progress_display.error(message)
            elif level == "DEBUG":
                self.progress_display.debug(message)
            else:
                self.progress_display.info(message)


class TemporaryFileManager:
    """临时文件管理器"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or config.temp_dir
        self._ensure_temp_dir()
        self.lock = threading.Lock()
    
    def _ensure_temp_dir(self):
        """确保临时目录存在"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_temp_file_path(self, music_id: str, thread_id: Optional[str] = None) -> str:
        """获取临时文件路径"""
        if thread_id is None:
            thread_id = str(uuid.uuid4())[:8]
        temp_filename = f"{music_id}_{thread_id}_{int(time.time())}.mp3"
        return os.path.join(self.temp_dir, temp_filename)
    
    def cleanup_temp_file(self, temp_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")


class DownloadTask:
    """下载任务类"""
    
    def __init__(self, music_id: str, priority: int = 0):
        self.music_id = music_id
        self.priority = priority
        self.created_time = time.time()
        
    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.priority < other.priority


class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers: Optional[int] = None, progress_display=None):
        self.max_workers = max_workers or config.thread_count
        self.progress_display = progress_display
        self.thread_safe_progress = ThreadSafeProgress(progress_display) if progress_display else None
        self.temp_manager = TemporaryFileManager()
        self.active_tasks: Dict[str, Any] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.lock = threading.Lock()
        
    def execute_downloads(self, music_ids: List[str], download_func: Callable,
                         batch_name: str = "下载任务") -> Tuple[int, int, int]:
        """执行批量下载任务"""
        if not config.threading_enabled or self.max_workers == 1:
            # 单线程模式
            return self._execute_single_thread(music_ids, download_func, batch_name)
        else:
            # 多线程模式
            return self._execute_multi_thread(music_ids, download_func, batch_name)
    
    def _execute_single_thread(self, music_ids: List[str], download_func: Callable,
                              batch_name: str) -> Tuple[int, int, int]:
        """单线程执行"""
        downloaded = 0
        skipped = 0
        failed = 0
        
        if self.thread_safe_progress:
            self.thread_safe_progress.add_thread_progress(
                "single_thread", len(music_ids), f"{batch_name} (单线程)")
        
        for i, music_id in enumerate(music_ids):
            try:
                if self.thread_safe_progress:
                    self.thread_safe_progress.update_thread_progress(
                        "single_thread", i + 1, f"处理 {i+1}/{len(music_ids)}")
                
                result = download_func(music_id, "single_thread")
                
                if result == "downloaded":
                    downloaded += 1
                elif result == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    
            except Exception as e:
                if self.thread_safe_progress:
                    self.thread_safe_progress.log_message(f"单线程下载出错 {music_id}: {e}", "ERROR")
                failed += 1
        
        if self.thread_safe_progress:
            self.thread_safe_progress.remove_thread_progress("single_thread")
        
        return downloaded, skipped, failed
    
    def _execute_multi_thread(self, music_ids: List[str], download_func: Callable,
                             batch_name: str) -> Tuple[int, int, int]:
        """多线程执行"""
        downloaded = 0
        skipped = 0
        failed = 0
        
        # 添加总体进度条
        if self.thread_safe_progress:
            self.thread_safe_progress.add_thread_progress(
                "songs", len(music_ids), f"{batch_name} 总进度")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_music_id = {}
            
            for music_id in music_ids:
                thread_id = str(uuid.uuid4())[:8]
                future = executor.submit(self._download_with_thread_id, 
                                       download_func, music_id, thread_id)
                future_to_music_id[future] = music_id
            
            # 收集结果
            completed_count = 0
            for future in as_completed(future_to_music_id):
                music_id = future_to_music_id[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    
                    if result == "downloaded":
                        downloaded += 1
                    elif result == "skipped":
                        skipped += 1
                    else:
                        failed += 1
                        
                    # 更新总进度
                    if self.thread_safe_progress:
                        self.thread_safe_progress.update_thread_progress(
                            "songs", completed_count, 
                            f"已完成 {completed_count}/{len(music_ids)}")
                        
                except Exception as e:
                    if self.thread_safe_progress:
                        self.thread_safe_progress.log_message(
                            f"多线程下载出错 {music_id}: {e}", "ERROR")
                    failed += 1
        
        # 移除总进度条
        if self.thread_safe_progress:
            self.thread_safe_progress.remove_thread_progress("songs")
        
        return downloaded, skipped, failed
    
    def _download_with_thread_id(self, download_func: Callable, music_id: str, thread_id: str):
        """带线程ID的下载包装函数"""
        try:
            return download_func(music_id, thread_id)
        except Exception as e:
            if self.thread_safe_progress:
                self.thread_safe_progress.log_message(
                    f"线程 {thread_id} 下载 {music_id} 失败: {e}", "ERROR")
            return "failed"
    
    def get_temp_file_path(self, music_id: str, thread_id: Optional[str] = None) -> str:
        """获取临时文件路径"""
        return self.temp_manager.get_temp_file_path(music_id, thread_id)
    
    def cleanup_temp_file(self, temp_path: str):
        """清理临时文件"""
        self.temp_manager.cleanup_temp_file(temp_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return {
                'max_workers': self.max_workers,
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'threading_enabled': config.threading_enabled
            }


# 全局线程池管理器实例
thread_manager = None

def get_thread_manager(progress_display=None) -> ThreadPoolManager:
    """获取全局线程管理器实例"""
    global thread_manager
    if thread_manager is None:
        thread_manager = ThreadPoolManager(progress_display=progress_display)
    return thread_manager