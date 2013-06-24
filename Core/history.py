import datetime
from Data.dataAccess import DataAccess
from threading import Thread
from extensions import PollingThread, PollingProcessor
from Robots.careobot import CareOBot

class ActionHistory(object):
    _defaultImageType = 'png'
    _runningThreads = {}
    
    def cancelPollingHistory(self, ruleName):
        if ActionHistory._runningThreads.has_key(ruleName):
            ah = ActionHistory._runningThreads[ruleName]
            ah.cancel()
            ah.join()
            return True
        else:
            return False

    def addPollingHistory(self, ruleName, delaySeconds):
        if not ActionHistory._runningThreads.has_key(ruleName):
            ahw = PollingThread(target=self.addHistory, delayTime=delaySeconds, args=(ruleName,), completeCallback=self._removePollingHistory)
            ahw.start()
            ActionHistory._runningThreads[ruleName] = ahw
        
        return ruleName
    
    def _removePollingHistory(self, ruleName):
        return ActionHistory._runningThreads.pop(ruleName, None)

    def addHistoryAsync(self, ruleName, imageBytes=None, imageType=None):
        Thread(target=self.addHistory, args=(ruleName, imageBytes, imageType)).start()

    def addHistory(self, ruleName, imageBytes=None, imageType=None):
        
        from Robots.robotFactory import Factory
        cob = Factory.getCurrentRobot()
        dao = DataAccess()
        dateNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        location = dao.getRobotByName(cob.name)['locationId']
        
        historyId = dao.saveHistory(dateNow, ruleName, location)
        
        if(historyId > 0):
            dao.saveSensorHistory(historyId)

            if imageType == None:
                imageType = ActionHistory._defaultImageType

            if imageBytes == None:
                imageBytes = cob.getImage(retFormat=imageType)

            if imageBytes != None:
                dao.saveHistoryImage(historyId, imageBytes, imageType)
        
        return historyId > 0

################################################################################
#
# Logger thread
#
# Logs channel value and / or status changes into a (separate) MySQL
# database table.
#
################################################################################
class SensorLog(PollingProcessor):    
    def __init__ (self, channels, name=''):
        super(SensorLog, self).__init__()
        self._dao = DataAccess().sensors
        self._channels = channels
        self._logCache = {}
        self._name = name
                
    def start(self):
        if self._name != '':
            print "Started updating database for %s sensor changes" % (self._name)
        else:
            print "Started updating database for [unknown] sensor changes"
        self._addPollingProcessor('sensorHistory', self.checkUpdateSensors, (self._channels, ), 0.01)

    def stop(self):
        if self._name != '':
            print "Stopped updating database for %s sensor changes" % (self._name)
        else:
            print "Stopped updating database for [unknown] sensor changes"

        self._removePollingProcessor('sensorHistory')

    def checkUpdateSensors(self, channels):
        for k in channels.keys():
            if not self._logCache.has_key(k):
                current = self._dao.getSensor(channels[k]['id'])
                self._logCache.setdefault(k, { 'value': current['value'], 'status': current['status']})
            if self._logCache[k]['status'] != channels[k]['status']:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                success = self._dao.saveSensorLog(
                                                  channels[k]['id'], 
                                                  channels[k]['value'], 
                                                  channels[k]['status'],
                                                  timestamp,
                                                  channels[k]['room'],
                                                  channels[k]['channel'])
                if success:
                    print "Updated sensor log for %(id)s to %(status)s" % { 
                                                                           'id':channels[k]['channel'], 
                                                                           'status': channels[k]['status']
                                                                           }
                    self._logCache[k]['value'] = channels[k]['value']
                    self._logCache[k]['status'] = channels[k]['status']
        

if __name__ == '__main__':
    import sys
    import config
    import sensors
    from Data.dataAccess import Locations
    from sensors import GEOSystem, ZigBee, ZWaveHomeController, ZWaveVeraLite
        
    activeLocation = Locations().getActiveExperimentLocation() 
    
    if activeLocation == None:
        print "Unable to determine active experiment Location"
        exit
    
    sensorPollers = []
    dataUpdaters = []
    for sensorType in config.locations_config[activeLocation['location']]['sensors']:
        sensor = None
        if sensorType == 'ZWaveHomeController':
            sensor = ZWaveHomeController(config.server_config['zwave_ip'])
        elif sensorType == 'ZWaveVeraLite':
            sensor = ZWaveVeraLite(config.server_config['zwave_ip'], config.server_config['zwave_port'])
        elif sensorType == 'ZigBee':
            sensor = ZigBee(config.server_config['udp_listen_port'])
        elif sensorType == 'GEOSystem':
            sensor = GEOSystem(config.server_config['mysql_geo_server'],
                            config.server_config['mysql_geo_user'],
                            config.server_config['mysql_geo_password'],
                            config.server_config['mysql_geo_db'],
                            config.server_config['mysql_geo_query'])

        if sensor != None:
            sensorPollers.append(sensor)
            dataUpdaters.append(SensorLog(sensor.channels, sensor.__class__.__name__))
        
    for sensorPoller in sensorPollers:
        sensorPoller.start()
    
    for dataUpdater in dataUpdaters:
        dataUpdater.start()
    
    while True:
        try:
            sys.stdin.read()
        except KeyboardInterrupt:
            break

    for sensorPoller in sensorPollers:
        sensorPoller.stop()
    
    for dataUpdater in dataUpdaters:
        dataUpdater.stop()
