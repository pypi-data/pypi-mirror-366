class EEGProcessingConfig:
    """
    统一的EEG处理配置类，包含所有EEG处理相关的配置参数
    """

    def __init__(self,
                 # 滤波器配置
                 sample_rate=250.0,
                 eeg_channel_count=2,
                 isDCRemove=True,
                 isNotch=True,
                 isBandPass=True,
                 bpType=1,
                 fl=1.0,
                 fh=45.0,
                 fftWindow=512,
                 bandsWindow=512,
                 mindRestStep=10,
                 minRestWindow=512,
                 eegDataNum=10,
                 # 频段配置
                 delta=0.5,
                 theta=4.0,
                 alpha=8.0,
                 beta=13.0,
                 gamma_min=30.0,
                 gamma_max=50.0,
                 # 正念度系数
                 mindfulness_coefficients=None):
        """
        初始化EEG处理配置
        
        Args:
            # 滤波器参数
            sample_rate (float): 采样率，默认250Hz
            eeg_channel_count (int): EEG通道数，默认2
            isDCRemove (bool): 是否启用去基线，默认True
            isNotch (bool): 是否启用陷波滤波，默认True
            isBandPass (bool): 是否启用带通滤波，默认True
            bpType (int): 带通滤波器类型，1:Butterworth, 2:ChebyshevI, 3:ChebyshevII，默认1
            fl (float): 下截止频率，默认1Hz
            fh (float): 上截止频率，默认45Hz
            fftWindow (int): FFT窗长，必须是2的幂次，默认512
            bandsWindow (int): 频段分析窗长，必须是2的幂次，默认512
            mindRestStep (int): 正念放松分析步长，默认10
            minRestWindow (int): 正念放松分析窗长，必须是2的幂次，默认512
            eegDataNum (int): eeg每个通道的有效数据点数，默认10
            # 频段参数
            delta (float): Delta频段上限，默认0.5Hz
            theta (float): Theta频段上限，默认4Hz
            alpha (float): Alpha频段上限，默认8Hz
            beta (float): Beta频段上限，默认13Hz
            gamma_min (float): Gamma频段下限，默认30Hz
            gamma_max (float): Gamma频段上限，默认50Hz
            # 正念度系数
            mindfulness_coefficients (list): 正念度系数，5个元素的列表
        """
        # 滤波器配置
        self.sample_rate = sample_rate
        self.eeg_channel_count = eeg_channel_count
        self.isDCRemove = isDCRemove
        self.isNotch = isNotch
        self.isBandPass = isBandPass
        self.bpType = bpType
        self.fl = fl
        self.fh = fh
        self.fftWindow = fftWindow
        self.bandsWindow = bandsWindow
        self.mindRestStep = mindRestStep
        self.minRestWindow = minRestWindow
        self.eegDataNum = eegDataNum
        
        # 频段配置
        self.delta = delta
        self.theta = theta
        self.alpha = alpha
        self.beta = beta
        self.gamma_min = gamma_min
        self.gamma_max = gamma_max
        
        # 正念度系数
        self.mindfulness_coefficients = mindfulness_coefficients or [1.0, 1.0, 1.0, 1.0, 1.0]

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """
        验证配置参数的有效性
        """
        # 验证滤波器配置
        if self.sample_rate <= 0:
            raise ValueError("采样率必须大于0")

        if self.eeg_channel_count <= 0:
            raise ValueError("EEG通道数必须大于0")

        if self.bpType not in [1, 2, 3]:
            raise ValueError("带通滤波器类型必须是1(Butterworth), 2(ChebyshevI), 或3(ChebyshevII)")

        if self.fl >= self.fh:
            raise ValueError("下截止频率必须小于上截止频率")

        if self.fh >= self.sample_rate / 2:
            raise ValueError("上截止频率必须小于奈奎斯特频率(采样率/2)")

        # 检查窗长是否为2的幂次
        if not self._is_power_of_2(self.fftWindow):
            raise ValueError("FFT窗长必须是2的幂次")

        if not self._is_power_of_2(self.bandsWindow):
            raise ValueError("频段分析窗长必须是2的幂次")

        if not self._is_power_of_2(self.minRestWindow):
            raise ValueError("正念放松分析窗长必须是2的幂次")
            
        # 验证频段配置
        bands = [self.delta, self.theta, self.alpha, self.beta, self.gamma_min, self.gamma_max]
        for i in range(len(bands) - 1):
            if bands[i] >= bands[i + 1]:
                raise ValueError(f"频段配置必须递增: {bands}")
                
        # 验证正念度系数
        if len(self.mindfulness_coefficients) != 5:
            raise ValueError("正念度系数必须包含5个元素")

    def _is_power_of_2(self, n):
        """
        检查数字是否为2的幂次
        """
        return n > 0 and (n & (n - 1)) == 0

    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            # 滤波器配置
            'sample_rate': self.sample_rate,
            'eeg_channel_count': self.eeg_channel_count,
            'isDCRemove': self.isDCRemove,
            'isNotch': self.isNotch,
            'isBandPass': self.isBandPass,
            'bpType': self.bpType,
            'fl': self.fl,
            'fh': self.fh,
            'fftWindow': self.fftWindow,
            'bandsWindow': self.bandsWindow,
            'mindRestStep': self.mindRestStep,
            'minRestWindow': self.minRestWindow,
            'eegDataNum': self.eegDataNum,
            # 频段配置
            'delta': self.delta,
            'theta': self.theta,
            'alpha': self.alpha,
            'beta': self.beta,
            'gamma_min': self.gamma_min,
            'gamma_max': self.gamma_max,
            # 正念度系数
            'mindfulness_coefficients': self.mindfulness_coefficients
        }
        
    def get_bands_array(self):
        """
        获取频段配置数组（用于DLL调用）
        """
        return [self.delta, self.theta, self.alpha, self.beta, self.gamma_min, self.gamma_max]

    @classmethod
    def from_dict(cls, config_dict):
        """
        从字典创建配置对象
        """
        return cls(**config_dict)

    @classmethod
    def create_default(cls):
        """
        创建默认配置
        """
        return cls()

    @classmethod
    def create_high_quality(cls):
        """
        创建高质量处理配置
        """
        return cls(
            sample_rate=500.0,  # 更高采样率
            fftWindow=1024,  # 更大FFT窗长
            bandsWindow=1024,  # 更大频段窗长
            minRestWindow=1024  # 更大正念放松窗长
        )

    @classmethod
    def create_fast_processing(cls):
        """
        创建快速处理配置（降低计算复杂度）
        """
        return cls(
            fftWindow=256,  # 较小FFT窗长
            bandsWindow=256,  # 较小频段窗长
            minRestWindow=256,  # 较小正念放松窗长
            mindRestStep=20  # 更大步长
        )
        


    def __str__(self):
        """
        字符串表示
        """
        return f"EEGProcessingConfig(sample_rate={self.sample_rate}, channels={self.eeg_channel_count}, " \
               f"DCRemove={self.isDCRemove}, Notch={self.isNotch}, BandPass={self.isBandPass}, " \
               f"bands=[δ:{self.delta}, θ:{self.theta}, α:{self.alpha}, β:{self.beta}, γ:{self.gamma_min}-{self.gamma_max}])"





# 预定义的配置模板
DEFAULT_CONFIG = EEGProcessingConfig.create_default()
HIGH_QUALITY_CONFIG = EEGProcessingConfig.create_high_quality()
FAST_PROCESSING_CONFIG = EEGProcessingConfig.create_fast_processing()
