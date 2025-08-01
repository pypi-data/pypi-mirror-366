# -*- coding: utf-8 -*-
"""音乐下载服务层"""

import time
from typing import List, Optional, Tuple, Any
from ..api.netease_api import NeteaseMusicAPI
from ..storage.database import MusicDatabase
from ..processors.file_processor import AudioFileProcessor
from ..config import config
from ..utils.logger import logger


class MusicDownloadService:
    """音乐下载服务"""
    
    def __init__(self, cookie: Optional[str] = None, save_path: Optional[str] = None, 
                 music_class: Optional[str] = None, delay: Optional[int] = None,
                 hashed_storage_enabled: Optional[bool] = None, hashed_storage_digit: Optional[int] = None):
        """初始化下载服务"""
        self.cookie = cookie or config.cookie
        self.save_path = save_path or config.save_path
        self.music_class = music_class or config.music_class
        self.delay = delay or config.delay
        self.hashed_storage_enabled = hashed_storage_enabled or config.hashed_storage_enabled
        self.hashed_storage_digit = hashed_storage_digit or config.hashed_storage_digit
        
        # 更新全局配置
        config.update(
            cookie=self.cookie,
            save_path=self.save_path,
            music_class=self.music_class,
            delay=self.delay
        )
        
        # 初始化各个组件
        self.api = NeteaseMusicAPI(self.cookie)
        self.database = MusicDatabase()
        self.file_processor = AudioFileProcessor(self.save_path, self.hashed_storage_enabled, self.hashed_storage_digit)
        self.progress_display: Optional[Any] = None

    def set_progress_display(self, progress_display: Any):
        """设置进度显示器"""
        self.progress_display = progress_display
        # 同时设置全局logger
        logger.set_progress_display(progress_display)

    def download_single_music(self, music_id: str) -> bool:
        """下载单个音乐"""
        try:
            if self.progress_display:
                self.progress_display.info(f'开始下载音乐 ID: {music_id}')
            else:
                print(f'开始下载音乐 ID: {music_id}')
            
            # 检查是否已存在
            if self.database.music_exists(music_id):
                if self.progress_display:
                    self.progress_display.warning(f'音乐 {music_id} 已存在，跳过下载')
                else:
                    print(f'音乐 {music_id} 已存在，跳过下载')
                return True
            
            # 获取歌曲信息
            subtitle, artist, album, title = self.api.get_song_info(music_id)
            if title is None:
                if self.progress_display:
                    self.progress_display.error(f'歌曲不可用 [ID: {music_id}]')
                else:
                    print(f'歌曲不可用 [ID: {music_id}]')
                return False
            
            logger.debug(f'获取到歌曲信息: {title} - {artist}')
            
            # 获取下载链接
            download_url = self.api.get_download_url(music_id)
            if not download_url:
                logger.warning(f'无法获取下载链接 [ID: {music_id}]')
                return False
            
            # 下载歌曲内容
            logger.info(f'正在下载: {title}')
            content = self.api.download_song_content(download_url)
            if not content:
                logger.error(f'下载失败 [ID: {music_id}]')
                return False
            
            # 保存临时文件
            temp_path = "./temp.mp3"
            if not self.file_processor.save_temp_file(content, temp_path):
                return False
            
            # 获取歌词和封面
            lyric = self.api.get_song_lyric(music_id)
            album_cover = self.api.get_album_cover(music_id)
            
            # 设置音频元数据
            if not self.file_processor.set_audio_metadata(
                None, music_id, title, subtitle or "", artist or "", album or "", 
                lyric, album_cover, self.music_class):
                logger.error(f'设置元数据失败 [ID: {music_id}]')
                return False
            
            # 移动到最终位置
            if not self.file_processor.move_temp_to_final(None, music_id):
                return False
            
            # 添加到数据库
            if not self.database.add_single_music(
                music_id, title, subtitle or "", artist or "", album or "", lyric or ""):
                logger.error(f'添加到数据库失败 [ID: {music_id}]')
                return False
            
            logger.success(f'成功下载: {title}')
            if self.delay:
                logger.info(f'等待 {self.delay} 秒后继续...')
                time.sleep(self.delay)  # 等待指定延时
            return True
            
        except Exception as e:
            logger.error(f'下载音乐 {music_id} 时出错: {e}')
            return False

    def download_music_list(self, music_ids: List[str]) -> Tuple[int, int, int]:
        """批量下载音乐列表"""
        logger.info(f'开始批量下载 {len(music_ids)} 首歌曲')
        
        downloaded_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i, music_id in enumerate(music_ids):
            try:
                # 更新列表进度条
                if self.progress_display:
                    self.progress_display.update_progress('歌曲列表', i + 1, f'处理第 {i+1}/{len(music_ids)} 首')
                
                logger.debug(f'进度: {i+1}/{len(music_ids)} ({(i+1)*100/len(music_ids):.1f}%)')
                
                # 检查是否已存在
                if self.database.music_exists(music_id):
                    logger.debug(f'歌曲 {music_id} 已存在，跳过')
                    skipped_count += 1
                    continue
                
                # 下载歌曲
                if self.download_single_music(music_id):
                    downloaded_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f'处理ID {music_id} 时出错: {e}')
                failed_count += 1
                continue
        
        # 完成后移除列表进度条
        if self.progress_display:
            self.progress_display.remove_progress_bar('歌曲列表')
        
        logger.success(f'批量下载完成！成功: {downloaded_count}, 跳过: {skipped_count}, 失败: {failed_count}')
        return downloaded_count, skipped_count, failed_count

    def download_playlist(self, playlist_id: str) -> bool:
        """下载指定歌单"""
        try:
            if self.progress_display:
                self.progress_display.info(f'开始下载歌单 ID: {playlist_id}')
            else:
                print(f'开始下载歌单 ID: {playlist_id}')
            
            # 获取歌单中的歌曲
            songs = self.api.get_playlist_songs(playlist_id)
            if not songs:
                if self.progress_display:
                    self.progress_display.warning('无法获取歌单信息或歌单为空')
                else:
                    print('无法获取歌单信息或歌单为空')
                return False
            
            if self.progress_display:
                self.progress_display.info(f'歌单共有 {len(songs)} 首歌曲')
                # 添加歌单内歌曲进度条
                self.progress_display.add_progress_bar("songs", len(songs), f"歌曲进度 - 歌单{playlist_id}")
            else:
                print(f'歌单共有 {len(songs)} 首歌曲')
            
            # 提取歌曲ID列表并逐个下载
            downloaded = 0
            skipped = 0
            failed = 0
            
            for i, song in enumerate(songs):
                try:
                    if self.progress_display:
                        self.progress_display.update_progress("songs", i, f"歌曲 {i+1}")
                        self.progress_display.display_update()
                    
                    # 安全获取href属性
                    href = ""
                    if hasattr(song, 'get'):
                        href = str(song.get('href', ''))
                    elif hasattr(song, 'attrs') and song.attrs:
                        href = str(song.attrs.get('href', ''))
                    
                    if href and '=' in href:
                        music_id = href.split('=')[1]
                        
                        # 检查是否已存在
                        if self.database.music_exists(music_id):
                            skipped += 1
                            continue
                        
                        # 下载歌曲
                        if self.download_single_music(music_id):
                            downloaded += 1
                        else:
                            failed += 1
                    
                except (AttributeError, IndexError) as e:
                    if self.progress_display:
                        self.progress_display.warning(f'解析歌曲链接失败: {e}')
                    failed += 1
                    continue
            
            # 完成歌曲进度条
            if self.progress_display:
                self.progress_display.update_progress("songs", len(songs), "歌单完成")
                self.progress_display.remove_progress_bar("songs")
                self.progress_display.success(f'歌单下载完成！总计: {len(songs)}, 成功: {downloaded}, 跳过: {skipped}, 失败: {failed}')
            else:
                print(f'歌单下载完成！总计: {len(songs)}, 成功: {downloaded}, 跳过: {skipped}, 失败: {failed}')
            return True
            
        except Exception as e:
            logger.error(f'下载歌单失败: {e}')
            return False

    def download_playlist_list(self, playlist_ids: List[str]) -> bool:
        """批量下载歌单列表"""
        logger.info(f'开始批量下载 {len(playlist_ids)} 个歌单')
        
        for i, playlist_id in enumerate(playlist_ids):
            try:
                # 更新歌单列表进度条
                if self.progress_display:
                    self.progress_display.update_progress('歌单列表', i + 1, f'处理第 {i+1}/{len(playlist_ids)} 个歌单')
                
                logger.debug(f'进度: {i+1}/{len(playlist_ids)} - 处理歌单 {playlist_id}')
                self.download_playlist(playlist_id)
            except Exception as e:
                logger.error(f'下载歌单 {playlist_id} 时出错: {e}')
                continue
        
        # 完成后移除歌单列表进度条
        if self.progress_display:
            self.progress_display.remove_progress_bar('歌单列表')
        
        logger.success('所有歌单下载任务完成！')
        return True

    def download_category_music(self, category: Optional[str] = None, max_pages: int = 20) -> bool:
        """下载指定分类的音乐"""
        if category:
            self.music_class = category
        
        if self.progress_display:
            self.progress_display.info(f'开始下载分类 "{self.music_class}" 的音乐')
            # 添加页面进度条
            self.progress_display.add_progress_bar("pages", max_pages, f"页面进度 - {self.music_class}")
        else:
            print(f'开始下载分类 "{self.music_class}" 的音乐')
        
        try:
            page = 0
            while page < max_pages:
                if self.progress_display:
                    self.progress_display.update_progress("pages", page, f"第 {page + 1} 页")
                    self.progress_display.info(f'正在处理第 {page + 1} 页...')
                    self.progress_display.display_update()
                else:
                    print(f'正在处理第 {page + 1} 页...')
                
                # 获取歌单列表
                playlists = self.api.get_playlist_list(self.music_class, page)
                if not playlists:
                    if self.progress_display:
                        self.progress_display.warning(f'第 {page + 1} 页无数据，结束下载')
                    else:
                        print(f'第 {page + 1} 页无数据，结束下载')
                    break
                
                # 添加歌单进度条
                if self.progress_display:
                    self.progress_display.add_progress_bar("playlists", len(playlists), f"歌单进度 - 第{page + 1}页")
                
                # 处理每个歌单
                for j, playlist in enumerate(playlists):
                    try:
                        if self.progress_display:
                            self.progress_display.update_progress("playlists", j, f"歌单 {j+1}")
                            self.progress_display.display_update()
                        
                        # 安全获取href属性
                        href = ""
                        if hasattr(playlist, 'get'):
                            href = str(playlist.get('href', ''))
                        elif hasattr(playlist, 'attrs') and playlist.attrs:
                            href = str(playlist.attrs.get('href', ''))
                        
                        if href and '=' in href:
                            playlist_id = href.split('=')[1]
                            if self.progress_display:
                                self.progress_display.debug(f'处理歌单 {j+1}/{len(playlists)}: {playlist_id}')
                            else:
                                print(f'处理歌单 {j+1}/{len(playlists)}: {playlist_id}')
                            self.download_playlist(playlist_id)
                    except (AttributeError, IndexError) as e:
                        if self.progress_display:
                            self.progress_display.warning(f'解析歌单链接失败: {e}')
                        continue
                
                # 完成当前页面的歌单进度条
                if self.progress_display:
                    self.progress_display.update_progress("playlists", len(playlists), "页面完成")
                    self.progress_display.remove_progress_bar("playlists")
                    self.progress_display.success(f'第 {page + 1} 页处理完成')
                else:
                    print(f'第 {page + 1} 页处理完成')
                
                page += 1
            
            # 完成页面进度条
            if self.progress_display:
                self.progress_display.update_progress("pages", max_pages, "类别完成")
                self.progress_display.remove_progress_bar("pages")
                self.progress_display.success(f'分类 "{self.music_class}" 下载完成')
            else:
                print(f'分类 "{self.music_class}" 下载完成')
            return True
            
        except Exception as e:
            if self.progress_display:
                self.progress_display.error(f'下载分类音乐失败: {e}')
            else:
                print(f'下载分类音乐失败: {e}')
            return False

    def get_download_links(self, music_ids: List[str]):
        """获取歌曲下载链接"""
        print(f'获取 {len(music_ids)} 个歌曲的下载链接')
        
        for i, music_id in enumerate(music_ids):
            try:
                print(f'\n--- {i+1}/{len(music_ids)} ---')
                print(f'音乐ID: {music_id}')
                
                download_url = self.api.get_download_url(music_id)
                print(f'下载链接: {download_url}')
                
            except Exception as e:
                print(f'获取ID {music_id} 的链接时出错: {e}')
                continue
        
        print('所有链接获取完成！')

    def download_all_categories(self, max_pages_per_category: Optional[int] = None) -> bool:
        """下载所有分类的音乐"""
        max_pages = max_pages_per_category or config.max_pages
        categories = config.get_all_categories()  
        
        if self.progress_display:
            self.progress_display.info(f'开始下载所有分类的音乐，共 {len(categories)} 个分类')
            # 添加类别进度条
            self.progress_display.add_progress_bar("categories", len(categories), "类别进度")
        else:
            print(f'开始下载所有分类的音乐，共 {len(categories)} 个分类')
            print(f'分类列表: {", ".join(categories)}')
        
        successful_categories = 0
        failed_categories = 0
        
        for i, category in enumerate(categories):
            try:
                if self.progress_display:
                    self.progress_display.update_progress("categories", i, f"正在下载: {category}")
                    self.progress_display.info(f'开始下载分类: {category} ({i+1}/{len(categories)})')
                    self.progress_display.display_update()
                else:
                    print(f'\n{"="*60}')
                    print(f'进度: {i+1}/{len(categories)} - 开始下载分类: {category}')
                    print(f'{"="*60}')
                
                # 更新当前分类
                original_class = self.music_class
                self.music_class = category
                config.update(music_class=category)
                
                # 下载该分类的音乐
                if self.download_category_music(category, max_pages):
                    successful_categories += 1
                    if self.progress_display:
                        self.progress_display.success(f'分类 "{category}" 下载完成')
                    else:
                        print(f'分类 "{category}" 下载完成')
                else:
                    failed_categories += 1
                    if self.progress_display:
                        self.progress_display.error(f'分类 "{category}" 下载失败')
                    else:
                        print(f'分类 "{category}" 下载失败')
                
                # 恢复原始分类
                self.music_class = original_class
                
            except Exception as e:
                if self.progress_display:
                    self.progress_display.error(f'下载分类 "{category}" 时出错: {e}')
                else:
                    print(f'下载分类 "{category}" 时出错: {e}')
                failed_categories += 1
                continue
        
        # 完成类别进度条
        if self.progress_display:
            self.progress_display.update_progress("categories", len(categories), "全部完成")
            self.progress_display.success(f'所有分类下载任务完成！成功: {successful_categories}，失败: {failed_categories}')
            self.progress_display.display_update()
        else:
            print(f'\n{"="*60}')
            print(f'所有分类下载任务完成！')
            print(f'成功: {successful_categories} 个分类')
            print(f'失败: {failed_categories} 个分类')
            print(f'总计: {len(categories)} 个分类')
            print(f'{"="*60}')
        
        return True

    def close(self):
        """关闭资源"""
        self.database.close()
