#include "UHCore.h"

/*
 be sure to link python during compilation ('-lpython2.6' for gcc linker)
 */

int main(int argc, char *argv[]) {
	// This has suddenly become necessary in python 2.7, will be fixed in a later version of UHCore
	if (!Py_IsInitialized()) {
		Py_Initialize();
		std::cout << "Python Initialized" << std::endl;
	}

	std::string modulePath = "/home/nathan/git/UHCore/Core";
	actionHistoryExample(modulePath);
	robotExample(modulePath);

	return 0;
}

void robotExample(std::string modulePath) {
	ActionHistory *hist = new ActionHistory(modulePath);
	const char* ruleName = "testPythonInterface";
	bool success = hist->addHistory(ruleName);
	hist->addHistoryAsync(ruleName);
	delete hist;
	return 0;
}

void robotExample(std::string modulePath) {
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

	int red[] = { 1, 0, 0 };
	rob->setLight(red);
	cout << "Set light to [1,0,0]" << endl;

	rob->setLight("white");
	cout << "Set light to 'white'" << endl;

	cout << "Done" << endl;

	return 0;
}
