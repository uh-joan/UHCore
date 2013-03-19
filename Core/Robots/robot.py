import io, math, time, sys
from PIL import Image
from extensions import PollingProcessor
from Data.dataAccess import Sensors
import Data.dataAccess
import rosHelper

class PoseUpdater(PollingProcessor):
    def __init__(self, robot):
        super(PoseUpdater, self).__init__()
        self._robot = robot
        self._ros = rosHelper.ROS()
        self._sensors = Sensors().findSensors()
        self._channels = {}
        self._warned = []
    
    def start(self):
        print "Started polling pose for %s" % (self._robot.name)
        self._addPollingProcessor('pose ' + self._robot.name, self.checkUpdatePose, (self._robot, ), .25)
    
    def stop(self):        
        print "Stopped polling pose for %s" % (self._robot.name)
        self._removePollingProcessor('pose ' + self._robot.name)
    
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
        self._rs = None
        self._ss = None
        self._tf = None
        self._name = name
        self._serverTopic = serverTopic
        self._imageTopic = imageTopic
        self._robInt = robotInterface
        
    @property
    def name(self):
        return self._name
    
    @property
    def _transform(self):
        if self._tf == None:
            self._tf = rosHelper.Transform(toTopic='/map', fromTopic='/base_footprint')
        return self._tf
    
    @property
    def _ros(self):
        if self._rs == None:
            #Wait to configure/initROS ROS till it's actually needed
            self._rs = rosHelper.ROS()
        return self._rs
    
    def getImage(self, retFormat='PNG'):
        img_msg = self._ros.getSingleMessage(self._imageTopic)
        if img_msg == None:
            return None
        
        imgBytes = io.BytesIO()
        imgBytes.write(img_msg.data)
        
        angle = self.getCameraAngle()

        imgBytes.seek(0)
        img = Image.open(imgBytes)
            
        #0=back, 180=front, 270=top, 90=bottom.  rotate if not front (0-180 are invalid angles, only included for 'buffer')
        if angle >= 90 and angle <= 270:
            img = img.rotate(180)
        else:
            pass
        
        retFormat = retFormat.upper()
        if retFormat == 'JPG':
            retFormat = 'JPEG'
            
        if retFormat not in Robot._imageFormats:
            retFormat = 'PNG' 
        
        imgBytes.seek(0)
        img.save(imgBytes, retFormat)

        return imgBytes.getvalue()

    def executeFunction(self, funcName, kwargs):
        return self._robInt.runFunction(funcName, kwargs)
    
    def getLocation(self, raw=False):
        p = self._pose
        ((x, y, _), rxy) = p.getRobotPose()
        if x == None or y == None:
            if raw:
                return (None, None, None)
            else:
                return (None, (None, None, None))
        
        angle = round(math.degrees(rxy))
        pos = (round(x, 3), round(y, 3), angle)
        
        if raw:
            return pos
        else:
            return Data.dataAccess.Locations.resolveLocation(pos)

    def setLight(self, colour):
        self._robInt.runComponent('light', colour)

    def setComponentState(self, name, value):
        status = self._robInt.runComponent(name, value)
        #There is a bug in the Gazebo COB interface that prevents proper trajectory tracking
        #this causes most status messages to come back as aborted while the operation is still
        #commencing, time delay to attempt to compensate...
        if status != 3 and len(self._ros.getTopics('/gazebo')) > 0:
            time.sleep(5)
            print >> sys.stderr, 'Gazebo hack: state ' + self._rs._states[status] + ' changed to state ' + self._rs._states[3]
            return self._ros._states[3]
        
        return self._ros._states[status]
        
    def getComponentPositions(self, componentName):
        try:
            self._ros.configureROS(packageName='rospy')
            import rospy
            return rospy.get_param('%s/%s' % (self._serverTopic, componentName))
        except:
            return []

    def getComponents(self):
        try:
            self._ros.configureROS(packageName='rospy')
            import rospy
            return rospy.get_param(self._serverTopic).keys()
        except:
            return []
        
    def getComponentState(self, componentName, raw=False):
        topic = '/%(name)s_controller/state' % { 'name': componentName }
        state = self._ros.getSingleMessage(topic)
        
        if raw:
            return state
        else:
            return self.resolveComponentState(componentName, state)
    
    def resolveComponentState(self, componentName, state, tolerance=0.10):
            return ('', state)
    
    def getValue(self, val):
        if type(val) is list:
            ret = val[0]
        else:
            ret = val
        
        return ret
