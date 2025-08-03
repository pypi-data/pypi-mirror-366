from setuptools import setup, find_packages

setup(
    name="biox-sdk",
    version="0.4.0",
    packages=find_packages(),
    package_data={
        'biox': ['data/dll/pkg_decode.dll', 'data/dll/signal_process.dll'],  # 包含DLL文件
    },
    install_requires=[
        "bleak>=0.19.0",  # 用于蓝牙通信的异步库
    ],
    python_requires=">=3.7",
    author="qiucheng.su",
    author_email="suqiucheng@zju.edu.cn",
    description="a sdk for connecting with a Biox device",
    keywords="bluetooth, ble, sdk",
)
