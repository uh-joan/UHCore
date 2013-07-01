#ifndef UHCORE_INTERFACE
#define UHCORE_INTERFACE
#include <string>
#include <vector>
#include "boost/python.hpp"
#include <string>
#include <vector>
#include <iostream>
#include <map>

class PythonInterface {
public:
	PythonInterface(std::string modulePath);
	virtual ~PythonInterface();
protected:
	virtual PyObject* getDefaultClassInstance() = 0;
	PyObject* getClassInstance(std::string moduleName, std::string className, PyObject* constructorArgs);
	PyObject* getClassObject(std::string moduleName, std::string className);
	template<typename T>
	PyObject* callMethod(std::string methodName, std::string argFormat, T arg) {
		return callMethod(getDefaultClassInstance(), methodName, argFormat, arg);
	}
	template<typename T, typename R>
	PyObject* callMethod(std::string methodName, std::string argFormat, T arg1, R arg2) {
		return callMethod(getDefaultClassInstance(), methodName, argFormat, arg1, arg2);
	}
	template<typename T, typename R, typename K>
	PyObject* callMethod(std::string methodName, std::string argFormat, T arg1, R arg2, K arg3) {
		return callMethod(getDefaultClassInstance(), methodName, argFormat, arg1, arg2, arg3);
	}
	PyObject* callMethod(std::string methodName) {
		return callMethod(getDefaultClassInstance(), methodName);
	}
	PyObject* callMethod(std::string methodName, std::string value) {
		return callMethod(getDefaultClassInstance(), methodName, value);
	}

	PyObject* callMethod(PyObject* pInstance, std::string methodName) {
		return callMethod(pInstance, methodName, "", "");
	}
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string value) {
		char* v = strdup(value.c_str());
		char* f = strdup("(s)");
		return callMethod(pInstance, methodName, f, v);
	}
	template<typename T>
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string argFormat, T arg);
	template<typename T, typename R>
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string argFormat, T arg1, R arg2);
	template<typename T, typename R, typename K>
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string argFormat, T arg1, R arg2, K arg3);
private:
	std::string modulePath;
	std::map<std::string, PyObject*> pObjectCache;
};

template<typename T, typename R, typename K>
PyObject* PythonInterface::callMethod(PyObject* instance, std::string methodName, std::string argFormat, T arg1, R arg2, K arg3) {
	char* m = strdup(methodName.c_str());

	PyObject *pValue;
	if (!argFormat.empty()) {
		char* f = strdup(argFormat.c_str());
		pValue = PyObject_CallMethod(instance, m, f, arg1, arg2, arg3);
	} else {
		pValue = PyObject_CallMethod(instance, m, NULL);
	}

	if (pValue != NULL) {
		return pValue;
	} else {
		std::cout << "Error while calling method" << '\n';
		PyErr_Print();
		PyErr_Clear();
		return NULL;
	}
}

template<typename T, typename R>
PyObject* PythonInterface::callMethod(PyObject* instance,
		std::string methodName, std::string argFormat, T arg1, R arg2) {
	char* m = strdup(methodName.c_str());

	PyObject *pValue;
	if (!argFormat.empty()) {
		char* f = strdup(argFormat.c_str());
		pValue = PyObject_CallMethod(instance, m, f, arg1, arg2);
	} else {
		pValue = PyObject_CallMethod(instance, m, NULL);
	}

	if (pValue != NULL) {
		return pValue;
	} else {
		std::cout << "Error while calling method" << '\n';
		PyErr_Print();
		PyErr_Clear();
		return NULL;
	}
}

template<typename T>
PyObject* PythonInterface::callMethod(PyObject* instance,
		std::string methodName, std::string argFormat, T arg) {
	char* m = strdup(methodName.c_str());

	PyObject *pValue;
	if (!argFormat.empty()) {
		char* f = strdup(argFormat.c_str());
		pValue = PyObject_CallMethod(instance, m, f, arg);
	} else {
		pValue = PyObject_CallMethod(instance, m, NULL);
	}

	if (pValue != NULL) {
		return pValue;
	} else {
		std::cout << "Error while calling method" << '\n';
		PyErr_Print();
		PyErr_Clear();
		return NULL;
	}
}

class Robot: public PythonInterface {
public:
	struct Location {
		// x position in world coordinates
		double x;

		// y position in world coordinates
		double y;

		// orientation in degrees
		double orientation;

		// if known, the name of the location
		std::string name;
	};

	struct Position {
		// the name of the position
		std::string name;

		// the joint values of the position
		std::vector<double> positions;
	};

	struct State: Position {

		// the joint names used in the position
		std::vector<std::string> joints;

		// the goal values for the joints
		std::vector<double> goals;
	};

	// modulePath is the URI to the UHCore module
	// create an interface to the current active robot
	Robot(std::string modulePath);

	// modulePath is the URI to the UHCore module
	// create an interface to the specified robot
	Robot(std::string modulePath, std::string robotName);

	// set the light to the specified RGB value
	void setLight(int color[]);

	// set the light to the specified color
	void setLight(std::string color);

	// returns the image from the robots camera, rotated if needed
	char* getImage(std::string retFormat);

	// return the current location of the robot
	Location getLocation();

	// set the named component to the named state
	std::string setComponentState(std::string name, std::string value, bool blocking);

	// set the named component to the specified position
	std::string setComponentState(std::string name, std::vector<double> jointGoals, bool blocking);

	// return all possible positions for a component
	std::vector<Position> getComponentPositions(std::string componentName);

	// return a string vector containing the name of all the components
	std::vector<std::string> getComponents();

	/// return the current state of a component
	State getComponentState(std::string componentName);
protected:
	std::vector<double> parseDoubleArray(PyObject* array);
	std::vector<std::string> parseStringArray(PyObject* array);
	PyObject* getDefaultClassInstance();

private:
	PyObject* pInstance;
	std::string name;
};

#endif //#UHCORE_INTERFACE
