#ifndef ACTION_HISTORY
#define ACTION_HISTORY
#include "base.h"
#include <string>
//#include <map>
//using namespace std;

class Robot: public PythonInterface {
public:
	struct Location {
		double x;
		double y;
		double orientation;
		std::string name;
	};

	struct Position {
		std::string name;
		std::vector<double> positions;
	};

	struct State: Position {
		std::vector<std::string> joints;
		std::vector<double> goals;
	};

	Robot(std::string modulePath, std::string robotName);
	void setLight(int color[]);
	char* getImage(std::string retFormat);
	//std::string executeFunction(std::string funcName, std::map kwargs);
	Location getLocation();
	std::string setComponentState(std::string name, std::string value);
	std::vector<Position> getComponentPositions(std::string componentName);
	std::vector<std::string> getComponents();
	State getComponentState(std::string componentName);
protected:
	std::vector<double> parseDoubleArray(PyObject* array);
	std::vector<std::string> parseStringArray(PyObject* array);
	PyObject* getDefaultClassInstance();

private:
	PyObject* pInstance;
	std::string name;
};

#endif //ACTION_HISTORY
