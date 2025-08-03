from bleak import BleakScanner
from typing import List, Optional
import asyncio

from biox.ble.constants import character1,character2
from biox.ble.device import BluetoothDevice
from biox.util.exceptions import ScanError


class BluetoothScanner:

    @staticmethod
    async def scan(timeout: float = 5.0, uuid: Optional[str] = None, name: Optional[str] = None) -> List[
        BluetoothDevice]:
        """
        扫描周围的蓝牙设备，并根据指定的 UUID 和名称进行过滤

        Args:
            timeout (float,optional): 扫描超时时间（秒）
            uuid (str,optional): 设备广播的 UUID（可选）
            name (str,optional): 设备名称（可选）

        Returns:
            List[BluetoothDevice]: 发现的蓝牙设备列表
        """
        try:
            devices = await BleakScanner.discover(timeout=timeout)
            filtered_devices = []

            for device in devices:
                if (uuid is None or uuid in device.metadata['uuids']) and (name is None or device.name == name):
                    filtered_devices.append(BluetoothDevice(device))
            return filtered_devices
        except Exception as e:
            raise ScanError(f"扫描蓝牙设备时发生错误: {str(e)}")

    async def get_device(self, uuid: str, name: str, address: str, timeout: float = 5.0) -> Optional[BluetoothDevice]:
        """
        根据 UUID 和名称获取特定的蓝牙设备

        Args:
            uuid (str): 设备广播 UUID
            name (str): 设备名称
            address (str): 设备地址
            timeout (float,optional): 扫描超时时间（秒）

        Returns:
            Optional[BluetoothDevice]: 发现的蓝牙设备，如果没有找到则返回 None
        """
        devices = await BluetoothScanner.scan(timeout, uuid, name)
        for device in devices:
            if device.address.lower() == address.lower():
                return device
        return None
