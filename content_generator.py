"""
智能文案生成器
根据商品名称和介绍，从模板库中选择合适的模板生成文案
"""

from docx import Document
import random
import re
import os

class ContentGenerator:
    """文案生成器"""

    def __init__(self, template_path=None):
        if template_path is None:
            # 使用相对路径，在部署时也能正常工作
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_dir, '文案.docx')
        self.template_path = template_path
        self.templates = {}  # 按款式分类的模板库
        self.load_templates()

    def load_templates(self):
        """加载并分类所有模板"""
        doc = Document(self.template_path)

        # 定义款式关键词映射
        category_keywords = {
            '羽绒马甲': ['羽绒马甲', '马甲外套'],
            '羽绒服': ['羽绒服', '鹅绒服', '保暖羽绒'],
            '羊毛衫': ['羊毛衫', '羊毛打底', '纯羊毛', '山羊绒'],
            '针织衫': ['针织', '条纹毛衣', '打底衫', '毛衣'],
            '开衫': ['开衫', '卫衣开衫'],
            '外套': ['外套', '夹克'],
            '其他': []
        }

        # 初始化分类
        for category in category_keywords.keys():
            self.templates[category] = []

        # 读取所有段落并分类
        for para in doc.paragraphs:
            text = para.text.strip()
            if len(text) < 50:  # 过滤太短的文本
                continue

            # 分类
            classified = False
            for category, keywords in category_keywords.items():
                if category == '其他':
                    continue
                for keyword in keywords:
                    if keyword in text:
                        self.templates[category].append(text)
                        classified = True
                        break
                if classified:
                    break

            if not classified:
                self.templates['其他'].append(text)

        print("=" * 60)
        print("模板库加载完成")
        print("=" * 60)
        for category, templates in self.templates.items():
            print(f"{category}: {len(templates)} 个模板")
        print("=" * 60)

    def identify_category(self, product_name, description):
        """识别商品款式"""
        combined_text = product_name + " " + description

        # 按优先级匹配
        if '马甲' in combined_text and ('羽绒' in combined_text or '鹅绒' in combined_text):
            return '羽绒马甲'
        elif '羽绒' in combined_text or '鹅绒' in combined_text:
            return '羽绒服'
        elif '羊毛' in combined_text or '羊绒' in combined_text:
            return '羊毛衫'
        elif '针织' in combined_text or '毛衣' in combined_text:
            return '针织衫'
        elif '开衫' in combined_text:
            return '开衫'
        elif '外套' in combined_text or '夹克' in combined_text:
            return '外套'
        else:
            return '其他'

    def generate_content(self, product_name, description, template_index=None):
        """
        生成文案

        Args:
            product_name: 商品名称，例如"羽绒马甲"
            description: 商品介绍
            template_index: 指定模板索引（用于重新生成）

        Returns:
            生成的文案
        """
        # 识别款式
        category = self.identify_category(product_name, description)

        # 获取该款式的模板列表
        category_templates = self.templates.get(category, [])

        if not category_templates:
            # 如果没有匹配的模板，使用"其他"类别
            category_templates = self.templates.get('其他', [])

        if not category_templates:
            return "未找到合适的模板"

        # 选择模板
        if template_index is not None and 0 <= template_index < len(category_templates):
            template = category_templates[template_index]
        else:
            template = random.choice(category_templates)

        # 智能融合用户提供的信息
        generated_content = self._merge_template_and_info(template, product_name, description)

        return {
            'content': generated_content,
            'category': category,
            'template_index': category_templates.index(template) if template in category_templates else 0,
            'total_templates': len(category_templates)
        }

    def _merge_template_and_info(self, template, product_name, description):
        """
        将模板与用户信息智能融合

        策略：
        1. 提取描述中的关键卖点
        2. 在模板中查找可替换的通用描述
        3. 进行智能替换
        """
        result = template

        # 提取商品特性关键词
        features = self._extract_features(description)

        # 智能替换商品名称 - 保留品牌名和标记词，只替换商品描述
        replaced = False

        # 模式1: 品牌名 + 的 + 商品描述
        # 例如: "皮尔卡丹的高档保暖羽绒马甲外套" -> "皮尔卡丹的秋冬男士加绒加厚圆领卫衣"
        brand_pattern = r'([\u4e00-\u9fa5A-Za-z0-9]+的)([秋冬春夏季]{0,4}[男女]?[士款式]?[高档专柜品质加厚轻薄保暖]{0,10}[\u4e00-\u9fa5]{0,15}(羽绒马甲|羽绒服|羊毛衫|针织衫|开衫|外套|卫衣|毛衣|夹克|大衣|棉服)[\u4e00-\u9fa5]{0,10})'
        match = re.search(brand_pattern, result)
        if match and product_name.strip():
            brand_prefix = match.group(1)  # 保留品牌名，如 "皮尔卡丹的"
            result = result.replace(match.group(0), brand_prefix + product_name, 1)
            replaced = True

        # 模式2: "这款/就是这款" + 商品描述
        if not replaced:
            marker_pattern = r'(这款|就是这款|就拿这款)([秋冬春夏季]{0,4}[男女]?[士款式]?[\u4e00-\u9fa5]{0,20}(羽绒马甲|羽绒服|羊毛衫|针织衫|开衫|外套|卫衣|毛衣|夹克|大衣|棉服)[\u4e00-\u9fa5]{0,10})'
            match = re.search(marker_pattern, result)
            if match and product_name.strip():
                marker = match.group(1)  # 保留"这款"等标记
                result = result.replace(match.group(0), marker + product_name, 1)
                replaced = True

        # 模式3: 直接的商品描述（句首或逗号/句号后）
        if not replaced:
            # 匹配句首的商品描述
            start_pattern = r'^([秋冬春夏季]{0,4}[男女]?[士款式]?[\u4e00-\u9fa5]{0,20}(羽绒马甲|羽绒服|羊毛衫|针织衫|开衫|外套|卫衣|毛衣|夹克|大衣|棉服)[\u4e00-\u9fa5]{0,10})'
            match = re.search(start_pattern, result)
            if match and product_name.strip():
                result = result.replace(match.group(0), product_name, 1)
                replaced = True

        # 模式4: 更宽泛的匹配 - 任何位置的商品描述
        if not replaced:
            general_pattern = r'[秋冬春夏季]{0,4}[男女]?[士款式]?[高档专柜品质加厚轻薄保暖]{0,10}[\u4e00-\u9fa5]{0,15}(羽绒马甲|羽绒服|羊毛衫|针织衫|开衫|外套|卫衣|毛衣|夹克|大衣|棉服)[\u4e00-\u9fa5外套]{0,10}'
            match = re.search(general_pattern, result)
            if match and product_name.strip():
                result = result.replace(match.group(0), product_name, 1)
                replaced = True

        # 如果描述中有特殊卖点，尝试融入
        if features and len(features) > 0:
            # 查找模板中的卖点描述部分，尝试融入用户的卖点
            # 这里使用简单策略：在文案开头或中间插入卖点
            feature_text = '、'.join(features[:3])  # 最多取3个卖点
            if feature_text:
                # 在第一句话后插入卖点
                sentences = result.split('。')
                if len(sentences) > 1:
                    sentences[0] = sentences[0] + f"，{feature_text}"
                    result = '。'.join(sentences)

        return result

    def _extract_features(self, description):
        """从描述中提取关键特性"""
        features = []

        # 定义常见卖点关键词
        feature_keywords = [
            '保暖', '轻便', '防风', '透气', '舒适', '柔软',
            '时尚', '百搭', '修身', '宽松', '休闲', '商务',
            '加厚', '超薄', '防水', '耐磨', '速干',
            '纯棉', '纯羊毛', '羊绒', '鹅绒', '鸭绒',
            '可拆卸', '多口袋', '拉链', '半高领', '立领',
        ]

        for keyword in feature_keywords:
            if keyword in description and keyword not in features:
                features.append(keyword)

        return features


def generate_content_simple(product_name, description, template_index=None):
    """简单接口：生成文案"""
    generator = ContentGenerator()
    return generator.generate_content(product_name, description, template_index)


if __name__ == '__main__':
    # 测试
    generator = ContentGenerator()

    # 测试案例1：羽绒马甲
    result = generator.generate_content(
        product_name="白鸭绒立领马甲",
        description="这件羽绒马甲真的太实用了，它是可脱卸帽的设计，而且里面填充的是白鸭绒，非常暖和，版型也很宽松，穿上身很舒服"
    )

    print("\n测试案例1：羽绒马甲")
    print("=" * 60)
    print(f"识别款式：{result['category']}")
    print(f"模板库大小：{result['total_templates']}")
    print(f"生成文案：\n{result['content']}")
    print("=" * 60)
