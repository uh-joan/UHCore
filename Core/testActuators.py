from actuators import actuators
import time

if __name__ == '__main__':
    act = actuators()

    time.sleep(4)
    act.setOn("Lamp01")

    time.sleep(4)
    act.setOff("Lamp01")

    time.sleep(4)
    act.setOn("Lamp01")

    time.sleep(4)
    act.setOff("Lamp01")


