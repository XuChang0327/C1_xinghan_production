"""
S-Z09《呆猫收纳盒》
硬件连接:
  - EncoderMotor: A
  - DistanceSensor: B

"""

from time import sleep
from r2_distance_sensor import DistanceSensor
from r2_encoder_motor import EncoderMotor
import r2


m1 = EncoderMotor('A')
ds = DistanceSensor('B')

m1.reset(0)

r2.matrix_show_light_effect(7, True, 255)
while True:
    n = ds.read()
    print(n)
    if n < 50:
        m1.to_angle(90, 100, 2, False)
        r2.play_audio(10)
        sleep(3)
    else:
        m1.to_angle(0, 100, 2, False)