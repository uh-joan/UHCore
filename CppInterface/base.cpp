#include "history.h"
#include "Python.h"
#include <string>
#include <iostream>
#include <exception>
#include <stdio.h>
#include <stdarg.h>

PythonInterface::PythonInterface(std::string modulePath) {
	PythonInterface::modulePath = modulePath;
	PythonInterface::pInstance = NULL;
	if (!Py_IsInitialized()) {
		Py_Initialize();
		std::cout << "Python Initialized" << std::endl;
	}
}

PythonInterface::~PythonInterface() {
	if (pInstance != NULL) {
		Py_DECREF(pInstance);
	}

	Py_Finalize();
}

PyObject* PythonInterface::getConstructorArgs() {
	return NULL;
}

PyObject* PythonInterface::getClassInstance() {
	if (PythonInterface::pInstance == NULL) {
		if (!modulePath.empty()) {

			PyRun_SimpleString("import sys");
			PyRun_SimpleString(
					("sys.path.append(\"" + std::string(modulePath) + "\")").c_str());
		}

		std::string modName = getModuleName();
		PyObject *pName = PyString_FromString(modName.c_str());
		PyObject *pModule = PyImport_Import(pName);
		Py_DECREF(pName);

		char* fileName = PyModule_GetFilename(pModule);
		char* argv[1] = { fileName };
		PySys_SetArgvEx(1, argv, 0);

		PyObject *pDict = PyModule_GetDict(pModule);
		Py_DECREF(pModule);

		PyObject *pClass = PyDict_GetItemString(pDict, getClassName().c_str());
		Py_DECREF(pDict);

		PyObject *pClassArgs = getConstructorArgs();
		if(pClassArgs != NULL && !PyTuple_Check(pClassArgs))
		{
			PyObject *temp = pClassArgs;
			pClassArgs = PyTuple_Pack(1, temp);
			Py_DECREF(temp);
		}

		PythonInterface::pInstance = PyObject_CallObject(pClass, pClassArgs);
		Py_DECREF(pClass);
		Py_XDECREF(pClassArgs);

		std::cout << modName << " Initialized" << std::endl;
	}

	return PythonInterface::pInstance;
}

PyObject* PythonInterface::callMethod(std::string methodName) {
	return callMethod(methodName, "", 0);
}

PyObject* PythonInterface::callMethod(std::string methodName, std::string value) {
	return callMethod(methodName, "(s)", strdup(value.c_str()));
}
