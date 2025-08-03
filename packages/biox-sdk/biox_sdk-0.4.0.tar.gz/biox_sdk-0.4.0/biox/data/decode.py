import ctypes
import os.path

from biox.data.pkg_data import Pkg, PkgData

pkg_data_decode_dll = None


def init():
    try:
        current_file_path = os.path.abspath(__file__)
        current_file_directory = os.path.dirname(current_file_path)
        dll_directory = os.path.join(current_file_directory,"dll")
        dll_file = os.path.join(dll_directory,"pkg_decode.dll")
        decode_dll = ctypes.CDLL(dll_file)
        decode_dll.get_pkg_buffer_length.restype = ctypes.c_int
        decode_dll.push_to_databuffer.restype = None
        decode_dll.push_to_databuffer.argtypes = [ctypes.c_uint8]
        decode_dll.pkgbuffer_pop.restype = None
        decode_dll.pkg_recv.restype = None
        decode_dll.decode.restype = ctypes.POINTER(Pkg)
        return decode_dll
    except OSError as e:
        print(f"Failed to load DLL: {e}")


def parse_packet(packet: bytes) -> PkgData:
    """
    Parses a packet into a Pkg object.
    :param packet: The packet to parse.
    :return: A Pkg object containing the parsed data.
    """
    global pkg_data_decode_dll
    if pkg_data_decode_dll is None:
        pkg_data_decode_dll = init()
    pkg_data_decode_dll.pkg_recv()
    for byte in packet:
        pkg_data_decode_dll.push_to_databuffer(byte)
    if pkg_data_decode_dll.get_pkg_buffer_length():
        pkg_ptr = pkg_data_decode_dll.decode()
        pkg = ctypes.cast(pkg_ptr, ctypes.POINTER(Pkg)).contents
        del pkg_ptr
        pkg_data_decode_dll.pkgbuffer_pop()
        return pkg.covert_to_pkg()
