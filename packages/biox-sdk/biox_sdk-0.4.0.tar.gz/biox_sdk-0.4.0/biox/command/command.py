# 检查通信设备是否正常工作
# 发送AT指令后，如果设备正常，会返回AT+OK
Check_Device_Work_Status_Command = "AT"

# 查询设备序列号
# 发送AT+SN?指令，可以查询当前设备序列号
# 应答：AT+SN=xxxx
Query_Device_Serial_Number_Command = "AT+SN"

# 查询设备蓝牙地址
# 发送AT+ADDR?指令，可以查询设备蓝牙地址
# 应答：AT+ADDR=xxxx
Query_Bluetooth_Address_Command = "AT+ADDR"

# 重启设备
# 发送AT+RESET指令，可以重启设备
# 应答：AT+RESET=OK
Reset_Device_Command = "AT+RESET"

# 查询设备版本号
# 发送AT+VERSION?指令，可以查询设备的版本号
# 应答：AT+VERSION=xxxx
Query_Device_Version_Command = "AT+VERSION"

# 恢复出厂设置
# 发送AT+RENEW指令，可以将蓝牙设备恢复到出厂设置
# 应答：AT+RENEW=OK
Restore_Factory_Settings_Command = "AT+RENEW"

# 开始采集所有数据
# 设备接收到AT+START_n指令后开始采集n型数据，并将数据发送至主机
# 应答：AT+START_n=OK，随后持续发送采集数据
Start_Data_Collection_Command = "AT+START_ALL"

# 开始采集EEG数据
# 设备接收到AT+START_n指令后开始采集n型数据，并将数据发送至主机
# 应答：AT+START_n=OK，随后持续发送采集数据
Start_Data_Collection_EEG_Command = "AT+START_EEG"

# 开始采集IR数据
# 设备接收到AT+START_n指令后开始采集n型数据，并将数据发送至主机
# 应答：AT+START_n=OK，随后持续发送采集数据
Start_Data_Collection_IR_Command = "AT+START_IR"

# 开始采集ACC数据
# 设备接收到AT+START_n指令后开始采集n型数据，并将数据发送至主机
# 应答：AT+START_n=OK，随后持续发送采集数据
Start_Data_Collection_ACC_Command = "AT+START_ACC"

# 开始采集TMP数据
# 设备接收到AT+START_n指令后开始采集n型数据，并将数据发送至主机
# 应答：AT+START_n=OK，随后持续发送采集数据
Start_Data_Collection_TMP_Command = "AT+START_TMP"

# 停止采集所有数据
# 设备接收到AT+STOP_n指令后停止采集n型数据
# 接收到数据后先停止采集数据并应答：AT+STOP_n=OK
Stop_Data_Collection_Command = "AT+STOP_ALL"

# 停止采集EEG数据
# 设备接收到AT+STOP_n指令后停止采集n型数据
# 接收到数据后先停止采集数据并应答：AT+STOP_n=OK
Stop_Data_Collection_EEG_Command = "AT+STOP_EEG"

# 停止采集IR数据
# 设备接收到AT+STOP_n指令后停止采集n型数据
# 接收到数据后先停止采集数据并应答：AT+STOP_n=OK
Stop_Data_Collection_IR_Command = "AT+STOP_IR"

# 停止采集ACC数据
# 设备接收到AT+STOP_n指令后停止采集n型数据
# 接收到数据后先停止采集数据并应答：AT+STOP_n=OK
Stop_Data_Collection_ACC_Command = "AT+STOP_ACC"

# 停止采集TMP数据
# 设备接收到AT+STOP_n指令后停止采集n型数据
# 接收到数据后先停止采集数据并应答：AT+STOP_n=OK
Stop_Data_Collection_TMP_Command = "AT+STOP_TMP"

# 设置/查询EEG数据采样率
# 发送AT+SR_n=xxx设置n类型数据采样率
# 发送AT+SR_n?查询n类型数据采样率
# 应答均为：AT+SR_n=xxx
Set_Query_Sampling_Rate_EEG_Command = "AT+SR_EEG"

# 设置/查询IR数据采样率
# 发送AT+SR_n=xxx设置n类型数据采样率
# 发送AT+SR_n?查询n类型数据采样率
# 应答均为：AT+SR_n=xxx
Set_Query_Sampling_Rate_IR_Command = "AT+SR_IR"

# 设置/查询TMP数据采样率
# 发送AT+SR_n=xxx设置n类型数据采样率
# 发送AT+SR_n?查询n类型数据采样率
# 应答均为：AT+SR_n=xxx
Set_Query_Sampling_Rate_TMP_Command = "AT+SR_T"

# 设置/查询IMU数据采样率
# 发送AT+SR_n=xxx设置n类型数据采样率
# 发送AT+SR_n?查询n类型数据采样率
# 应答均为：AT+SR_n=xxx
Set_Query_Sampling_Rate_IMU_Command = "AT+SR_IMU"

# 设置/查询EEG数据放大倍数
# 发送AT+GAIN_n=xxx设置n型数据放大倍数
# 发送AT+GAIN_n?查询n型数据放大倍数
# 应答均为：AT+GAIN_n=xxx
Set_Query_Gain_EEG_Command = "AT+GAIN_EEG"

# 设置/查询IR数据放大倍数
# 发送AT+GAIN_n=xxx设置n型数据放大倍数
# 发送AT+GAIN_n?查询n型数据放大倍数
# 应答均为：AT+GAIN_n=xxx
Set_Query_Gain_IR_Command = "AT+GAIN_IR"

# 设置/查询TMP数据放大倍数
# 发送AT+GAIN_n=xxx设置n型数据放大倍数
# 发送AT+GAIN_n?查询n型数据放大倍数
# 应答均为：AT+GAIN_n=xxx
Set_Query_Gain_TMP_Command = "AT+GAIN_T"

# 设置/查询IMU数据放大倍数
# 发送AT+GAIN_n=xxx设置n型数据放大倍数
# 发送AT+GAIN_n?查询n型数据放大倍数
# 应答均为：AT+GAIN_n=xxx
Set_Query_Gain_IMU_Command = "AT+GAIN_IMU"

# 设置/查询当前从设备时间
# 发送AT+TIME=xxxx设置从设备当前计时
# 发送AT+TIME?查询从设备当前计时
# 应答均为：AT+TIME=xxxx，返回从设备当前计时
Set_Query_Current_Time_Command = "AT+TIME"

# 查询电池剩余电量和状态
# 应答：AT+CBC=xxx，xxx，返回电量百分比和电池电压
Query_Battery_Level_Command = "AT+CBC"

# 设置设备进入低功耗状态
# 应答：AT+LPMODE=OK，随后断开连接并进入低功耗状态
Enter_Low_Power_Mode_Command = "AT+LPMODE"

# 查询设备错误状态
# 应答：AT+ERR=xxx，xxx
# 多个异常码之间使用“，”连接
Query_Error_Status_Command = "AT+ERR"

# 设置/查询当前IR运行模式
# 发送AT+IRMODE=n设置当前IR运行模式
# 发送AT+IRMODE?查询当前IR运行模式
# 应答均为：AT+IRMODE=n，返回IR运行模式
# n取值 说明
# 0 IR运行在双波长模式
# 1 IR运行在三波长模式
Set_Query_IR_Mode_Command = "AT+IRMODE"

# 设置/查询IR工作电流
# 发送AT+IRECRNT=n设置IR工作电流, 电流大小为50+n*20 (mA), n的输入格式为hex(带0x前缀)
# 发送AT+IRECRNT? 查询IR工作电流
# 应答均为：AT+IRECRNT=n，返回IR工作电流
Set_Query_IR_Current_Command = "AT+IRECRNT"

# 设置ADS129x寄存器参数，然后复位ADS129x
# 设置: 发送AT+SET_ADS=0xAA,0xBB设置寄存器值,其中0xAA为寄存器地址,0xBB为需要设置的值,设置完成后会进行一次ADS1299复位.
# 应答: AT+SET_ADS=0xAA,0xBB
Set_ADS_Parameters_Command = "AT+SET_ADS"

# 关机指令
# 发送: AT+PWROFF 进行软件关机
# 应答: AT+PWROFF=OK
Power_Off_Command = "AT+PWROFF"

# 重置计时与缓存
# 应答: AT+CLRTIM=OK
Reset_Device_Timer_Command = "AT+CLRTIM"
