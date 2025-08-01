# 🎵 Melodia

> 网易云音乐下载工具

[![PyPI version](https://badge.fury.io/py/pymelodia.svg)](https://badge.fury.io/py/pymelodia)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 快速开始

### 安装

```bash
pip install pymelodia
```

### 基本使用

```bash
# 下载单首歌曲
melodia download song 390345

# 下载歌单
melodia download playlist 123456

# 下载指定分类的音乐
melodia download category 华语

# 下载所有分类
melodia download all

# 获取下载链接
melodia get link 390345

# 清理重复文件
melodia clean /path/to/music
```

## 📖 详细使用

### 下载命令

```bash
# 单曲下载
melodia download song 390345

# 批量下载多首歌曲
melodia download song "['390345', '123456', '789012']"

# 歌单下载
melodia download playlist 2829883282

# 批量下载多个歌单
melodia download playlist "['2829883282', '3779629']"

# 分类下载（支持华语、欧美、日语等）
melodia download category 华语

# 下载所有支持的分类
melodia download all
```

### 配置选项

```bash
# 设置保存路径
melodia --save-path /path/to/music download song 390345

# 设置请求延时（避免频率限制）
melodia --delay 1 download category 华语

# 设置最大页数
melodia --max-pages 50 download all

# 设置用户Cookie（提升成功率）
melodia --cookie "your_cookie_here" download playlist 123456
```

### 支持的音乐分类

**语言分类**：华语、欧美、日语、韩语、粤语

**风格分类**：流行、摇滚、民谣、电子、舞曲、说唱、轻音乐、爵士、乡村

**场景分类**：清晨、夜晚、学习、工作、午休、下午茶、地铁、驾车

**情感分类**：怀旧、清新、浪漫、伤感、治愈、放松、孤独、感动

**主题分类**：综艺、影视原声、ACG、儿童、校园、游戏、经典

## 🎯 界面预览

```
🎵 Melodia 下载进度 🎵
════════════════════════════════════════════════════════════════

歌曲列表                   [████████████░░░░░░░░░░] 60.0% (3/5)
歌单列表                   [██████████████████░░] 90.0% (9/10)
categories                 [████████████████████] 100.0% (8/8)

📝 实时日志
────────────────────────────────────────────────────────────────
[14:32:15] [INFO] ℹ️ 开始下载歌曲 ID: 390345
[14:32:16] [SUCCESS] ✅ 成功下载: xxxx
[14:32:17] [INFO] ℹ️ 正在处理歌单...
```

## ⚙️ 高级配置

### 配置文件

程序会在用户目录下创建配置文件 `~/.melodia/config.json`：

```json
{
  "save_path": "./music/",
  "delay": 3,
  "max_pages": 20,
  "cookie": "",
  "music_class": "全部",
  "temp_path": "./temp.mp3",
  "hashed_storage_enabled": true,
  "hashed_storage_digit": 3
}
```

### 环境变量


```bash
export MD_SAVE_PATH=./music/
export MD_TEMP_PATH=./temp/
export MD_CLASS=华语
export MD_DELAY=3
export MD_COOKIE=""
export MD_MAX_PAGES=20
export MD_HASHED_STORAGE=False
export MD_HASHED_STORAGE_DIGIT=2
```

### 配置管理命令

```bash
# 显示当前配置信息
melodia config show
melodia get config

# 保存配置到文件
melodia config save --hashed-storage --hashed-storage-digit 30
```

### 参数优先级

命令行参数 > 环境变量 > 配置文件 > 默认值

## 🛠️ 开发

### 本地开发

```bash
git clone https://github.com/yht0511/MusicSpider.git
cd MusicSpider
pip install -e .
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本工具仅供学习和研究使用，请勿用于商业用途。下载的音乐文件请在24小时内删除，如需长期使用请购买正版音乐。

