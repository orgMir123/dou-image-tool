"""
Web版抠图工具 - 基于Flask
功能：
1. 上传图片
2. 自动去背景
3. 下载处理后的图片
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import zipfile
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
from rembg import remove
from rembg.session_factory import new_session
import io
import config
import numpy as np
import cv2
from content_generator import ContentGenerator

app = Flask(__name__)

# 初始化文案生成器（全局单例，避免重复加载模板）
content_generator = ContentGenerator()

# 配置
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大50MB
app.config['UPLOAD_FOLDER'] = 'web_uploads'
app.config['OUTPUT_FOLDER'] = 'web_outputs'

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image):
    """预处理图片：增强对比度和亮度，帮助AI更好地识别前景"""
    # 增强对比度（1.2倍）
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)

    # 轻微增强亮度（1.1倍）
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)

    # 增强锐度（1.15倍）
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.15)

    return image


def postprocess_mask(image_with_alpha):
    """后处理：填补mask中的小空洞，修复误删的前景"""
    # 转换为numpy数组
    img_array = np.array(image_with_alpha)

    # 提取alpha通道
    if img_array.shape[2] == 4:
        alpha = img_array[:, :, 3]

        # 使用形态学闭操作填补小空洞
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        alpha_closed = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 使用开操作去除小噪点
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        alpha_processed = cv2.morphologyEx(alpha_closed, cv2.MORPH_OPEN, kernel_open, iterations=1)

        # 替换alpha通道
        img_array[:, :, 3] = alpha_processed

        # 转回PIL Image
        return Image.fromarray(img_array)

    return image_with_alpha


def remove_background_single(input_path, output_path, model_name=None):
    """去除单张图片背景"""
    try:
        # 读取图片
        input_image = Image.open(input_path)

        # 创建模型 session - 使用指定的模型或默认模型
        selected_model = model_name if model_name else config.REMBG_CONFIG['model']
        session = new_session(selected_model)

        # 去除背景
        output_image = remove(
            input_image,
            session=session,
            alpha_matting=config.REMBG_CONFIG['alpha_matting'],
            alpha_matting_foreground_threshold=config.REMBG_CONFIG['alpha_matting_foreground_threshold'],
            alpha_matting_background_threshold=config.REMBG_CONFIG['alpha_matting_background_threshold'],
            alpha_matting_erode_size=config.REMBG_CONFIG['alpha_matting_erode_size'],
            post_process_mask=config.REMBG_CONFIG.get('post_process_mask', False),
        )

        # 后处理：填补小空洞（轻度修复）
        output_image = postprocess_mask(output_image)

        # 保存 - PNG无损格式，最高质量
        output_image.save(output_path, format='PNG', compress_level=1, optimize=True)
        return True

    except Exception as e:
        print(f"处理图片失败: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """处理上传的文件"""
    if 'files[]' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    files = request.files.getlist('files[]')

    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 获取用户选择的模型（如果有）
    selected_model = request.form.get('model', 'u2net')
    print(f"使用模型: {selected_model}")

    # ✨ 每次上传新图片时，自动清空之前的输出文件
    # 这样下载时只包含当前这一批的图片
    for filename in os.listdir(app.config['OUTPUT_FOLDER']):
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        try:
            os.remove(file_path)
        except:
            pass

    processed_files = []
    failed_files = []

    for file in files:
        if file and allowed_file(file.filename):
            # 保存原始文件
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            # 处理图片 - 传递选择的模型
            output_filename = os.path.splitext(filename)[0] + '_nobg.png'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            if remove_background_single(upload_path, output_path, model_name=selected_model):
                processed_files.append({
                    'original': filename,
                    'processed': output_filename,
                    'download_url': f'/download/{output_filename}'
                })
            else:
                failed_files.append(filename)

            # 删除上传的原始文件
            os.remove(upload_path)

    return jsonify({
        'success': True,
        'processed': len(processed_files),
        'failed': len(failed_files),
        'files': processed_files
    })


@app.route('/download/<filename>')
def download_file(filename):
    """下载单个处理后的文件"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "文件不存在", 404


@app.route('/download_all')
def download_all():
    """打包下载所有处理后的文件"""
    output_files = os.listdir(app.config['OUTPUT_FOLDER'])

    if not output_files:
        return "没有文件可下载", 404

    # 创建ZIP文件
    zip_path = 'all_processed.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in output_files:
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            zipf.write(file_path, filename)

    return send_file(zip_path, as_attachment=True, download_name='processed_images.zip')


@app.route('/clear')
def clear_files():
    """清空输出目录"""
    for filename in os.listdir(app.config['OUTPUT_FOLDER']):
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        os.remove(file_path)

    return jsonify({'success': True, 'message': '已清空所有文件'})


@app.route('/generate_content', methods=['POST'])
def generate_content():
    """生成文案"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        description = data.get('description', '').strip()
        template_index = data.get('template_index')  # 用于重新生成

        if not product_name or not description:
            return jsonify({
                'success': False,
                'error': '请输入商品名称和商品介绍'
            })

        print(f"生成文案 - 商品: {product_name}, 描述长度: {len(description)}")

        # 生成文案
        result = content_generator.generate_content(
            product_name=product_name,
            description=description,
            template_index=template_index
        )

        return jsonify({
            'success': True,
            'content': result['content'],
            'category': result['category'],
            'template_index': result['template_index'],
            'total_templates': result['total_templates']
        })

    except Exception as e:
        print(f"生成文案失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug_mode = os.getenv('FLASK_ENV') != 'production'

    print("="*60)
    print(" "*20 + "Web抠图工具")
    print("="*60)
    print(f"\n访问地址: http://localhost:{port}")
    print("\n功能:")
    print("  1. 上传图片（支持多张）")
    print("  2. 自动去除背景")
    print("  3. 下载处理后的图片")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")

    app.run(debug=debug_mode, host='0.0.0.0', port=port)
