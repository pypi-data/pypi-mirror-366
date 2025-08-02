# -*- coding: utf-8 -*-
"""美化的命令行接口模块"""

import sys
import ast
import time
import argparse
from typing import List, Optional
from ..services.download_service import MusicDownloadService
from ..processors.file_processor import MusicRemoveDuplicates
from ..ui.progress_display import Colors, progress_display
from ..config import config


class CommandLineInterface:
    """命令行接口"""
    
    def __init__(self):
        """初始化CLI"""
        self.service: Optional[MusicDownloadService] = None
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            prog='melodia',
            description=f'{Colors.BOLD}{Colors.BRIGHT_CYAN}🎵 Melodia - 网易云音乐下载工具 🎵{Colors.RESET}',
            formatter_class=argparse.RawDescriptionHelpFormatter,
#             epilog=f"""
# {Colors.BOLD}支持的音乐分类:{Colors.RESET}
#   {Colors.CYAN}全部{Colors.RESET}
#   {Colors.CYAN}语言:{Colors.RESET} 华语、欧美、日语、韩语、粤语
#   {Colors.CYAN}风格:{Colors.RESET} 流行、摇滚、民谣、电子、舞曲、说唱、轻音乐、爵士、乡村
#   {Colors.CYAN}场景:{Colors.RESET} 清晨、夜晚、学习、工作、午休、下午茶、地铁、驾车
#   {Colors.CYAN}情感:{Colors.RESET} 怀旧、清新、浪漫、伤感、治愈、放松、孤独、感动
#   {Colors.CYAN}主题:{Colors.RESET} 综艺、影视原声、ACG、儿童、校园、游戏、经典
# """
        )

        # 配置参数
        parser.add_argument('--cookie', '-c', default=None, help='设置用户Cookie')
        parser.add_argument('--save-path', '-p', default=None, help='设置保存路径')
        parser.add_argument('--delay', '-d', type=int, default=None, help='设置请求延时(秒)')
        parser.add_argument('--max-pages', '-mp', type=int, default=None, help='设置最大页数')
        parser.add_argument('--hashed-storage', type=bool, default=None, help='启用哈希存储')
        parser.add_argument('--hashed-storage-digit', type=int, default=None, help='设置哈希存储的目录层级')
        parser.add_argument('--threading', '-t', action='store_true', default=None, help='启用多线程下载')
        parser.add_argument('--no-threading', action='store_true', default=None, help='禁用多线程下载')
        parser.add_argument('--thread-count', '-tc', type=int, default=None, help='设置线程数量')
        parser.add_argument('--temp-dir', default=None, help='设置临时文件目录')

        # 创建子命令
        subparsers = parser.add_subparsers(dest='command', help='可用命令')

        # download 命令
        download_parser = subparsers.add_parser(
            'download', 
            help='下载音乐内容',
            description=f'{Colors.BOLD}下载音乐内容{Colors.RESET}'
        )
        download_subparsers = download_parser.add_subparsers(dest='download_type', help='下载类型')

        # download song
        song_parser = download_subparsers.add_parser('song', help='下载歌曲')
        song_parser.add_argument('ids', help='歌曲ID或ID列表 (支持格式: 123456 或 "[\'123456\', \'789012\']")')

        # download playlist
        playlist_parser = download_subparsers.add_parser('playlist', help='下载歌单')
        playlist_parser.add_argument('ids', help='歌单ID或ID列表 (支持格式: 123456 或 "[\'123456\', \'789012\']")')

        # download category
        category_parser = download_subparsers.add_parser('category', help='下载音乐分类')
        category_parser.add_argument('name', nargs='?', default='全部', help='分类名称 (默认: 全部)')

        # download all
        download_subparsers.add_parser('all', help='下载所有分类')

        # get 命令
        get_parser = subparsers.add_parser('get', help='获取信息')
        get_subparsers = get_parser.add_subparsers(dest='get_type', help='获取类型')

        # get link
        link_parser = get_subparsers.add_parser('link', help='获取下载链接')
        link_parser.add_argument('ids', help='歌曲ID或ID列表')

        # get config
        config_parser = get_subparsers.add_parser('config', help='显示配置信息')

        # clean 命令
        clean_parser = subparsers.add_parser('clean', help='清理重复文件')
        clean_parser.add_argument('path', help='要清理的文件夹路径')

        # config 命令
        config_main_parser = subparsers.add_parser('config', help='配置管理')
        config_subparsers = config_main_parser.add_subparsers(dest='config_action', help='配置操作')

        # config show
        show_parser = config_subparsers.add_parser('show', help='显示当前配置')

        # config save
        save_parser = config_subparsers.add_parser('save', help='保存当前配置到文件')
        save_parser.add_argument('--cookie', '-c', default=None, help='设置用户Cookie')
        save_parser.add_argument('--save-path', '-p', default=None, help='设置保存路径')
        save_parser.add_argument('--delay', '-d', type=int, default=None, help='设置请求延时(秒)')
        save_parser.add_argument('--max-pages', '-mp', type=int, default=None, help='设置最大页数')
        save_parser.add_argument('--hashed-storage', action='store_true', default=None, help='启用哈希存储')
        save_parser.add_argument('--hashed-storage-digit', type=int, default=None, help='哈希存储位数')
        save_parser.add_argument('--threading', '-t', action='store_true', default=None, help='启用多线程下载')
        save_parser.add_argument('--no-threading', action='store_true', default=None, help='禁用多线程下载')
        save_parser.add_argument('--thread-count', '-tc', type=int, default=None, help='设置线程数量')
        save_parser.add_argument('--temp-dir', default=None, help='设置临时文件目录')

        return parser

    def _init_service(self, args) -> bool:
        """初始化下载服务"""
        if self.service is None:
            
            # 处理线程配置
            threading_enabled = None
            if hasattr(args, 'threading') and args.threading:
                threading_enabled = True
            elif hasattr(args, 'no_threading') and args.no_threading:
                threading_enabled = False
            
            # 使用新的配置系统：命令行参数 > 环境变量 > 配置文件 > 默认值
            config.update_from_args(
                cookie=args.cookie,
                save_path=args.save_path,
                delay=args.delay,
                max_pages=args.max_pages,
                hashed_storage_enabled=args.hashed_storage,
                hashed_storage_digit=args.hashed_storage_digit,
                threading_enabled=threading_enabled,
                thread_count=getattr(args, 'thread_count', None),
                temp_dir=getattr(args, 'temp_dir', None)
            )

            self.service = MusicDownloadService(
                cookie=config.cookie,
                save_path=config.save_path,
                delay=config.delay,
                hashed_storage_enabled=config.hashed_storage_enabled,
                hashed_storage_digit=config.hashed_storage_digit
            )
            
            # 设置进度显示器
            self.service.set_progress_display(progress_display)
            
            return True
        return True

    def _parse_id_list(self, id_string: str) -> List[str]:
        """解析ID列表字符串"""
        if isinstance(id_string, str) and id_string.startswith('[') and id_string.endswith(']'):
            try:
                id_list = ast.literal_eval(id_string)
                if isinstance(id_list, list):
                    return [str(item) for item in id_list]
            except Exception as e:
                progress_display.warning(f'解析列表失败: {e}，将作为单个ID处理')
        
        return [str(id_string)]

    def handle_download_song(self, args):
        """处理下载歌曲命令"""
        if not self._init_service(args):
            return
        
        music_ids = self._parse_id_list(args.ids)
        
        if len(music_ids) > 1:
            progress_display.info(f'检测到列表模式，准备下载 {len(music_ids)} 首歌曲')
            # 添加列表总进度条
            progress_display.add_progress_bar('歌曲列表', len(music_ids), f'批量下载 ({len(music_ids)} 首)')
            self.service.download_music_list(music_ids)
        else:
            progress_display.info(f'准备下载歌曲 ID: {music_ids[0]}')
            self.service.download_single_music(music_ids[0])

    def handle_download_playlist(self, args):
        """处理下载歌单命令"""
        if not self._init_service(args):
            return
        
        playlist_ids = self._parse_id_list(args.ids)
        
        if len(playlist_ids) > 1:
            progress_display.info(f'检测到列表模式，准备下载 {len(playlist_ids)} 个歌单')
            # 添加歌单列表总进度条
            progress_display.add_progress_bar('歌单列表', len(playlist_ids), f'批量下载 ({len(playlist_ids)} 个歌单)')
            self.service.download_playlist_list(playlist_ids)
        else:
            progress_display.info(f'准备下载歌单 ID: {playlist_ids[0]}')
            self.service.download_playlist(playlist_ids[0])

    def handle_download_category(self, args):
        """处理下载分类命令"""
        if not self._init_service(args):
            return
        
        progress_display.info(f'准备下载分类: {args.name}')
        self.service.download_category_music(args.name)

    def handle_download_all(self, args):
        """处理下载所有分类命令"""
        if not self._init_service(args):
            return
        
        progress_display.info('准备下载所有分类的音乐')
        self.service.download_all_categories()

    def handle_get_link(self, args):
        """处理获取下载链接命令"""
        if not self._init_service(args):
            return
        
        music_ids = self._parse_id_list(args.ids)
        progress_display.info(f'准备获取 {len(music_ids)} 首歌曲的下载链接')
        self.service.get_download_links(music_ids)

    def handle_clean(self, args):
        """处理清理重复文件命令"""
        progress_display.info(f'准备清理文件夹: {args.path}')
        processor = MusicRemoveDuplicates()
        processor.init_remove_repeat(args.path)

    def handle_config(self, args):
        """处理配置命令"""
        from ..config import config
        
        if args.config_action == 'show':
            self.show_config()
        elif args.config_action == 'save':
            # 处理线程配置
            threading_enabled = None
            if hasattr(args, 'threading') and args.threading:
                threading_enabled = True
            elif hasattr(args, 'no_threading') and args.no_threading:
                threading_enabled = False
                
            # 从命令行参数更新配置（支持 config save --delay 30 这样的语法）
            config.update_from_args(
                cookie=getattr(args, 'cookie', None),
                save_path=getattr(args, 'save_path', None),
                delay=getattr(args, 'delay', None),
                max_pages=getattr(args, 'max_pages', None),
                hashed_storage_enabled=getattr(args, 'hashed_storage', None),
                hashed_storage_digit=getattr(args, 'hashed_storage_digit', None),
                threading_enabled=threading_enabled,
                thread_count=getattr(args, 'thread_count', None),
                temp_dir=getattr(args, 'temp_dir', None)
            )
            config.save_config_file()
            progress_display.success('配置已保存到文件')
        else:
            progress_display.error('请指定配置操作: show, save')
    
    def handle_get_config(self, args):
        """处理获取配置信息命令"""
        self.show_config()
    
    def show_config(self):
        """显示配置信息"""
        
        config_info = config.get_config_info()
        
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}📁 Melodia 配置信息{Colors.RESET}")
        print("=" * 60)
        
        print(f"\n{Colors.BOLD}📂 配置文件:{Colors.RESET}")
        print(f"  路径: {config_info['配置文件路径']}")
        print(f"  存在: {'✅ 是' if config_info['配置文件存在'] else '❌ 否'}")
        
        print(f"\n{Colors.BOLD}⚙️ 当前配置:{Colors.RESET}")
        current = config_info['当前配置']
        for key, value in current.items():
            print(f"  {key}: {value}")
        
        print(f"\n{Colors.BOLD}🌍 环境变量:{Colors.RESET}")
        env_vars = config_info['环境变量']
        has_env = False
        for key, value in env_vars.items():
            if value is not None:
                print(f"  {key}: {value}")
                has_env = True
        if not has_env:
            print("  (未设置)")
        
        print(f"\n{Colors.BOLD}📋 优先级:{Colors.RESET}")
        print("  命令行参数 > 环境变量 > 配置文件 > 默认值")
        
        print(f"\n{Colors.BOLD}💡 使用提示:{Colors.RESET}")
        print("  保存配置: melodia config save")
        print("  设置环境变量: export MD_SAVE_PATH=./music/")
        print("  命令行覆盖: melodia --save-path ./custom/ download song 123456")
        print("  启用多线程: melodia --threading --thread-count 8 download playlist 123456")
        print("  禁用多线程: melodia --no-threading download playlist 123456")
        print()

    def run(self, argv: Optional[List[str]] = None):
        """运行命令行程序"""
        if argv is None:
            argv = sys.argv[1:]
        
        # 如果没有参数，显示帮助
        if not argv:
            self.parser.print_help()
            return

        try:
            args = self.parser.parse_args(argv)
            
            # 初始化进度显示
            progress_display.clear_screen()
            
            # 开始实际操作，切换到固定进度条模式
            progress_display.display_initial()
            
            # 根据命令分发处理
            if args.command == 'download':
                if args.download_type == 'song':
                    self.handle_download_song(args)
                elif args.download_type == 'playlist':
                    self.handle_download_playlist(args)
                elif args.download_type == 'category':
                    self.handle_download_category(args)
                elif args.download_type == 'all':
                    self.handle_download_all(args)
                else:
                    progress_display.error('请指定下载类型: song, playlist, category, all')
            
            elif args.command == 'get':
                if args.get_type == 'link':
                    self.handle_get_link(args)
                elif args.get_type == 'config':
                    self.handle_get_config(args)
                else:
                    progress_display.error('请指定获取类型: link, config')
            
            elif args.command == 'clean':
                self.handle_clean(args)
            
            elif args.command == 'config':
                self.handle_config(args)
            
            else:
                self.parser.print_help()

        except KeyboardInterrupt:
            progress_display.warning('用户中断操作')
        except Exception as e:
            progress_display.error(f'执行出错: {str(e)}')
        finally:
            # 清理资源
            if self.service:
                self.service.close()
            # 显示光标
            progress_display.show_cursor()


def main():
    """主函数"""
    cli = CommandLineInterface()
    cli.run()


if __name__ == '__main__':
    main()
