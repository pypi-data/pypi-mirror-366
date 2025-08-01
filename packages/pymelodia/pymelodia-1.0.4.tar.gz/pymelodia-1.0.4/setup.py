# -*- coding: utf-8 -*-
"""
pymelodia - 优雅的网易云音乐下载工具
"""

from setuptools import setup, find_packages
import os

# 读取 README
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# 读取版本
def get_version():
    with open(os.path.join('pymelodia', '__init__.py'), encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.4'

setup(
    name='pymelodia',
    version=get_version(),
    author='yht0511',
    author_email='admin@teclab.org.cn',  # 请替换为你的邮箱
    description='🎵 网易云音乐下载工具',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/yht0511/melodia',
    packages=find_packages(),
    # package_dir={'': 'pymelodia'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        'lxml>=4.9.0',
        'eyed3>=0.9.6',
        'pycryptodome>=3.17.0',
        'PyExecJS>=1.5.1',
    ],
    entry_points={
        'console_scripts': [
            'melodia=pymelodia.cli.command_line:main',
        ],
    },
    keywords='music download netease 网易云 音乐下载 命令行工具',
    project_urls={
        'Bug Reports': 'https://github.com/yht0511/melodia/issues',
        'Source': 'https://github.com/yht0511/melodia',
        'Documentation': 'https://github.com/yht0511/melodia/blob/main/README.md',
    },
    include_package_data=True,
    zip_safe=False,
)
