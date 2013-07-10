from Data.dataAccess import Robots, Locations
import careobot
import sunflower

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
                print "No data retrieved for robot ID %s" % activeLocation['activeRobot']
        else:
            print "No robots set for experiment location %s" % activeLocation['location']
        
        return None
        
    @staticmethod
    def getRobot(robotName):
        if robotName == None or robotName == '':
            return Factory.getCurrentRobot()
        
        print "Building class for %s" % robotName
        if robotName.startswith('Care-O-Bot'):
            cobVersion = robotName[11:].replace('.', '-')
            rosMaster = "http://cob%s-pc1:11311" % cobVersion
            return careobot.CareOBot(robotName, rosMaster)
        if robotName.startswith('UH Sunflower'):
            return sunflower.Sunflower(robotName)
        else:
            print "Unknown robot %s" % robotName
