import math, sys
from PIL import Image
import robot
import rosHelper
from config import robot_config
from exceptions import StopIteration

class CareOBot(robot.Robot):
    _imageFormats = ['BMP', 'EPS', 'GIF', 'IM', 'JPEG', 'PCD', 'PCX', 'PDF', 'PNG', 'PPM', 'TIFF', 'XBM', 'XPM']

    def __init__(self, name, rosMaster):
        rosHelper.ROS.configureROS(rosMaster = rosMaster)
        super(CareOBot, self).__init__(name, ActionLib(), 'script_server', '/stereo/right/image_color/compressed')
        #super(CareOBot, self).__init__(name, ScriptServer(), 'script_server', '/stereo/right/image_color/compressed')
                
    def getCameraAngle(self):
        (_, cameraState) = self.getComponentState('head', True)
        
        pos = cameraState['positions'][0]
        angle = round(math.degrees(pos), 2)
        angle = angle % 360
            
        return angle
        
    def setComponentState(self, name, value, blocking=True):
        #check if the component has been initialised, and init if it hasn't
        if len(self._ros.getTopics('/%(name)s_controller' % { 'name': name })) == 0:
            self._robInt.initComponent(name)
        
        return super(CareOBot, self).setComponentState(name, value, blocking)
    
class ScriptServer(object):

    def __init__(self):
        self._ros = rosHelper.ROS()
        self._ros.configureROS(packageName='cob_script_server')
        import simple_script_server
        self._ros.initROS()
        self._ss = simple_script_server.simple_script_server()
    
    def runFunction(self, funcName, kwargs):
        try:
            func = getattr(self._ss, funcName)
        except AttributeError:
            raise Exception('Unknown function: %s' % (funcName))
        
        return func(**kwargs)
        
    
    def initComponent(self, name):
        return self._ss.initROS(name, True).get_state()
    
    def runComponent(self, name, value, mode='', blocking=True):
        if name == 'light':
            return self._ss.set_light(value, blocking).get_state()
        elif name == 'sound':
            return self._ss.say(value, blocking).get_state()
        else:
            return self._ss.move(name, value, blocking, mode).get_state()

class ActionLib(object):
    _specialCases = {
                    'light': {'function': 'set_light', 'mode': ''},
                    'sound': {'function': 'say', 'mode': 'FEST_EN' }
                    }
    
    def __init__(self):
        self._ros = rosHelper.ROS()
        self._ros.configureROS(packageName='actionlib_interface')
        import actionlib, cob_script_server.msg
        self._ssMsgs = cob_script_server.msg
        
        self._ros.initROS()
        self._client = actionlib.SimpleActionClient('/script_server', self._ssMsgs.ScriptAction)
        self._client.wait_for_server()
        
    def runFunction(self, funcName, kwargs):
        name = None
        value = None
        mode = None
        blocking = True
        service_name = None
        duration = None
        
        if kwargs.has_key('component_name'):
            name = str(kwargs['component_name']).encode('ascii', 'ignore')
            
        if kwargs.has_key('parameter_name'):
            value = str(kwargs['parameter_name']).encode('ascii', 'ignore')
                        
        if kwargs.has_key('mode'):
            mode = str(kwargs['mode']).encode('ascii', 'ignore')
            
        if kwargs.has_key('blocking'):
            blocking = bool(kwargs['blocking'])
            
        if kwargs.has_key('service_name'):
            service_name = str(kwargs['service_name']).encode('ascii', 'ignore')
            
        if kwargs.has_key('duration'):
            duration = float(kwargs['duration'])

        goal = self._ssMsgs.ScriptGoal(
                          function_name=str(funcName).encode('ascii', 'ignore'),
                          component_name=name,
                          parameter_name=value,
                          mode=mode,
                          #blocking=blocking,
                          service_name=service_name,
                          duration=duration
                          )
        
        if blocking:
            return self._client.send_goal_and_wait(goal)
        else:
            return self._client.send_goal(goal)
        
    def initComponent(self, name):
        if name not in ActionLib._specialCases.keys():
            func = 'init'
            goal = self._ssMsgs.ScriptGoal(
                              function_name=func.encode('ascii', 'ignore'),
                              component_name=name.encode('ascii', 'ignore'),
                              blocking=True)
            return self._client.send_goal_and_wait(goal)
        return 3
    
    def runComponent(self, name, value, mode=None, blocking=True):
        if name not in ActionLib._specialCases.keys():
            func = "move"
        else:
            func = ActionLib._specialCases[name]['function']
            mode = ActionLib._specialCases[name]['mode']

        goal = self._ssMsgs.ScriptGoal(
                          function_name=str(func).encode('ascii', 'ignore'),
                          component_name=str(name).encode('ascii', 'ignore'),
                          parameter_name=str(value).encode('ascii', 'ignore'),
                          mode=str(mode).encode('ascii', 'ignore'),
                          #blocking=bool(blocking)
                          )
        
        if(blocking):
            status = self._client.send_goal_and_wait(goal)
        else:
            self._client.send_goal(goal)
            status = 1
            
        return status

class PoseUpdater(robot.PoseUpdater):
    def __init__(self, robot):
        super(PoseUpdater, self).__init__(robot)
        self._rangeSensors = robot_config[robot.name]['phidgets']
        self._trayState = robot_config[robot.name]['tray']
        self._headState = robot_config[robot.name]['head']
    
    def checkUpdatePose(self, robot):
        self.updateTray(robot)
        self.updateHead(robot)
        
    def updateHead(self, robot):
        (name, _) = robot.getComponentState('head')
        if name == self._headState['front']:
            headPosition = 'front'
        elif name == self._headState['back']:
            headPosition = 'back'
        else:
            headPosition = 'inProgress'
            
        _states = {
                   'eyePosition': (headPosition, headPosition),
                   }

        for key, value in _states.items():
            if value[1] != None:
                try:
                    #sensor = next(s for s in self._sensors if s['ChannelDescriptor'] == "%s:%s" % (self._robot.name, key))
                    sensor = next(s for s in self._sensors if s['name'] == "%s" % (key))
                    if key in self._warned:
                        self._warned.remove(key)
                except StopIteration:
                    if key not in self._warned:
                        print >> sys.stderr, "Warning: Unable to locate sensor record for %s sensor %s." % (self._robot.name, key)
                        self._warned.append(key)
                    continue
                
                _id = sensor['sensorId']
                self._channels[key] = {
                                         'id': _id,
                                         'room': self._robot.name,
                                         'channel': key,
                                         'value': value[0],
                                         'status': value[1] }
        

    def updateTray(self, robot):
        (name, _) = robot.getComponentState('tray')

        trayPosition = None
        trayIsEmpty = None
        if name == self._trayState['raised']:
            trayPosition = 'raised'
        elif name == self._trayState['lowered']:
            trayPosition = 'lowered'
        else:
            trayPosition = 'inProgress'
        
        ranges = []
        for topic in self._rangeSensors:
            ranges.append(self._ros.getSingleMessage(topic=topic, timeout=0.25))
        
        if None not in ranges:
            threshold = 0.2
            trayIsEmpty = 'empty'
            for range_ in ranges:
                if range_ < threshold:
                    trayIsEmpty = 'full'
                    break

            if 'phidget'in self._warned:
                self._warned.remove('phidget')
        else:
            trayIsEmpty = 'unknown'
            if 'phidget' not in self._warned: 
                self._warned.append('phidget')
                print "Phidget sensors not ready before timeout"

        _states = {
                   'trayStatus': (trayPosition, trayPosition),
                   'trayIs': (trayIsEmpty, trayIsEmpty) }

        for key, value in _states.items():
            if value[1] != None:
                try:
                    #sensor = next(s for s in self._sensors if s['ChannelDescriptor'] == "%s:%s" % (self._robot.name, key))
                    sensor = next(s for s in self._sensors if s['name'] == "%s" % (key))
                    if key in self._warned:
                        self._warned.remove(key)
                except StopIteration:
                    if key not in self._warned:
                        print >> sys.stderr, "Warning: Unable to locate sensor record for %s sensor %s." % (self._robot.name, key)
                        self._warned.append(key)
                    continue
                
                _id = sensor['sensorId']
                self._channels[key] = {
                                         'id': _id,
                                         'room': self._robot.name,
                                         'channel': key,
                                         'value': value[0],
                                         'status': value[1] }
                
if __name__ == '__main__':
    from robotFactory import Factory
    robot = Factory.getCurrentRobot()
    """
    frequency=math.pi*2/100
    phase1=2
    phase2=0
    phase3=4
    center=128
    width=127
    l=50
    robot = CareOBot('Care-O-Bot 3.2', 'http://cob3-2-pc1:11311')
    while True:
        for i in range(0, l):
            red = (math.sin(frequency*i + phase1) * width + center) / 255
            grn = (math.sin(frequency*i + phase2) * width + center) / 255
            blu = (math.sin(frequency*i + phase3) * width + center) / 255
            robot.setLight([red, grn, blu])

    """
    import locations
    from history import SensorLog
    l = locations.RobotLocationProcessor(robot)
    rp = PoseUpdater(robot)
    sr = SensorLog(rp.channels, rp.robot.name)

    rp.start()
    sr.start()
    
    l.start()
    
    while True:
        try:
            sys.stdin.read()
        except KeyboardInterrupt:
            break
    l.stop()

    sr.stop()
    rp.stop()