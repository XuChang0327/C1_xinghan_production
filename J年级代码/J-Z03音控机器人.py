print('J-Z03《音控机器人》')
print('硬件连接:')
print('  - EncoderMotor: A')
print('  - SoundSensor: B')


from time import sleep
from r2_encoder_motor import EncoderMotor
from r2_sound_sensor import SoundSensor


m1 = EncoderMotor('A')
ss = SoundSensor('B')

while True:
    n1 = ss.read()
    # 映射到 0-70：满量程若用 100 易因速度过大导致机器人跌倒
    n2 = round(n1 / 4095 * 70)
    print(f"sound:{n1} | motor:{n2}")
    m1.start(1, n2)
    sleep(0.1)