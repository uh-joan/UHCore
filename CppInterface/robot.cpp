#include "robot.h"
#include "Python.h"
#include <string>
#include <vector>
#include <iostream>
#include <stdio.h>

Robot::Robot(std::string modulePath) :
		PythonInterface(modulePath) {
	Robot::name = "";
	Robot::pInstance = NULL;
}

Robot::Robot(std::string modulePath, std::string robotName) :
		PythonInterface(modulePath) {
	Robot::name = robotName;
	Robot::pInstance = NULL;
}

PyObject* Robot::getDefaultClassInstance() {
	if (pInstance == NULL) {
		PyObject* pClass = getClassObject("Robots.robotFactory", "Factory");
		if (Robot::name != "") {
			pInstance = callMethod(pClass, "getRobot", Robot::name.c_str());
		} else {
			pInstance = callMethod(pClass, "getCurrentRobot");
		}
		Py_DECREF(pClass);
	}

	return pInstance;
}

void Robot::setLight(int color[]) {
	PyObject *pValue = callMethod("setLight", "([i,i,i])", color);
	Py_XDECREF(pValue);
}

void Robot::setLight(std::string color) {
	PyObject *pValue = callMethod("setLight", color);
	Py_XDECREF(pValue);
}

Robot::Location Robot::getLocation() {
	PyObject *pValue = callMethod("getLocation");
	/** pValue = ('locName', (x, y, orientation)) **/

	Robot::Location l;
	if (pValue != NULL) {
		if (!PySequence_Check(pValue)) {
			//problem!
		} else {
			l.name = PyString_AsString(PySequence_GetItem(pValue, 0));
			l.x = PyFloat_AsDouble(
					PySequence_GetItem(PySequence_GetItem(pValue, 1), 0));
			l.y = PyFloat_AsDouble(
					PySequence_GetItem(PySequence_GetItem(pValue, 1), 1));
			l.orientation = PyFloat_AsDouble(
					PySequence_GetItem(PySequence_GetItem(pValue, 1), 2));
		}

		Py_DECREF(pValue);
	}

	return l;
}

std::string Robot::setComponentState(std::string name,
		std::vector<double> jointGoals, bool blocking) {

	std::string format = "(s, [";
	for (int i = 0; i < jointGoals.size(); i++) {
		format += "i,";
	}
	format = format.substr(0, format.length() - 1) + "], b)";

	double goals[jointGoals.size()];
	std::copy(jointGoals.begin(), jointGoals.end(), goals);
	char* n = strdup(name.c_str());
	char* f = strdup(format.c_str());

	PyObject *pValue = callMethod("setComponentState", n, f, goals, blocking);
	/** pValue = "SUCCESS" **/

	if (pValue != NULL) {
		char* ret = PyString_AsString(pValue);
		Py_DECREF(pValue);
		return ret;
	} else {
		std::cout << "Error while calling method" << '\n';
		PyErr_Print();
	}

	return "Error";
}

std::string Robot::setComponentState(std::string name, std::string value, bool blocking) {
	char* n = strdup(name.c_str());
	char* v = strdup(value.c_str());
	PyObject *pValue = callMethod("setComponentState", "(s,s, b)", n, v, blocking);
	/** pValue = "SUCCESS" **/

	if (pValue != NULL) {
		char* ret = PyString_AsString(pValue);
		Py_DECREF(pValue);
		return ret;
	} else {
		std::cout << "Error while calling method" << '\n';
		PyErr_Print();
	}

	return "Error";
}

std::vector<Robot::Position> Robot::getComponentPositions(
		std::string componentName) {
	PyObject *pValue = callMethod("getComponentPositions", componentName);
	/** pValue = {folded:(0.0, 1.1, ...)), wave:(in, out), joint_names:('elbo', 'wrist'), ...} **/

	std::vector<Robot::Position> ret = std::vector<Robot::Position>();
	if (pValue != NULL) {
		if (!PyDict_Check(pValue)) {
			//Error!
		} else {
			PyObject *key, *value;
			Py_ssize_t pos = 0;

			while (PyDict_Next(pValue, &pos, &key, &value)) {
				Robot::Position p;
				p.name = PyString_AsString(key);
				p.positions = parseDoubleArray(value);
				ret.push_back(p);
			}
		}

		Py_DECREF(pValue);
	}

	return ret;
}

std::vector<double> Robot::parseDoubleArray(PyObject* array) {
	std::vector<double> ret = std::vector<double>();
	if (PySequence_Check(array)) {
		for (int i = 0; i < PySequence_Size(array); i++) {
			ret.push_back(PyFloat_AsDouble(PySequence_GetItem(array, i)));
		}
	}

	return ret;
}

std::vector<std::string> Robot::parseStringArray(PyObject* array) {
	std::vector<std::string> ret = std::vector<std::string>();
	if (PySequence_Check(array)) {
		for (int i = 0; i < PySequence_Size(array); i++) {
			ret.push_back(PyString_AsString(PySequence_GetItem(array, i)));
		}
	}

	return ret;
}

std::vector<std::string> Robot::getComponents() {
	PyObject *pValue = callMethod("getComponents");
	/** pValue = ('arm', 'head', ...) **/

	if (pValue != NULL) {
		std::vector<std::string> ret = parseStringArray(pValue);
		Py_DECREF(pValue);
		return ret;
	}

	return std::vector<std::string>();
}

Robot::State Robot::getComponentState(std::string componentName) {
	PyObject *pValue = callMethod("getComponentState", componentName);
	/** pValue = ('home', {name:'arm', joints:('elbo', 'wrist', ...), positions:(0.0, 1.1, ...), goals:(0.0, 1.1, ...)}) **/

	Robot::State s;
	if (pValue != NULL) {
		if (!PySequence_Check(pValue)) {
			//Error!
		} else {
			s.name = PyString_AsString(PySequence_GetItem(pValue, 0));
			PyObject* values = PySequence_GetItem(pValue, 1);
			if (PyDict_Check(values)) {
				PyObject* key = PyString_FromString("goals");
				s.goals = parseDoubleArray(PyDict_GetItem(values, key));
				Py_DecRef(key);
				key = PyString_FromString("positions");
				s.positions = parseDoubleArray(PyDict_GetItem(values, key));
				Py_DecRef(key);
				key = PyString_FromString("joints");
				s.joints = parseStringArray(PyDict_GetItem(values, key));
				Py_DecRef(key);
			}
		}

		Py_DecRef(pValue);
	}

	return s;
}
