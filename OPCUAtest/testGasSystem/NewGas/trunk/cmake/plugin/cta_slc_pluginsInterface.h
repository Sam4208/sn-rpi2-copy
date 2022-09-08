/**
 *******************************************************************************
 *
 * @file    cta_slc_pluginsInterface.h
 * @authors panazol@lapp.in2p3.fr
 * @date    25/04/2016
 * @version v3.0.0
 * @brief description :

 *
 *------------------------------------------------------------------------------
 *
 * @copyright Copyright © 2014, LAPP/CNRS
 *
 *******************************************************************************
 */

#ifndef CTA_SLC_PLUGINSINTERFACE_H
#define CTA_SLC_PLUGINSINTERFACE_H 
#include <stdio.h>
#include <boost/any.hpp>


typedef unsigned char Byte;

namespace CTA_Hardware {
class HardWareInterface;
}
;
typedef int Info;


/**
 * class PluginsInterface
 *
 * @authors panazol@lapp.in2p3.fr
 * @date creation :   25/04/2014
 * @date modification with description:
 *   15/03/16 : add 2 virtual methods
 *  afterStart() : call automaticaly by the "MOS" progam  when the "MOS" program is launched and the server is "ready"
 *  cmdAsynch()  : add in order to to use the asynchrone datapoint access in the server with the dataAcessClientOPCUA 
 *
 * @brief description of this function :
 *    Interface for the plugin library
 *    All functions are pure virtual
 *    All "plugins project" have to implement all this functions.
 */
class PluginsInterface{
protected:
public:
	PluginsInterface() {};
	virtual int init(std::string chaine)=0;
	virtual int afterStart()=0;
	virtual int close()=0;

	virtual int cmd(std::string chaine, int commandStringAck, std::string *result)=0;
	virtual int cmdAsynch(std::string command, int commandStringAck, std::string datapointName, int nameSpace, std::string *result)=0;

	virtual int get(std::string chaine,int commandStringAck, std::vector<boost::any> *tabValue)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<boost::any> tabValue)=0;

   	//void Change(int valeur);

};
#endif //CTA_SLC_PLUGINSINTERFACE_H
