import asyncio
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from bleak import BleakGATTCharacteristic
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet

if __name__ == '__main__':
    """
    根据设备的name连接设备，采集数据，一段时间后关闭采集
    """


    async def main():
        ble_device = None
        while ble_device is None:
            devices = await BluetoothScanner.scan()
            for device in devices:
                if device and device.device.name and "Biox" in device.device.name:
                    ble_device = device
                    break

        collector = Collector(ble_device)

        # 注册处理数据的回调函数，其中character默认不填写
        def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
            data = parse_packet(data)
            if data and data.pkg_type != 0:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} after parse data:{data}")

        await collector.register_notify(callback=notification_handler)
        await collector.start()
        # 清理掉之前的命令
        await collector.stop_data_collection()
        await collector.start_data_collection()
        time.sleep(10)
        print("stop")
        await collector.stop_data_collection()
        
        # 确保释放连接
        await collector.stop()
        print("设备连接已释放")


    asyncio.run(main())
