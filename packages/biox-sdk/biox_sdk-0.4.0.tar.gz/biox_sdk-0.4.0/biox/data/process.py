import ctypes
import os.path
from ctypes import c_double, c_int, c_bool, POINTER

from biox.data.eeg_config import EEGProcessingConfig
from biox.data.signal_config import SignalConfig

signal_process_dll = None

DoubleArray = POINTER(c_double)


def init():
    """
    初始化signal_process.dll并设置所有函数的参数类型和返回值类型
    返回：已配置好的DLL实例
    """
    try:
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        current_file_directory = os.path.dirname(current_file_path)
        # 构建DLL文件的完整路径
        dll_directory = os.path.join(current_file_directory, "dll")
        dll_file = os.path.join(dll_directory, "signal_process.dll")
        # 加载DLL文件
        process_dll = ctypes.CDLL(dll_file)

        # ====== 脑电信号处理相关函数配置 ======
        # 初始化50Hz和100Hz陷波滤波器
        # 参数说明：
        # sample_rate (double): 采样率
        # channel (int): EEG总通道数
        process_dll.init_notch_filter.restype = None
        process_dll.init_notch_filter.argtypes = [c_double, c_int]

        # 50Hz陷波滤波器处理
        # 参数说明：
        # channel (int): EEG总通道数
        # input (DoubleArray): 输入数据数组
        # output (DoubleArray): 输出数据数组
        process_dll.run_notch_filter_50Hz.restype = None
        process_dll.run_notch_filter_50Hz.argtypes = [c_int, DoubleArray, DoubleArray]

        # 100Hz陷波滤波器处理
        # 参数说明：
        # channel (int): EEG总通道数
        # input (DoubleArray): 输入数据数组
        # output (DoubleArray): 输出数据数组
        process_dll.run_notch_filter_100Hz.restype = None
        process_dll.run_notch_filter_100Hz.argtypes = [c_int, DoubleArray, DoubleArray]

        # EEG基线去除
        # 参数说明：
        # channel (int): EEG总通道数
        # input (DoubleArray): 输入数据数组
        # output (DoubleArray): 输出数据数组（去基线后的数据）
        process_dll.run_dc_remove_eeg.restype = None
        process_dll.run_dc_remove_eeg.argtypes = [c_int, DoubleArray, DoubleArray]

        # 初始化用于脑电节律显示的带通滤波器
        # 参数说明：
        # sample_rate (double): 采样率
        # channel (int): 总通道数
        process_dll.init_eegbp_filter_eegbands.restype = None
        process_dll.init_eegbp_filter_eegbands.argtypes = [c_double, c_int]

        # 运行脑电节律带通滤波器
        # 参数说明：
        # channel (int): 当前通道
        # input (DoubleArray): 输入数据
        # y1~y5 (DoubleArray): 五个频段的输出数据
        process_dll.run_eegbp_filter_eegbands.restype = None
        process_dll.run_eegbp_filter_eegbands.argtypes = [c_int] + [DoubleArray] * 6

        # 初始化用于主画图时域视窗的带通滤波器
        # 参数说明：
        # sample_rate (double): 采样率
        # channel (int): 总通道数
        # fl (double): 下截止频率
        # fh (double): 上截止频率
        process_dll.init_eegbp_filter_draw.restype = None
        process_dll.init_eegbp_filter_draw.argtypes = [c_double, c_int, c_double, c_double]

        # 运行时域视窗带通滤波器
        # 参数说明：
        # filter_type (int): 滤波器类型(1:Butterworth, 2:ChebyshevI, 3:ChebyshevII)
        # channel (int): 当前通道
        # input (DoubleArray): 输入数据
        # output (DoubleArray): 滤波后数据
        process_dll.run_eegbp_filter_draw.restype = None
        process_dll.run_eegbp_filter_draw.argtypes = [c_int, c_int, DoubleArray, DoubleArray]

        # ====== FFT相关函数配置 ======
        # FFT功率谱计算
        # 参数说明：
        # channel (int): 通道号
        # sample_rate (double): 采样率
        # x (double): 输入数据
        # step (int): 步长
        # window (int): FFT窗长
        # ps (DoubleArray): 输出功率谱数据
        # psd (DoubleArray): 输出功率谱密度数据
        process_dll.fft_ps.restype = c_bool
        process_dll.fft_ps.argtypes = [c_int, c_double, c_double, c_int, c_int, DoubleArray, DoubleArray]

        # 脑电节律FFT功率谱计算
        # 参数说明：
        # channel (int): 通道号
        # sample_rate (double): 采样率
        # x (double): 输入数据
        # step (int): 步长
        # window (int): FFT窗长
        # psd_relative (DoubleArray): 相对功率谱密度(单位：uV^2/Hz)
        # psd_relative_percent (DoubleArray): 相对功率谱密度百分比
        process_dll.fft_ps_eegbands.restype = c_bool
        process_dll.fft_ps_eegbands.argtypes = [c_int, c_double, c_double, c_int, c_int, DoubleArray, DoubleArray]

        # ====== 近红外信号处理相关函数配置 ======
        # 初始化近红外带通滤波器
        # 参数说明：
        # sample_rate (double): 采样率
        # total_channel (int): 总通道数
        # fl (double): 下截止频率
        # fh (double): 上截止频率
        process_dll.init_irbp_filter.restype = None
        process_dll.init_irbp_filter.argtypes = [c_double, c_int, c_double, c_double]

        # 运行近红外带通滤波器
        # 参数说明：
        # filter_type (int): 滤波器类型(1:Butterworth, 2:ChebyshevI, 3:ChebyshevII)
        # channel (int): 当前通道
        # input (DoubleArray): 输入数据
        # output (DoubleArray): 滤波后数据
        process_dll.run_irbp_filter.restype = None
        process_dll.run_irbp_filter.argtypes = [c_int, c_int, DoubleArray, DoubleArray]

        # 近红外报告数据滤波处理
        # 参数说明：
        # filter_type (int): 滤波器类型
        # channel (int): 当前通道
        # input (DoubleArray): 输入数据
        # output (DoubleArray): 滤波后数据
        process_dll.run_irbp_filter_report.restype = None
        process_dll.run_irbp_filter_report.argtypes = [c_int, c_int, DoubleArray, DoubleArray]

        # 基线归零
        process_dll.clear_baseline.restype = None
        process_dll.clear_baseline.argtypes = []

        # 计算基线
        # 参数说明：
        # channel (int): 当前通道数（每个通道包含λ1,λ31,λ2,λ32四个波长数据）
        # sample_rate (double): 采样率
        # base_line_time (int): 用于计算基线的时间长度(秒)
        # step (int): 滑窗步长(点数)
        # input (DoubleArray): 输入数据
        # output (DoubleArray): 去基线后的数据
        process_dll.calc_baseline.restype = c_bool
        process_dll.calc_baseline.argtypes = [c_int, c_double, c_int, c_int, DoubleArray, DoubleArray]

        # 计算光密度
        # 参数说明：
        # channel (int): 当前通道数（每个通道包含λ1,λ31,λ2,λ32四个波长数据）
        # sample_rate (double): 采样率
        # base_line_time (int): 用于计算基线的时间长度(秒)
        # step (int): 滑窗步长(点数)
        # input (DoubleArray): 输入数据
        # output (DoubleArray): 各通道光密度数据
        process_dll.calc_od.restype = c_bool
        process_dll.calc_od.argtypes = [c_int, c_double, c_int, c_int, DoubleArray, DoubleArray]

        # 2波长血红蛋白浓度计算
        # 参数说明：
        # age (int): 受试者年龄
        # L (double): 发射到接收的距离(cm)
        # input (DoubleArray): OD数据数组(4个波长)
        # output (DoubleArray): [hbo,hb,hbt,SaO2]
        #   - hbo: 氧合血红蛋白浓度
        #   - hb: 脱氧血红蛋白浓度
        #   - hbt: 血红蛋白总浓度
        #   - SaO2: 血氧饱和度(%)
        process_dll.calc_hb_2wave.restype = c_bool
        process_dll.calc_hb_2wave.argtypes = [c_int, c_double, DoubleArray, DoubleArray]

        # 3波长血红蛋白浓度计算
        # 参数说明：
        # age (int): 受试者年龄
        # L (double): 发射到接收的距离(cm)
        # input (DoubleArray): OD数据数组(4个波长)
        # output (DoubleArray): [hbo,hb,hbt,SaO2]
        #   - hbo: 氧合血红蛋白浓度
        #   - hb: 脱氧血红蛋白浓度
        #   - hbt: 血红蛋白总浓度
        #   - SaO2: 血氧饱和度(%)
        process_dll.calc_hb_3wave.restype = c_bool
        process_dll.calc_hb_3wave.argtypes = [c_int, c_double, DoubleArray, DoubleArray]

        # ====== 其他功能函数配置 ======
        # 正念度和放松度计算
        # 参数说明：
        # channel (int): 当前通道
        # sample_rate (double): 采样率
        # x (double): 当前通道输入数据
        # step (int): 步长(点数)
        # window (int): FFT窗长(建议512，需为2的幂次)
        # output (DoubleArray): 输出数组[mindfulness,restfulness]
        process_dll.Mindfulness_Restfulness.restype = c_bool
        process_dll.Mindfulness_Restfulness.argtypes = [c_int, c_double, c_double, c_int, c_int, DoubleArray]

        # 清理FFT缓存
        process_dll.clear_fft_cache.restype = None
        process_dll.clear_fft_cache.argtypes = []

        # 设置脑电节律频率分割点
        # 参数说明：
        # sample_rate (double): 采样率
        # channel (int): 通道数
        # eegbands_user (DoubleArray): 6位数组，按顺序为6个频率分割点
        process_dll.set_eegbands.restype = None
        process_dll.set_eegbands.argtypes = [c_double, c_int, DoubleArray]

        # 设置正念度指标系数
        # 参数说明：
        # coefficients_user (DoubleArray): 5位数组，为mindfulness指标系数
        process_dll.set_coefficient_mainfulness.restype = None
        process_dll.set_coefficient_mainfulness.argtypes = [DoubleArray]

        # 信号质量评估
        # 参数说明：
        # Fs (double): 近红外采样率
        # age (int): 受试者年龄
        # L (double): 当前通道发射到接收的距离(cm)
        # current_channel (int): 当前通道
        # OD (DoubleArray): 当前通道的OD数组
        process_dll.get_signal_quality.restype = c_double
        process_dll.get_signal_quality.argtypes = [c_double, c_int, c_double, c_int, DoubleArray]

        # 血氧饱和度计算
        # 参数说明：
        # Fs (double): 采样率
        # near_infrared_ch1 (DoubleArray): S1D1或S2D5通道的近红外数据
        # near_infrared_ch2 (DoubleArray): S1D4或S2D8通道的近红外数据
        process_dll.calc_SaO2.restype = c_double
        process_dll.calc_SaO2.argtypes = [c_double, DoubleArray, DoubleArray]

        return process_dll
    except OSError as e:
        print(f"Failed to load DLL: {e}")


class Processing:
    def __init__(self, config: SignalConfig):
        """
        初始化信号处理类
        Args:
            config: 信号处理配置对象
        """
        self.config = config
        self.signal_process = init()  # 初始化DLL

        # 初始化
        self.init()

    def init(self):
        """初始化所有处理参数和数组"""
        # 脑电初始化
        channel = self.config.eeg_process.eeg_channel_count

        # 初始化滤波器
        self.signal_process.init_notch_filter(
            self.config.eeg_process.sample_rate,
            channel
        )
        self.signal_process.init_eegbp_filter_eegbands(
            self.config.eeg_process.sample_rate,
            channel
        )
        self.signal_process.init_eegbp_filter_draw(
            self.config.eeg_process.sample_rate,
            channel,
            self.config.eeg_process.fl,
            self.config.eeg_process.fh
        )

        # 近红外初始化
        self.signal_process.clear_baseline()
        self.signal_process.init_irbp_filter(
            self.config.ir_filter.ir_sample_rate,
            self.config.ir_filter.ir_channel,
            self.config.ir_filter.fl,
            self.config.ir_filter.fh
        )

        # 设置脑电节律
        eegbands = (c_double * 6)(*[0.5, 4, 8, 13, 30, 50])  # 默认频段分割点
        self.set_eegbands(
            self.config.eeg_process.sample_rate,
            self.config.eeg_process.eeg_channel_count,
            eegbands
        )

    # ====== EEG相关方法 ======
    def run_notch_filter_50hz(self, channel, input_data, output_data):
        """
        50Hz陷波滤波器处理
        Args:
            channel: EEG总通道数
            input_data: 输入数据数组
            output_data: 输出数据数组
        """
        self.signal_process.run_notch_filter_50Hz(channel, input_data, output_data)

    def run_notch_filter_100hz(self, channel, input_data, output_data):
        """
        100Hz陷波滤波器处理
        Args:
            channel: EEG总通道数
            input_data: 输入数据数组
            output_data: 输出数据数组
        """
        self.signal_process.run_notch_filter_100Hz(channel, input_data, output_data)

    def run_dc_remove_eeg(self, channel, input_data, output_data):
        """
        EEG基线去除
        Args:
            channel: EEG总通道数
            input_data: 输入数据数组
            output_data: 输出数据数组（去基线后的数据）
        """
        self.signal_process.run_dc_remove_eeg(channel, input_data, output_data)

    def run_eegbp_filter_eegbands(self, channel, input_data, y1, y2, y3, y4, y5):
        """
        运行脑电节律带通滤波器
        Args:
            channel: 当前通道
            input_data: 输入数据
            y1~y5: 五个频段的输出数据
        """
        self.signal_process.run_eegbp_filter_eegbands(channel, input_data, y1, y2, y3, y4, y5)

    def run_eegbp_filter_draw(self, filter_type, channel, input_data, output_data):
        """
        运行时域视窗带通滤波器
        Args:
            filter_type: 滤波器类型(1:Butterworth, 2:ChebyshevI, 3:ChebyshevII)
            channel: 当前通道
            input_data: 输入数据
            output_data: 滤波后数据
        """
        self.signal_process.run_eegbp_filter_draw(filter_type, channel, input_data, output_data)

    # ====== FFT相关方法 ======

    def fft_ps(self, channel, sample_rate, x, step, window, ps, psd):
        """
        FFT功率谱计算
        Args:
            channel: 通道号
            sample_rate: 采样率
            x: 输入数据
            step: 步长
            window: FFT窗长
            ps: 输出功率谱数据
            psd: 输出功率谱密度数据
        Returns:
            是否成功
        """
        return self.signal_process.fft_ps(channel, sample_rate, x, step, window, ps, psd)

    def fft_ps_eegbands(self, channel, sample_rate, x, step, window, psd_relative, psd_relative_percent):
        """
        脑电节律FFT功率谱计算
        Args:
            channel: 通道号
            sample_rate: 采样率
            x: 输入数据
            step: 步长
            window: FFT窗长
            psd_relative: 相对功率谱密度(单位：uV^2/Hz)
            psd_relative_percent: 相对功率谱密度百分比
        Returns:
            是否成功
        """
        return self.signal_process.fft_ps_eegbands(channel, sample_rate, x, step, window, psd_relative,
                                                   psd_relative_percent)

    # ====== 近红外信号处理相关方法 ======

    def run_irbp_filter(self, filter_type, channel, input_data, output_data):
        """
        运行近红外带通滤波器
        Args:
            filter_type: 滤波器类型(1:Butterworth, 2:ChebyshevI, 3:ChebyshevII)
            channel: 当前通道
            input_data: 输入数据
            output_data: 滤波后数据
        """
        self.signal_process.run_irbp_filter(filter_type, channel, input_data, output_data)

    def run_irbp_filter_report(self, filter_type, channel, input_data, output_data):
        """
        近红外报告数据滤波处理
        Args:
            filter_type: 滤波器类型
            channel: 当前通道
            input_data: 输入数据
            output_data: 滤波后数据
        """
        self.signal_process.run_irbp_filter_report(filter_type, channel, input_data, output_data)

    def clear_baseline(self):
        """基线归零"""
        self.signal_process.clear_baseline()

    def calc_baseline(self, channel, sample_rate, base_line_time, step, input_data, output_data):
        """
        计算基线
        Args:
            channel: 当前通道数（每个通道包含λ1,λ31,λ2,λ32四个波长数据）
            sample_rate: 采样率
            base_line_time: 用于计算基线的时间长度(秒)
            step: 滑窗步长(点数)
            input_data: 输入数据
            output_data: 去基线后的数据
        Returns:
            是否成功
        """
        return self.signal_process.calc_baseline(channel, sample_rate, base_line_time, step, input_data, output_data)

    def calc_od(self, channel, sample_rate, base_line_time, step, input_data, output_data):
        """
        计算光密度
        Args:
            channel: 当前通道数（每个通道包含λ1,λ31,λ2,λ32四个波长数据）
            sample_rate: 采样率
            base_line_time: 用于计算基线的时间长度(秒)
            step: 滑窗步长(点数)
            input_data: 输入数据
            output_data: 各通道光密度数据
        Returns:
            是否成功
        """
        return self.signal_process.calc_od(channel, sample_rate, base_line_time, step, input_data, output_data)

    def calc_hb_2wave(self, age, L, input_data, output_data):
        """
        2波长血红蛋白浓度计算
        Args:
            age: 受试者年龄
            L: 发射到接收的距离(cm)
            input_data: OD数据数组(4个波长)
            output_data: [hbo,hb,hbt,SaO2]
        Returns:
            是否成功
        """
        return self.signal_process.calc_hb_2wave(age, L, input_data, output_data)

    def calc_hb_3wave(self, age, L, input_data, output_data):
        """
        3波长血红蛋白浓度计算
        Args:
            age: 受试者年龄
            L: 发射到接收的距离(cm)
            input_data: OD数据数组(4个波长)
            output_data: [hbo,hb,hbt,SaO2]
        Returns:
            是否成功
        """
        return self.signal_process.calc_hb_3wave(age, L, input_data, output_data)

    # ====== 其他功能方法 ======

    def mindfulness_restfulness(self, channel, sample_rate, x, step, window, output_data):
        """
        正念度和放松度计算
        Args:
            channel: 当前通道
            sample_rate: 采样率
            x: 当前通道输入数据
            step: 步长(点数)
            window: FFT窗长(建议512，需为2的幂次)
            output_data: 输出数组[mindfulness,restfulness]
        Returns:
            是否成功
        """
        return self.signal_process.Mindfulness_Restfulness(channel, sample_rate, x, step, window, output_data)

    def clear_fft_cache(self):
        """清理FFT缓存"""
        self.signal_process.clear_fft_cache()

    def set_eegbands(self, sample_rate, channel, eegbands_user):
        """
        设置脑电节律频率分割点
        Args:
            sample_rate: 采样率
            channel: 通道数
            eegbands_user: 6位数组，按顺序为6个频率分割点
        """
        self.signal_process.set_eegbands(sample_rate, channel, eegbands_user)

    def set_coefficient_mindfulness(self, coefficients_user):
        """
        设置正念度指标系数
        Args:
            coefficients_user: 5位数组，为mindfulness指标系数
        """
        self.signal_process.set_coefficient_mainfulness(coefficients_user)

    def get_signal_quality(self, Fs, age, L, current_channel, OD):
        """
        信号质量评估
        Args:
            Fs: 近红外采样率
            age: 受试者年龄
            L: 当前通道发射到接收的距离(cm)
            current_channel: 当前通道
            OD: 当前通道的OD数组
        Returns:
            信号质量评分
        """
        return self.signal_process.get_signal_quality(Fs, age, L, current_channel, OD)

    def calc_sao2(self, Fs, near_infrared_ch1, near_infrared_ch2):
        """
        血氧饱和度计算
        Args:
            Fs: 采样率
            near_infrared_ch1: S1D1或S2D5通道的近红外数据
            near_infrared_ch2: S1D4或S2D8通道的近红外数据
        Returns:
            血氧饱和度值
        """
        return self.signal_process.calc_SaO2(Fs, near_infrared_ch1, near_infrared_ch2)

    # ====== 高级封装方法（保持原有的便捷方法） ======

    def process_eeg_data(self, datas, config: EEGProcessingConfig):
        """
        处理脑电数据（所有通道）
        该函数为示例函数，可按照该函数的处理方法对eeg数据进行处理

        Args:
            config: EEGProcessingConfig
            datas: 二维列表，形状为 (num_channels, num_samples)
                                每个子列表是一个通道的时间序列数据

        Returns:
            处理后的二维列表，形状相同
        """
        num_channels = config.eeg_channel_count
        num_samples = config.eegDataNum

        # 创建输出数据结构
        processed_data = [[0.0] * num_samples for _ in range(num_channels)]

        # 对每个时间点进行处理
        for i in range(num_samples):
            # 创建当前时间点的输入数组（包含所有通道的数据）
            input_data = (c_double * num_channels)()
            for ch in range(num_channels):
                input_data[ch] = datas[ch][i]

            output_data = (c_double * num_channels)()
            self.run_dc_remove_eeg(
                num_channels,
                input_data,
                output_data)
            # 创建输出数组
            output_50 = (c_double * num_channels)()
            output_100 = (c_double * num_channels)()
            output_eeg_bp = (c_double * num_channels)()

            # 运行50Hz陷波滤波器
            self.run_notch_filter_50hz(
                num_channels,  # 通道数
                output_data,  # 输入数组（当前时间点所有通道的数据）
                output_50  # 输出数组
            )

            # 运行100Hz滤波器
            self.run_notch_filter_100hz(
                num_channels,  # 通道数
                output_50,  # 输入数组（50Hz滤波后的结果）
                output_100  # 输出数组
            )

            self.run_eegbp_filter_draw(
                1,  # Butterworth过滤类型
                num_channels,  # 通道数
                output_100,  # 输入数组（100Hz滤波后的结果）
                output_eeg_bp  # 输出数组
            )

            # 将结果写回输出数据结构
            for ch in range(num_channels):
                processed_data[ch][i] = output_eeg_bp[ch]

        return processed_data

    def process_ir_data(self, channel, data):
        """
        处理近红外数据
        Args:
            channel: 通道号
            data: 输入数据数组
        Returns:
            处理后的数据
        """
        # 创建输入输出数组
        input_array = (c_double * len(data))(*data)
        output_array = (c_double * len(data))()

        # 运行带通滤波器
        # 使用Butterworth滤波器
        self.run_irbp_filter(1, channel, input_array, output_array)

        return list(output_array)

    def calculate_od(self, channel, data, sample_rate, base_line_time=10, step=2):
        """
        计算光密度
        Args:
            channel: 通道号
            data: 输入数据数组
            sample_rate: 采样率
            base_line_time: 基线时间（秒）
            step: 步长
        Returns:
            光密度数据
        """
        input_array = (c_double * len(data))(*data)
        output_array = (c_double * len(data))()

        success = self.calc_od(
            channel,
            sample_rate,
            base_line_time,
            step,
            input_array,
            output_array
        )

        if success:
            return list(output_array)
        return None

    def calculate_hb_concentration(self, age, L, od_data, use_3wave=False):
        """
        计算血红蛋白浓度
        Args:
            age: 受试者年龄
            L: 发射到接收的距离(cm)
            od_data: OD数据数组
            use_3wave: 是否使用3波长计算
        Returns:
            [hbo, hb, hbt, SaO2] 或 None
        """
        input_array = (c_double * len(od_data))(*od_data)
        output_array = (c_double * 4)()

        if use_3wave:
            success = self.signal_process.calc_hb_3wave(age, L, input_array, output_array)
        else:
            success = self.calc_hb_2wave(age, L, input_array, output_array)

        if success:
            return list(output_array)
        return None

    def calculate_mindfulness_restfulness(self, channel, data, sample_rate, step=10, window=512):
        """
        计算正念度和放松度
        Args:
            channel: 通道号
            data: 输入数据
            sample_rate: 采样率
            step: 步长
            window: FFT窗长
        Returns:
            [mindfulness, restfulness] 或 None
        """
        output_array = (c_double * 2)()

        success = self.mindfulness_restfulness(
            channel,
            sample_rate,
            data,
            step,
            window,
            output_array
        )

        if success:
            return list(output_array)
        return None

    def get_signal_quality(self, sample_rate, age, L, channel, od_data):
        """
        获取信号质量评分
        Args:
            sample_rate: 采样率
            age: 受试者年龄
            L: 发射到接收的距离(cm)
            channel: 通道号
            od_data: OD数据数组
        Returns:
            信号质量评分
        """
        input_array = (c_double * len(od_data))(*od_data)
        return self.get_signal_quality(sample_rate, age, L, channel, input_array)

    def calculate_sao2(self, sample_rate, ch1_data, ch2_data):
        """
        计算血氧饱和度
        Args:
            sample_rate: 采样率
            ch1_data: S1D1或S2D5通道数据
            ch2_data: S1D4或S2D8通道数据
        Returns:
            血氧饱和度值
        """
        ch1_array = (c_double * len(ch1_data))(*ch1_data)
        ch2_array = (c_double * len(ch2_data))(*ch2_data)
        return self.calc_SaO2(sample_rate, ch1_array, ch2_array)

    def process_eeg_advanced_analysis(self, pkg_data, config: EEGProcessingConfig):
        """
        EEG高级分析处理函数
        
        该函数在基础EEG数据处理的基础上，额外提供以下高级分析功能：
        - 脑电节律频段滤波分析
        - FFT功率谱计算
        - 脑电节律FFT分析
        - 正念度和放松度计算
        
        Args:
            pkg_data: 脑电通道数据 [channel][sample]
            config: EEG处理配置对象
        
        Returns:
            dict: 处理结果，包含：
                - processed_data: 基础处理后的脑电数据（复用process_eeg_data的结果）
                - time_e_s_multiple: 时域频段数据
                - psd_s_multiple: FFT功率谱密度数据
                - psd_relative_s_multiple: 脑电节律相对功率谱密度数据
                - psd_relative_percent_s_multiple: 脑电节律相对功率谱密度百分比数据
                - mindfulness_restfulness_s: 正念度和放松度数据
                - pkg_data: 更新后的包数据
        """
        # 1. 首先使用基础的process_eeg_data函数进行标准EEG数据处理
        processed_data = self.process_eeg_data(pkg_data, config)

        # 2. 进行高级分析处理
        eeg_config = config
        channel = eeg_config.eeg_channel_count
        eeg_data_num = eeg_config.eegDataNum

        # 初始化高级分析结果数组
        time_e_s_multiple = []
        psd_s_multiple = []
        psd_relative_s_multiple = []
        psd_relative_percent_s_multiple = []
        mindfulness_restfulness_s = [[0.0, 0.0] for _ in range(channel)]

        # 循环处理每个EEG数据点进行高级分析
        for i in range(eeg_data_num):
            # 创建当前时间点的输入数组（使用原始数据进行高级分析）
            brain_data_original = (c_double * channel)()
            brain_data_processed = (c_double * channel)()
            
            for current_channel in range(channel):
                brain_data_original[current_channel] = pkg_data[current_channel][i]
                brain_data_processed[current_channel] = processed_data[current_channel][i]

            # 创建去基线输出数组（用于高级分析）
            remove_output = (c_double * channel)()
            self.run_dc_remove_eeg(channel, brain_data_original, remove_output)

            # 频段滤波输出数组（用于脑电节律分析）
            e1 = (c_double * channel)()  # Delta频段 (0.5-4Hz)
            e2 = (c_double * channel)()  # Theta频段 (4-8Hz)
            e3 = (c_double * channel)()  # Alpha频段 (8-13Hz)
            e4 = (c_double * channel)()  # Beta频段 (13-30Hz)
            e5 = (c_double * channel)()  # Gamma频段 (30-50Hz)

            # 脑电节律频段滤波（用于EEG Bands视图）
            self.run_eegbp_filter_eegbands(channel, remove_output, e1, e2, e3, e4, e5)

            # 初始化当前时间点的结果数组
            time_e_s = []
            psd_s = []
            psd_relative_s = []
            psd_relative_percent_s = []

            # 处理每个通道的高级分析
            for current_channel in range(channel):
                # 保存时域频段数据
                time_e_s.append([
                    e1[current_channel],  # Delta
                    e2[current_channel],  # Theta
                    e3[current_channel],  # Alpha
                    e4[current_channel],  # Beta
                    e5[current_channel]   # Gamma
                ])

                # FFT功率谱计算（用于Spectrum视图）
                ps_output = (c_double * (eeg_config.fftWindow // 2 + 1))()
                psd_output = (c_double * (eeg_config.fftWindow // 2 + 1))()

                step = 10  # FFT步长
                self.fft_ps(
                    current_channel,
                    eeg_config.sample_rate,
                    brain_data_processed[current_channel],  # 使用处理后的数据
                    step,
                    eeg_config.fftWindow,
                    ps_output,
                    psd_output
                )

                # 保存功率谱密度数据
                psd_s.append(list(psd_output))

                # 脑电节律FFT计算（用于EEG Bands视图）
                psd_relative_output = (c_double * 5)()
                psd_relative_percent_output = (c_double * 5)()

                self.fft_ps_eegbands(
                    current_channel,
                    eeg_config.sample_rate,
                    remove_output[current_channel],  # 使用去基线后的原始数据
                    step,
                    eeg_config.bandsWindow,
                    psd_relative_output,
                    psd_relative_percent_output
                )

                # 保存相对功率谱密度数据
                psd_relative_s.append(list(psd_relative_output))
                psd_relative_percent_s.append(list(psd_relative_percent_output))

                # 正念度和放松度计算
                mindfulness_output = (c_double * 2)()
                self.mindfulness_restfulness(
                    current_channel,
                    eeg_config.sample_rate,
                    remove_output[current_channel],  # 使用去基线后的原始数据
                    eeg_config.mindRestStep,
                    eeg_config.minRestWindow,
                    mindfulness_output
                )

                mindfulness_restfulness_s[current_channel] = list(mindfulness_output)

            # 保存当前时间点的所有高级分析结果
            time_e_s_multiple.append(time_e_s)
            psd_s_multiple.append(psd_s)
            psd_relative_s_multiple.append(psd_relative_s)
            psd_relative_percent_s_multiple.append(psd_relative_percent_s)

        return {
            'processed_data': processed_data,  # 基础处理后的数据
            'time_e_s_multiple': time_e_s_multiple,  # 时域频段数据
            'psd_s_multiple': psd_s_multiple,  # FFT功率谱密度数据
            'psd_relative_s_multiple': psd_relative_s_multiple,  # 脑电节律相对功率谱密度
            'psd_relative_percent_s_multiple': psd_relative_percent_s_multiple,  # 脑电节律相对功率谱密度百分比
            'mindfulness_restfulness_s': mindfulness_restfulness_s,  # 正念度和放松度
            'pkg_data': pkg_data  # 返回处理后的脑电通道数据
        }
