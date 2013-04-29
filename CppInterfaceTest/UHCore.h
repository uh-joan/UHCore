#include <string>
#include <vector>

class PythonInterface {
public:
	PythonInterface(std::string modulePath);
	virtual ~PythonInterface();
};

class Robot: public PythonInterface {
public:
	enum RobotType {
		CareOBot, Sunflower
	};

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

	struct State : Position{
		std::vector<std::string> joints;
		std::vector<double> goals;
	};

	Robot(std::string modulePath, std::string robotName, RobotType robotType);
	void setLight(int color[]);
	char* getImage(std::string retFormat);
	//std::string executeFunction(std::string funcName, std::map kwargs);
	Location getLocation();
	std::string setComponentState(std::string name, std::string value);
	std::vector<Position> getComponentPositions(std::string componentName);
	std::vector<std::string> getComponents();
	State getComponentState(std::string componentName);
};

class ActionHistory: public PythonInterface {
public:
	ActionHistory(std::string modulePath);
	bool cancelPollingHistory(std::string ruleName);
	char* addPollingHistory(std::string ruleName, float delaySeconds);
	void addHistoryAsync(std::string ruleName);
	bool addHistory(std::string ruleName);
};

