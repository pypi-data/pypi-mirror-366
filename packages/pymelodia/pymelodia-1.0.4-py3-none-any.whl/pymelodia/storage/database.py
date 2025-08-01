# -*- coding: utf-8 -*-
"""数据库管理模块"""

import sqlite3
import os
from typing import Optional, Tuple
from ..utils.logger import logger
from pathlib import Path

class MusicDatabase:
    """音乐数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接"""
        if db_path is None:
            # 确保data目录存在
            DATA_DIR = Path.home() / ".melodia"
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            db_path = os.path.join(DATA_DIR, 'data.db')
        
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建数据库表"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS musicBasicData (
            id INTEGER PRIMARY KEY,
            title TEXT,
            subtitle TEXT,
            artist TEXT,
            album TEXT,
            lyric TEXT
        )
        ''')
        self.connection.commit()

    def music_exists(self, music_id: str) -> bool:
        """检查音乐是否存在"""
        self.cursor.execute('SELECT * FROM musicBasicData WHERE id = ?', (music_id,))
        return self.cursor.fetchone() is not None

    def detect_repeat_by_nsa(self, name: str, subtitle: str, artist: str) -> bool:
        """通过名称、副标题、艺术家检测重复"""
        self.cursor.execute(
            'SELECT * FROM musicBasicData WHERE subtitle = ? AND title = ? AND artist = ?', 
            (subtitle, name, artist)
        )
        return self.cursor.fetchone() is not None

    def add_single_music(self, music_id: str, name: str, subtitle: str, 
                        artist: str, album: str, lyric: str) -> bool:
        """添加单个音乐记录"""
        try:
            self.cursor.execute('''
                INSERT INTO musicBasicData(id, title, subtitle, artist, album, lyric) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (music_id, name, subtitle, artist, album, lyric))
            self.connection.commit()
            logger.debug(f'音乐 {name} 已添加到数据库')
            return True
        except Exception as e:
            logger.error(f'添加音乐到数据库失败: {e}')
            return False

    def get_single_music_by_id(self, music_id: str) -> Optional[Tuple]:
        """通过ID获取单个音乐记录"""
        self.cursor.execute('SELECT * FROM musicBasicData WHERE id = ?', (str(music_id),))
        return self.cursor.fetchone()

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
