"""
文本智能分段模块
用于将长文本按照标点符号和语义智能切分成多个片段
"""

import re


class TextSplitter:
    """智能文本分段器"""

    def __init__(self, max_length: int = 150):
        """
        初始化分段器

        参数:
            max_length: 每段最大长度
        """
        self.max_length = max_length

    def split(self, text: str) -> list:
        """
        智能分段

        策略:
        1. 优先按句号、问号、感叹号等强标点分段
        2. 其次按逗号、分号等弱标点分段
        3. 确保每段不超过max_length

        参数:
            text: 要分段的文本

        返回:
            分段后的文本列表
        """
        if len(text) <= self.max_length:
            return [text]

        # 第一步：按强标点符号（句号、问号、感叹号）预分段
        # 使用正则表达式保留标点符号
        strong_pattern = r'([。！？!?]+)'
        segments = re.split(strong_pattern, text)

        # 重新组合，保留标点符号
        pre_segments = []
        for i in range(0, len(segments), 2):
            if i + 1 < len(segments):
                pre_segments.append(segments[i] + segments[i + 1])
            elif segments[i]:  # 最后一段可能没有标点
                pre_segments.append(segments[i])

        # 第二步：合并短段，拆分长段
        result = []
        current = ""

        for segment in pre_segments:
            # 如果当前段为空，直接加入
            if not current:
                if len(segment) <= self.max_length:
                    current = segment
                else:
                    # 段落太长，需要进一步拆分
                    result.extend(self._split_long_segment(segment))
            else:
                # 尝试合并
                if len(current) + len(segment) <= self.max_length:
                    current += segment
                else:
                    # 无法合并，保存当前段
                    result.append(current)
                    if len(segment) <= self.max_length:
                        current = segment
                    else:
                        # 段落太长，需要进一步拆分
                        result.extend(self._split_long_segment(segment))
                        current = ""

        # 添加最后一段
        if current:
            result.append(current)

        return result

    def _split_long_segment(self, segment: str) -> list:
        """
        拆分过长的段落
        按逗号、顿号等弱标点符号拆分

        参数:
            segment: 过长的段落

        返回:
            拆分后的段落列表
        """
        if len(segment) <= self.max_length:
            return [segment]

        # 按弱标点符号（逗号、顿号、分号等）分段
        weak_pattern = r'([，、；,;]+)'
        parts = re.split(weak_pattern, segment)

        # 重新组合
        sub_segments = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                sub_segments.append(parts[i] + parts[i + 1])
            elif parts[i]:
                sub_segments.append(parts[i])

        # 合并短段
        result = []
        current = ""

        for sub in sub_segments:
            if not current:
                current = sub
            elif len(current) + len(sub) <= self.max_length:
                current += sub
            else:
                result.append(current)
                current = sub

        if current:
            result.append(current)

        # 如果还是有段落过长，强制按字数切分
        final_result = []
        for part in result:
            if len(part) <= self.max_length:
                final_result.append(part)
            else:
                # 强制切分
                final_result.extend(self._force_split(part))

        return final_result

    def _force_split(self, text: str) -> list:
        """
        强制按字数切分（最后的保底措施）

        参数:
            text: 要切分的文本

        返回:
            切分后的文本列表
        """
        result = []
        pos = 0

        while pos < len(text):
            end = pos + self.max_length
            result.append(text[pos:end])
            pos = end

        return result


if __name__ == '__main__':
    # 测试代码
    splitter = TextSplitter(max_length=150)

    # 测试文本
    test_text = """
    反季买衣服真的能省好几百啊。厂家清仓一批秋冬爆款的羽绒保暖马甲了，今天的价格低到我亲眼见了才敢信。这可是去年的大爆款，原来一直卖的老贵了，老板清点库存，发现颜色尺码不全，只剩一百多件，才线上不计成本，清了具体多少。你点开小黄车看看，妥妥的捡大便宜，抢到的大哥收到货，保准高兴的合不拢嘴。老顾客都清楚这马甲的品质，做工没话说，上身舒适保暖，还毫无束缚感。内里填的是优质羽绒，蓬松度够所问性强，穿着轻薄不臃肿，还特别显时尚大气，款式高档又耐看，现在入手正适合穿，经典大方的版型，不挑年龄身材，内搭外穿都出彩。配羊毛衫卫衣，既舒适又帅气，立体剪裁设计，让上身挺括有型，板正利落质感，直接拉满品牌专卖店。直发正品有保障，买着放心。秋冬有这么一件马甲穿搭，直接省事儿，保暖时髦两手抓，关键价格还这么划算，趁活动赶紧冲下方小黄车，建议带两件换着穿，不管谁穿都好看。这波福利可别错过。
    """.strip()

    print(f"原文长度: {len(test_text)} 字符\n")
    print(f"原文:\n{test_text}\n")
    print("=" * 60)

    segments = splitter.split(test_text)

    print(f"\n分段结果（共 {len(segments)} 段）:\n")
    for i, seg in enumerate(segments, 1):
        print(f"第 {i} 段（{len(seg)} 字符）:")
        print(seg)
        print("-" * 60)
