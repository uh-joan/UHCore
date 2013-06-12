import careobot
import time
import rosHelper
rosHelper.ROS.configureROS(rosMaster='http://cob3-2-pc1:11311')

if __name__ == '__main__':
    c = careobot.CareOBot()
	#base straight
    c.setComponentState('base', [1.52,0.4,1.55],False)
    c.setComponentState('torso', [[0,0,0,0.35]])
    c.setComponentState('torso', 'home')
    c.setComponentState('torso', [[0,0,0,0.35]])
    c.setComponentState('torso', 'home')
