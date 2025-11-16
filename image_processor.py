"""
图片处理模块 - 核心抠图功能
"""

import os
from PIL import Image
from rembg import remove
import config


class ImageProcessor:
    """图片处理器 - 负责抠图和图片优化"""

    def __init__(self):
        self.input_dir = config.INPUT_DIR
        self.output_dir = config.OUTPUT_DIR

        # 确保目录存在
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def remove_background(self, input_path, output_path=None):
        """
        去除图片背景（抠图）

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（可选）

        Returns:
            output_path: 输出图片路径
        """
        try:
            # 读取图片
            print(f"正在处理: {os.path.basename(input_path)}")
            input_image = Image.open(input_path)

            # 去除背景
            print("  - 正在去除背景...")
            output_image = remove(
                input_image,
                alpha_matting=config.REMBG_CONFIG['alpha_matting'],
                alpha_matting_foreground_threshold=config.REMBG_CONFIG['alpha_matting_foreground_threshold'],
                alpha_matting_background_threshold=config.REMBG_CONFIG['alpha_matting_background_threshold'],
                alpha_matting_erode_size=config.REMBG_CONFIG['alpha_matting_erode_size'],
            )

            # 生成输出路径
            if output_path is None:
                filename = os.path.basename(input_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_nobg.png"
                output_path = os.path.join(self.output_dir, output_filename)

            # 保存图片
            output_image.save(
                output_path,
                format=config.IMAGE_CONFIG['format'],
                quality=config.IMAGE_CONFIG['quality']
            )

            print(f"  ✓ 保存成功: {os.path.basename(output_path)}")
            return output_path

        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            return None

    def batch_remove_background(self, input_files=None):
        """
        批量去除背景

        Args:
            input_files: 输入文件列表，如果为None则处理input目录下所有图片

        Returns:
            成功处理的文件列表
        """
        # 如果没有指定文件，则处理input目录下所有图片
        if input_files is None:
            input_files = self.get_input_images()

        if not input_files:
            print("没有找到需要处理的图片")
            return []

        print(f"\n开始批量处理 {len(input_files)} 张图片...\n")
        print("="*60)

        success_files = []
        failed_files = []

        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}]")

            result = self.remove_background(input_file)
            if result:
                success_files.append(result)
            else:
                failed_files.append(input_file)

        # 显示统计
        print("\n" + "="*60)
        print(f"处理完成！")
        print(f"  成功: {len(success_files)} 张")
        print(f"  失败: {len(failed_files)} 张")

        if success_files:
            print(f"\n输出目录: {self.output_dir}")

        return success_files

    def get_input_images(self):
        """获取input目录下的所有图片文件"""
        image_files = []

        if not os.path.exists(self.input_dir):
            return image_files

        for filename in os.listdir(self.input_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext in config.SUPPORTED_FORMATS:
                file_path = os.path.join(self.input_dir, filename)
                image_files.append(file_path)

        return sorted(image_files)

    def resize_image(self, image_path, max_size=None):
        """
        调整图片尺寸（保持高清）

        Args:
            image_path: 图片路径
            max_size: 最大尺寸 (width, height)
        """
        if max_size is None:
            max_size = config.IMAGE_CONFIG['max_size']

        try:
            image = Image.open(image_path)

            # 如果图片尺寸小于最大尺寸，不需要调整
            if image.width <= max_size[0] and image.height <= max_size[1]:
                return image

            # 计算缩放比例
            ratio = min(max_size[0] / image.width, max_size[1] / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))

            # 使用高质量重采样
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            return resized

        except Exception as e:
            print(f"调整尺寸失败: {e}")
            return None


if __name__ == '__main__':
    # 测试代码
    processor = ImageProcessor()

    # 检查input目录
    images = processor.get_input_images()

    if images:
        print(f"找到 {len(images)} 张图片:")
        for img in images:
            print(f"  - {os.path.basename(img)}")

        print("\n开始处理...")
        processor.batch_remove_background()
    else:
        print("=" * 60)
        print("input 目录为空！")
        print("=" * 60)
        print("\n请将需要处理的图片放入以下目录：")
        print(f"  {processor.input_dir}")
        print("\n然后重新运行此脚本。")
