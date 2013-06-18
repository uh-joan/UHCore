import math
import Robots.rosHelper

class ProxemicMover(object):

    def __init__(self, robot):
        self._robot = robot
        Robots.rosHelper.ROS.configureROS(packageName='accompany_proxemics')
        import rospy
        import tf
        import accompany_context_aware_planner.GetPotentialProxemicsLocations
        self._rospy = rospy
        self._tf = tf
    
    def gotoTarget(self, user, posture, x, y, theta):
        if self._robot == None:
            #TODO error handling
            return False
        
        self._rospy.wait_for_service('get_potential_proxemics_locations')
        getProxemicLocation = self._rospy.ServiceProxy('get_potential_proxemics_locations', accompany_context_aware_planner.GetPotentialProxemicsLocations)
        try:
            pose = ()
            pose.orientation = math.radians(theta)
            pose.position = (x, y, 0)
            response = getProxemicLocation(userId=user, userPosture=posture, userPose=pose)
            if len(response.targetPoses) == 0:
                self._rospy.loginfo("No valid target pose was found.")
            else:
                self._rospy.loginfo("Response target Poses size is: %d" % (len(response.targetPoses)))
                self._rospy.loginfo("Request is:  x=%f, y=%f, z=%f yaw=%f" % (x, y, 0, theta))
                
                for targets in targets.targetPoses:
                    self._rospy.loginfo("MsgSeq=%d, time=%2f, coordinate frame=%s " % (
                                                                                    targets.header.seq,
                                                                                    self._rospy.Time.now().toSec()-targets.header.stamp.toSec(),
                                                                                    targets.header.frame_id.c_str()))
                    
                    (_, _, yaw) = self._tf.transformations.euler_from_quaternion(targets.pose.orientation)
                    self._rospy.info("Response is: x=%f, y=%f, z=%f yaw=%f" % (
                                                                                targets.pose.position.x,
                                                                                targets.pose.position.y,
                                                                                targets.pose.position.z,
                                                                                math.degrees(yaw)))
                    
                    if self._robot.setComponentState('base', [x,y,yaw]) == 3:
                        return True

        except self._rospy.ServiceException, e:
            print "Service did not process request: %s"%str(e)
        
        return False

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser('proxemics.py userId userPosture X(m) Y(m) Orientation(deg)')
    (_, args) = parser.parse_args()
    if(len(args) != 5):
        parser.error("incorrect number of arguments")
        
    from Robots.careobot import CareOBot
    r = CareOBot('Care-O-Bot 3.2', 'http://cob3-2-pc1:11311')
    p = ProxemicMover(r)
    p.gotoTarget(int(args[1]), int(args[2]), float(args[3]), float(args[4]), float(args[5]))
    