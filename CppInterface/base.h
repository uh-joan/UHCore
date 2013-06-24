#ifndef PYTHON_INTERFACE
#define PYTHON_INTERFACE
#include "Python.h"
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
	PyObject* callMethod(PyObject* pInstance, std::string methodName);
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string value);
	PyObject* getClassInstance(std::string moduleName, std::string className, PyObject* constructorArgs);
	PyObject* getClassObject(std::string moduleName, std::string className);
	template<typename T>
	PyObject* callMethod(PyObject* pInstance, std::string methodName, std::string argFormat, T arg);
	PyObject* callMethod(std::string methodName) {
		return callMethod(getDefaultClassInstance(), methodName);
	}
	PyObject* callMethod(std::string methodName, std::string value) {
		return callMethod(getDefaultClassInstance(), methodName, value);
	}
	template<typename T>
	PyObject* callMethod(std::string methodName, std::string argFormat, T arg) {
		return callMethod(getDefaultClassInstance(), methodName, argFormat, arg);
	}
private:
	std::string modulePath;
	std::map<std::string, PyObject*> pObjectCache;
};

template<typename T>
PyObject* PythonInterface::callMethod(PyObject* instance, std::string methodName,
		std::string argFormat, T arg) {
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

#endif //PYTHON_INTERFACE
