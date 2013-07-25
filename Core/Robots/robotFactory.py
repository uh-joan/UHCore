from Data.dataAccess import Robots, Locations
import sys

class Factory(object):

    @staticmethod
    def getCurrentRobot():
        activeLocation = Locations().getActiveExperimentLocation()
        if activeLocation == None:
            print "No experiment location set"
        elif activeLocation['activeRobot'] != None and activeLocation['activeRobot'] != '':
            robotData = Robots().getRobot(activeLocation['activeRobot'])
            if robotData != None and robotData['robotName'] != '':
                return Factory.getRobot(robotData['robotName'])
            else:
                print >> sys.stderr, "No data retrieved for robot ID %s" % activeLocation['activeRobot']
        else:
            print >> sys.stderr, "No robots set for experiment location %s" % activeLocation['location']
        
        return None
        
    @staticmethod
    def getRobot(robotName):
        if robotName == None or robotName == '':
            return Factory.getCurrentRobot()
        
        print "Building class for robot named: %s" % robotName
        robot = None
        if robotName.lower().startswith('care-o-bot'):
            print "Found cob"
            import careobot
            cobVersion = robotName[11:].replace('.', '-')
            rosMaster = "http://cob%s-pc1:11311" % cobVersion
            robot = careobot.CareOBot(robotName, rosMaster)
        if robotName.lower().startswith('sunflower'):
            print "Found sf"
            import sunflower
            robot = sunflower.Sunflower(robotName)
        if robotName.lower().startswith('dummy'):
            print "Found dummy"
            import dummy
            robot = dummy.DummyRobot(robotName)
        else:
            print >> sys.stderr, "Unknown robot %s" % robotName

        print "Finished building class %s" % robot.__class__.__name__
        return robot