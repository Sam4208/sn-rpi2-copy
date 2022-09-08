#include "shell.h"
#include <cstring>
#include <cstdlib>
#define couleur(param) printf("\033[%sm",param)

using namespace std;



/*.............................................................................
Function : get
Allow to get different values of the LI pulser box
If the pulser box pulses continuously :
return : 0 = ok | 1 = error
...............................................................................*/
int shellPlugin::get(std::string value, int commandStringAck, std::vector<boost::any> *tabValue) {
//#ifdef DEBUG
        printf("sonde jl ici shellPlugin::get()\n");
//#endif
        int ret = 0;
        char buf[1024];
        printf("\n(Plugin) : shellPlugin::get(): %s\n",value.c_str());
        if(!value.empty()) {
        	FILE *pp=NULL;
        	pp=popen(value.c_str(), "r");
        	if (pp == NULL)
        	{
        	        perror("popen");
        	        ret=-1;
		}
        	while (fgets(buf, sizeof(buf), pp));
        	pclose(pp);
        	if (int *pi = boost::any_cast <int> (&(*tabValue)[0])) {
				*pi=atoi(buf);
		}else if (short *pi = boost::any_cast <short> (&(*tabValue)[0])){
				*pi=atoi(buf);
		}else if (long *pi = boost::any_cast <long> (&(*tabValue)[0])){
				*pi=atol(buf);
		}else if (double *pi = boost::any_cast <double> (&(*tabValue)[0])){
				*pi=atof(buf);
		}else if (float *pi = boost::any_cast <float> (&(*tabValue)[0])){
	                        *pi =  atof(buf);
		}else if (bool *pi = boost::any_cast <bool> (&(*tabValue)[0])){
	                        *pi =  atoi(buf);
		}else if(string *pstr = boost::any_cast<string>(&(*tabValue)[0])){
	                        *pstr = buf;
		}
	}
printf("sonde jl ret=%d\n",ret);
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



int shellPlugin::set(std::string value,int commandStringAck, std::vector<boost::any> tabValue) {
        int ret = 0;
        char buf[1024];
        FILE *pp;
        std::string valueFinal;
 		if (int *pi = boost::any_cast <int> (&tabValue[0]))
                         sprintf(buf,"%s %d",value.c_str(),*pi);
                else if (short *pi = boost::any_cast <short> (&tabValue[0]))
                         sprintf(buf,"%s %d",value.c_str(),*pi);
                else if (long *pi = boost::any_cast <long> (&tabValue[0]))
                         sprintf(buf,"%s %ld",value.c_str(),*pi);
                else if (double *pi = boost::any_cast <double> (&tabValue[0]))
                         sprintf(buf,"%s %f",value.c_str(),*pi);
                else if (float *pi = boost::any_cast <float> (&tabValue[0]))
                         sprintf(buf,"%s %f",value.c_str(),*pi);
                else if (bool *pi = boost::any_cast <bool> (&tabValue[0]))
                         sprintf(buf,"%s %d",value.c_str(),*pi);
                else if(string *pstr = boost::any_cast<string>(&tabValue[0]))
                         sprintf(buf,"%s %s",value.c_str(),*pi);
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

