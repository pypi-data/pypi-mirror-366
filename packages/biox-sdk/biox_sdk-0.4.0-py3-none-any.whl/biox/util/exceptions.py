class BluetoothSDKError(Exception):
    """蓝牙SDK基础异常类"""
    pass


class ScanError(BluetoothSDKError):
    """扫描设备时的异常"""
    pass


class ConnectionError(BluetoothSDKError):
    """连接设备时的异常"""
    pass


class DataCollectionError(BluetoothSDKError):
    """数据收集时的异常"""
    pass
