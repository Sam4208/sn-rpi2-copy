/**
 *******************************************************************************
 *
 * @file    pluginInterfaceClientOPCUA.h
 * @authors panazol@lapp.in2p3.fr
 * @date    16/02/2016
 * @version v1.0.0
 * @brief description :
 * This header file allow to use the OPCUA client API from UnifiedAutomation with a dynamic loading librairy
 * To use it, you need to include this header file in your implemenation and use the libPluginAPIClientOPCUA.so file.
 * This file is usually installed in /MOS/lib
 *
 *------------------------------------------------------------------------------
 *
 * @copyright Copyright © 2016, LAPP/CNRS
 *
 *******************************************************************************
 */

#ifndef DATAACCESSCLIENTOPCUA_H
#define DATAACCESSCLIENTOPCUA_H 
#include <stdio.h>
#include <vector>
#include <boost/any.hpp>


typedef std::vector<std::string> PARAM;
typedef unsigned char Byte;

/**
 * class DataAccessClientOPCUA
 *
 * @authors panazol@lapp.in2p3.fr
 * @date creation :   16/02/2016
 * @date modification with description:
 *
 * @brief description of this function :
 *    Interface for the plugin library (libPluginAPIClientOPCUA.so)
 *    All functions are pure virtual
 */
class DataAccessClientOPCUA {
public:
	DataAccessClientOPCUA() {};
	virtual int  connect(const std::string& serverUrl)=0;
    	virtual int  disconnect()=0;
    //	virtual int  callMethod(std::string method,int nameSpace, std::vector<PARAM> callRequest,std::string *resultCall)=0;
        virtual int  callMethod(std::string method,int nameSpace, std::vector<boost::any> callRequest,std::string *resultCall)=0;


    	virtual int  getDatapoint(std::string object, int nameSpace,std::string *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,Byte *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,short *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,int *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,long *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,float *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,double *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,bool *resultElement)=0;

    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<Byte> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<short> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<int> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<long> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<float> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<double> *resultElement)=0;
    	virtual int  getDatapoint(std::string object, int nameSpace,std::vector<bool> *resultElement)=0;

    	virtual int  setDatapoint(std::string object, int nameSpace,std::string element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,Byte element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,short element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,int element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,long element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,float element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,double element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,bool element)=0;

    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<std::string> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<Byte> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<short> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<int> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<long> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<float> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<double> element)=0;
    	virtual int  setDatapoint(std::string object, int nameSpace,std::vector<bool> element)=0;

};
#endif //DATAACCESSCLIENTOPCUA_H
