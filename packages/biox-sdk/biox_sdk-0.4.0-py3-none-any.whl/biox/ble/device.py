import asyncio
from typing import Dict

from bleak import BleakClient, BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from biox.ble.constants import character1, character2
from biox.command import command
from biox.data.decode import parse_packet
from biox.util.exceptions import ConnectionError


class BluetoothDevice:
    def __init__(self, device: BLEDevice,
                 notify_callbacks: Dict[str, callable] = None,
                 disconnected_callback: callable = None):
        self.device: BLEDevice = device
        self.client: BleakClient = None
        self.connected: bool = False
        if notify_callbacks is None:
            self.notify_callbacks = {}
        else:
            self.notify_callbacks = notify_callbacks

        # 用于处理命令响应的notify机制
        self._command_response_future = None
        self._command_response_registered = False

        if disconnected_callback is None:
            def on_disconnected(client: BleakClient, *args, **kwargs):
                # 断开连接时的回调函数
                self.connected = False

            disconnected_callback = on_disconnected
        self.disconnected_callback = disconnected_callback

    async def set_disconnected_callback(self, callback: callable):
        """设置设备断开回调函数，需要在connect之前设置

        Args:
            callback (callable): 设备断开回调函数
        """
        if self.connected:
            raise ConnectionError("设备连接，无法设置断开回调函数")
        self.disconnected_callback = callback

    async def connect(self) -> bool:
        """
        连接设备
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = BleakClient(
                address_or_ble_device=self.device,
                disconnected_callback=self.disconnected_callback
            )
            await self.client.connect()
            self.connected = True

            # 注册character1的notify用于接收命令响应
            await self._register_command_response_notify()

            for char_specifier, callback in self.notify_callbacks.items():
                await self.start_notify(char_specifier, callback, self.client)
            print("连接设备成功")
            return True
        except Exception as e:
            raise ConnectionError(f"连接设备失败: {str(e)}")

    async def disconnect(self):
        """断开与设备的连接"""
        if self.connected and self.client and self.client.is_connected:
            await self.client.disconnect()
            for char_specifier in self.notify_callbacks.keys():
                await self.stop_notify(char_specifier)

        self.connected = False

    async def get_client(self) -> BleakClient:
        """获取设备客户端"""
        if self.client and self.client.is_connected:
            return self.client
        await self.connect()
        return self.client

    async def start_notify(self, char_specifier: str, callback: callable, client: BleakClient) -> None:
        """注册并开始通知，client从某个char_specifier中不断得到数据，并将其传给callback处理,一般在采集数据时使用

        Args:
            char_specifier (str): 设备特征值
            callback (callable): 回调函数
            client (BleakClient): device的客户端
        """
        if client is None:
            await (await self.get_client()).start_notify(char_specifier, callback)
        else:
            await client.start_notify(char_specifier, callback)

    async def stop_notify(self, char_specifier: str) -> None:
        """停止通知

        Args:
            char_specifier (str): 设备特征值
        """
        await (await self.get_client()).stop_notify(char_specifier)

    async def write_gatt_char(self, char_specifier: str, data: bytes, response: bool = False) -> None:
        """写入设备特征值

        Args:
            char_specifier (str): 设备特征值
            data (bytes): 数据
            response (bool, optional): 是否回显. Defaults to False.
        """
        try:
            await (await self.get_client()).write_gatt_char(char_specifier, data, response)
        except Exception as e:
            raise ConnectionError(f"写入设备特征值失败: {str(e)}")

    async def read_gatt_char(self, char_specifier: str) -> bytes:
        """读取设备特征值

        Args:
            char_specifier (str): 设备特征值

        Returns:
            bytes: 数据
        """
        try:
            client = await self.get_client()
        except Exception as e:
            raise ConnectionError(f"device failed to connect, {str(e)}")

        try:
            data = await client.read_gatt_char(char_specifier)
        except Exception as e:
            raise ConnectionError(f"读取特征值失败: {str(e)}")
        return data

    async def _register_command_response_notify(self):
        """注册character1的notify用于接收命令响应"""
        if not self._command_response_registered:
            await self.client.start_notify(character1, self._command_response_handler)
            self._command_response_registered = True

    def _command_response_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """处理命令响应的notify回调"""
        if self._command_response_future and not self._command_response_future.done():
            self._command_response_future.set_result(bytes(data))

    async def _send_command_and_wait_response(self, command_bytes: bytes, timeout: float = 5.0) -> bytes:
        """发送命令并等待notify响应
        
        Args:
            command_bytes (bytes): 要发送的命令字节
            timeout (float): 超时时间（秒）
            
        Returns:
            bytes: 响应数据
        """
        # 创建一个Future来等待响应
        self._command_response_future = asyncio.Future()
        
        try:
            # 发送命令
            await self.write_gatt_char(character1, command_bytes)
            
            # 等待响应
            response = await asyncio.wait_for(self._command_response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            raise ConnectionError(f"命令响应超时")
        finally:
            self._command_response_future = None

    async def check_device_work_status(self) -> str:
        """检查设备是否工作正常

        Returns:
            str: 设备工作的状态
        """
        send_command = command.Check_Device_Work_Status_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_device_serial_number(self) -> str:
        """查询设备序列号

        Returns:
            str: 设备序列号
        """
        send_command = command.Query_Device_Serial_Number_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_bluetooth_address(self) -> str:
        """查询设备蓝牙地址

        Returns:
            str: 设备蓝牙地址
        """
        send_command = command.Query_Bluetooth_Address_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_device_version(self) -> str:
        """查询设备版本号

        Returns:
            str: 设备版本号
        """
        send_command = command.Query_Device_Version_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_sampling_rate_EEG(self, rate: int) -> str:
        """设置EEG数据采样率

        Returns:
            str: EEG数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_EEG_Command + "=" + str(rate) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_sampling_rate_IR(self, rate: int) -> str:
        """设置IR数据采样率

        Returns:
            str: IR数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_IR_Command + "=" + str(rate) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_sampling_rate_IR(self) -> str:
        """查询IR数据采样率

        Returns:
            str: IR数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_IR_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_sampling_rate_TMP(self, rate: int) -> str:
        """设置TMP数据采样率

        Returns:
            str: TMP数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_TMP_Command + "=" + str(rate) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_sampling_rate_TMP(self) -> str:
        """查询TMP数据采样率

        Returns:
            str: TMP数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_TMP_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_sampling_rate_IMU(self, rate: int) -> str:
        """设置IMU数据采样率

        Returns:
            str: IMU数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_IMU_Command + "=" + str(rate) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_sampling_rate_IMU(self) -> str:
        """查询IMU数据采样率

        Returns:
            str: IMU数据采样率
        """
        send_command = command.Set_Query_Sampling_Rate_IMU_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_gain_EEG(self, gain: int) -> str:
        """设置EEG数据放大倍数

        Returns:
            str: EEG数据放大倍数
        """
        send_command = command.Set_Query_Gain_EEG_Command + "=" + str(gain) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_gain_EEG(self) -> str:
        """查询EEG数据放大倍数

        Returns:
            str: EEG数据放大倍数
        """
        send_command = command.Set_Query_Gain_EEG_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_gain_IR(self, gain: int) -> str:
        """设置IR数据放大倍数

        Returns:
            str: IR数据放大倍数
        """
        send_command = command.Set_Query_Gain_IR_Command + "=" + str(gain) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_gain_IR(self) -> str:
        """查询IR数据放大倍数

        Returns:
            str: IR数据放大倍数
        """
        send_command = command.Set_Query_Gain_IR_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_gain_TMP(self, gain: int) -> str:
        """设置TMP数据放大倍数

        Returns:
            str: TMP数据放大倍数
        """
        send_command = command.Set_Query_Gain_TMP_Command + "=" + str(gain) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_gain_TMP(self) -> str:
        """查询TMP数据放大倍数

        Returns:
            str: TMP数据放大倍数
        """
        send_command = command.Set_Query_Gain_TMP_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_gain_IMU(self, gain: int) -> str:
        """设置IMU数据放大倍数

        Returns:
            str: IMU数据放大倍数
        """
        send_command = command.Set_Query_Gain_IMU_Command + "=" + str(gain) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_gain_IMU(self) -> str:
        """查询IMU数据放大倍数

        Returns:
            str: IMU数据放大倍数
        """
        send_command = command.Set_Query_Gain_IMU_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_current_time(self, current_time: str) -> str:
        """设置设备当前时间

        Args:
            current_time (str): 当前时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'

        Returns:
            str: 设置结果或确认信息
        """
        send_command = command.Set_Query_Current_Time_Command + "=" + current_time + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_current_time(self) -> str:
        """查询设备当前时间

        Returns:
            str: 当前设备时间
        """
        send_command = command.Set_Query_Current_Time_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_battery_level(self) -> str:
        """查询电池剩余电量和状态

        Returns:
            str: 电池剩余电量和状态信息
        """
        send_command = command.Query_Battery_Level_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_error_status(self) -> str:
        """查询设备的错误状态

        Returns:
            str: 错误状态信息
        """
        send_command = command.Query_Error_Status_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_ir_mode(self, mode: int) -> str:
        """设置IR的运行模式

        Args:
            mode (int): 模式值，0代表双波长模式，1代表三波长模式

        Returns:
            str: 设置结果或确认信息
        """
        if mode not in (0, 1):
            raise ValueError("模式值必须是0（双波长模式）或1（三波长模式）")

        send_command = command.Set_Query_IR_Mode_Command + "=" + str(mode) + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_ir_mode(self) -> str:
        """查询当前IR的运行模式

        Returns:
            str: 当前IR模式信息
        """
        send_command = command.Set_Query_IR_Mode_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def set_ir_current(self, n: str) -> str:
        """设置IR工作电流

        Args:
            n (str): 输入值，格式为十六进制字符串（带0x前缀）

        Returns:
            str: 设置结果或确认信息
        """
        try:
            # 将十六进制字符串转换为整数
            n_value = int(n, 16)
        except ValueError:
            raise ValueError("输入值必须是有效的十六进制字符串（带0x前缀）")

        send_command = command.Set_Query_IR_Current_Command + str(n_value) + "mA\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def query_ir_current(self) -> str:
        """查询当前IR工作电流

        Returns:
            str: 当前IR工作电流信息
        """
        send_command = command.Set_Query_IR_Current_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def reset_device(self):
        """重启设备

        Returns:
            str: 重启结果或确认信息
        """
        send_command = command.Reset_Device_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def restore_factory_settings(self):
        """恢复设备出厂设置

        Returns:
            str: 恢复结果或确认信息
        """
        send_command = command.Restore_Factory_Settings_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        resp = await self._send_command_and_wait_response(command_bytes)
        return extract_data(resp)

    async def enter_low_power_mode(self) -> None:
        """设备进入低功耗状态"""
        send_command = command.Enter_Low_Power_Mode_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.write_gatt_char(character1, command_bytes)

    async def power_off(self) -> None:
        """使设备关机"""
        send_command = command.Power_Off_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.write_gatt_char(character1, command_bytes)

    async def reset_device_timer(self) -> None:
        """重置设备的计时与缓存"""
        send_command = command.Reset_Device_Timer_Command + "\r"
        command_bytes = send_command.encode('utf-8')

        await self.write_gatt_char(character1, command_bytes)

    async def register_notify(self, character: str = "", callback: callable = None) -> None:
        """注册非脑电、近红外、温度等数据的通知"""

        def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
            data = parse_packet(data)
            print("rev data:", data)

        if callback is None:
            callback = notification_handler
        if character == "":
            character = character2
        if self.notify_callbacks is None:
            self.notify_callbacks = {}
        self.notify_callbacks[character] = callback


def extract_data(data: bytes) -> str:
    # 尝试解码为字符串
    # 查找第一个出现的 '\r' 的索引
    end_index = data.find(b'\r')

    if end_index == -1:
        # 如果没有找到 '\r'，假设整个数据都是有用的信息
        response = data.decode('ascii', errors='ignore').rstrip('\r')
    else:
        # 解码从开始到第一个 '\r' 之间的字节为字符串
        response = data[:end_index].decode('ascii', errors='ignore')
    
    # 解析 'command=实际值' 格式的响应
    # 查找等号的位置
    equals_index = response.find('=')
    if equals_index != -1:
        # 如果找到等号，返回等号后面的实际值
        return response[equals_index + 1:]
    else:
        # 如果没有找到等号，返回整个响应（用于处理像 'AT+OK' 这样的简单响应）
        return response
