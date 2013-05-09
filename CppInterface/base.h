#ifndef PYTHON_INTERFACE
#define PYTHON_INTERFACE
#include "Python.h"
#include <string>
#include <vector>
#include <iostream>

class PythonInterface {
public:
	PythonInterface(std::string modulePath);
	virtual ~PythonInterface();
protected:
	virtual std::string getModuleName() = 0;
	virtual std::string getClassName() = 0;
	virtual PyObject* getConstructorArgs();
	PyObject* callMethod(std::string methodName);
	PyObject* callMethod(std::string methodName, std::string value);
	PyObject* getClassInstance();
	template<typename T>
	PyObject* callMethod(std::string methodName, std::string argFormat, T arg);

private:
	std::string modulePath;
	PyObject* pInstance;
};

template<typename T>
PyObject* PythonInterface::callMethod(std::string methodName,
		std::string argFormat, T arg) {
	char* m = strdup(methodName.c_str());

	PyObject *pValue;
	if (!argFormat.empty()) {
		char* f = strdup(argFormat.c_str());
		pValue = PyObject_CallMethod(getClassInstance(), m, f, arg);
	} else {
		m = strdup("getComponents");
		pValue = PyObject_CallMethod(getClassInstance(), m, NULL);
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
