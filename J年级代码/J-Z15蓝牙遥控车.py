"""
J-Z15《蓝牙遥控车》

遥控器：A 开灯、B 关灯；设置键（SETUP/SET 等）转向回正；行驶与转向见下方分支。
近距离时禁止前进、允许后退。
"""

from r2_encoder_motor import EncoderMotor
from r2_remoter import Remoter
from r2_rgb_ring import RGBRing
from r2_distance_sensor import DistanceSensor
from time import sleep
import r2

motor1 = EncoderMotor('A')  # 控制转向
motor2 = EncoderMotor('B')  # 控制前进
distance_sensor = DistanceSensor('C')  # 距离传感器连接在C口
rgb_ring = RGBRing('D')  # 灯环连接在D口


# 方向角度：上电复位；前进/后退/OK 不会自动回正（仅左右键改转向）
INITIAL_ANGLE = 0
motor1.reset(INITIAL_ANGLE)
# 方向角度设置
LEFT_ANGLE = 330  # 左转角度
RIGHT_ANGLE = 30   # 右转角度

# 速度（固定档位，不再用加减键调速）
SPEED = 100  # 电机速度（0-100）

# 距离阈值（mm）：小于此值视为过近，禁止前进，可后退
DISTANCE_NEAR_MM = 100


# 按键状态跟踪
current_key = None
# 灯状态
light_on = False
# 电机运行状态跟踪
current_motor_state = None  # 0=前进, 1=后退, None=停止


def handle_remote(code):
    global current_key
    current_key = code
    print(f"按下按键: {code}")


remoter = Remoter()
remoter.start_receiving_code(handle_remote)


while True:
    # 灯光：A 开灯、B 关灯（优先处理；固件可能返回 'a'/'A'）
    if current_key is not None:
        lk = str(current_key).strip().upper()
        if lk == 'A':
            light_on = True
            print("开灯")
            current_key = None
        elif lk == 'B':
            light_on = False
            print("关灯")
            current_key = None

    distance = distance_sensor.read()
    too_close = distance < DISTANCE_NEAR_MM

    # 距离过近时：若正在前进则强制停车；后退不受影响
    if too_close and current_motor_state == 0:
        print(f"距离过近: {distance}mm，禁止前进，已停车")
        motor2.start(0, 0)
        current_motor_state = None
        sleep(0.05)

    # 电机控制状态
    motor_direction = None  # 0=前进, 1=后退, None=本帧无行驶指令
    steer_direction = None  # 'left'/'right'/'center'(设置键回正), None=转向不动
    stop_drive = False  # True=仅停止前进电机，转向保持当前角度

    # 根据当前按键状态更新变量（行驶、鸣笛）
    k = str(current_key).strip().upper() if current_key is not None else None
    if k == 'UP':  # 前进（近距离不允许）
        if too_close:
            print(f"距离过近({distance}mm)，无法前进")
            current_key = None
        else:
            print(f"前进，速度: {SPEED}%")
            motor_direction = 0
            current_key = None
    elif k == 'DOWN':  # 后退（近距离仍允许）
        print(f"后退，速度: {SPEED}%")
        motor_direction = 1
        current_key = None
    elif k == 'LEFT':  # 左转
        print("左转")
        steer_direction = 'left'
        current_key = None
    elif k == 'RIGHT':  # 右转
        print("右转")
        steer_direction = 'right'
        current_key = None
    elif k == 'OK':  # OK键 - 仅停止行驶，转向保持当前角度不回正
        print("OK键 - 停止")
        stop_drive = True
        current_key = None
    elif k in ('SETUP', 'SET', 'SETTINGS', 'MENU') or k == '设置':
        print("设置键 - 转向回正")
        steer_direction = 'center'
        current_key = None
    elif k == 'C':  # C键 - 鸣笛
        print("鸣笛")
        r2.play_audio(8)  # 播放鸣笛声音
        current_key = None

    # 控制前进电机（motor2）；前进/后退/OK 均不会令转向电机回正
    if stop_drive:
        motor2.start(0, 0)
        current_motor_state = None
    elif motor_direction == 0:
        motor2.start(0, SPEED)  # 前进（近距离时本帧不会收到 UP）
        current_motor_state = 0
    elif motor_direction == 1:
        motor2.start(1, SPEED)  # 后退
        current_motor_state = 1

    # 控制转向：左右转向；设置键回正到 INITIAL_ANGLE
    if steer_direction == 'left':
        motor1.to_angle(LEFT_ANGLE, 100, 2, False)
    elif steer_direction == 'right':
        motor1.to_angle(RIGHT_ANGLE, 100, 2, False)
    elif steer_direction == 'center':
        motor1.to_angle(INITIAL_ANGLE, 100, 2, False)

    # 控制灯光
    if light_on:
        rgb_ring.set_all(255, 255, 255)  # 白色灯
    else:
        rgb_ring.clear_color()  # 关闭灯
