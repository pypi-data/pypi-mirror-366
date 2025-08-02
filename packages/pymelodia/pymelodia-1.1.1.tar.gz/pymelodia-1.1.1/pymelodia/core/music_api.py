# -*- coding: utf-8 -*-
"""网易云音乐API接口封装"""

import requests
from bs4 import BeautifulSoup
from .crypto_helper import WanYiYun


class NeteaseMusicAPI:
    """网易云音乐API封装类"""
    
    def __init__(self, cookie=""):
        self.cookie = cookie
        self.crypto_helper = WanYiYun()
        self.default_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'sec-ch-ua-platform': 'Windows',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-fetch-dest': 'iframe',
        }

    def get_playlist_list(self, category="全部", page=0):
        """获取指定分类的歌单列表"""
        if page > 19:
            return []
            
        url = 'https://music.163.com/discover/playlist/'
        headers = {**self.default_headers, 'cookie': self.cookie}
        params = {
            'order': 'hot',
            'cat': category,
            'limit': '35',
            'offset': 35 * page,
        }
        
        try:
            response = requests.get(url=url, params=params, headers=headers)
            bs = BeautifulSoup(response.text, 'lxml')
            return bs.find_all('a', {"class": "msk"})
        except Exception as e:
            print(f'获取歌单列表失败: {e}')
            return []

    def get_playlist_songs(self, playlist_id):
        """获取歌单中的歌曲列表"""
        url = 'https://music.163.com/playlist'
        headers = {**self.default_headers, 'cookie': self.cookie + ";os=pc"}
        params = {'id': playlist_id}
        
        try:
            response = requests.get(url=url, params=params, headers=headers)
            bs = BeautifulSoup(response.text, 'lxml')
            return bs.select('ul.f-hide>li>a')
        except Exception as e:
            print(f'获取歌单歌曲失败: {e}')
            return []

    def get_song_info(self, music_id):
        """获取歌曲基本信息"""
        url = f'https://music.163.com/song?id={music_id}'
        headers = self.default_headers
        
        try:
            response = requests.get(url=url, headers=headers)
            bs = BeautifulSoup(response.text, 'lxml')
            
            # 检查歌曲是否可用
            if len(bs.select('a.u-btni-play')) != 0:
                return None, None, None, None
            
            title = bs.select('em.f-ff2')[0].text if bs.select('em.f-ff2') else ""
            subtitle = bs.select('div.subtit')[0].text if bs.select('div.subtit') else ""
            artist_elements = bs.select('p.s-fc4>span')
            artist = artist_elements[0].get('title', '') if artist_elements and hasattr(artist_elements[0], 'get') else ""
            
            album_meta = bs.find_all('meta', {'property': 'og:music:album'})
            album = ""
            if album_meta and hasattr(album_meta[0], 'attrs'):
                album = album_meta[0].attrs.get('content', '')
            elif album_meta and hasattr(album_meta[0], 'get'):
                album = album_meta[0].get('content', '')
            
            return subtitle, artist, album, title
            
        except Exception as e:
            print(f'获取歌曲信息失败 [{music_id}]: {e}')
            return None, None, None, None

    def get_song_lyric(self, music_id):
        """获取歌曲歌词"""
        url = f'http://music.163.com/api/song/lyric?id={music_id}&lv=-1&kv=-1&tv=-1'
        headers = {**self.default_headers, 'cookie': self.cookie}
        
        try:
            response = requests.get(url=url, headers=headers)
            return response.json()['lrc']['lyric']
        except Exception as e:
            print(f'获取歌词失败 [{music_id}]: {e}')
            return None

    def get_album_cover(self, music_id):
        """获取专辑封面"""
        url = f'https://music.163.com/song?id={music_id}'
        headers = {**self.default_headers, 'cookie': self.cookie}
        
        try:
            response = requests.get(url=url, headers=headers)
            bs = BeautifulSoup(response.text, 'lxml')
            
            # 尝试多种方式获取封面URL
            img_url = None
            
            # 方法1: class为j-img的img标签
            img_elements = bs.find_all('img', {'class': 'j-img'})
            if img_elements:
                img_element = img_elements[0]
                img_url = img_element.get('data-src') or img_element.get('src')
            
            # 方法2: 专辑封面的其他位置
            if not img_url:
                cover_elements = bs.select('div.u-cover img')
                if cover_elements:
                    img_url = cover_elements[0].get('src') or cover_elements[0].get('data-src')
            
            # 方法3: meta标签
            if not img_url:
                meta_img = bs.find('meta', {'property': 'og:image'})
                if meta_img:
                    img_url = meta_img.get('content')
            
            if img_url:
                # 确保URL完整
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://music.163.com' + img_url
                
                # 下载图片
                img_response = requests.get(img_url, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    return img_response.content
            
            return None
            
        except Exception as e:
            print(f'获取专辑封面失败 [{music_id}]: {e}')
            return None

    def get_download_url(self, music_id):
        """获取歌曲下载链接"""
        try:
            return self.crypto_helper.getDownloadUrl(music_id, self.cookie)
        except Exception as e:
            print(f'获取下载链接失败 [{music_id}]: {e}')
            return None

    def download_song_content(self, download_url):
        """下载歌曲内容"""
        if not download_url:
            return None
            
        headers = {**self.default_headers, 'cookie': self.cookie}
        
        try:
            response = requests.get(url=download_url, headers=headers)
            return response.content
        except Exception as e:
            print(f'下载歌曲内容失败: {e}')
            return None
