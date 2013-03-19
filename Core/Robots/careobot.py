import math, sys
from PIL import Image
import robot
import rosHelper
from exceptions import StopIteration

class CareOBot(object):
    _imageFormats = ['BMP', 'EPS', 'GIF', 'IM', 'JPEG', 'PCD', 'PCX', 'PDF', 'PNG', 'PPM', 'TIFF', 'XBM', 'XPM']

    def __init__(self, name='Care-O-Bot 3.2'):
        super(CareOBot, self).__init__(name, ActionLib(), 'script_server', '/stereo/right/image_color/compressed')
                
    def getCameraAngle(self):
        cameraState = self.getComponentState('head', True)
        
        angle = round(math.degrees(cameraState.actual.positions[0]), 2)
        angle = angle % 360
            
        return angle
        
    def setComponentState(self, name, value):
        #check if the component has been initialised, and init if it hasn't
        if len(self._ros.getTopics('/%(name)s_controller' % { 'name': name })) == 0:
            self._robInt.initComponent(name)
        
        return super(CareOBot, self).setComponentState(name, value)
    
    def resolveComponentState(self, componentName, state, tolerance=0.10):
        if state == None:
            return (None, None)
        
        curPos = state.actual.positions

        positions = self.getComponentPositions(componentName)

        if len(positions) == 0:
            return ('', curPos)

        name = None
        diff = None
        for positionName in positions:
            positionValue = self.getValue(positions[positionName])
            if type(positionValue) is not list:
                #we don't currently handle nested types
                continue

            if len(positionValue) != len(curPos):
                #raise Exception("Arguement lengths don't match")
                continue
            
            dist = 0
            for index in range(len(positionValue)):
                dist += math.pow(curPos[index] - positionValue[index], 2)
            dist = math.sqrt(dist)
            if name == None or dist < diff:
                name = positionName
                diff = dist
                        
        if diff <= tolerance:
            return (name, curPos)
        else:
            return ('', curPos)    

class ScriptServer(object):

    def __init__(self):
        self._ros = rosHelper.ROS()
        self._ros.configureROS(packageName='simple_script_server')
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
    def __init__(self, robot=None):
        if robot == None:
            robot = CareOBot()
        super(PoseUpdater, self).__init__(robot)
    
    def checkUpdatePose(self, robot):
        self.updateTray(robot)

    def updateTray(self, robot):
        (name, _) = robot.getComponentState('tray')

        trayIsRaised = None
        trayIsLowered = None
        trayIsEmpty = None
        if name == 'up':
            trayIsRaised = 'up'
        else:
            trayIsRaised = ''
            
        if name == 'down':
            trayIsLowered = 'down'
        else:
            trayIsLowered = ''
            
        range0 = self._ros.getSingleMessage(topic='/range_0', timeout=0.25)
        range1 = self._ros.getSingleMessage(topic='/range_0', timeout=0.25)
        range2 = self._ros.getSingleMessage(topic='/range_0', timeout=0.25)
        range3 = self._ros.getSingleMessage(topic='/range_0', timeout=0.25)
        if range0 != None and range1 != None and range2 != None and range3 != None:
            threshold = 0.2
            if range0.range < threshold or range1.range < threshold or range2.range < threshold or range3.range < threshold:
                trayIsEmpty = 'full'
                
            else:
                trayIsEmpty = 'empty'
        else:
            trayIsEmpty = None
            print "Phidget sensors not ready before timeout"

        _states = {
                   'trayIsRaised': (trayIsRaised == 'up', trayIsRaised),
                   'trayIsLowered': (trayIsLowered == 'down', trayIsLowered),
                   'trayIsEmpty': (trayIsEmpty == 'empty', trayIsEmpty) }

        for key, value in _states.items():
            if value[1] != None:
                try:                           
                    sensor = next(s for s in self._sensors if s['ChannelDescriptor'] == "%s:%s" % (self._robot.name, key))
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
    robot = CareOBot()
    """
    frequency=math.pi*2/100
    phase1=2
    phase2=0
    phase3=4
    center=128
    width=127
    l=50
    robot = CareOBot()
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
    
