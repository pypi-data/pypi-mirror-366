import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bleak import BleakGATTCharacteristic
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet

if __name__ == '__main__':
    """
    根据设备的uuid连接设备
    """


    async def main():
        try:
            ble_device = None
            while ble_device is None:
                devices = await BluetoothScanner.scan()
                for device in devices:
                    if device and device.device.address and "00:80:E1:26:00:BD" in device.device.address:
                        ble_device = device
                        break

            collector = Collector(ble_device)

            # 注册处理数据的回调函数，其中character默认不填写
            def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
                data = parse_packet(data)
                print("after parse data:", data)

            await collector.register_notify(callback=notification_handler)
            await collector.start()
            await collector.stop_data_collection()
            await collector.start_data_collection()
            await collector.wait_for_stop()
        finally:
            # 确保释放连接
            await collector.stop()
            print("设备连接已释放")


    asyncio.run(main())
