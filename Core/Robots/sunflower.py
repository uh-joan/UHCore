import math
from robot import Robot

class Sunflower(Robot):
    _imageFormats = ['BMP', 'EPS', 'GIF', 'IM', 'JPEG', 'PCD', 'PCX', 'PDF', 'PNG', 'PPM', 'TIFF', 'XBM', 'XPM']

    def __init__(self, name='Sunflower'):
        from rosHelper import ROS
        ROS.configureROS(version='electric', rosMaster='http://sf1-1-pc1:11311', overlayPath='/home/nathan/git/sunflower/')
        super(Sunflower, self).__init__(name, ActionLib(), 'sf_controller', '')

    def getImage(self, leftRight='right', retFormat='PNG'):
        pass

class ActionLib(object):
        
    def __init__(self):
        import rosHelper
        self._ros = rosHelper.ROS()
        self._ros.configureROS(packageName='sf_controller')
        self._ros.configureROS(packageName='sf_lights')
        
        import actionlib, sf_controller.msg, sf_lights.msg
        self._sfMsgs = sf_controller.msg
        self._sfLights = sf_lights.msg
        
        self._ros.initROS()
        self._sfClient = actionlib.SimpleActionClient('/sf_controller', self._sfMsgs.SunflowerAction)
        self._sfClient.wait_for_server()

        self._sfLight = actionlib.SimpleActionClient('/lights', self._sfLights.LightsAction)
        self._sfLight.wait_for_server()
        
    def runFunction(self, funcName, kwargs):
        return 5
        
    def initComponent(self, name):
        return 3
    
    def runComponent(self, name, value, mode=None, blocking=True):
        if name == 'light':
            goal = self._sfLights.LightsGoal(rgb=value)
            client = self._sfLight
        else:
            (namedPosition, joints) = (value, []) if str == type(value) else ('', value)
            
            goal = self._sfMsgs.SunflowerGoal(
                                                   component=name,
                                                   namedPosition=namedPosition,
                                                   jointPositions=joints)
            client = self._sfClient

        if(blocking):
            status = client.send_goal_and_wait(goal)
        else:
            client.send_goal(goal)
            status = 1
            
        return status
    
if __name__ == '__main__':
    s = Sunflower()
    print s.setLight([1,0,0])
    # joint_names: ["head_pan", "head_tilt", "neck_upper", "neck_lower"]
    print s.setComponentState('head',
                               [ math.pi * (7.0 / 4),
                                 math.pi * (1.0 / 4),
                                 math.pi * (2.0 / 4),
                                 math.pi * (-2.0 / 4)])
    #time.sleep(2)
    print s.setComponentState('head',
                               [ math.pi * (-7.0 / 4),
                                 math.pi * (-1.0 / 4),
                                 math.pi * (2.0 / 4),
                                 math.pi * (-2.0 / 4)])
    #time.sleep(2)
    # print s.setComponentState('tray', {'component':'head', 'position':'', 'jointPositions':[4.0, 1.0, 0.0, 0.0]})
    # time.sleep(2)
    print s.setComponentState('head', 'home')
    print s.setLight([0,0,0])
    
