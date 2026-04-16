# S-Z15《遥控机器人》：遥控器 A 开灯、B 关灯

from r2_encoder_motor import EncoderMotor
from r2_remoter import Remoter
from r2_rgb_ring import RGBRing
from r2_distance_sensor import DistanceSensor
from time import sleep


motor1 = EncoderMotor('A')
motor2 = EncoderMotor('B')
rgb_ring = RGBRing('F')
distance_sensor = DistanceSensor('E')

SPEED = 30

light_on = False
current_key = None
current_motor_state = None

def handle_remote(code):
    global current_key
    current_key = code
    print(f"按下按键: {code}")

remoter = Remoter()
remoter.start_receiving_code(handle_remote)


while True:
    # 灯光：A 开灯、B 关灯（优先处理）
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
    if distance < 150:
        if current_motor_state == 0:
            print(f"距离过近: {distance}mm，自动停车")
            motor1.start(0, 0)
            motor2.start(0, 0)
            current_motor_state = None
            sleep(0.5)
            continue
    
    motor_direction = None
    
    k = str(current_key).strip().upper() if current_key is not None else None
    if k == 'UP':
        print(f"前进，速度: {SPEED}%")
        motor_direction = 0
        current_key = None
    elif k == 'DOWN':
        print(f"后退，速度: {SPEED}%")
        motor_direction = 1
        current_key = None
    elif k == 'LEFT':
        print("左转")
        motor1.start(1, SPEED)
        motor2.start(1, SPEED)
        current_key = None
    elif k == 'RIGHT':
        print("右转")
        motor1.start(0, SPEED)
        motor2.start(0, SPEED)
        current_key = None
    elif k == 'OK':
        print("停止")
        motor1.start(0, 0)
        motor2.start(0, 0)
        motor_direction = None
        current_motor_state = None
        current_key = None
    
    if motor_direction == 0:
        motor1.start(1, SPEED)
        motor2.start(0, SPEED)
        current_motor_state = 0
    elif motor_direction == 1:
        motor1.start(0, SPEED)
        motor2.start(1, SPEED)
        current_motor_state = 1
    
    if light_on:
        rgb_ring.set_all(255, 255, 255)
    else:
        rgb_ring.clear_color()
    
    sleep(0.1)
