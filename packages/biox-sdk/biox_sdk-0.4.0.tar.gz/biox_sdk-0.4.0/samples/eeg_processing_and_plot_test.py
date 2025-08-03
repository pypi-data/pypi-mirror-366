"""
Refactored Sample7 - Using Decoupled Visualization

This is a refactored version of sample7.py that uses the new decoupled
RealtimePlotter for visualization, demonstrating the separation of concerns.
"""

import asyncio
import os
import sys
import threading
import atexit
from bleak import BleakGATTCharacteristic

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biox.visualization import RealtimePlotter
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet
from biox.data.process import Processing
from biox.data.signal_config import SignalConfig


class EEGApp:
    """
    Simplified EEG application using the decoupled visualization module.
    """

    def __init__(self):
        # Initialize the visualization component
        self.plotter = RealtimePlotter(
            num_channels=2,
            plot_duration=10.0,
            sampling_rate=250.0,
            update_interval=50,
            window_title='Real-time EEG Visualization - Refactored',
            window_size=(1000, 800)
        )

        # Initialize data processing components
        self.signal_config = SignalConfig.default()
        self.processor = Processing(self.signal_config)

        # 创建EEG处理配置
        self.eeg_config = self.signal_config.eeg_process

        # Device management
        self.collector = None
        
        # Application state
        self.running = True

        # Register cleanup function
        atexit.register(self.cleanup_on_exit)
        
        # Register window close callback
        self.plotter.add_close_callback(self.on_window_close)

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """Handle incoming EEG data and feed it to the plotter."""
        # start_time = time.time()

        parsed = parse_packet(data)
        if parsed and parsed.pkg_type == 1:
            # Process EEG data
            result = self.processor.process_eeg_data(parsed.brain_elec, self.eeg_config)

            # Feed data to the plotter - this is now completely decoupled!
            self.plotter.add_multi_channel_data(result)

            # Monitor processing time
            # proc_time = (time.time() - start_time) * 1000
            # if proc_time > 50:
            #     print(f"Warning: Processing took {proc_time:.2f}ms")

    async def connect_and_run(self):
        """Connect to device and start data collection."""
        try:
            # Find and connect to device
            ble_device = None
            print("扫描Biox设备...")
            while ble_device is None and self.running:
                devices = await BluetoothScanner.scan()
                for device in devices:
                    if device and device.device.name and "Biox" in device.device.name:
                        ble_device = device
                        print(f"找到设备: {device.device.name} ({device.device.address})")
                        break
                if ble_device is None:
                    print("未找到Biox设备，3秒后重试...")
                    await asyncio.sleep(3)

            print("\n连接设备...")
            self.collector = Collector(ble_device)
            await self.collector.register_notify(callback=self.notification_handler)
            await self.collector.start()
            await self.collector.stop_data_collection()
            await self.collector.start_data_collection()

            # Keep async loop running and process Qt events
            while self.running:
                await asyncio.sleep(0.05)
                self.plotter.app.processEvents()
                
        except Exception as e:
            print(f"异步运行过程中发生错误: {e}")
        finally:
            # 简单地断开连接
            if self.collector.device.connected:
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
        # Start the plotter
        self.plotter.start()

        # Run async operations in separate thread
        def run_async():
            try:
                asyncio.run(self.connect_and_run())
            except Exception as e:
                print(f"异步线程发生错误: {e}")
            finally:
                print("异步线程已结束")

        async_thread = threading.Thread(target=run_async, daemon=True)
        async_thread.start()

        # Run Qt main loop
        try:
            return self.plotter.run()
        finally:
            # 确保清理完成
            self.running = False


if __name__ == '__main__':
    app = EEGApp()
    app.run()
