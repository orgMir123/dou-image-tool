# Cookie 登录设置指南

## 为什么需要保存 Cookie？

使用 Cookie 可以绕过抖音的滑块验证，实现自动化下载。你只需要手动登录**一次**，之后程序会自动使用保存的登录状态。

---

## 步骤1：保存登录 Cookie

在终端中运行：

```bash
cd /Users/haihui/dou
source venv/bin/activate
python save_cookies.py
```

程序会：
1. 打开浏览器，访问抖音精选联盟
2. 等待你手动完成登录
3. 登录成功后，按回车保存 Cookie

**重要提示：**
- 请确保完全登录成功，能看到精选联盟的主界面
- 如果有滑块验证，请手动完成
- Cookie 保存后会生成两个文件：`cookies.pkl` 和 `cookies.json`

---

## 步骤2：测试 Cookie 是否有效

运行测试脚本：

```bash
cd /Users/haihui/dou
source venv/bin/activate
python test_with_cookies.py
```

如果 Cookie 有效：
- 程序会自动加载登录状态
- 访问商品页不再需要滑块验证
- 自动下载所有商品图片

---

## 步骤3：正常使用

Cookie 保存后，使用主程序：

```bash
cd /Users/haihui/dou
source venv/bin/activate
python main.py
```

选择功能：
- **1. 下载商品图片** - 自动使用 Cookie，无需验证
- **4. 一键完成** - 下载 + 自动抠图

---

## 常见问题

**Q: Cookie 会过期吗？**
A: 会的。通常7-30天后需要重新保存。如果发现又需要验证，重新运行 `save_cookies.py`

**Q: 如何删除已保存的 Cookie？**
A: 删除 `cookies.pkl` 和 `cookies.json` 文件即可

**Q: 可以在多台电脑上使用同一个 Cookie 吗？**
A: 可以，但可能触发安全验证。建议每台电脑单独保存

**Q: Cookie 保存失败怎么办？**
A:
1. 确保已完全登录成功
2. 确保网络连接正常
3. 重新运行 `save_cookies.py` 重试

---

## 文件说明

- `cookies.pkl` - Cookie 二进制文件（程序使用）
- `cookies.json` - Cookie JSON 文件（方便查看）
- `cookie_manager.py` - Cookie 管理工具
- `save_cookies.py` - Cookie 保存脚本

---

**下一步：运行 `python save_cookies.py` 开始保存登录状态！**
