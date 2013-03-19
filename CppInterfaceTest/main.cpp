#include "UHCore.h"
#include <iostream>

using namespace std;

/*
 be sure to link in python during compilation ('-lpython2.6' for gcc linker)
 */

int main(int argc, char *argv[]) {

	std::string modulePath = "/home/nathan/git/UHCore/Core";
	ActionHistory *hist = new ActionHistory(modulePath);
	std::string ruleName = "testPythonInterface";
	std::cout << hist->addHistory(ruleName) << '\n';
	hist->addHistoryAsync(ruleName);

	std::string robotName = "Sunflower";
	Robot *rob = new Robot(modulePath, robotName, Robot::Sunflower);
	int color[] = {0,0,0};
	std::cout << rob->setLight(color) << '\n';
	//std::cout << rob->

	cout << "Done" << endl;
	return 0;
}

