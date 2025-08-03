from dataclasses import dataclass

from biox.data.eeg_config import EEGProcessingConfig


@dataclass
class IRFilterConfig:
    """近红外滤波器配置"""
    ir_sample_rate: float  # 近红外采样率
    ir_channel: int  # 近红外通道数
    fl: float  # 下截止频率
    fh: float  # 上截止频率


@dataclass
class SignalConfig:
    """信号处理配置"""
    eeg_process: EEGProcessingConfig  # 脑电滤波器配置
    ir_filter: IRFilterConfig  # 近红外滤波器配置

    @classmethod
    def default(cls) -> 'SignalConfig':
        """创建默认配置"""
        return cls(
            eeg_process=EEGProcessingConfig.create_default(),
            ir_filter=IRFilterConfig(
                ir_sample_rate=10.0,
                ir_channel=8,
                fl=0.01,
                fh=0.5
            )
        )
