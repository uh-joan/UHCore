# Add project reference
import sys, os
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
sys.path.append(path)

import io, math, time
from extensions import PollingProcessor
from Data.dataAccess import Sensors, Users
from Data.proxemics import ProxemicMover
from config import robot_config
import Data.dataAccess

_states = {
        0: 'PENDING',
        1: 'ACTIVE',
        2: 'PREEMPTED',
        3: 'SUCCEEDED',
        4: 'ABORTED',
        5: 'REJECTED',
        6: 'PREEMPTING',
        7: 'RECALLING',
        8: 'RECALLED',
        9: 'LOST'}

class PoseUpdater(PollingProcessor):
    def __init__(self, robot):
        super(PoseUpdater, self).__init__()
        self._robot = robot
        self._sensors = Sensors().findSensors(None, False)
        self._channels = {}
        self._warned = []
    
    def start(self):
        print "Started polling pose for %s" % (self._robot.name)
        self._addPollingProcessor('pose ' + self._robot.name, self.checkUpdatePose, (self._robot,), .25)
    
    def stop(self):        
        print "Stopped polling pose for %s" % (self._robot.name)
        self._removePollingProcessor('pose ' + self._robot.name)
    
    def updateStates(self, states):
        for key, value in states.items():
            if value != None and value[1] != None:
                try:
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
        
    @property
    def robot(self):
        return self._robot
    
    @property
    def channels(self):
        if self._channels == None:
            self._channels = {}
        
        return self._channels
    
    def checkUpdatePose(self, robot):
        pass

class Robot(object):
    _imageFormats = ['BMP', 'EPS', 'GIF', 'IM', 'JPEG', 'PCD', 'PCX', 'PDF', 'PNG', 'PPM', 'TIFF', 'XBM', 'XPM']

    def __init__(self, name, robotInterface, serverTopic, imageTopic):
        self._name = name
        self._robIntClass = robotInterface
        self._robIntInstance = None
        
    @property
    def _robInt(self):
        if self._robIntInstance == None:
            self._robIntInstance = self._robIntClass()
            
        return self._robIntInstance
        
    @property
    def name(self):
        return self._name
    
    @property
    def _transform(self):
        return None
            
    def getImage(self, retFormat='PNG'):
        return None
    
    def play(self, fileName, blocking=True):
        print "Play: %s" % fileName 
    
    def say(self, text, languageCode="en-gb", blocking=True):
        print "Say (%s): %s" % (languageCode, text)
        
    def sleep(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def executeFunction(self, funcName, kwargs):
        return self._robInt.runFunction(funcName, kwargs)
    
    def getLocation(self, dontResolveName=False):
        return ('', (None, None, None))

    def setLight(self, colour):
        self._robInt.runComponent('light', colour)

    def setComponentState(self, name, value, blocking=True):
        if robot_config[self.name].has_key(name) and robot_config[self.name][name].has_key('positions') and robot_config[self.name][name]['positions'].has_key(value):
            value = robot_config[self.name][name]['positions'][value]
            
        if name == "base" and value == "userLocation":
            user = Users().getActiveUser()
            if user['xCoord'] != None and user['yCoord'] != None and user['orientation'] != None:
                try:
                    p = ProxemicMover(self)
                    if p.gotoTarget(user['userId'], user['poseId'], user['xCoord'], user['yCoord'], user['orientation']):
                        return self._ros._states[3]
                    else:
                        pass
                        #return self._ros._states[4]
                except Exception as e:
                    print >> sys.stderr, "Exception occured while calling proxemics: %s" % e
                
                value = [user['xCoord'], user['yCoord'], math.radians(user['orientation'])]
                print >> sys.stderr, "Proxemics failed, proceeding directly to location (%s, %s, %s)" % (
                                                                                                            user['xCoord'], 
                                                                                                            user['yCoord'], 
                                                                                                            user['orientation'])
            else:
                print >> sys.stderr, "Could not go to user location, missing information.  X:%s, Y:%s, T:%s" % (
                                                                                                            user['xCoord'], 
                                                                                                            user['yCoord'], 
                                                                                                            user['orientation'])

        status = self._robInt.runComponent(name, value, None, blocking)
        return _states[status]
    
    def getComponentPositions(self, componentName):
        return {}

    def getComponents(self):
        return []
        
    def getComponentState(self, componentName, dontResolveName=False):
        ret = {'name': '', 'positions': [], 'goals': [], 'joints': [] }
        return ('', ret)
        
    def resolveComponentState(self, componentName, state, tolerance=0.5):
        if state == None:
            return (None, None)
        
        curPos = state['positions']

        positions = self.getComponentPositions(componentName)

        if len(positions) == 0:
            return ('', state)

        name = None
        diff = None
        for positionName in positions:
            positionValue = self._getValue(positions[positionName])
            if type(positionValue) is not list:
                # we don't currently handle nested types
                continue

            if len(positionValue) != len(curPos):
                # raise Exception("Arguement lengths don't match")
                continue
            
            dist = 0
            for index in range(len(positionValue)):
                dist += math.pow(curPos[index] - positionValue[index], 2)
            dist = math.sqrt(dist)
            if name == None or dist < diff:
                name = positionName
                diff = dist
                        
        if diff <= tolerance:
            if robot_config[self.name].has_key(componentName) and robot_config[self.name][componentName].has_key('positions'):
                positions = robot_config[self.name][componentName]['positions']
                for key, value in positions.items():
                    if value == name:
                        return (key, state)
            return (name, state)
        else:
            return ('', state)
    
    def _getValue(self, val):
        if type(val) is list:
            ret = val[0]
        else:
            ret = val
        
        return ret


class ROSRobot(Robot):
    _imageFormats = ['BMP', 'EPS', 'GIF', 'IM', 'JPEG', 'PCD', 'PCX', 'PDF', 'PNG', 'PPM', 'TIFF', 'XBM', 'XPM']

    def __init__(self, name, robotInterface, serverTopic, imageTopic):
        super(ROSRobot, self).__init__(name, robotInterface)
        self._rs = None
        self._tf = None
        self._serverTopic = serverTopic
        self._imageTopic = imageTopic
    
    @property
    def _transform(self):
        if self._tf == None:
            try:
                import rosHelper
                self._tf = rosHelper.Transform(rosHelper=self._rs, toTopic='/map', fromTopic='/base_footprint')
            except Exception as e:
                print >> sys.stderr, "Error occured while calling transform: %s" % repr(e)
        return self._tf
        
    @property
    def _ros(self):
        if self._rs == None:
            import rosHelper
            # Wait to configure/initROS ROS till it's actually needed
            self._rs = rosHelper.ROS()
        return self._rs
    
    def getImage(self, retFormat='PNG'):
        if not robot_config[self.name]['head'].has_key('camera'):
            return None
        
        img_msg = self._ros.getSingleMessage(self._imageTopic)
        if img_msg == None:
            return None
        
        from PIL import Image
        imgBytes = io.BytesIO()
        imgBytes.write(img_msg.data)
        
        imgBytes.seek(0)
        img = Image.open(imgBytes)

        if robot_config[self._name]['head']['camera'].has_key('rotate'):
            angle = self.getCameraAngle() or 0
    
            a = abs(angle - robot_config[self._name]['head']['camera']['rotate']['angle'])
            if a > 180:
                a = abs(a - 360)
            
            # 0=back, 180=front, 270=top, 90=bottom.  rotate if not front (0-180 are invalid angles, only included for 'buffer')
            # if angle <= 90 and angle >= 270:
            if a <= robot_config[self._name]['head']['camera']['rotate']['distance']:
                img = img.rotate(robot_config[self._name]['head']['camera']['rotate']['amount'])
        
        retFormat = retFormat.upper()
        if retFormat == 'JPG':
            retFormat = 'JPEG'
            
        if retFormat not in Robot._imageFormats:
            retFormat = 'PNG' 
        
        imgBytes.seek(0)
        img.save(imgBytes, retFormat)

        return imgBytes.getvalue()
    
    def getLocation(self, dontResolveName=False):
        tf = self._transform
        if tf == None:
            return ('', (None, None, None))

        ((x, y, _), rxy) = tf.getTransform()
        if x == None or y == None:
            return ('', (None, None, None))
        
        angle = round(math.degrees(rxy))
        pos = (round(x, 3), round(y, 3), angle)
        
        if dontResolveName:
            return ('', pos)
        else:
            return Data.dataAccess.Locations.resolveLocation(pos)

    def setComponentState(self, name, value, blocking=True):
        status = super(ROSRobot, self).setComponentState(name, value, blocking)
        # There is a bug in the Gazebo COB interface that prevents proper trajectory tracking
        # this causes most status messages to come back as aborted while the operation is still
        # commencing, time delay to attempt to compensate...
        if status != 3 and len(self._ros.getTopics('/gazebo')) > 0:
            time.sleep(1)
            print >> sys.stderr, 'Gazebo hack: state ' + self._rs._states[status] + ' changed to state ' + self._rs._states[3]
            return _states[3]
        
        return _states[status]
    
    def getComponentPositions(self, componentName):
        return self._ros.getParam('%s/%s' % (self._serverTopic, componentName))

    def getComponents(self):
        return self._ros.getParam(self._serverTopic).keys()
        
    def getComponentState(self, componentName, dontResolveName=False):
        topic = '/%(name)s_controller/state' % { 'name': componentName }
        state = self._ros.getSingleMessage(topic)
        
        try:
            ret = {'name': componentName, 'positions': state.actual.positions, 'goals': state.desired.positions, 'joints': state.joint_names }
        except:
            print "Error retrieving joint state" 
            ret = {'name': componentName, 'positions': (), 'goals': (), 'joints': () }
            
        if dontResolveName:
            return ('', ret)
        else:
            return self.resolveComponentState(componentName, ret)

if __name__ == "__main__":
    from robotFactory import Factory
    c = Factory.getCurrentRobot()
    print c.getComponents()
