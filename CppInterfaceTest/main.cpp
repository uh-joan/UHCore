#include "../CppInterface/include/robot.h"
#include <iostream>
#include <sstream>

using namespace std;

/*
 python sources need to be included (-I/usr/include/python2.x)
 python library (-lpython2.x) and UHCore (-lUHCore) libraries need to be linked
 */

template<typename T>
std::string vectorPrint(vector<T> v) {
	int size = v.size();
	std::stringstream ret;
	ret << "[";
	for(int i = 0; i < size; i++) {
		ret << v.at(i);
		if(i != size - 1) {
			ret << ",";
		}
	}
	ret << "]";
	return ret.str();
}

int main(int argc, char *argv[]) {

	std::string modulePath = "/home/nathan/git/UHCore/Core";
//	ActionHistory *hist = new ActionHistory(modulePath);
//	std::string ruleName = "testPythonInterface";
//	std::cout << hist->addHistory(ruleName) << '\n';
//	hist->addHistoryAsync(ruleName);

	Robot *rob = new Robot(modulePath); //use the current robot specified in the sessioncontrol table

	Robot::State state = rob->getComponentState("arm");

	cout << "State: " << state.name << endl;
	cout << " Joints: " << vectorPrint(state.joints) << endl;
	cout << " Positions: " << vectorPrint(state.positions) << endl;
	cout << " Goals: " << vectorPrint(state.goals) << endl;

	std::string result = rob->setComponentState("arm", "wave", true);
	cout << "Set arm to 'wave', result: " << result << endl;

	result = rob->setComponentState("tray", "raised", true);
	cout << "Set tray to 'raised', result: " << result << endl;

	int red[] = {1,0,0};
	rob->setLight(red);
	cout << "Set light to [1,0,0]" << endl;

	rob->setLight("white");
	cout << "Set light to 'white'" << endl;

	cout << "Done" << endl;

	return 0;
}
