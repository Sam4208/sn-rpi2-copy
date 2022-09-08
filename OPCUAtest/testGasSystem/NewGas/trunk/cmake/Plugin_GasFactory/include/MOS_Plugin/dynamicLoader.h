/**
 *******************************************************************************
 *
 * @file    dynamicLoader.h
 * @authors panazol@lapp.in2p3.fr
 * @date    15/03/2016
 * @version v1.0.0
 * @brief description :

 *
 *------------------------------------------------------------------------------
 *
 * @copyright Copyright © 2014, LAPP/CNRS
 *
 * @section LICENSE
 *
 *******************************************************************************
 */

#ifndef DYNAMICLOADER_H
#define DYNAMICLOADER_H
#include <dlfcn.h>
#include <string>

#include "dataAccessClientOPCUA.h"

/**
 * class DynamicLoader
 *
 * @authors panazol@lapp.in2p3.fr
 * @date creation :   15/03/2016
 * @date modification with description:
 *
 * @brief description of this function :
 *    This class is a launcher
 *    Allow to load the library file in your porject (plugin or other)
 */
class DynamicLoader {
	typedef DataAccessClientOPCUA *(*maker_Plugins)();
public:
	DynamicLoader(std::string myLibFile, std::string className){
	        hndl = NULL;
	        m_myLibFile = myLibFile;
printf("sonde jl DynamicLoader avec %s\n",myLibFile.c_str());
	        m_className = className;
	};

	~DynamicLoader(){
	        if (hndl != NULL)
        	        dlclose(hndl);
	}


	DataAccessClientOPCUA *load() {
        	maker_Plugins pMaker;
        	std::string msg;

        	msg = "open lib or plugin : ";
        	msg += m_myLibFile;

        	hndl = dlopen(m_myLibFile.c_str(), RTLD_LAZY);
        	if (hndl == NULL) {
       		        msg = "dlopen : ";
        	        msg += dlerror();
        	        fprintf(stderr,"msg=%s\n",msg.c_str());
        	        return NULL;
        	}
        	// Chargement de la classe
        	void *mkr = dlsym(hndl, m_className.c_str());
        	if (mkr == NULL) {
        	        msg = "dlsym : ";
        	        msg += dlerror();
        	        fprintf(stderr,"msg=%s\n",msg.c_str());
        	        return NULL;
        	}

        	pMaker = (maker_Plugins) mkr;
        	m_classRef = pMaker();
	
        	return m_classRef;
	}


private:
	void *hndl;
	std::string m_myLibFile;
	std::string m_className;
	DataAccessClientOPCUA *m_classRef;
};

#endif // DYNAMICLOADER
