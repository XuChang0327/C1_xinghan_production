"""
J-Z15《蓝牙遥控车》
为了实现可以实时加速、减速，增加了在处理遥控器按键时，根据当前速度动态调整电机速度。
"""

from r2_encoder_motor import EncoderMotor
from r2_remoter import Remoter
from r2_rgb_ring import RGBRing
from r2_distance_sensor import DistanceSensor
from time import sleep
import r2

motor1 = EncoderMotor('A')  # 控制转向
motor2 = EncoderMotor('B') # 控制前进
distance_sensor = DistanceSensor('C')  # 距离传感器连接在C口
rgb_ring = RGBRing('D')  # 灯环连接在D口


# 重置方向电机到初始角度
motor1.reset(0)
INITIAL_ANGLE = 0  # 初始角度
# 方向角度设置
LEFT_ANGLE = 330  # 左转角度
RIGHT_ANGLE = 30   # 右转角度

# 速度设置
SPEED = 100  # 电机速度（0-100）
MIN_SPEED = 10  # 最小速度
MAX_SPEED = 100  # 最大速度
SPEED_STEP = 10  # 速度调整步长


# 按键状态跟踪
current_key = None
# 灯状态
light_on = False
# 电机运行状态跟踪
current_motor_state = None  # 0=前进, 1=后退, None=停止

# 定义遥控器按键处理函数 - 只更新按键状态
def handle_remote(code):
    global current_key
    current_key = code
    print(f"按下按键: {code}")

# 创建遥控器对象并开始接收编码
remoter = Remoter()
remoter.start_receiving_code(handle_remote)


while True:
    # 检测距离传感器，小于100mm时自动停车
    distance = distance_sensor.read()
    if distance < 100 :
        print(f"距离过近: {distance}mm，自动停车")
        motor1.start(0, 0)  # 停止动力电机
        current_motor_state = None  # 更新电机状态为停止
        sleep(0.1)
    
    # 电机控制状态
    motor_direction = None  # 0=前进, 1=后退, None=停止
    steer_direction = None  # 'left'=左转, 'right'=右转, 'center'=回正, None=不变
    
    # 根据当前按键状态更新变量
    if current_key == 'UP':  # 前进
        print(f"前进，速度: {SPEED}%")
        motor_direction = 0
        current_key = None
    elif current_key == 'DOWN':  # 后退
        print(f"后退，速度: {SPEED}%")
        motor_direction = 1
        current_key = None
    elif current_key == 'LEFT':  # 左转
        print("左转")
        steer_direction = 'left'
        current_key = None
    elif current_key == 'RIGHT':  # 右转
        print("右转")
        steer_direction = 'right'
        current_key = None
    elif current_key == 'OK':  # OK键 - 停止并回正
        print("OK键 - 停止并回正")
        motor_direction = None
        steer_direction = 'center'
        current_key = None
    elif current_key == 'A':  # A键 - 开灯
        light_on = True
        print("开灯")
        current_key = None
    elif current_key == 'B':  # B键 - 关灯
        light_on = False
        print("关灯")
        current_key = None
    elif current_key == 'C':  # C键 - 鸣笛
        print("鸣笛")
        r2.play_audio(1)  # 播放鸣笛声音
        current_key = None
    elif current_key == '+':  # +键 - 增加速度
        if SPEED < MAX_SPEED:
            SPEED += SPEED_STEP
            print(f"速度增加到: {SPEED}%")
            # 如果电机正在运行，应用新速度
            if current_motor_state is not None:
                motor_direction = current_motor_state
        else:
            print("已达到最大速度")
        current_key = None
    elif current_key == '-':  # -键 - 减小速度
        if SPEED > MIN_SPEED:
            SPEED -= SPEED_STEP
            print(f"速度减小到: {SPEED}%")
            # 如果电机正在运行，应用新速度
            if current_motor_state is not None:
                motor_direction = current_motor_state
        else:
            print("已达到最小速度")
        current_key = None
    
    # 执行硬件控制操作
    # 控制电机
    if motor_direction == 0:
        motor2.start(0, SPEED)  # 前进
        current_motor_state = 0
    elif motor_direction == 1:
        motor2.start(1, SPEED)  # 后退
        current_motor_state = 1
    elif motor_direction is None and steer_direction == 'center':
        motor2.start(0, 0)  # 停止
        current_motor_state = None
    
    # 控制转向
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
    

