from Data.dataAccess import Robots, Locations
import careobot
import sunflower

class Factory(object):

    @staticmethod
    def getCurrentRobot():
        activeLocation = Locations().getActiveExperimentLocation()
        if activeLocation == None:
            return None
        robotData = Robots().getRobot(activeLocation['activeRobot'])
        if robotData != None:
            return Factory.getRobot(robotData['robotName'])
        return None
        
    @staticmethod
    def getRobot(robotName):
        print "Building class for %s" % robotName
        if robotName.startswith('Care-O-Bot'):
            cobVersion = robotName[11:].replace('.', '-')
            rosMaster = "http://cob%s-pc1:11311" % cobVersion
            return careobot.CareOBot(robotName, rosMaster)
        if robotName.startswith('UH Sunflower'):
            return sunflower.Sunflower(robotName)
        else:
            print "Unknown robot %s" % robotName
