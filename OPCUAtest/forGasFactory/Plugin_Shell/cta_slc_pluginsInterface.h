/**
 *******************************************************************************
 *
 * @file    cta_slc_pluginsInterface.h
 * @authors panazol@lapp.in2p3.fr
 * @date    25/04/2014
 * @version v1.0.2
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
typedef unsigned char Byte;

namespace CTA_Hardware {
class HardWareInterface;
}
;

/**
 * class PluginsInterface
 *
 * @authors panazol@lapp.in2p3.fr
 * @date creation :   25/04/2014
 * @date modification with description:
 *
 * @brief description of this function :
 *    Interface for the plugin library
 *    All functions are pure virtual
 *    All "plugins project" have to implement all this functions.
 */
class PluginsInterface {
protected:
public:
	PluginsInterface() {
	}
	;
	virtual int init(std::string chaine)=0;
	virtual int close()=0;

	virtual int cmd(std::string chaine, int commandStringAck, std::string *result)=0;

	virtual int set(std::string chaine,int commandStringAck)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<Byte> tabValue)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<short int> res)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<int> res)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<long> res)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<float> res)=0;
	// rajout 20/09/14
	virtual int set(std::string chaine,int commandStringAck, std::vector<bool> res)=0;
	virtual int set(std::string chaine,int commandStringAck, std::vector<double> res)=0;

	virtual int get(std::string chaine,int commandStringAck, std::string *result)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<Byte> *tabValue)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<short int> *res)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<int> *res)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<long> *res)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<float> *res)=0;
	// rajout 20/09/14
	virtual int get(std::string chaine,int commandStringAck, std::vector<double> *res)=0;
	virtual int get(std::string chaine,int commandStringAck, std::vector<bool> *res)=0;

};
#endif //CTA_SLC_PLUGINSINTERFACE_H
