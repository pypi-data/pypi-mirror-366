import asyncio
import os
import sys
import threading
import atexit
import time
from bleak import BleakGATTCharacteristic

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biox.visualization import RealtimePlotter
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet
from biox.data.process import Processing
from biox.data.signal_config import SignalConfig


class EEGAppWithBatteryMonitor:
    """
    EEG应用程序，包含电量监控功能。
    基于 eeg_processing_and_plot_test.py，增加了每5秒查询一次设备电量的功能。
    """

    def __init__(self):
        # Initialize the visualization component
        self.plotter = RealtimePlotter(
            num_channels=2,
            plot_duration=10.0,
            sampling_rate=250.0,
            update_interval=50,
            window_title='Real-time EEG with Battery Monitor',
            window_size=(1000, 800)
        )

        # Initialize data processing components
        self.signal_config = SignalConfig.default()
        self.processor = Processing(self.signal_config)
        self.eeg_config = self.signal_config.eeg_process

        # Device management
        self.collector = None
        self.ble_device = None
        
        # Application state
        self.running = True
        
        # Battery monitoring
        self.last_battery_check = 0
        self.battery_check_interval = 5.0  # 5秒检查一次电量

        # Register cleanup function
        atexit.register(self.cleanup_on_exit)
        self.plotter.add_close_callback(self.on_window_close)

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """Handle incoming EEG data and feed it to the plotter."""
        parsed = parse_packet(data)
        if parsed and parsed.pkg_type == 1:
            result = self.processor.process_eeg_data(parsed.brain_elec, self.eeg_config)
            self.plotter.add_multi_channel_data(result)

    async def check_battery_async(self):
        """异步方式检查电池电量"""
        current_time = time.time()
        if current_time - self.last_battery_check >= self.battery_check_interval:
            if self.ble_device and self.ble_device.connected:
                try:
                    battery_level = await self.ble_device.query_battery_level()
                    current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(f"[{current_time_str}] 设备电量: {battery_level}%")
                except Exception as e:
                    print(f"查询电池电量失败: {e}")
                
                self.last_battery_check = current_time

    async def connect_and_run(self):
        """Connect to device and start data collection."""
        try:
            # Find and connect to device
            print("扫描Biox设备...")
            while self.ble_device is None and self.running:
                devices = await BluetoothScanner.scan()
                for device in devices:
                    if device and device.device.name and "Biox" in device.device.name:
                        self.ble_device = device
                        print(f"找到设备: {device.device.name} ({device.device.address})")
                        break
                if self.ble_device is None:
                    print("未找到Biox设备，3秒后重试...")
                    await asyncio.sleep(3)

            print("连接设备...")
            self.collector = Collector(self.ble_device)
            await self.collector.register_notify(callback=self.notification_handler)
            await self.collector.start()
            await self.collector.stop_data_collection()
            await self.collector.start_data_collection()

            print("开始EEG数据采集和电量监控...")
            print("电量监控间隔: 5秒")
            print("-" * 50)

            # Keep async loop running and process Qt events
            while self.running:
                await asyncio.sleep(0.05)
                self.plotter.app.processEvents()
                await self.check_battery_async()
                
        except Exception as e:
            print(f"异步运行过程中发生错误: {e}")
        finally:
            if self.collector and self.collector.device.connected:
                try:
                    print("设备连接断开中...")
                    await self.collector.stop()
                    print("设备连接已断开")
                except Exception as e:
                    print(f"断开连接时发生错误: {e}")
            print("异步循环已停止")

    def on_window_close(self):
        """当窗口关闭时调用的回调函数"""
        print("检测到窗口关闭，程序即将退出...")
        self.running = False
        self.plotter.app.quit()

    def cleanup_on_exit(self):
        """Clean up resources on application exit."""
        print("程序退出时清理资源...")
        self.running = False

    def run(self):
        """Run the application."""
        self.plotter.start()

        def run_async():
            try:
                asyncio.run(self.connect_and_run())
            except Exception as e:
                print(f"异步线程发生错误: {e}")
            finally:
                print("异步线程已结束")

        async_thread = threading.Thread(target=run_async, daemon=True)
        async_thread.start()

        try:
            return self.plotter.run()
        finally:
            self.running = False


if __name__ == '__main__':
    print("EEG数据处理和电量监控程序")
    print("功能:")
    print("1. 实时EEG数据采集和可视化")
    print("2. 每5秒查询一次设备电量并打印")
    print("3. 在异步循环中查询电量，避免事件循环冲突")
    print("=" * 50)
    
    app = EEGAppWithBatteryMonitor()
    app.run()