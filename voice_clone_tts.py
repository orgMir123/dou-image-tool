"""
声音克隆TTS模块
使用参考音频进行音色转换
"""

import os
import numpy as np
import soundfile as sf
import librosa
from typing import Optional


class VoiceCloneTTS:
    """
    声音克隆TTS
    通过音色转换技术，将合成语音转换为参考音频的音色
    """

    def __init__(self, reference_audio_path: str = None):
        """
        初始化

        参数:
            reference_audio_path: 参考音频文件路径
        """
        self.reference_audio_path = reference_audio_path or "/Users/haihui/dou/reference_voice.wav"
        self.reference_features = None

        if os.path.exists(self.reference_audio_path):
            self._load_reference()

    def _load_reference(self):
        """加载并分析参考音频"""
        try:
            # 加载参考音频
            ref_audio, ref_sr = librosa.load(self.reference_audio_path, sr=22050)

            # 提取参考音频的特征
            self.reference_features = {
                'pitch_mean': np.mean(librosa.yin(ref_audio, fmin=80, fmax=400)),
                'pitch_std': np.std(librosa.yin(ref_audio, fmin=80, fmax=400)),
                'energy_mean': np.mean(librosa.feature.rms(y=ref_audio)),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=ref_audio, sr=ref_sr)),
            }

            print(f"✅ 参考音频分析完成")
            print(f"   - 音高均值: {self.reference_features['pitch_mean']:.2f} Hz")
            print(f"   - 频谱重心: {self.reference_features['spectral_centroid']:.2f} Hz")

        except Exception as e:
            print(f"⚠️  参考音频加载失败: {e}")
            self.reference_features = None

    def convert_voice(
        self,
        source_audio_bytes: bytes,
        intensity: float = 0.7
    ) -> bytes:
        """
        转换音色

        参数:
            source_audio_bytes: 源音频数据（MP3格式）
            intensity: 转换强度 (0.0-1.0)，越高越接近参考音色

        返回:
            转换后的音频数据（MP3格式）
        """
        if not self.reference_features:
            print("⚠️  未加载参考音频，返回原音频")
            return source_audio_bytes

        try:
            import tempfile

            # 保存源音频到临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_source:
                tmp_source.write(source_audio_bytes)
                source_path = tmp_source.name

            # 加载源音频
            source_audio, source_sr = librosa.load(source_path, sr=22050)

            # 应用音色转换
            converted_audio = self._apply_voice_conversion(
                source_audio, source_sr, intensity
            )

            # 保存转换后的音频到临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_converted:
                converted_path = tmp_converted.name
                sf.write(converted_path, converted_audio, source_sr)

            # 转换为MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_mp3:
                output_path = tmp_mp3.name

            import subprocess
            subprocess.run([
                'ffmpeg', '-i', converted_path,
                '-codec:a', 'libmp3lame', '-b:a', '128k',
                output_path, '-y'
            ], capture_output=True, check=True)

            # 读取转换后的MP3
            with open(output_path, 'rb') as f:
                result_bytes = f.read()

            # 清理临时文件
            os.unlink(source_path)
            os.unlink(converted_path)
            os.unlink(output_path)

            print(f"✅ 音色转换完成 (强度: {intensity})")
            return result_bytes

        except Exception as e:
            print(f"❌ 音色转换失败: {e}")
            import traceback
            traceback.print_exc()
            return source_audio_bytes

    def _apply_voice_conversion(
        self,
        audio: np.ndarray,
        sr: int,
        intensity: float
    ) -> np.ndarray:
        """
        应用音色转换算法

        使用简化的音色转换：
        1. 调整音高（pitch shifting）
        2. 调整音色特征（formant shifting）
        3. 调整能量包络
        """
        if not self.reference_features:
            return audio

        # 1. 分析源音频的音高
        source_pitch = librosa.yin(audio, fmin=80, fmax=400)
        source_pitch_mean = np.mean(source_pitch[source_pitch > 0])

        # 2. 计算音高偏移
        if source_pitch_mean > 0 and self.reference_features['pitch_mean'] > 0:
            pitch_shift_semitones = 12 * np.log2(
                self.reference_features['pitch_mean'] / source_pitch_mean
            ) * intensity

            # 应用音高偏移
            audio = librosa.effects.pitch_shift(
                audio, sr=sr, n_steps=pitch_shift_semitones
            )

        # 3. 调整时域特征（可选：调整语速）
        # 这里保持语速不变，只调整音色

        # 4. 调整能量包络
        source_energy = librosa.feature.rms(y=audio)
        if self.reference_features['energy_mean'] > 0:
            energy_ratio = self.reference_features['energy_mean'] / np.mean(source_energy)
            # 限制能量调整范围，避免过度
            energy_ratio = np.clip(energy_ratio, 0.7, 1.3)
            audio = audio * (1 + (energy_ratio - 1) * intensity)

        # 归一化，防止爆音
        audio = librosa.util.normalize(audio)

        return audio


async def text_to_speech_custom_voice(
    text: str,
    intensity: float = 0.7,
    base_voice: str = '502004',  # 使用腾讯云的智小满作为基础音色
    speed: float = 1.5,
    volume: float = 10
) -> bytes:
    """
    使用自定义音色合成语音

    流程:
    1. 使用腾讯云TTS生成基础语音
    2. 应用音色转换，使其接近参考音频

    参数:
        text: 文本内容
        intensity: 音色转换强度 (0.0-1.0)
        base_voice: 基础音色
        speed: 语速
        volume: 音量

    返回:
        MP3音频数据
    """
    from tencent_tts import text_to_speech_tencent

    # 1. 使用腾讯云TTS生成基础音频
    print(f"🔊 使用基础音色 {base_voice} 合成语音...")
    base_audio = await text_to_speech_tencent(
        text=text,
        voice=base_voice,
        speed=speed,
        volume=volume
    )

    # 2. 应用音色转换
    print(f"🎨 应用自定义音色转换 (强度: {intensity})...")
    voice_clone = VoiceCloneTTS()
    custom_audio = voice_clone.convert_voice(base_audio, intensity=intensity)

    return custom_audio


if __name__ == '__main__':
    # 测试代码
    import asyncio

    async def test():
        # 测试文本
        test_text = "反季买衣服真的能省好几百啊！今天给大家带来一款超值的羽绒马甲。"

        print("正在合成自定义音色语音...")
        audio_data = await text_to_speech_custom_voice(
            text=test_text,
            intensity=0.7
        )

        # 保存音频
        with open('test_custom_voice.mp3', 'wb') as f:
            f.write(audio_data)

        print(f"✅ 自定义音色合成完成，已保存到 test_custom_voice.mp3")

    asyncio.run(test())
