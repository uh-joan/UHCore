import careobot
import time
import rosHelper
rosHelper.ROS.configureROS(rosMaster='http://cob3-2-pc1:11311')

if __name__ == '__main__':
    c = careobot.CareOBot()
    #c.setComponentState('base', [4.35,1,0])
    #c.setComponentState('base', [4.35,1,-0.4])
    #c.setComponentState('base', [4.35,1,0.4])
    #c.setComponentState('base', [4.35,1,0])
    c.setComponentState('head', 'front')
    c.setComponentState('torso', 'left')
    c.setComponentState('torso', 'right')
    c.setComponentState('torso', 'front')
    c.setComponentState('head', [[-3.0]], False)
    time.sleep(1)
    c.setComponentState('head', [[-2.8]], False)
    time.sleep(1)
    c.setComponentState('head', [[-3.0]], False)
    time.sleep(1)
    c.setComponentState('head', [[-2.8]], False)
