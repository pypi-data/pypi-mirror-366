# -*- coding: utf-8 -*-
"""文件处理和音频标签管理模块"""

import os
import eyed3
from typing import Optional
from ..config import config
from ..utils.logger import logger


class AudioFileProcessor:
    """音频文件处理器"""
    
    def __init__(self, save_path: Optional[str] = None,
                 hashed_storage_enabled: Optional[bool] = None, 
                 hashed_storage_digit: Optional[int] = None):
        """初始化文件处理器"""
        self.save_path = save_path or config.save_path
        self.hashed_storage_enabled = hashed_storage_enabled or config.hashed_storage_enabled
        self.hashed_storage_digit = hashed_storage_digit or config.hashed_storage_digit
        self._ensure_save_path_exists()

    def _ensure_save_path_exists(self):
        """确保保存路径存在"""
        if not self.save_path.endswith('/'):
            self.save_path += '/'
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def get_file_path(self, music_id: str) -> str:
        """获取音乐文件的完整路径"""
        if self.hashed_storage_enabled:
            # 如果启用哈希存储，使用音乐ID每一位创建目录
            digit = self.hashed_storage_digit
            if digit < 1 or digit > len(music_id):
                digit = len(music_id)
            hashed_dir = os.path.join(self.save_path, *music_id[:digit])
            os.makedirs(hashed_dir, exist_ok=True)
            return os.path.join(hashed_dir, f"{music_id}.mp3")
        else:
            return os.path.join(self.save_path, f"{music_id}.mp3")

    def save_temp_file(self, content: bytes, temp_path: Optional[str] = None) -> bool:
        """保存临时文件"""
        temp_path = temp_path or config.temp_path
        try:
            # 确保临时文件目录存在
            temp_dir = os.path.dirname(temp_path)
            if temp_dir and not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f'保存临时文件失败: {e}')
            return False

    def set_audio_metadata(self, temp_path: Optional[str], music_id: str, title: str, 
                          subtitle: str, artist: str, album: str, 
                          lyric: Optional[str] = None, album_cover: Optional[bytes] = None,
                          genre: Optional[str] = None) -> bool:
        """为音频文件设置元数据"""
        temp_path = temp_path or config.temp_path
        genre = genre or config.music_class
        
        try:
            audiofile = eyed3.load(temp_path)
            if audiofile is None:
                logger.error(f'无法加载音频文件: {music_id} - {title}')
                return False
            
            # 确保tag存在
            if audiofile.tag is None:
                audiofile.initTag()
            
            # 设置基本信息
            audiofile.tag.title = title + (subtitle or "")
            audiofile.tag.artist = artist
            audiofile.tag.album = album
            audiofile.tag.album_artist = artist
            
            # 写入歌词
            if lyric and lyric != "null":
                try:
                    # 使用USLT帧写入歌词
                    from eyed3.id3.frames import UserTextFrame
                    audiofile.tag.lyrics.set(lyric)
                    logger.debug(f'已为 {title} 写入歌词到ID3标签')
                except Exception as lyric_error:
                    logger.warning(f'写入歌词失败: {lyric_error}')
            
            # 写入专辑封面
            if album_cover and isinstance(album_cover, bytes):
                try:
                    audiofile.tag.images.set(3, album_cover, 'image/jpeg', u'Cover')
                    logger.debug(f'已为 {title} 写入专辑封面到ID3标签')
                except Exception as img_error:
                    logger.warning(f'写入专辑封面失败: {img_error}')
            
            # 添加注释
            try:
                audiofile.tag.comments.set(genre, description="Genre")
            except Exception as comment_error:
                logger.warning(f'写入注释失败: {comment_error}')
            
            # 保存标签
            audiofile.tag.save(encoding='utf-8')
            logger.debug(f'已为 {title} 完成ID3标签写入')
            return True
            
        except Exception as e:
            logger.error(f'设置音频元数据失败: {e}')
            return False

    def move_temp_to_final(self, temp_path: Optional[str], music_id: str) -> bool:
        """将临时文件移动到最终位置"""
        temp_path = temp_path or config.temp_path
        try:
            final_path = self.get_file_path(music_id)
            
            # 确保目标目录存在
            final_dir = os.path.dirname(final_path)
            if final_dir and not os.path.exists(final_dir):
                os.makedirs(final_dir, exist_ok=True)
            
            with open(final_path, 'wb') as f:
                with open(temp_path, 'rb') as temp_f:
                    f.write(temp_f.read())
            
            # 删除临时文件
            self.cleanup_temp_file(temp_path)
            
            final_path = final_path.replace('\\', '/')
            logger.debug(f'文件已保存到: {final_path}')
            return True
            
        except Exception as e:
            logger.error(f'移动文件失败: {e}')
            return False
    
    def cleanup_temp_file(self, temp_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.debug(f'临时文件已删除: {temp_path}')
        except Exception as e:
            logger.warning(f'删除临时文件失败: {e}')

    def file_exists(self, music_id: str) -> bool:
        """检查文件是否存在（使用数据库检查）"""
        from ..storage.database import MusicDatabase
        db = MusicDatabase()
        exists = db.music_exists(music_id)
        db.close()
        return exists


class MusicRemoveDuplicates:
    """音乐去重处理器"""
    
    def __init__(self):
        self.processed_data = []

    def init_remove_repeat(self, scan_path: str):
        """初始化去重处理"""
        if not scan_path.endswith('/'):
            scan_path += '/'
            
        try:
            files = os.listdir(scan_path)
            total_files = len(files)
            logger.info('开始音乐去重扫描...')
            
            processed_count = 0
            last_percent = -1
            message = ""
            
            for file_name in files:
                try:
                    current_percent = int(processed_count * 1000 / total_files)
                    if current_percent != last_percent:
                        progress = round(processed_count * 100 / total_files, 3)
                        logger.info(f'\n正在扫描音乐文件... {progress}% 已完成')
                        last_percent = current_percent
                    
                    file_path = os.path.join(scan_path, file_name)
                    
                    # 只处理mp3文件且不是目录
                    if not os.path.isdir(file_path) and file_name.endswith('.mp3'):
                        audiofile = eyed3.load(file_path)
                        
                        if not audiofile or not audiofile.tag:
                            # 删除无效文件
                            self._remove_file_and_lyric(file_path)
                            message += f'删除: {file_name} (无效文件)\n'
                            continue
                        
                        # 检查是否重复
                        song_info = [audiofile.tag.title, audiofile.tag.artist]
                        if song_info in self.processed_data:
                            self._remove_file_and_lyric(file_path)
                            message += f'删除: {audiofile.tag.title} (重复)\n'
                        else:
                            self.processed_data.append(song_info)
                    
                    processed_count += 1
                    
                except Exception as e:
                    message += f'处理文件 {file_name} 时出错: {e}\n'
                    processed_count += 1
            
            logger.info('音乐去重处理完成')
            if message:
                logger.info(f'处理详情:\n{message}')

        except Exception as e:
            logger.error(f'去重处理失败: {e}')

    def _remove_file_and_lyric(self, file_path: str):
        """删除音乐文件及其对应的歌词文件"""
        try:
            # 删除歌词文件
            lyric_path = file_path.replace('.mp3', '.lrc')
            if os.path.exists(lyric_path):
                os.remove(lyric_path)
            
            # 删除音乐文件
            os.remove(file_path)
            
        except Exception as e:
            logger.error(f'删除文件失败: {e}')

    def detect_repeat(self, title: str, artist: str) -> bool:
        """检测是否重复"""
        return [title, artist] in self.processed_data
