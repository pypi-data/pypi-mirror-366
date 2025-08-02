# -*- coding: utf-8 -*-
"""音乐下载服务层"""

import os
import time
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
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
                 hashed_storage_enabled: Optional[bool] = None, hashed_storage_digit: Optional[int] = None,
                 temp_path: Optional[str] = None):
        """初始化下载服务"""
        self.cookie = cookie or config.cookie
        self.save_path = save_path or config.save_path
        self.music_class = music_class or config.music_class
        self.delay = delay or config.delay
        self.temp_path = temp_path or config.temp_path
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
        
        # 多线程相关
        self._progress_lock = threading.Lock()
        self._thread_local = threading.local()

    def set_progress_display(self, progress_display: Any):
        """设置进度显示器"""
        self.progress_display = progress_display
        # 同时设置全局logger
        logger.set_progress_display(progress_display)

    def _get_thread_api(self):
        """获取线程本地的API实例"""
        if not hasattr(self._thread_local, 'api'):
            # 为每个线程创建独立的API实例
            self._thread_local.api = NeteaseMusicAPI(self.cookie)
        return self._thread_local.api

    def _get_thread_database(self):
        """获取线程本地的数据库实例"""
        if not hasattr(self._thread_local, 'database'):
            # 为每个线程创建独立的数据库连接
            from ..storage.database import MusicDatabase
            self._thread_local.database = MusicDatabase()
        return self._thread_local.database

    def _generate_temp_filename(self, music_id: str) -> str:
        """生成线程安全的临时文件名"""
        thread_id = threading.current_thread().ident or 0
        unique_id = str(uuid.uuid4())[:8]
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        return f"{self.temp_path}/temp_{thread_id}_{unique_id}_{music_id}.mp3"

    def download_single_music(self, music_id: str, use_thread_api: bool = False) -> bool:
        """下载单个音乐
        
        Args:
            music_id: 音乐ID
            use_thread_api: 是否使用线程本地API实例（多线程调用时使用）
        """
        try:
            # 根据是否多线程调用选择API和数据库实例
            api = self._get_thread_api() if use_thread_api else self.api
            database = self._get_thread_database() if use_thread_api else self.database

            logger.info(f'开始下载音乐 ID: {music_id}')

            # 检查是否已存在
            if database.music_exists(music_id):
                logger.warning(f'音乐 {music_id} 已存在，跳过下载')
                return True
            
            # 获取歌曲信息
            subtitle, artist, album, title = api.get_song_info(music_id)
            if title is None:
                logger.error(f'歌曲不可用 [ID: {music_id}]')
                return False
            
            if not use_thread_api:
                logger.debug(f'获取到歌曲信息: {title} - {artist}')
            
            # 获取下载链接
            download_url = api.get_download_url(music_id)
            if not download_url:
                if not use_thread_api:
                    logger.warning(f'无法获取下载链接 [ID: {music_id}]')
                return False
            
            # 下载歌曲内容
            logger.info(f'正在下载: {title}')
            content = api.download_song_content(download_url)
            if not content:
                logger.error(f'下载失败 [ID: {music_id}]')
                return False
            
            # 生成线程安全的临时文件名
            temp_path = self._generate_temp_filename(music_id) if use_thread_api else None
            if not self.file_processor.save_temp_file(content, temp_path):
                return False
            
            # 获取歌词和封面
            lyric = api.get_song_lyric(music_id)
            album_cover = api.get_album_cover(music_id)
            
            # 设置音频元数据
            if not self.file_processor.set_audio_metadata(
                temp_path, music_id, title, str(subtitle or ""), str(artist or ""), str(album or ""), 
                lyric, album_cover, self.music_class):
                logger.error(f'设置元数据失败 [ID: {music_id}]')
                return False
            
            # 移动到最终位置
            if not self.file_processor.move_temp_to_final(temp_path, music_id):
                return False
            
            # 添加到数据库
            if not database.add_single_music(
                music_id, title, str(subtitle or ""), str(artist or ""), str(album or ""), lyric or ""):
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

    def download_music_list_parallel(self, music_ids: List[str]) -> Tuple[int, int, int]:
        """并行批量下载音乐列表（多线程版本）"""
        if not config.enable_multithreading:
            return self.download_music_list(music_ids)
        
        logger.info(f'开始并行下载 {len(music_ids)} 首歌曲，使用 {config.max_threads} 个线程')
        
        downloaded_count = 0
        skipped_count = 0
        failed_count = 0
        
        # 线程安全的统计计数器
        stats_lock = threading.Lock()
        
        def download_task(music_id: str) -> str:
            """单个下载任务"""
            nonlocal downloaded_count, skipped_count, failed_count
            
            try:
                # 使用线程本地的数据库检查是否已存在
                thread_database = self._get_thread_database()
                if thread_database.music_exists(music_id):
                    with stats_lock:
                        skipped_count += 1
                    return f"skipped_{music_id}"
                
                # 使用线程本地API下载
                if self.download_single_music(music_id, use_thread_api=True):
                    with stats_lock:
                        downloaded_count += 1
                    return f"success_{music_id}"
                else:
                    with stats_lock:
                        failed_count += 1
                    return f"failed_{music_id}"
                    
            except Exception as e:
                with stats_lock:
                    failed_count += 1
                logger.error(f'下载任务 {music_id} 异常: {e}')
                return f"error_{music_id}"
        
        # 使用线程池并行下载，支持键盘中断
        completed = 0
        total = len(music_ids)
        
        try:
            with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
                # 提交所有任务
                future_to_id = {executor.submit(download_task, music_id): music_id for music_id in music_ids}
                
                # 使用循环处理完成的任务，支持键盘中断
                while future_to_id:
                    try:
                        # 短超时循环，使得可以响应KeyboardInterrupt
                        for future in as_completed(future_to_id, timeout=0.5):
                            music_id = future_to_id.pop(future)
                            completed += 1
                            
                            try:
                                result = future.result()
                                logger.debug(f'任务完成 ({completed}/{total}): {result}')
                                
                                # 实时更新进度条
                                if self.progress_display:
                                    with self._progress_lock:
                                        self.progress_display.update_progress(
                                            'songs', 
                                            completed
                                        )
                                        self.progress_display.display_update()
                                
                            except Exception as exc:
                                logger.error(f'任务 {music_id} 产生异常: {exc}')
                                
                    except TimeoutError:
                        continue
                        
        except KeyboardInterrupt:
            logger.warning(f'用户中断下载，已完成 {completed}/{total} 个任务')
            # 立即返回，不执行后续代码
            if self.progress_display:
                self.progress_display.remove_progress_bar('songs')
            return downloaded_count, skipped_count, failed_count
        except Exception as e:
            logger.error(f'并行下载过程中出错: {e}')
            return downloaded_count, skipped_count, failed_count
        
        logger.success(f'并行下载完成！成功: {downloaded_count}, 跳过: {skipped_count}, 失败: {failed_count}')
        return downloaded_count, skipped_count, failed_count

    def download_playlist(self, playlist_id: str) -> bool:
        """下载指定歌单"""
        try:
            logger.info(f'开始下载歌单 ID: {playlist_id}')
            
            # 获取歌单中的歌曲
            songs = self.api.get_playlist_songs(playlist_id)
            if not songs:
                logger.warning('无法获取歌单信息或歌单为空')
                return False

            logger.info(f'歌单共有 {len(songs)} 首歌曲')
            # 添加歌单内歌曲进度条
            self.progress_display.add_progress_bar("songs", len(songs), f"歌曲进度 - 歌单{playlist_id}")

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
                        logger.warning(f'解析歌曲链接失败: {e}')
                    failed += 1
                    continue
            
            # 完成歌曲进度条
            self.progress_display.update_progress("songs", len(songs), "歌单完成")
            self.progress_display.remove_progress_bar("songs")
            logger.success(f'歌单下载完成！总计: {len(songs)}, 成功: {downloaded}, 跳过: {skipped}, 失败: {failed}')
            return True
            
        except Exception as e:
            logger.error(f'下载歌单失败: {e}')
            return False

    def download_playlist_parallel(self, playlist_id: str) -> bool:
        """并行下载指定歌单（多线程版本）"""
        if not config.enable_multithreading:
            return self.download_playlist(playlist_id)
        
        try:
            logger.info(f'开始并行下载歌单 ID: {playlist_id}')
            
            # 获取歌单中的歌曲
            songs = self.api.get_playlist_songs(playlist_id)
            if not songs:
                logger.warning('无法获取歌单信息或歌单为空')
                return False
            
            # 提取歌曲ID列表
            music_ids = []
            for song in songs:
                try:
                    # 安全获取href属性
                    href = ""
                    if hasattr(song, 'get'):
                        href = str(song.get('href', ''))
                    elif hasattr(song, 'attrs') and song.attrs:
                        href = str(song.attrs.get('href', ''))
                    
                    if href and '=' in href:
                        music_id = href.split('=')[1]
                        music_ids.append(music_id)
                        
                except (AttributeError, IndexError):
                    continue
            
            if not music_ids:
                logger.warning('歌单中没有有效的歌曲')
                return False
            
            logger.info(f'歌单共有 {len(music_ids)} 首歌曲，使用 {config.max_threads} 个线程并行下载')
            
            logger.info(f'歌单共有 {len(music_ids)} 首歌曲，使用 {config.max_threads} 个线程并行下载')
            # 添加歌单内歌曲进度条
            self.progress_display.add_progress_bar("songs", len(music_ids), f"并行下载 - 歌单{playlist_id}")
            
            # 使用已有的并行下载方法
            downloaded, skipped, failed = self.download_music_list_parallel(music_ids)
            
            # 完成歌曲进度条
            self.progress_display.update_progress("songs", len(music_ids), "歌单完成")
            self.progress_display.remove_progress_bar("songs")
            logger.success(
                f'歌单并行下载完成！总计: {len(music_ids)}, 成功: {downloaded}, 跳过: {skipped}, 失败: {failed}'
            )
            
            return True
            
        except Exception as e:
            logger.error(f'并行下载歌单失败: {e}')
            return False

    def download_playlist_list(self, playlist_ids: List[str]) -> bool:
        """批量下载歌单列表"""
        logger.info(f'开始批量下载 {len(playlist_ids)} 个歌单')
        
        for i, playlist_id in enumerate(playlist_ids):
            try:
                # 更新歌单列表进度条
                self.progress_display.update_progress('歌单列表', i + 1, f'处理第 {i+1}/{len(playlist_ids)} 个歌单')
                
                logger.debug(f'进度: {i+1}/{len(playlist_ids)} - 处理歌单 {playlist_id}')
                self.download_playlist(playlist_id)
            except Exception as e:
                logger.error(f'下载歌单 {playlist_id} 时出错: {e}')
                continue
        
        # 完成后移除歌单列表进度条
        self.progress_display.remove_progress_bar('歌单列表')
        
        logger.success('所有歌单下载任务完成！')
        return True

    def download_category_music(self, category: Optional[str] = None, max_pages: int = 20) -> bool:
        """下载指定分类的音乐"""
        if category:
            self.music_class = category
        
        logger.info(f'开始下载分类 "{self.music_class}" 的音乐')
        # 添加页面进度条
        self.progress_display.add_progress_bar("pages", max_pages, f"页面进度 - {self.music_class}")
        
        try:
            page = 0
            while page < max_pages:
                self.progress_display.update_progress("pages", page, f"第 {page + 1} 页")
                logger.info(f'正在处理第 {page + 1} 页...')
                self.progress_display.display_update()
                
                # 获取歌单列表
                playlists = self.api.get_playlist_list(self.music_class, page)
                if not playlists:
                    logger.warning(f'第 {page + 1} 页无数据，结束下载')
                    break
                
                # 添加歌单进度条
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
                            logger.debug(f'处理歌单 {j+1}/{len(playlists)}: {playlist_id}')
                            self.download_playlist_parallel(playlist_id)
                    except (AttributeError, IndexError) as e:
                        if self.progress_display:
                            logger.warning(f'解析歌单链接失败: {e}')
                        continue
                
                # 完成当前页面的歌单进度条
                if self.progress_display:
                    self.progress_display.update_progress("playlists", len(playlists), "页面完成")
                    self.progress_display.remove_progress_bar("playlists")
                logger.success(f'第 {page + 1} 页处理完成')
                
                page += 1
            
            # 完成页面进度条
            if self.progress_display:
                self.progress_display.update_progress("pages", max_pages, "类别完成")
                self.progress_display.remove_progress_bar("pages")
            logger.success(f'分类 "{self.music_class}" 下载完成')
            return True
            
        except Exception as e:
            logger.error(f'下载分类音乐失败: {e}')
            return False

    def get_download_links(self, music_ids: List[str]):
        """获取歌曲下载链接"""
        
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
        
        logger.info(f'开始下载所有分类的音乐，共 {len(categories)} 个分类')
        logger.info(f'分类列表: {", ".join(categories)}')
        if self.progress_display:
            # 添加类别进度条
            self.progress_display.add_progress_bar("categories", len(categories), "类别进度")
        
        successful_categories = 0
        failed_categories = 0
        
        for i, category in enumerate(categories):
            try:
                if self.progress_display:
                    self.progress_display.update_progress("categories", i, f"正在下载: {category}")
                    self.progress_display.display_update()
                logger.info(f'开始下载分类: {category} ({i+1}/{len(categories)})')
                
                # 更新当前分类
                original_class = self.music_class
                self.music_class = category
                config.update(music_class=category)
                
                # 下载该分类的音乐
                if self.download_category_music(category, max_pages):
                    successful_categories += 1
                    logger.success(f'分类 "{category}" 下载完成')
                else:
                    failed_categories += 1
                    logger.error(f'分类 "{category}" 下载失败')
                
                # 恢复原始分类
                self.music_class = original_class
                
            except Exception as e:
                logger.error(f'下载分类 "{category}" 时出错: {e}')
                failed_categories += 1
                continue
        
        # 完成类别进度条
        if self.progress_display:
            self.progress_display.update_progress("categories", len(categories), "全部完成")
            self.progress_display.display_update()
        logger.success(f'所有分类下载任务完成！成功: {successful_categories}，失败: {failed_categories}')
        logger.info(f'总计: {len(categories)} 个分类')
        
        return True

    def close(self):
        """关闭资源"""
        self.database.close()
