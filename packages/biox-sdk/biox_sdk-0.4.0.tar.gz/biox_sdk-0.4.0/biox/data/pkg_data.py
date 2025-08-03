import ctypes
from dataclasses import dataclass
from typing import List, Optional

from biox.util import constants

# 定义常量
max_eeg_group_num = 256
max_channel = 16
max_wave_channel = 4
max_ir_channel=256

@dataclass
class PkgData:
    pkglen: int
    pkgnum: int
    time_mark: int
    pkg_type: int
    eeg_channel: int
    eeg_data_num: int
    ir_channel: int
    brain_elec: Optional[List[List[float]]] = None
    near_infrared: Optional[List[List[float]]] = None
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    temperature: Optional[float] = None
    Battery_State: Optional[float] = None
    fall_off: Optional[int] = None
    error_state: Optional[int] = None

# 定义结构体
class Pkg(ctypes.Structure):
    _fields_ = [
        ("pkglen", ctypes.c_int16),
        ("pkgnum", ctypes.c_int32),
        ("time_mark", ctypes.c_int32),
        ("pkg_type", ctypes.c_uint8),
        ("eeg_channel", ctypes.c_uint8),
        ("eeg_data_num", ctypes.c_uint8),
        ("ir_channel", ctypes.c_uint8),
        ("brain_elec", (ctypes.c_float * max_eeg_group_num) * max_channel),
        ("near_infrared", (ctypes.c_float * max_wave_channel) * max_ir_channel),
        ("acceleration_x", ctypes.c_float),
        ("acceleration_y", ctypes.c_float),
        ("acceleration_z", ctypes.c_float),
        ("temperature", ctypes.c_float),
        ("Battery_State", ctypes.c_float),
        ("fall_off", ctypes.c_int32),
        ("error_state", ctypes.c_int32),
    ]

    def covert_to_pkg(self) -> PkgData:
        pkg_type = getattr(self, "pkg_type", None)
        brain_elec = None
        near_infrared = None
        if pkg_type == constants.PKG_EEG_TYPE:
            brain_elec = [list(sublist) for sublist in getattr(self, "brain_elec", [])]
        elif pkg_type == constants.PKG_IR_TYPE:
            near_infrared = [list(sublist) for sublist in getattr(self, "near_infrared", [])]
        return PkgData(
            pkglen=self.pkglen,
            pkgnum=self.pkgnum,
            time_mark=self.time_mark,
            pkg_type=self.pkg_type,
            eeg_channel=self.eeg_channel,
            eeg_data_num=self.eeg_data_num,
            ir_channel=self.ir_channel,
            brain_elec=brain_elec,
            near_infrared=near_infrared,
            acceleration_x=self.acceleration_x,
            acceleration_y=self.acceleration_y,
            acceleration_z=self.acceleration_z,
            temperature=self.temperature,
            Battery_State=self.Battery_State,
            fall_off=self.fall_off,
            error_state=self.error_state
        )