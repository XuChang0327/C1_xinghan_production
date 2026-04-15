# -*- coding: utf-8 -*-
"""
编码电机测距程序：通过轮子转动计算行驶距离
基于星瀚（YBC R2）r2_encoder_motor API
请在星瀚设备上运行，r2_encoder_motor 为设备内置模块。
"""
import time
import math
from r2_encoder_motor import EncoderMotor  # type: ignore
from r2_touchscreen_text import Text  # type: ignore


# 轮子直径（毫米），请根据实际轮子测量后修改
WHEEL_DIAMETER_MM = 65.0
# 端口：编码电机连接的端口（A-H 或 blue/magenta 等）
MOTOR_PORT = "F"


def wheel_circumference_mm(diameter_mm):
    """轮子周长（毫米）= π × 直径"""
    return math.pi * diameter_mm


def angle_delta(prev_angle, curr_angle, direction):
    """
    计算两次采样间转过的角度（考虑 0/359 跨越）。
    direction: 0=顺时针(角度增加), 1=逆时针(角度减少)
    """
    raw_delta = curr_angle - prev_angle
    # 处理跨越 359->0 或 0->359
    if raw_delta > 180:
        raw_delta -= 360
    elif raw_delta < -180:
        raw_delta += 360
    if direction == 1:
        raw_delta = -raw_delta
    return raw_delta


def _update_screen_text(text_widget, dist_mm, total_degrees, elapsed_s, title="测距中", target_cm=None):
    """更新触屏显示的文本内容。"""
    dist_cm = dist_mm / 10.0
    lines = [
        title,
        "距离: {:.2f} cm  ({:.0f} mm)".format(dist_cm, dist_mm),
        "角度: {:.1f} deg".format(total_degrees),
        "用时: {:.2f} s".format(elapsed_s),
    ]
    if target_cm is not None:
        lines.append("目标: {:.2f} cm".format(target_cm))
    content = "\n".join(lines)
    # 使用位置参数（设备上不支持 keyword arguments）
    text_widget.draw_string(content, 10, 20, 30, 255, 255, 255)


def measure_distance(port=MOTOR_PORT, wheel_diameter_mm=WHEEL_DIAMETER_MM,
                     poll_interval_s=0.05, duration_s=None, show_screen=True):
    """
    在电机转动过程中持续计算并打印累计距离。

    参数:
        port: 编码电机端口
        wheel_diameter_mm: 轮子直径（毫米）
        poll_interval_s: 轮询 state() 的间隔（秒）
        duration_s: 测量总时长（秒），None 表示一直测到手动中断
        show_screen: 是否在触屏上实时显示结果（默认 True）
    """
    motor = EncoderMotor(port)
    circ_mm = wheel_circumference_mm(wheel_diameter_mm)

    # 软重置：把当前位置当作 0 度，便于累计
    motor.reset(reset_type=1)
    time.sleep(0.1)

    prev_angle = 0
    total_degrees = 0.0
    start = time.ticks_ms()
    last_print = start

    screen_text = None
    if show_screen:
        # Text(text, font_size, x, y, r, g, b) 仅位置参数
        screen_text = Text("测距中...", 10, 20, 20, 0, 255, 255)
        screen_text.show()

    print("开始测距（Ctrl+C 结束）")
    print("轮子直径: {:.1f} mm, 周长: {:.2f} mm".format(wheel_diameter_mm, circ_mm))
    print("-" * 40)

    try:
        while True:
            state = motor.state()
            direction, speed, angle, is_torque, is_blocked, stop_reason = state
            now_ms = time.ticks_ms()

            delta = angle_delta(prev_angle, angle, direction)
            total_degrees += delta
            prev_angle = angle

            dist_mm = (total_degrees / 360.0) * circ_mm
            elapsed_s = time.ticks_diff(now_ms, start) / 1000.0

            # 实时更新触屏显示
            if show_screen and screen_text is not None:
                _update_screen_text(screen_text, dist_mm, total_degrees, elapsed_s, title="测距中")

            # 每 0.5 秒打印一次
            if time.ticks_diff(now_ms, last_print) >= 500:
                print("距离: {:.2f} mm  ({:.2f} cm)  |  累计角度: {:.1f}°  |  用时: {:.2f} s".format(
                    dist_mm, dist_mm / 10.0, total_degrees, elapsed_s))
                last_print = now_ms

            if duration_s is not None:
                if time.ticks_diff(now_ms, start) >= duration_s * 1000:
                    break

            time.sleep(poll_interval_s)

    except KeyboardInterrupt:
        pass

    motor.stop()
    dist_mm = (total_degrees / 360.0) * circ_mm
    elapsed_s = time.ticks_diff(time.ticks_ms(), start) / 1000.0

    if show_screen and screen_text is not None:
        _update_screen_text(screen_text, dist_mm, total_degrees, elapsed_s, title="测量结束")

    print("-" * 40)
    print("测量结束 | 总距离: {:.2f} mm ({:.2f} cm) | 总角度: {:.1f}° | 用时: {:.2f} s".format(
        dist_mm, dist_mm / 10.0, total_degrees, elapsed_s))
    return dist_mm


def run_forward_and_measure_cm(target_cm, port=MOTOR_PORT, wheel_diameter_mm=WHEEL_DIAMETER_MM,
                               speed=50, poll_interval_s=0.05, show_screen=True):
    """
    让电机正转，直到轮子走过的距离达到 target_cm（厘米），然后停止并返回实际距离。

    参数:
        target_cm: 目标距离（厘米）
        port: 编码电机端口
        wheel_diameter_mm: 轮子直径（毫米）
        speed: 电机速度 0~100
        poll_interval_s: 轮询间隔（秒）
        show_screen: 是否在触屏上实时显示结果（默认 True）
    """
    motor = EncoderMotor(port)
    circ_mm = wheel_circumference_mm(wheel_diameter_mm)
    target_mm = target_cm * 10.0

    motor.reset(reset_type=1)
    time.sleep(0.1)
    motor.start(direction=0, speed=speed)  # 0=顺时针

    prev_angle = 0
    total_degrees = 0.0
    start = time.ticks_ms()

    try:
        while True:
            state = motor.state()
            direction, speed_val, angle, _, _, _ = state
            delta = angle_delta(prev_angle, angle, direction)
            total_degrees += delta
            prev_angle = angle

            dist_mm = (total_degrees / 360.0) * circ_mm
            elapsed_s = time.ticks_diff(time.ticks_ms(), start) / 1000.0

            if show_screen and screen_text is not None:
                _update_screen_text(
                    screen_text, dist_mm, total_degrees, elapsed_s,
                    title="行驶中", target_cm=target_cm
                )

            if dist_mm >= target_mm:
                break
            time.sleep(poll_interval_s)
    finally:
        motor.stop()

    dist_mm = (total_degrees / 360.0) * circ_mm
    elapsed_s = time.ticks_diff(time.ticks_ms(), start) / 1000.0
    if show_screen and screen_text is not None:
        _update_screen_text(
            screen_text, dist_mm, total_degrees, elapsed_s,
            title="到达", target_cm=target_cm
        )
    print("目标: {:.2f} cm, 实际: {:.2f} cm ({:.2f} mm)".format(target_cm, dist_mm / 10.0, dist_mm))
    return dist_mm / 10.0


# ============ 使用示例 ============
if __name__ == "__main__":
    # 方式1：手动控制电机，程序只负责测距（例如在别处 motor.start()，这里只测距）
    # 测量 10 秒后自动结束
    measure_distance(port="F", wheel_diameter_mm=85.0, duration_s=100)
    # 方式2：让电机正转直到走满 50 cm 后停止
    # run_forward_and_measure_cm(50, port="A", wheel_diameter_mm=65.0, speed=50)
