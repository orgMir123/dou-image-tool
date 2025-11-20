---
title: 批量抠图工具
emoji: 🖼️
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# 批量抠图工具

基于 rembg 的在线图片背景移除工具。

## 功能

- 上传图片（支持多张批量处理）
- 自动去除背景
- 下载处理后的 PNG 图片
- 商品文案生成

## 使用方法

1. 点击上传区域或拖拽图片
2. 选择合适的模型
3. 等待处理完成
4. 下载处理后的图片

## 支持的图片格式

PNG, JPG, JPEG, WebP, BMP

## 技术栈

- Flask
- rembg (U2-Net)
- OpenCV
- Pillow
