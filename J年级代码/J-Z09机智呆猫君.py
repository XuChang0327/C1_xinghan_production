print('J-Z09《机智呆猫君》')
print('Distance: B, Motor Head: D, Motor Hand: F')

from time import sleep
from r2_distance_sensor import DistanceSensor
from r2_encoder_motor import EncoderMotor
import r2


ds = DistanceSensor('B')
m_head = EncoderMotor('D') # 头
m_hand = EncoderMotor('F') # 手


m_hand.reset(0)
m_head.reset(0)

while True:
    n = ds.read()
    print(n)

    if n < 100:
        print('近')
        m_head.to_angle(0, 100, 2, False)
        r2.play_audio(12) # 小猫叫
        m_hand.to_angle(270, 100, 2, False)
        sleep(0.1)
        m_hand.to_angle(0, 100, 2, False)
        sleep(0.1)

    else:
        print('远')
        sleep(0.01)
        m_head.to_angle(30, 100, 2, False)
        sleep(0.01)
        m_head.to_angle(330, 100, 2, False)
        sleep(0.01)
