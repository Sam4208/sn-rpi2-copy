#ifndef PluginsBase_H_
#define PluginsBase_H_

#include <iostream>
#include "map"
#include "vector"
#include "dynamicLoader.h"
#include "cta_slc_pluginsInterface.h"

#define API_LIB_PATH "/MOS/lib/libDataAccessClientOPCUA.so";

class PluginsBase: public PluginsInterface {
public:
	PluginsBase();
	~PluginsBase();
        int init(std::string chaine);
        int afterStart();

        DataAccessClientOPCUA* getDataAccessClientOPCUARef() ;
        std::vector<std::string>* getListControlRef();
        std::vector<std::string>* getListMonitoringRef();

	private :
                std::vector<std::string>    m_listControl;
                std::vector<std::string>    m_listMonitoring;
                std::vector<std::string> split_string(const std::string& str,const std::string& delimiter);
                DynamicLoader *m_pluginsLoader;
                DataAccessClientOPCUA* m_dataAccessClientOPCUA;
                std::string my_serverInfo;
                std::string m_deviceRootName;

};
#endif //  PluginsBase_H_
