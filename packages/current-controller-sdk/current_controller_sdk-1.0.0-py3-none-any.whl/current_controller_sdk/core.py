# -*- coding: utf-8 -*-
'''
@time: 2025/8/4 11:47
@ author: hxp
'''
# -*- coding: utf-8 -*-
'''
@time: 2025/8/3 11:03
@ author: hxp
'''
import serial
import time


class CurrentControllerSDK:
    def __init__(self, port, baudrate=9600, timeout=1):
        """初始化串口连接"""
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        if not self.ser.is_open:
            self.ser.open()

    def _checksum(self, data: bytes) -> int:
        """XOR校验计算"""
        xor = 0
        for b in data:
            xor ^= b
        return xor

    def _build_packet(self, cmd, channel, params: bytes) -> bytes:
        """构建完整数据包：帧头+功能码+通道+参数+校验+帧尾"""
        header = bytes([0xA0])
        tail = bytes([0xAF])
        body = bytes([cmd, channel]) + params
        xor = self._checksum((header+body))
        return header + body + bytes([xor]) + tail

    def _send_and_receive(self, packet: bytes):
        """发送数据包并接收响应"""
        self.ser.write(packet)
        time.sleep(0.01)  # 等待设备处理
        response = self.ser.read(64)  # 最大读取64字节
        return response

    def _validate_channel(self, channel):
        """验证通道号合法性（0x00~0x02）"""
        if channel not in (0x00, 0x01, 0x02):
            raise ValueError("通道号必须为0x00、0x01或0x02")

    # 1. 设置电流上下限（功能码0x10）
    def set_current_limit(self, channel: int, upper_ma: int, lower_ma: int):
        """
        设置电流上下限（单位：mA）
        :param channel: 通道号（0x00~0x02）
        :param upper_ma: 电流上限（mA）
        :param lower_ma: 电流下限（mA）
        """
        self._validate_channel(channel)
        # 编码为2字节大端模式
        upper_bytes = upper_ma.to_bytes(2, 'big')
        lower_bytes = lower_ma.to_bytes(2, 'big')
        params = upper_bytes + lower_bytes
        pkt = self._build_packet(0x10, channel, params)
        return self._send_and_receive(pkt)

    # 2. 设置启动延时（功能码0x11）
    def set_start_delay(self, channel: int, delay_ms: int):
        """
        设置启动延时（单位：ms）
        :param channel: 通道号（0x00~0x02）
        :param delay_ms: 延时毫秒数
        """
        self._validate_channel(channel)
        delay_bytes = delay_ms.to_bytes(2, 'big')  # 2字节大端
        pkt = self._build_packet(0x11, channel, delay_bytes)
        return self._send_and_receive(pkt)

    # 3. 设置状态模式（功能码0x12）
    def set_status(self, channel: int, start: bool):
        """
        设置通道启动/停止
        :param channel: 通道号（0x00~0x02）
        :param start: True=启动（0xA2），False=停止（0xA1）
        """
        self._validate_channel(channel)
        mode = 0xA2 if start else 0xA1
        pkt = self._build_packet(0x12, channel, bytes([mode]))
        return self._send_and_receive(pkt)

    # 4. 设置输出模式（功能码0x13）
    def set_output_mode(self, channel: int, mode: str):
        """
        设置输出模式
        :param channel: 通道号（0x00~0x02）
        :param mode: 模式：'pulse'（0xB1）、'sine'（0xB2）、'dc'（0xB3）
        """
        self._validate_channel(channel)
        mode_map = {'pulse': 0xB1, 'sine': 0xB2, 'dc': 0xB3}
        if mode not in mode_map:
            raise ValueError("模式必须为 'pulse'、'sine' 或 'dc'")
        pkt = self._build_packet(0x13, channel, bytes([mode_map[mode]]))
        return self._send_and_receive(pkt)

    # 5. 设置正弦模式参数（功能码0x14）
    def set_sine_parameters(self, channel: int, amp: float, omega: float, phase: float, offset: float):
        """
        设置正弦波参数
        :param channel: 通道号（0x00~0x02）
        :param amp: 振幅（如+3.25）
        :param omega: 角频率（如+2.50）
        :param phase: 相位（如-1.75）
        :param offset: 偏移（如+0.80）
        """
        self._validate_channel(channel)

        def encode_param(value: float) -> bytes:
            """编码单个浮点参数为3字节：符号(1)+整数(2)+小数(1)"""
            sign = 0x00 if value >= 0 else 0x01
            abs_val = abs(value)
            int_part = int(abs_val)
            frac_part = int(round((abs_val - int_part) * 100))  # 保留2位小数
            return bytes([sign]) + bytes([int_part]) + bytes([frac_part])
        params = (
                encode_param(amp) +
                encode_param(omega) +
                encode_param(phase) +
                encode_param(offset)
        )
        print(f"params:{params.hex().upper()}")
        pkt = self._build_packet(0x14, channel, params)
        return self._send_and_receive(pkt)

    # 6. 设置脉冲模式参数（功能码0x15）
    def set_pulse_parameters(self, channel: int, duty_percent: float, period_s: float):
        """
        设置脉冲模式参数
        :param channel: 通道号（0x00~0x02）
        :param duty_percent: 占空比（%，如60.0%）
        :param period_s: 周期（秒，如0.5s）
        """
        self._validate_channel(channel)
        # 占空比：单位0.01%，转换为整数（60% → 6000）
        duty = int(duty_percent * 100).to_bytes(2, 'big')
        # 周期：单位0.1s，转换为整数（0.5s → 5）
        period = int(period_s * 10).to_bytes(2, 'big')
        params = duty + period
        pkt = self._build_packet(0x15, channel, params)
        return self._send_and_receive(pkt)

    # 7. 设置恒流模式参数（功能码0x16）
    def set_constant_current(self, channel: int, current_ma: int):
        """
        设置恒流值（单位：mA）
        :param channel: 通道号（0x00~0x02）
        :param current_ma: 电流值（毫安）
        """
        self._validate_channel(channel)
        current_bytes = current_ma.to_bytes(2, 'big')  # 2字节大端
        pkt = self._build_packet(0x16, channel, current_bytes)
        return self._send_and_receive(pkt)

    # 8. 全通道启动/停止（功能码0x17）
    def control_all_channels(self, start: bool):
        """
        控制所有通道启动/停止
        :param start: True=全启动（0xC1），False=全停止（0xC2）
        """
        mode = 0xC1 if start else 0xC2
        pkt = self._build_packet(0x17, 0xFF, bytes([mode]))  # 通道固定为0xFF
        return self._send_and_receive(pkt)

    # 9. 清空全通道参数（功能码0x18）
    def clear_all_parameters(self):
        """清空所有通道的参数"""
        pkt = self._build_packet(0x18, 0xFF, bytes([0xC3]))  # 通道0xFF，参数0xC3
        return self._send_and_receive(pkt)

    # 10. 获取当前全通道实际电流（功能码0x20）
    def get_all_channel_current(self):
        """
        获取所有通道的实际电流值
        :return: 响应数据（字节流）
        """
        # 构建数据包：0xA0 20 FF [校验] 0xAF
        pkt = self._build_packet(0x20, 0xFF, bytes())
        return self._send_and_receive(pkt)

    # 11. 获取错误代码（功能码0x21）
    def get_error_code(self):
        """
        获取当前错误代码
        :return: 响应数据（字节流）
        """
        pkt = self._build_packet(0x21, 0xFF, bytes())

        return self._send_and_receive(pkt)

    # 12. 软件单片机复位（功能码0x22）
    def software_reset(self):
        """
        触发单片机软件复位
        :return: 响应数据（字节流）
        """
        pkt = self._build_packet(0x22, 0xFF, bytes())
        print("发送的请求包:", pkt.hex().upper())  # 十六进制显示更直观
        return self._send_and_receive(pkt)

    # 13. 清空错误代码（功能码0x23）
    def clear_error_code(self):
        """
        清空当前错误代码
        :return: 响应数据（字节流）
        """
        pkt = self._build_packet(0x23, 0xFF, bytes())
        print("发送的请求包:", pkt.hex().upper())  # 十六进制显示更直观
        return self._send_and_receive(pkt)

    # 14. 获取已连接的通道（功能码0x24）
    def get_connected_channels(self):
        """
        获取所有已连接的通道信息
        :return: 响应数据（字节流）
        """
        pkt = self._build_packet(0x24, 0xFF, bytes())
        return self._send_and_receive(pkt)

    def close(self):
        """关闭串口连接"""
        if self.ser.is_open:
            self.ser.close()
        print("串口已关闭")


# 测试代码
if __name__ == '__main__':
    pass