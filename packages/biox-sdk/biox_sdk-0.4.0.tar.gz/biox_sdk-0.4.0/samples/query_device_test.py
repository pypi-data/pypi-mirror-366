import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biox.collector.collector import Collector
from biox.ble.scanner import BluetoothScanner

if __name__ == '__main__':
    """
    测试设备查询函数是否正常工作
    """


    async def main():
        print("开始扫描设备...")

        ble_device = None
        while ble_device is None:
            devices = await BluetoothScanner.scan()
            for device in devices:
                if device and device.device.name and "Biox" in device.device.name:
                    ble_device = device
                    break

            if ble_device is None:
                print("未找到Biox设备，继续扫描...")
                await asyncio.sleep(1)

        print(f"找到设备: {ble_device.device.name} ({ble_device.device.address})")

        collector = Collector(ble_device)
        try:
            await collector.start()
            # await ble_device.connect()
            print("设备连接成功")

            print("\n=== 测试设备查询功能 ===")

            try:
                status = await ble_device.check_device_work_status()
                print(f"设备工作状态: {status}")
            except Exception as e:
                print(f"查询设备工作状态失败: {e}")

            try:
                serial = await ble_device.query_device_serial_number()
                print(f"设备序列号: {serial}")
            except Exception as e:
                print(f"查询设备序列号失败: {e}")

            try:
                version = await ble_device.query_device_version()
                print(f"设备版本: {version}")
            except Exception as e:
                print(f"查询设备版本失败: {e}")

            try:
                address = await ble_device.query_bluetooth_address()
                print(f"蓝牙地址: {address}")
            except Exception as e:
                print(f"查询蓝牙地址失败: {e}")

            try:
                battery = await ble_device.query_battery_level()
                print(f"电池电量: {battery}")
            except Exception as e:
                print(f"查询电池电量失败: {e}")

            try:
                error_status = await ble_device.query_error_status()
                print(f"错误状态: {error_status}")
            except Exception as e:
                print(f"查询错误状态失败: {e}")

            try:
                current_time = await ble_device.query_current_time()
                print(f"当前时间: {current_time}")
            except Exception as e:
                print(f"查询当前时间失败: {e}")

            print("\n=== 测试采样率查询功能 ===")

            try:
                eeg_rate = await ble_device.set_sampling_rate_EEG(50)
                print(f"EEG采样率: {eeg_rate}")
            except Exception as e:
                print(f"查询EEG采样率失败: {e}")

            try:
                ir_rate = await ble_device.query_sampling_rate_IR()
                print(f"IR采样率: {ir_rate}")
            except Exception as e:
                print(f"查询IR采样率失败: {e}")

            print("\n测试完成!")

        except Exception as e:
            print(f"测试过程中发生错误: {e}")

        finally:
            try:
                await ble_device.disconnect()
                print("设备已断开连接")
            except Exception as e:
                print(f"断开连接时发生错误: {e}")

    print("请确保有Biox设备在附近并且已开启\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试失败: {e}")
