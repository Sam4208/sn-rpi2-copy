#ifndef SHELL_H_
#define SHELL_H_

#include <iostream>
#include "map"
#include "vector"

//#include "cta_slc_pluginsInterface.h"
class PluginsBase;

//class shellPlugin: public PluginsInterface {
class shellPlugin: public PluginsBase {
public:
	shellPlugin() {m_cpt=0;};
	int close();
 	int init(std::string chaine);

	int cmd(std::string chaine, int commandStringAck, std::string *result);
	// new virtual methods appears with the version 3.0 of MOS
	int afterStart() {
		int ret=0;	
		// Mandatory allways need
		ret = PluginsBase::afterStart();
		return ret; 
	};
	int cmdAsynch(std::string command, int commandStringAck, std::string datapointName, int nameSpace, std::string *result) {return 0;};

	// new virtual methods who replace the setAnay getAny methods  with the version 4.0 of MOS
	int get(std::string chaine,int commandStringAck, std::vector<boost::any> *tabValue);
	int set(std::string chaine,int commandStringAck, std::vector<boost::any> tabValue);
private:
        int parse(std::string chaine);
	int m_cpt;
};

typedef shellPlugin *(*maker_protocole1)();
#endif //  shellPlugin_H_
