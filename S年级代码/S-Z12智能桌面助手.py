import r2
from time import sleep
from r2_rgb_ring import RGBRing


rr = RGBRing('A')

r2.start_online_instruct_speech_recognition() # True会使用大模型，False会使用关键字匹配

brightness = 128
while True:
    sleep(0.2)
    res = r2.consume_last_instruction()
    print(res)
    if res == '打开' or res == '开灯':
        rr.set_all(brightness,brightness,brightness)
        r2.speak_online('灯已经打开啦！')
        
    if res == '关闭' or res == '关灯':
        rr.clear_color()
        r2.speak_online('灯已经关闭啦！')
        
    if res == '红色':
        rr.set_all(brightness,0,0)
        r2.speak_online('灯已经是红色啦！')

    if res == '蓝色':
        rr.set_all(0,0,brightness)
        r2.speak_online('灯已经是蓝色啦！')
        
    if res == '放大':
        brightness = brightness + 40
        rr.set_all(brightness,brightness,brightness)
        r2.speak_online('亮度增加啦！')

    if res == '缩小':
        brightness = brightness - 40
        rr.set_all(brightness,brightness,brightness)
        r2.speak_online('亮度减小啦！')
