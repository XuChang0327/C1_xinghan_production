from time import sleep
from r2_encoder_motor import EncoderMotor
from r2_sound_sensor import SoundSensor
import r2


m1 = EncoderMotor('A')
ss = SoundSensor('B')

while True:
    n1 = ss.read()
    n2 = round(n1 * 100 / 4095)
    print(n2)
    m1.start(0,n2)
    sleep(0.5)
