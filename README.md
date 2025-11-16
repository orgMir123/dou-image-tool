# 抖音商品图片处理工具

一个专门用于处理抖音商品图片的工具，支持链接解析、图片下载和智能抠图（去背景）。

## 功能特点

✓ **链接解析** - 识别三种格式的抖音商品链接
  - 精选联盟链接
  - 抖音商城分享链接
  - 带货后台链接

✓ **智能抠图** - AI驱动的背景去除
  - 使用U2-Net深度学习模型
  - Alpha matting边缘优化
  - 保持高清质量

✓ **批量处理** - 一键处理多张图片

✓ **高质量输出** - PNG格式，透明背景

## 项目结构

```
dou/
├── config.py            # 配置文件
├── image_processor.py   # 图片处理模块（核心抠图功能）
├── link_parser.py       # 链接解析模块
├── main.py             # 主程序（交互式界面）
├── requirements.txt    # 依赖包
├── input/              # 输入图片目录
├── output/             # 输出图片目录（去背景后）
└── temp/               # 临时文件目录
```

## 快速开始

### 1. 安装依赖

```bash
cd ~/dou
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**注意**: 首次运行会自动下载AI模型（约180MB），需要等待几分钟。

### 2. 准备图片

将需要处理的商品图片放入 `input/` 目录。

### 3. 运行程序

#### 方式1：交互式界面（推荐）

```bash
python main.py
```

然后根据菜单选择功能。

#### 方式2：直接批量处理

```bash
python image_processor.py
```

会自动处理 `input/` 目录下的所有图片。

#### 方式3：测试链接解析

```bash
python link_parser.py
```

## 使用示例

### 示例1：解析抖音链接

```python
from link_parser import DouyinLinkParser

parser = DouyinLinkParser()

# 精选联盟链接
link1 = "https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3648266819162238212"

# 抖音分享链接
link2 = "4.12 h@O.Kw 【抖音商城】https://v.douyin.com/LA0vanfVBPY/ jeep吉普棉衣..."

result = parser.parse(link1)
print(f"商品ID: {result['product_id']}")
```

### 示例2：批量去背景

```python
from image_processor import ImageProcessor

processor = ImageProcessor()

# 处理 input 目录下所有图片
processor.batch_remove_background()

# 或指定特定图片
processor.remove_background('input/product1.jpg', 'output/product1_nobg.png')
```

### 示例3：自定义配置

编辑 `config.py` 文件：

```python
# 更改抠图模型（更快或更精确）
REMBG_CONFIG = {
    'model': 'u2netp',  # 更快的模型
    # 或 'isnet-general-use'  # 更精确的模型
}

# 更改输出质量
IMAGE_CONFIG = {
    'quality': 100,  # 最高质量
    'format': 'PNG',
}
```

## 工作流程

### 完整流程（手动下载图片）

由于抖音的反爬虫限制，目前推荐以下流程：

1. **复制商品链接** → 使用程序解析（功能1）
2. **手动访问商品页** → 右键保存商品图片到 `input/` 目录
3. **运行抠图程序** → 使用功能2批量处理
4. **获取结果** → 在 `output/` 目录查看无背景图片

### 快速流程（仅抠图）

如果已有商品图片：

1. 将图片放入 `input/` 目录
2. 运行 `python image_processor.py`
3. 在 `output/` 目录获取结果

## 配置说明

### 抠图模型选择

| 模型 | 速度 | 精度 | 适用场景 |
|------|------|------|----------|
| u2net | 中等 | 高 | 通用场景（推荐） |
| u2netp | 快 | 中 | 快速处理 |
| isnet-general-use | 慢 | 极高 | 精细抠图 |

### 支持的图片格式

输入：JPG, JPEG, PNG, WEBP, BMP
输出：PNG（透明背景）

## 常见问题

**Q: 首次运行很慢？**
A: 首次运行会下载AI模型（约180MB），之后会快很多。

**Q: 抠图效果不好？**
A: 尝试在 `config.py` 中更换模型为 `isnet-general-use`，或调整 alpha matting 参数。

**Q: 能否自动下载商品图片？**
A: 由于抖音反爬虫限制，目前需要手动下载。未来会尝试更多方案。

**Q: 图片质量会降低吗？**
A: 不会。程序保持原始分辨率，使用高质量PNG输出。

**Q: 可以处理多少张图片？**
A: 理论上无限制，但建议每批50张以内，避免内存占用过大。

## 技术栈

- **Python 3.8+**
- **rembg** - AI抠图引擎
- **Pillow** - 图片处理
- **U2-Net** - 深度学习模型

## 后续计划

- [ ] 实现自动化商品图片获取（绕过反爬虫）
- [ ] 添加Web界面
- [ ] 支持更多图片处理功能（压缩、裁剪、水印等）
- [ ] 添加批量下载功能
- [ ] GPU加速支持

## 注意事项

1. 本工具仅用于学习和个人使用
2. 请遵守抖音的使用条款
3. 不要用于商业用途
4. 处理的图片仅供个人使用

## 许可证

仅供学习使用

---

**当前版本**: v1.0.0
**更新日期**: 2025-11-14
