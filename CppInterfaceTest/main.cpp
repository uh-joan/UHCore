#include "UHCore.h"
#include <iostream>
#include <sstream>

using namespace std;

/*
 be sure to link in python during compilation ('-lpython2.6' for gcc linker)
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

	Robot *rob = new Robot(modulePath, "Care-O-Bot 3.2", Robot::CareOBot);
	Robot::State state = rob->getComponentState("arm");

	cout << "State: " << state.name << endl;
	cout << " Joints: " << vectorPrint(state.joints) << endl;
	cout << " Positions: " << vectorPrint(state.positions) << endl;
	cout << " Goals: " << vectorPrint(state.goals) << endl;

	cout << "Done" << endl;
	return 0;
}
