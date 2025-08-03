import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector

if __name__ == '__main__':
    async def main():
        try:
            ble_device = None
            while ble_device is None:
                devices = await BluetoothScanner.scan()
                for device in devices:
                    if device and device.device.name and "Biox" in device.device.name:
                        ble_device = device
                        break

            collector = Collector(ble_device)
            await collector.register_notify()
            await collector.start()
            await collector.stop_data_collection()
            await collector.start_data_collection()
            await collector.wait_for_stop()
        finally:
            # 确保释放连接
            await collector.stop()
            print("设备连接已释放")


    asyncio.run(main())
