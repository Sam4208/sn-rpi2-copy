#ifndef SHELL_H_
#define SHELL_H_

#include <iostream>
#include "map"
#include "vector"

#include "cta_slc_pluginsInterface.h"

class shellPlugin: public PluginsInterface {
public:
	shellPlugin() {};
	int close();
 	int init(std::string chaine);

	int cmd(std::string chaine, int commandStringAck, std::string *result);
	int set(std::string value, int commandStringAck, std::vector<Byte> res) {
		return setAny(value, commandStringAck,res,"int8");
        };
	int set(std::string value, int commandStringAck, std::vector<short int> res) {
		return setAny(value, commandStringAck,res,"int16");
        };
	int set(std::string value, int commandStringAck, std::vector<int> res) {
		return setAny(value, commandStringAck,res,"int32");
        };
	int set(std::string value, int commandStringAck, std::vector<long> res) {
		return setAny(value, commandStringAck,res,"int64");
        };
	int set(std::string value, int commandStringAck, std::vector<float> res) {
		return setAny(value, commandStringAck,res,"float");
        };
	int set(std::string value, int commandStringAck, std::vector<bool> res) {
		return setAny(value, commandStringAck,res,"bool");
        };
	int set(std::string value, int commandStringAck, std::vector<double> res) {
		return setAny(value, commandStringAck,res,"double");
        };
	int set(std::string chaine, int commandStringAck) {
		int ret = -1;
		std::string res;
        	return cmd(chaine,commandStringAck,&res);
	};

	int get(std::string value, int commandStringAck, std::vector<Byte> *res) {
		return getAny(value, commandStringAck,res,"int8");
        };
	int get(std::string value, int commandStringAck, std::vector<short int> *res) {
		return getAny(value, commandStringAck,res,"int16");
        };
	int get(std::string value, int commandStringAck, std::vector<int> *res) {
		return getAny(value, commandStringAck,res,"int32");
        };
	int get(std::string value, int commandStringAck, std::vector<long> *res) {
		return getAny(value, commandStringAck,res,"int64");
        };
	int get(std::string value, int commandStringAck, std::vector<float> *res){
		return getAny(value, commandStringAck,res,"float");
        };
	int get(std::string value, int commandStringAck, std::vector<double>*res){
		return getAny(value, commandStringAck,res,"double");
        };
 	int get(std::string value, int commandStringAck, std::vector<bool>*res){
		return getAny(value, commandStringAck,res,"bool");
        };
	int get(std::string chaine, int commandStringAck, std::string *result) {
		int ret = -1;
        	return ret;
	}

private:
        template<class T>
        int setAny(std::string value, int commandStringAck,std::vector<T> res,std::string type) ;
        template<class T>
        int getAny(std::string value, int commandStringAck, std::vector<T> *res,std::string type);
        int parse(std::string chaine);
};

typedef shellPlugin *(*maker_protocole1)();
#endif //  shellPlugin_H_
