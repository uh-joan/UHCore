from ouimeaux.environment import Environment
from Data.dataAccess import Sensors

class actuators():

    def __init__ (self):
	self._env = Environment(self._setup_switch)
        self._sensors = Sensors()

    def _setup_switch(self,switch):
	print "Switch found!", switch.name

    def start(self):
	self._env.start()

    def _getName(self):
	sensorName=self._env.list_switches()
	return sensorName[0]

    def _getNameList(self):
	sensorNameList=self._env.list_switches()
	return sensorNameList

    def _getIdFromName(self, name):
	if name=='Lamp01':
		idSensor='91'
	elif name=='LivingRoomLamp':
		idSensor='92'
	elif name=='KitchenCoffeMachine':
		idSensor='93'
	elif name=='LivingRoomTV':
		idSensor='94'
	else:
		idSensor=null
	return idSensor

    def _getValue(self, name):
	if name=='Lamp01':
		idSensor='91'
	elif name=='LivingRoomLamp':
		idSensor='92'
	elif name=='KitchenCoffeMachine':
		idSensor='93'
	elif name=='LivingRoomTV':
		idSensor='94'
	else:
		idSensor=null
	return self._sensors.getSensor(idSensor)

    def _get_switch(self, name):
	return self._env.get_switch(name)

    def _on_switch(self, switch):
	switch.basicevent.SetBinaryState(BinaryState=1)

    def _off_switch(self, switch):
	switch.basicevent.SetBinaryState(BinaryState=0)

    def setOn(self, name):
	self._sensors.updateSensor(self._getIdFromName(name), 1.0, 'On')
	print " %s has been switched On" % name

    def setOff(self, name):
	self._sensors.updateSensor(self._getIdFromName(name), 0.0, 'Off')
	print " %s has been switched Off" % name


if __name__ == '__main__':
    import sys,time
    act = actuators()
    act.start()

    #ini the previous State of each Switch, in order to check if it has changed in the DB
    prevSwitchStatus = []
    for pSS in act._getNameList():
	#prevSwitchStatus[] = act._getValue(act._getName())['status']
	prevSwitchStatus.append({'name':pSS , 'status':act._getValue(pSS)['status']})

    while True:
	time.sleep(1)

	#get actual status of the Switches
	switchStatus = []
	for sS in act._getNameList():
		#switchStatus = act._getValue(act._getName())['status']
		switchStatus.append({'name':sS , 'status':act._getValue(sS)['status']})
      
	#go over actual and previous status of the swtches
	for sS in switchStatus:
		for pSS in prevSwitchStatus:
			if sS['name']==pSS['name']:
				if sS['status'] == 'On' and pSS['status']== 'Off':
				#if it has gone in the DB from OFF to ON switch on the corresponding Switch
					print "%s is %s, was %s. Change value." % (sS['name'], sS['status'], pSS['status'])
					act._on_switch(act._get_switch(sS['name']))
					print "changed %s to %s " % (sS['name'], sS['status'])
				elif sS['status'] == 'Off' and pSS['status']== 'On':
				#if it has gone in the DB from ON to OFF switch off the corresponding Switch
					print "%s is %s, was %s. Change value." % (sS['name'], sS['status'], pSS['status'])
					act._off_switch(act._get_switch(sS['name']))
					print "changed %s to %s " % (sS['name'], sS['status'])

	prevSwitchStatus = switchStatus

