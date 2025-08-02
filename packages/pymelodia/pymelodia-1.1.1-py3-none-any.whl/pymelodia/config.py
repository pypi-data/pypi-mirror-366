# -*- coding: utf-8 -*-
"""配置管理模块"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class Config:
    """配置管理类 - 支持配置文件、环境变量和命令行参数"""
    
    # 默认配置
    DEFAULT_SAVE_PATH = "./music/"
    DEFAULT_TEMP_PATH = "./temp.mp3"
    DEFAULT_TEMP_DIR = "./temp/"
    DEFAULT_MUSIC_CLASS = "全部"
    DEFAULT_DELAY = 0
    DEFAULT_COOKIE = ""
    DEFAULT_MAX_PAGES = 20
    DEFAULT_HASHED_STORAGE_ENABLED = False
    DEFAULT_HASHED_STORAGE_DIGIT = 2
    DEFAULT_THREADING_ENABLED = True
    DEFAULT_THREAD_COUNT = 4
    
    # 配置文件路径
    CONFIG_DIR = Path.home() / ".melodia"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    # 音乐分类列表（从generate_sh.py移植）
    MUSIC_CATEGORIES = [
        "全部",
        
        # 语言分类
        "华语", "欧美", "日语", "韩语", "粤语",

        # 风格分类
        "流行", "摇滚", "民谣", "电子", "舞曲", "说唱", "轻音乐", "爵士", "乡村", 
        "R&B/Soul", "古典", "民族", "英伦", "金属", "朋克", "蓝调", "雷鬼", 
        "世界音乐", "拉丁", "New Age", "古风", "后摇", "Bossa Nova",
        
        # 场景分类
        "清晨", "夜晚", "学习", "工作", "午休", "下午茶", "地铁", "驾车", 
        "运动", "旅行", "散步", "酒吧",
        
        # 情感分类
        "怀旧", "清新", "浪漫", "伤感", "治愈", "放松", "孤独", "感动", 
        "兴奋", "快乐", "安静", "思念",
        
        # 主题分类
        "综艺", "影视原声", "ACG", "儿童", "校园", "游戏", "70后", "80后", 
        "90后", "网络歌曲", "KTV", "经典", "翻唱", "吉他", "钢琴", "器乐", 
        "榜单", "00后"
    ]
    
    def __init__(self):
        """初始化配置 - 按优先级加载：命令行参数 > 环境变量 > 配置文件 > 默认值"""
        # 1. 从默认值开始
        self._load_defaults()
        
        # 2. 加载配置文件
        self._load_config_file()
        
        # 3. 加载环境变量（覆盖配置文件）
        self._load_environment()
        
        # 命令行参数在运行时通过 update_from_args() 方法设置
    
    def _load_defaults(self):
        """加载默认配置"""
        self.save_path = self.DEFAULT_SAVE_PATH
        self.temp_path = self.DEFAULT_TEMP_PATH
        self.temp_dir = self.DEFAULT_TEMP_DIR
        self.music_class = self.DEFAULT_MUSIC_CLASS
        self.delay = self.DEFAULT_DELAY
        self.cookie = self.DEFAULT_COOKIE
        self.max_pages = self.DEFAULT_MAX_PAGES
        self.hashed_storage_enabled = self.DEFAULT_HASHED_STORAGE_ENABLED
        self.hashed_storage_digit = self.DEFAULT_HASHED_STORAGE_DIGIT
        self.threading_enabled = self.DEFAULT_THREADING_ENABLED
        self.thread_count = self.DEFAULT_THREAD_COUNT
    
    def _load_config_file(self):
        """从配置文件加载配置"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 安全地更新配置
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                        
            except (json.JSONDecodeError, OSError) as e:
                print(f"警告: 配置文件加载失败 {self.CONFIG_FILE}: {e}")
    
    def _load_environment(self):
        """从环境变量加载配置"""
        env_mapping = {
            'MD_SAVE_PATH': ('save_path', str),
            'MD_TEMP_PATH': ('temp_path', str),
            'MD_TEMP_DIR': ('temp_dir', str),
            'MD_CLASS': ('music_class', str),
            'MD_DELAY': ('delay', int),
            'MD_COOKIE': ('cookie', str),
            'MD_MAX_PAGES': ('max_pages', int),
            'MD_HASHED_STORAGE': ('hashed_storage_enabled', lambda x: x.lower() == 'true'),
            'MD_HASHED_STORAGE_DIGIT': ('hashed_storage_digit', int),
            'MD_THREADING_ENABLED': ('threading_enabled', lambda x: x.lower() == 'true'),
            'MD_THREAD_COUNT': ('thread_count', int),
        }
        
        for env_var, (attr_name, converter) in env_mapping.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    setattr(self, attr_name, converter(env_value))
                except (ValueError, TypeError) as e:
                    print(f"警告: 环境变量 {env_var} 转换失败: {e}")
    
    def save_config_file(self):
        """保存当前配置到配置文件"""
        # 确保配置目录存在
        self.CONFIG_DIR.mkdir(exist_ok=True)
        
        config_data = {
            'save_path': self.save_path,
            'delay': self.delay,
            'max_pages': self.max_pages,
            'cookie': self.cookie,
            'music_class': self.music_class,
            'temp_path': self.temp_path,
            'temp_dir': self.temp_dir,
            'hashed_storage_enabled': self.hashed_storage_enabled,
            'hashed_storage_digit': self.hashed_storage_digit,
            'threading_enabled': self.threading_enabled,
            'thread_count': self.thread_count
        }
        
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {self.CONFIG_FILE}")
        except OSError as e:
            print(f"警告: 配置文件保存失败: {e}")
    
    def update_from_args(self, **kwargs):
        """从命令行参数更新配置（最高优先级）"""
        updated = False
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
                updated = True
        
        # 如果有更新且配置文件不存在，创建一个
        if updated and not self.CONFIG_FILE.exists():
            self.save_config_file()
    
    def update(self, **kwargs):
        """更新配置（保持向后兼容）"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取当前配置信息"""
        return {
            '配置文件路径': str(self.CONFIG_FILE),
            '配置文件存在': self.CONFIG_FILE.exists(),
            '当前配置': self.to_dict(),
            '环境变量': {
                'MD_SAVE_PATH': os.environ.get('MD_SAVE_PATH'),
                'MD_TEMP_PATH': os.environ.get('MD_TEMP_PATH'),
                'MD_TEMP_DIR': os.environ.get('MD_TEMP_DIR'),
                'MD_CLASS': os.environ.get('MD_CLASS'),
                'MD_DELAY': os.environ.get('MD_DELAY'),
                'MD_COOKIE': os.environ.get('MD_COOKIE'),
                'MD_MAX_PAGES': os.environ.get('MD_MAX_PAGES'),
                'MD_HASHED_STORAGE': os.environ.get('MD_HASHED_STORAGE'),
                'MD_HASHED_STORAGE_DIGIT': os.environ.get('MD_HASHED_STORAGE_DIGIT'),
                'MD_THREADING_ENABLED': os.environ.get('MD_THREADING_ENABLED'),
                'MD_THREAD_COUNT': os.environ.get('MD_THREAD_COUNT'),
            }
        }
    
    def get_all_categories(self) -> List[str]:
        """获取所有音乐分类"""
        return self.MUSIC_CATEGORIES.copy()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'save_path': self.save_path,
            'temp_path': self.temp_path,
            'temp_dir': self.temp_dir,
            'music_class': self.music_class,
            'delay': self.delay,
            'cookie': self.cookie,
            'max_pages': self.max_pages,
            'hashed_storage_enabled': self.hashed_storage_enabled,
            'hashed_storage_digit': self.hashed_storage_digit,
            'threading_enabled': self.threading_enabled,
            'thread_count': self.thread_count
        }


# 全局配置实例
config = Config()
