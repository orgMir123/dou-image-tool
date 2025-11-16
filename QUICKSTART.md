# 快速开始指南

## 当前已完成的功能

✅ 项目框架已搭建完成
✅ 图片去背景（抠图）功能已实现
✅ 抖音链接解析器已实现
✅ 交互式主程序已完成
✅ 虚拟环境和依赖已安装

## 立即测试

### 方法1：测试链接解析

```bash
cd /Users/haihui/dou
source venv/bin/activate
python link_parser.py
```

这会测试三种抖音链接格式的解析。

### 方法2：测试抠图功能（推荐）

**步骤1**: 准备测试图片

从你的抖音商品页面下载几张图片，放入 `input/` 目录：

```bash
# 可以手动拖拽图片到 input 文件夹
# 或使用命令行
open /Users/haihui/dou/input
```

**步骤2**: 运行抠图程序

```bash
cd /Users/haihui/dou
source venv/bin/activate
python image_processor.py
```

**步骤3**: 查看结果

处理后的图片会保存在 `output/` 目录，所有背景已去除，保存为PNG格式。

```bash
open /Users/haihui/dou/output
```

### 方法3：使用交互式界面

```bash
cd /Users/haihui/dou
source venv/bin/activate
python main.py
```

然后根据菜单选择功能：
- 选项1: 解析抖音链接
- 选项2: 批量处理图片
- 选项3: 处理单张图片

## 完整工作流程示例

假设你有一个抖音商品需要处理：

### 1. 复制商品链接

从抖音复制商品链接，比如：
```
https://v.douyin.com/LA0vanfVBPY/
```

### 2. 解析链接

```bash
python link_parser.py
# 或在 main.py 中选择功能1
```

### 3. 手动下载图片

- 在浏览器打开商品页面
- 右键保存商品图片到 `input/` 目录

### 4. 批量抠图

```bash
python image_processor.py
```

### 5. 获取结果

- 打开 `output/` 目录
- 所有图片已去除背景
- 可直接使用

## 首次运行注意事项

⚠️ **首次运行时会下载AI模型（约180MB）**

当你第一次运行抠图程序时，`rembg` 会自动下载U2-Net模型。这个过程需要：
- 时间：3-5分钟（取决于网速）
- 空间：约180MB
- 位置：`~/.u2net/u2net.onnx`

下载完成后，后续运行会很快。

## 测试建议

1. **先测试1-2张图片**
   - 验证抠图效果
   - 确认输出质量

2. **调整配置（如果需要）**
   - 编辑 `config.py`
   - 更改模型或参数

3. **批量处理**
   - 确认效果满意后
   - 可以处理更多图片

## 常见问题

**Q: 虚拟环境如何激活？**
```bash
cd /Users/haihui/dou
source venv/bin/activate
# 看到 (venv) 前缀表示激活成功
```

**Q: 如何退出虚拟环境？**
```bash
deactivate
```

**Q: 抠图效果不理想？**

编辑 `config.py`，尝试更精确的模型：
```python
REMBG_CONFIG = {
    'model': 'isnet-general-use',  # 更精确但慢
}
```

**Q: 图片太大怎么办？**

程序会自动保持高清，但如果需要压缩：
```python
IMAGE_CONFIG = {
    'max_size': (1500, 1500),  # 限制最大尺寸
}
```

## 项目状态

✅ **第一阶段完成** - 核心功能已实现
- 链接解析 ✓
- 图片抠图 ✓
- 批量处理 ✓

⏳ **第二阶段待开发** - 自动化功能
- 自动下载商品图片（需要突破反爬虫）
- Web界面
- 更多图片处理功能

## 下一步

1. 测试当前功能
2. 根据实际使用反馈调整
3. 如需新功能，随时告诉我

---

**项目路径**: `/Users/haihui/dou`
**文档**: 查看 `README.md` 了解完整功能
