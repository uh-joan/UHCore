#include "robot.h"
#include <iostream>
#include <sstream>
#include <boost/thread.hpp>

using namespace std;

// python sources need to be included (-I/usr/include/python2.x)
// python library (-lpython2.x) and UHCore (-lUHCore) libraries need to be linked

template<typename T>
string vectorPrint(vector<T> v) {
	int size = v.size();
	stringstream ret;
	ret << "[";
	for (int i = 0; i < size; i++) {
		ret << v.at(i);
		if (i != size - 1) {
			ret << ",";
		}
	}
	ret << "]";
	return ret.str();
}

Robot *rob;

void testRobotFuncs() {
	//	Robot::State state = rob->getComponentState("arm");
	//
	//	cout << "State: " << state.name << endl;
	//	cout << " Joints: " << vectorPrint(state.joints) << endl;
	//	cout << " Positions: " << vectorPrint(state.positions) << endl;
	//	cout << " Goals: " << vectorPrint(state.goals) << endl;
	//
	string result = "";
	//	result = rob->setComponentState("arm", "wave", false);
	//	cout << "Set arm to 'wave', result: " << result << endl;
	//
	//	Robot::Location pos = rob->getLocation();
	//	cout << "Start Pose: [" << pos.x << "," << pos.y << "," << pos.orientation << "]" << endl;
	//
	//	vector<double> newPos(3);
	//	newPos[0] = pos.x;
	//	newPos[1] = pos.y;
	//	newPos[2] = (pos.orientation + 90) * 0.0174532925;
	//
	//	cout << "Pose: " << vectorPrint(newPos) << endl;
	//	result = rob->setComponentState("base", newPos, true);
	//	cout << "Rotate 90 degrees: " << result << endl;

	result = rob->setComponentState("base", "userLocation", true);
	cout << "Robot to user: " << result << endl;

	result = rob->setComponentState("tray", "raised", true);
	cout << "Set tray to 'raised', result: " << result << endl;

	result = rob->setComponentState("torso", "shake", true);
	cout << "Set torso to 'left', result: " << result << endl;

	cout << "Sleep for 500ms...";
	rob->sleep(500);

	int red[] = { 1, 0, 0 };
	rob->setLight(red);
	cout << "Set light to [1,0,0]" << endl;

	rob->setLight("white");
	cout << "Set light to 'white'" << endl;

	rob->play("filename.wav");
	rob->say("test");
	rob->say("test", "en-us");

}

void threadChainer() {
	boost::thread threads[10];
	for (int i = 0; i < 10; i++) {
		threads[i] = boost::thread(testRobotFuncs);
	}

	for (int i = 0; i < 10; i++) {
		threads[i].join();
	}
}

int main(int argc, char *argv[]) {

	string modulePath = "/home/nathan/git/UHCore/Core";
	rob = new Robot(modulePath, "Dummy Test robot"); //use the current robot specified in the sessioncontrol table

//	ActionHistory *hist = new ActionHistory(modulePath);
//	string ruleName = "testPythonInterface";
//	cout << hist->addHistory(ruleName) << '\n';
//	hist->addHistoryAsync(ruleName);

	boost::thread threads[10];
	for (int i = 0; i < 10; i++) {
		threads[i] = boost::thread(threadChainer);
	}

	for (int i = 0; i < 10; i++) {
		threads[i].join();
	}

	cout << "Done" << endl;

	return 0;
}
