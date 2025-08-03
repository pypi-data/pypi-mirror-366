import asyncio

from biox.ble.constants import character1
from biox.ble.device import BluetoothDevice
from biox.command import command


class Collector:
    def __init__(self, device: BluetoothDevice):
        self.device: BluetoothDevice = device
        self.stop_status: bool = False

    async def start_data_collection(self) -> None:
        """开始采集所有数据"""
        send_command = command.Start_Data_Collection_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def start_data_collection_EEG(self) -> None:
        """开始采集EEG数据"""
        send_command = command.Start_Data_Collection_EEG_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def start_data_collection_IR(self) -> None:
        """开始采集IR数据"""
        send_command = command.Start_Data_Collection_IR_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def start_data_collection_ACC(self) -> None:
        """开始采集加速度计数据"""
        send_command = command.Start_Data_Collection_ACC_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def start_data_collection_TMP(self) -> None:
        """开始采集温度数据"""
        send_command = command.Start_Data_Collection_TMP_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def stop_data_collection(self) -> None:
        """停止采集所有数据"""
        send_command = command.Stop_Data_Collection_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def stop_data_collection_EEG(self) -> None:
        """停止采集EEG数据"""
        send_command = command.Stop_Data_Collection_EEG_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def stop_data_collection_IR(self) -> None:
        """停止采集IR数据"""
        send_command = command.Stop_Data_Collection_IR_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def stop_data_collection_ACC(self) -> None:
        """停止采集加速度计数据"""
        send_command = command.Stop_Data_Collection_ACC_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def stop_data_collection_TMP(self) -> None:
        """停止采集温度数据"""
        send_command = command.Stop_Data_Collection_TMP_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.device.write_gatt_char(character1, command_bytes)

    async def register_notify(self, character: str = "", callback: callable = None) -> None:
        """注册非脑电、近红外、温度等数据的通知"""
        await self.device.register_notify(character, callback)

    async def start(self, max_retries: int = 2, retry_delay: float = 2.0):
        """注册回调函数，处理数据
        
        Args:
            max_retries (int): 最大重试次数，默认为2次
            retry_delay (float): 重试间隔时间（秒），默认为2秒
        """
        retry_count = 0
        last_exception = None
        
        while retry_count < max_retries:
            try:
                await self.device.connect()
                self.stop_status = False
                return
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                if retry_count <= max_retries:
                    await asyncio.sleep(retry_delay)
                else:
                    break
        
        # 如果所有重试都失败了，抛出最后一个异常
        if last_exception:
            raise last_exception

    async def stop(self):
        """停止回调函数"""
        await self.device.disconnect()
        self.stop_status = True

    async def wait_for_stop(self):
        """设备运行、停止、异常等状态监听"""
        while not self.stop_status and self.device.connected:
            await asyncio.sleep(1)
        await self.stop()
