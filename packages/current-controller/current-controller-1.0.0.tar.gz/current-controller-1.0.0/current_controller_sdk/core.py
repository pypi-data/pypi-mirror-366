# -*- coding: utf-8 -*-
'''
@time: 2025/8/4 14:49
@ author: hxp
'''
# -*- coding: utf-8 -*-
"""
电流控制器SDK：用于通过串口与电流控制器设备通信，支持参数配置、状态查询等功能。
"""
import serial
import time
from serial import SerialException


class CurrentControllerSDK:
    def __init__(self, port, baudrate=9600, timeout=1, default_delay=0.01):
        """
        初始化串口连接

        :param port: 串口名称（如Windows的'COM3'，Linux的'/dev/ttyUSB0'）
        :param baudrate: 波特率，默认9600
        :param timeout: 串口读取超时时间（秒），默认1秒
        :param default_delay: 指令发送后等待设备响应的默认延时（秒），默认0.1秒
        :raises SerialException: 串口打开失败时抛出异常
        """
        self.default_delay = default_delay  # 设备处理默认延时
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
            )
            if not self.ser.is_open:
                self.ser.open()
            print(f"串口 {port} 连接成功（波特率：{baudrate}）")
        except SerialException as e:
            raise SerialException(f"串口连接失败：{str(e)}") from e

    def _checksum(self, data: bytes) -> int:
        """
        XOR校验计算：对输入字节流进行异或校验

        :param data: 待校验的字节流
        :return: 校验结果（单字节）
        """
        xor = 0
        for b in data:
            xor ^= b
        return xor

    def _build_packet(self, cmd: int, channel: int, params: bytes) -> bytes:
        """
        构建完整数据包：帧头+功能码+通道+参数+校验+帧尾

        :param cmd: 功能码（如0x10、0x21）
        :param channel: 通道号（0x00~0x02，全通道用0xFF）
        :param params: 参数字节流
        :return: 完整数据包字节流
        """
        header = bytes([0xA0])  # 帧头固定为0xA0
        tail = bytes([0xAF])  # 帧尾固定为0xAF
        body = bytes([cmd, channel]) + params  # 功能码+通道+参数
        xor = self._checksum(header + body)  # 计算校验位
        return header + body + bytes([xor]) + tail

    def _send_and_receive(self, packet: bytes, delay: float = 0.01) -> bytes:
        """
        发送数据包并接收设备响应

        :param packet: 待发送的完整数据包
        :param delay: 等待设备响应的延时（秒），默认使用default_delay
        :return: 设备返回的响应字节流
        """
        delay = delay or self.default_delay  # 优先使用传入的延时，否则用默认值
        try:
            self.ser.flushInput()  # 清空接收缓冲区
            self.ser.write(packet)  # 发送数据包
            time.sleep(delay)  # 等待设备处理
            response = self.ser.read(64)  # 读取最多64字节响应
            return response
        except SerialException as e:
            print(f"串口通信错误：{str(e)}")
            return b""

    def _validate_channel(self, channel: int):
        """
        验证通道号合法性（仅允许0x00~0x02）

        :param channel: 待验证的通道号
        :raises ValueError: 通道号不合法时抛出异常
        """
        if channel not in (0x00, 0x01, 0x02):
            raise ValueError(f"通道号必须为0x00、0x01或0x02，当前输入：{channel}")

    # 1. 设置电流上下限（功能码0x10）
    def set_current_limit(self, channel: int, upper_ma: int, lower_ma: int) -> bytes:
        """
        设置指定通道的电流上下限（单位：mA）

        :param channel: 通道号（0x00~0x02）
        :param upper_ma: 电流上限（0~65535 mA，2字节范围）
        :param lower_ma: 电流下限（0~65535 mA，2字节范围）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)
        # 转换为2字节大端模式（高位在前）
        upper_bytes = upper_ma.to_bytes(2, 'big')
        lower_bytes = lower_ma.to_bytes(2, 'big')
        params = upper_bytes + lower_bytes
        pkt = self._build_packet(0x10, channel, params)
        return self._send_and_receive(pkt)

    # 2. 设置启动延时（功能码0x11）
    def set_start_delay(self, channel: int, delay_ms: int) -> bytes:
        """
        设置指定通道的启动延时（单位：ms）

        :param channel: 通道号（0x00~0x02）
        :param delay_ms: 延时时间（0~65535 ms，2字节范围）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)
        delay_bytes = delay_ms.to_bytes(2, 'big')  # 2字节大端模式
        pkt = self._build_packet(0x11, channel, delay_bytes)
        return self._send_and_receive(pkt)

    # 3. 设置通道启动/停止（功能码0x12）
    def set_status(self, channel: int, start: bool) -> bytes:
        """
        控制指定通道的启动或停止

        :param channel: 通道号（0x00~0x02）
        :param start: True=启动（0xA2），False=停止（0xA1）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)
        mode = 0xA2 if start else 0xA1  # 启动/停止指令码
        pkt = self._build_packet(0x12, channel, bytes([mode]))
        return self._send_and_receive(pkt)

    # 4. 设置输出模式（功能码0x13）
    def set_output_mode(self, channel: int, mode: str) -> bytes:
        """
        设置指定通道的输出模式（脉冲/正弦/恒流）

        :param channel: 通道号（0x00~0x02）
        :param mode: 模式字符串：'pulse'（脉冲）、'sine'（正弦）、'dc'（恒流）
        :return: 设备响应字节流
        :raises ValueError: 模式不合法时抛出异常
        """
        self._validate_channel(channel)
        mode_map = {
            'pulse': 0xB1,  # 脉冲模式指令码
            'sine': 0xB2,  # 正弦模式指令码
            'dc': 0xB3  # 恒流模式指令码
        }
        if mode not in mode_map:
            raise ValueError(f"模式必须为 'pulse'、'sine' 或 'dc'，当前输入：{mode}")
        pkt = self._build_packet(0x13, channel, bytes([mode_map[mode]]))
        return self._send_and_receive(pkt)

    # 5. 设置正弦模式参数（功能码0x14）
    def set_sine_parameters(self, channel: int, amp: float, omega: float, phase: float, offset: float) -> bytes:
        """
        设置指定通道的正弦波参数（振幅、角频率、相位、偏移）

        :param channel: 通道号（0x00~0x02）
        :param amp: 振幅（-655.35~+655.35，保留2位小数）
        :param omega: 角频率（-655.35~+655.35，保留2位小数）
        :param phase: 相位（-655.35~+655.35，保留2位小数）
        :param offset: 偏移（-655.35~+655.35，保留2位小数）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)

        def encode_param(value: float) -> bytes:
            """编码单个浮点参数为3字节：符号(1)+整数(2)+小数(1)"""
            sign = 0x00 if value >= 0 else 0x01
            abs_val = abs(value)
            part = int(round(abs_val * 100)).to_bytes(2, 'big')
            return bytes([sign]) + part

        params = (
                encode_param(amp) +
                encode_param(omega) +
                encode_param(phase) +
                encode_param(offset)
        )
        pkt = self._build_packet(0x14, channel, params)
        return self._send_and_receive(pkt, delay=0.01)  # 复杂参数配置延时延长

    # 6. 设置脉冲模式参数（功能码0x15）
    def set_pulse_parameters(self, channel: int, duty_percent: float, period_s: float) -> bytes:
        """
        设置指定通道的脉冲模式参数（占空比、周期）

        :param channel: 通道号（0x00~0x02）
        :param duty_percent: 占空比（0.00%~100.00%，保留2位小数）
        :param period_s: 周期（0.0~6553.5秒，保留1位小数，单位0.1s）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)
        # 占空比：转换为0.01%单位（如60.0% → 6000），2字节大端
        duty = int(round(duty_percent * 100)).to_bytes(2, 'big')
        # 周期：转换为0.1s单位（如0.5s → 5），2字节大端
        period = int(round(period_s * 10)).to_bytes(2, 'big')
        params = duty + period
        pkt = self._build_packet(0x15, channel, params)
        return self._send_and_receive(pkt)

    # 7. 设置恒流模式参数（功能码0x16）
    def set_constant_current(self, channel: int, current_ma: int) -> bytes:
        """
        设置指定通道的恒流输出值（单位：mA）

        :param channel: 通道号（0x00~0x02）
        :param current_ma: 恒流值（0~65535 mA，2字节范围）
        :return: 设备响应字节流
        """
        self._validate_channel(channel)
        current_bytes = current_ma.to_bytes(2, 'big')  # 2字节大端模式
        pkt = self._build_packet(0x16, channel, current_bytes)
        return self._send_and_receive(pkt)

    # 8. 全通道启动/停止（功能码0x17）
    def control_all_channels(self, start: bool) -> bytes:
        """
        控制所有通道同时启动或停止

        :param start: True=全启动（0xC1），False=全停止（0xC2）
        :return: 设备响应字节流
        """
        mode = 0xC1 if start else 0xC2  # 全启动/全停止指令码
        pkt = self._build_packet(0x17, 0xFF, bytes([mode]))  # 通道固定为0xFF（全通道）
        return self._send_and_receive(pkt)

    # 9. 清空全通道参数（功能码0x18）
    def clear_all_parameters(self) -> bytes:
        """
        清空所有通道的配置参数（恢复默认值）

        :return: 设备响应字节流
        """
        pkt = self._build_packet(0x18, 0xFF, bytes([0xC3]))  # 参数固定为0xC3
        return self._send_and_receive(pkt, delay=0.3)  # 清空参数延时延长

    # 10. 获取当前全通道实际电流（功能码0x20）
    def get_all_channel_current(self):
        """
        获取所有通道的实际电流值
        :return: 响应数据（字节流）
        """
        # 构建数据包：0xA0 20 FF [校验] 0xAF
        pkt = self._build_packet(0x20, 0xFF, bytes())

        data = self._send_and_receive(pkt)

        # 提取3个通道的电流（每个通道2字节，大端模式）
        # 通道1：字节3-4，通道2：字节5-6，通道3：字节7-8
        channel1 = (data[3] << 8) | data[4]  # 高8位<<8 + 低8位
        channel2 = (data[5] << 8) | data[6]
        channel3 = (data[7] << 8) | data[8]

        # 转换为安培（mA -> A，除以1000）
        print("通道1电流(A):",channel1 / 1000.0,
            "通道2电流(A):", channel2 / 1000.0,
            "通道3电流(A):", channel3 / 1000.0)

    # 11. 获取错误代码（功能码0x21）
    def get_error_code(self):
        """
        获取当前错误代码
        :return: 响应数据（字节流）
        """
        pkt = self._build_packet(0x21, 0xFF, bytes())

        data = self._send_and_receive(pkt)

        """解析三个通道的错误代码，根据bit位定义输出具体错误信息"""
        # 1. 验证帧结构（总长度11字节，帧头0xB0，功能码0xE1）
        if len(data) < 11 or data[0] != 0xB0 or data[1] != 0xE1:
            print("错误代码格式错误：帧头、功能码或长度不匹配")
            return

        # 2. 提取三个通道的错误码（每个通道2字节，大端模式）
        # 通道1：字节3-4，通道2：字节5-6，通道3：字节7-8
        channel1_code = (data[3] << 8) | data[4]  # 通道1错误码（高8位<<8 + 低8位）
        channel2_code = (data[5] << 8) | data[6]  # 通道2错误码
        channel3_code = (data[7] << 8) | data[8]  # 通道3错误码

        # 3. 定义错误信息映射（bit位从0开始，对应表格bit1~bit9）
        error_messages = [
            ("系统参数错误", 0),  # bit0 → 表格bit1
            ("温度读取（IIC）失败", 1),  # bit1 → 表格bit2
            ("温度预警", 2),  # bit2 → 表格bit3
            ("过温警报", 3),  # bit3 → 表格bit4
            ("过流警报", 4),  # bit4 → 表格bit5
            ("电流采样超时", 5),  # bit5 → 表格bit6
            ("485通信超时", 6),  # bit6 → 表格bit7
            ("串口通信超时", 7),  # bit7 → 表格bit8
            ("SPI写入DAC错误", 8)  # bit8 → 表格bit9（高8位）
        ]

        # 4. 解析单个通道错误的函数
        def parse_single_channel(channel_num, code):
            errors = []
            for msg, bit in error_messages:
                if code & (1 << bit):  # 检查对应bit是否置位
                    errors.append(msg)
            if not errors:
                return f"通道{channel_num}：正常（无错误）"
            else:
                return (
                    f"通道{channel_num}：\n"
                    f"  错误代码: 0x{code:04X}\n"
                    f"  二进制表示: {bin(code)[2:].zfill(16)}\n"
                    f"  错误信息: {'; '.join(errors)}"
                )

        # 5. 解析并打印所有通道错误
        print("=== 各通道错误代码解析结果 ===")
        print(parse_single_channel(1, channel1_code))
        print(parse_single_channel(2, channel2_code))
        print(parse_single_channel(3, channel3_code))

    # 12. 软件单片机复位（功能码0x22）
    def software_reset(self) -> bytes:
        """
        触发设备单片机软件复位（复位后参数可能恢复默认）

        :return: 设备响应字节流
        """
        pkt = self._build_packet(0x22, 0xFF, bytes())  # 无参数
        return self._send_and_receive(pkt, delay=0.5)  # 复位延时延长

    # 13. 清空错误代码（功能码0x23）
    def clear_error_code(self) -> bytes:
        """
        清空设备当前的错误代码记录

        :return: 设备响应字节流
        """
        pkt = self._build_packet(0x23, 0xFF, bytes())  # 无参数
        return self._send_and_receive(pkt)

    # 14. 获取已连接的通道（功能码0x24）
    def get_connected_channels(self) -> bytes:
        """
        获取当前物理连接的有效通道列表（如0x00、0x01）

        :return: 设备响应字节流（包含连接通道信息）
        """
        pkt = self._build_packet(0x24, 0xFF, bytes())  # 无参数
        return self._send_and_receive(pkt)

    def close(self):
        """关闭串口连接，释放资源"""
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("串口已关闭")


# 测试示例（实际使用时可删除或注释）
if __name__ == '__main__':
    try:
        # 初始化SDK（替换为实际串口）
        sdk = CurrentControllerSDK(port='COM8', baudrate=115200)

        # 示例1：设置通道0为正弦模式
        sdk.set_output_mode(channel=0x00, mode='sine')

        # 示例2：配置正弦参数（振幅3.25，角频率2.50，相位-1.75，偏移0.80）
        sdk.set_sine_parameters(
            channel=0x00,
            amp=3.25,
            omega=2.50,
            phase=-1.75,
            offset=0.80
        )

        # 示例3：启动通道0
        # sdk.set_status(channel=0x00, start=True)

        # 示例4：获取全通道电流
        sdk.get_all_channel_current()

    except Exception as e:
        print(f"测试错误：{str(e)}")
    # finally:
    #     if 'sdk' in locals():
    #         sdk.close()

    while True:
        res = sdk.get_all_channel_current()

        # print(f"current:{res.hex().upper()}")

        res1 = sdk.get_error_code()

        # print(f"error_code:{res1.hex().upper()}")