#include "shell.h"
#include <cstring>
#include <cstdlib>
#define couleur(param) printf("\033[%sm",param)

using namespace std;


template <class T>
int shellPlugin::getAny(std::string value, int commandStringAck, std::vector<T> *res, std::string type) {
#ifdef DEBUG
        printf("sonde jl ici shellPlugin::get() avec any et type=%s\n",type.c_str());
#endif
        int ret = 0;
        char buf[1024];
        printf("\n(Plugin) : shellPlugin::get(): %s\n",value.c_str());
        FILE *pp;
        pp=popen(value.c_str(), "r");
        if (pp == NULL)
        {
                perror("popen");
                ret=-1;
        }
        while (fgets(buf, sizeof(buf), pp));
        pclose(pp);
        res->resize(1);
        if(type.compare("int8")==0) (*res)[0] = atoi(buf);
        if(type.compare("int16")==0) (*res)[0] = atoi(buf);
        if(type.compare("int32")==0) (*res)[0] = atoi(buf);
        if(type.compare("int64")==0) (*res)[0] = atol(buf);
        if(type.compare("float")==0) (*res)[0] = atof(buf);
        if(type.compare("double")==0) (*res)[0] = atof(buf);
        if(type.compare("bool")==0) (*res)[0] = atoi(buf);
        return ret;
}

int shellPlugin::cmd(std::string chaine, int commandStringAck, std::string *result) {
	int ret = 0;
	char buf[1024];
	couleur("0");
        printf("\n(Plugin) : shellPlugin::cmd(): %s\n",chaine.c_str());
	couleur("0");
	FILE *pp; 
	pp=popen(chaine.c_str(), "r");
	if (pp == NULL) 
	{ 
		perror("popen"); 
      		ret=-1;
	} 
	while (fgets(buf, sizeof(buf), pp));
	pclose(pp);

        *result = buf;
	return ret;
};

template <class T>
int shellPlugin::setAny(std::string value, int commandStringAck,std::vector<T> res,std::string type) {
#ifdef DEBUG
        printf("sonde jl ici shellPlugin::setAny avec value=%s\n",value.c_str());
#endif

        int ret = 0;
        char buf[1024];
        FILE *pp;
	std::string valueFinal;
       	if(type.compare("int8")==0) sprintf(buf,"%s %d",value.c_str(),res.at(0));
        if(type.compare("int16")==0)sprintf(buf,"%s %d",value.c_str(),res.at(0));  
        if(type.compare("int32")==0)sprintf(buf,"%s %d",value.c_str(),res.at(0)); 
        if(type.compare("int64")==0)sprintf(buf,"%s %ld",value.c_str(),res.at(0)); 
        if(type.compare("float")==0)sprintf(buf,"%s %f",value.c_str(),res.at(0)); 
        if(type.compare("double")==0)sprintf(buf,"%s %f",value.c_str(),res.at(0)); 
        if(type.compare("bool")==0)sprintf(buf,"%s %d",value.c_str(),res.at(0)); 
        if(type.compare("string")==0)sprintf(buf,"%s %s",value.c_str(),res.at(0)); 

        printf("\n(Plugin) : shellPlugin::set(): %s\n",buf);

        pp=popen(buf, "r");
        if (pp == NULL)
        {
                perror("popen");
                ret=-1;
        }
        while (fgets(buf, sizeof(buf), pp));
        pclose(pp);
        return ret;
}


int shellPlugin::close() {
	couleur("0");
        printf("\n(Plugin) : shellPlugin::close() : \n");
        couleur("0");
	return 0;
};

int shellPlugin::init(std::string chaine) {
	couleur("0");
        printf("\n(Plugin) : shellPlugin::init() : %s\n",chaine.c_str());
        couleur("0");
	return 0;
};

int shellPlugin::parse(std::string paramString) {

        /***********************/
        /* variables definition */
        /***********************/
        int ret=0;
        paramString += " ";
        //int pos;
        size_t pos;
        std::string valueString;
        std::string nameString;
        std::string subChaine1 = paramString;
        std::string subChaine2 = paramString;

        int flag=1;

        /***************************/
        /* End variable definition */
        /***************************/

        /**
                This part extract all informations from "paramString"
        */
        while (flag) {
                subChaine1 = subChaine2;
                pos = subChaine2.find(' '); // cherche separateur ' '
                if (pos  == std::string::npos) {// il n'y a plus rien : alors on sort
                        flag = 0;
                        pos = strlen(subChaine2.c_str());
                }

                        subChaine1.erase(pos); // isole le binome name:value
                        subChaine2.erase(0, pos + 1); // reste

                        valueString = subChaine1;
                        nameString = subChaine1;
                        pos = valueString.find_first_of(':'); // caratere separateur name:value = ':'
                        if (pos != std::string::npos) {
                                nameString.erase(pos); // isole dans le biname name
                                valueString.erase(0, pos + 1); // isole dans le binome value
                                // maintenant on traite
                        }
        }
        return ret;
}

extern "C" {
shellPlugin *ptr_Plugin() {
	return new shellPlugin();
}
}

