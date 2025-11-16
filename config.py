"""
抖音商品图片处理工具 - 配置文件
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 目录配置
INPUT_DIR = os.path.join(BASE_DIR, 'input')    # 输入图片目录
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')  # 输出图片目录
TEMP_DIR = os.path.join(BASE_DIR, 'temp')      # 临时文件目录

# 图片处理配置
IMAGE_CONFIG = {
    'max_size': (2000, 2000),  # 最大尺寸
    'quality': 95,              # 输出质量 (1-100)
    'format': 'PNG',            # 输出格式
    'keep_original': True,      # 是否保留原图
}

# 抠图配置
REMBG_CONFIG = {
    'model': 'u2net',              # 经过测试，u2net 对商品图片效果最好
    'alpha_matting': False,        # 关闭alpha matting，得到清晰硬边缘
    'alpha_matting_foreground_threshold': 240,
    'alpha_matting_background_threshold': 10,
    'alpha_matting_erode_size': 10,
    'post_process_mask': True,     # 后处理，让边缘更平滑
}

# 支持的图片格式
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

# 抖音链接正则表达式
DOUYIN_PATTERNS = {
    'jinritemai': r'https://haohuo\.jinritemai\.com/ecommerce/trade/detail/index\.html\?[^\s]+',
    'jinritemai_id': r'id=(\d+)',
    'douyin_share': r'https://v\.douyin\.com/([A-Za-z0-9]+)',
    'product_id': r'id=(\d+)',
}
