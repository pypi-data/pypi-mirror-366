import asyncio
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bleak import BleakGATTCharacteristic
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet
from biox.data.process import Processing
from biox.data.signal_config import SignalConfig


class EEGProcessor:
    def __init__(self):
        # 初始化信号处理器
        self.signal_config = SignalConfig.default()
        self.processor = Processing(self.signal_config)

        # 创建EEG处理配置
        self.eeg_config = self.signal_config.eeg_process

        # 统计信息
        self.packet_count = 0
        self.eeg_packet_count = 0
        self.start_time = time.time()

        print(f"初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"EEG配置: {self.eeg_config.eeg_channel_count}通道, {self.eeg_config.sample_rate}Hz")
        print(
            f"处理流程: DC去除={self.eeg_config.isDCRemove}, 陷波={self.eeg_config.isNotch}, 带通={self.eeg_config.isBandPass}")
        print("等待设备连接...\n")

    def process_eeg_data(self, parsed_data):
        """
        处理EEG数据包
        """
        try:
            # 检查是否为EEG数据包
            if parsed_data.pkg_type != 1:
                return

            self.eeg_packet_count += 1

            # 构造EEG数据包格式
            pkg_data = {
                'pkg_type': parsed_data.pkg_type,
                'brain_elec_channel': parsed_data.brain_elec,
                'pkgnum': parsed_data.pkgnum,
                'time_mark': parsed_data.time_mark
            }

            print(f"\n--- EEG数据包 #{self.eeg_packet_count} ---")
            print(f"时间戳: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            print(f"包序号: {pkg_data['pkgnum']}")
            print(f"通道数: {len(pkg_data['brain_elec_channel'])}")

            # 显示原始数据样本（只显示前2个通道，每个通道前10个数据点）
            if pkg_data['brain_elec_channel']:
                print("原始数据样本:")
                for ch_idx, channel_data in enumerate(pkg_data['brain_elec_channel'][:2]):  # 只显示前2个通道
                    if len(channel_data) >= 10:
                        data_sample = [f"{val:.2f}" for val in channel_data[:10]]  # 前10个数据点
                        print(f"  通道{ch_idx + 1}: [{', '.join(data_sample)}, ...]")
                    elif len(channel_data) > 0:
                        data_sample = [f"{val:.2f}" for val in channel_data]
                        print(f"  通道{ch_idx + 1}: [{', '.join(data_sample)}]")
                    else:
                        print(f"  通道{ch_idx + 1}: []")

            # 执行EEG数据处理
            print("\n执行EEG高级分析处理...")
            processing_start = time.time()

            result = self.processor.process_eeg_advanced_analysis(parsed_data.brain_elec, self.eeg_config)

            processing_time = (time.time() - processing_start) * 1000
            print(f"处理耗时: {processing_time:.2f}ms")

            # 显示处理结果
            self._display_processing_results(result)

        except Exception as e:
            print(f"\nEEG数据处理错误: {e}")
            import traceback
            traceback.print_exc()

    def _display_processing_results(self, result):
        """
        显示处理结果
        """
        print("\n处理结果:")

        # 处理后的数据
        if 'processed_data' in result and result['processed_data']:
            print(f"✓ 处理后数据: {len(result['processed_data'])}通道 x {len(result['processed_data'][0])}点")

            # 显示处理后数据样本（只显示前2个通道的所有数据点）
            print("处理后数据样本:")
            for ch_idx, channel_data in enumerate(result['processed_data'][:2]):  # 只显示前2个通道
                if len(channel_data) > 0:
                    data_sample = [f"{val:.2f}" for val in channel_data]  # 所有数据点
                    print(f"  通道{ch_idx + 1}: [{', '.join(data_sample)}]")
                else:
                    print(f"  通道{ch_idx + 1}: []")

        # 时域频段数据
        if 'time_e_s_multiple' in result and result['time_e_s_multiple']:
            print(f"✓ 时域频段数据: {len(result['time_e_s_multiple'])}个时间点")

            # 显示最新的频段数据
            if result['time_e_s_multiple']:
                latest_bands = result['time_e_s_multiple'][-1]
                print("最新频段功率:")
                band_names = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
                for ch_idx, channel_bands in enumerate(latest_bands[:2]):  # 只显示前2个通道
                    print(f"  通道{ch_idx + 1}:")
                    for band_idx, power in enumerate(channel_bands):
                        if band_idx < len(band_names):
                            print(f"    {band_names[band_idx]}: {power:.4f}")

        # 功率谱密度数据
        if 'psd_s_multiple' in result and result['psd_s_multiple']:
            print(f"功率谱密度: {len(result['psd_s_multiple'])}个时间点")

        # 正念放松度
        if 'mindfulness_restfulness_s' in result and result['mindfulness_restfulness_s']:
            print(f"正念放松度: {len(result['mindfulness_restfulness_s'])}通道")

            print("正念放松度:")
            for ch_idx, (mindfulness, restfulness) in enumerate(result['mindfulness_restfulness_s'][:2]):  # 只显示前2个通道
                print(f"  通道{ch_idx + 1}: 正念度={mindfulness:.4f}, 放松度={restfulness:.4f}")

        print("-" * 50)

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """
        数据接收回调函数
        """
        self.packet_count += 1

        # 解析数据包
        parsed_data = parse_packet(data)

        # 显示基本信息（每10个包显示一次统计）
        if self.packet_count % 10 == 0:
            elapsed_time = time.time() - self.start_time
            print(f"\n统计信息 (运行时间: {elapsed_time:.1f}s)")
            print(f"总包数: {self.packet_count}, EEG包数: {self.eeg_packet_count}")
            print(f"包接收率: {self.packet_count / elapsed_time:.1f} 包/秒")

        # 处理EEG数据
        if parsed_data and parsed_data.pkg_type == 1:
            self.process_eeg_data(parsed_data)
        elif parsed_data:
            # 显示非EEG包的基本信息
            if self.packet_count <= 5:  # 只显示前5个非EEG包
                print(f"收到数据包: 类型={parsed_data.pkg_type}, 序号={parsed_data.pkgnum}")


async def main():
    """
    主函数
    """
    processor = EEGProcessor()
    collector = None

    try:
        # 扫描并连接设备
        ble_device = None
        print("扫描Biox设备...")

        while ble_device is None:
            devices = await BluetoothScanner.scan()
            for device in devices:
                if device and device.device.name and "Biox" in device.device.name:
                    ble_device = device
                    print(f"找到设备: {device.device.name} ({device.device.address})")
                    break

            if ble_device is None:
                print("未找到Biox设备，3秒后重试...")
                await asyncio.sleep(3)

        # 创建收集器并连接
        print("\n连接设备...")
        collector = Collector(ble_device)

        # 注册数据处理回调
        await collector.register_notify(callback=processor.notification_handler)
        await collector.start()

        print("✓ 设备连接成功")
        print("\n开始数据采集...")

        # 停止数据采集（如果正在进行）
        await collector.stop_data_collection()

        # 开始数据采集
        await collector.start_data_collection()

        print("✓ 数据采集已开始")
        print("\n等待EEG数据...")
        print("按 Ctrl+C 停止采集\n")

        # 等待停止信号
        await collector.wait_for_stop()

    except KeyboardInterrupt:
        print("\n\n用户中断，正在停止...")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保释放连接
        if collector:
            try:
                await collector.stop()
                print("\n✓ 设备连接已释放")
            except Exception as e:
                print(f"释放连接时出错: {e}")

        # 显示最终统计
        elapsed_time = time.time() - processor.start_time
        print(f"\n最终统计:")
        print(f"运行时间: {elapsed_time:.1f}秒")
        print(f"总数据包: {processor.packet_count}")
        print(f"EEG数据包: {processor.eeg_packet_count}")
        print(f"平均包率: {processor.packet_count / elapsed_time:.1f} 包/秒")
        print("\n测试完成！")


if __name__ == '__main__':
    print("启动EEG测试...")
    print("请确保:")
    print("1. Biox设备已开机并处于可连接状态")
    print("2. 设备佩戴正确，能够采集到EEG信号")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
        sys.exit(1)
