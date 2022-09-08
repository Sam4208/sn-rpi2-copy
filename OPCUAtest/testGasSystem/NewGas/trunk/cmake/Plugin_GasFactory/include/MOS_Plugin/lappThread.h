#ifndef LAPPTHREAD_H_
#define LAPPTHREAD_H_

#include <iostream>

class LAPPThread
{
public:
    virtual void *run(void *params)=0;
    void start(void * params)
    {
        this->params = params;
        pthread_create(&threadId, 0, &LAPPThread::static_run, this);
    }

    static void* static_run(void * void_this)
    {
         LAPPThread *thread_this = static_cast<LAPPThread*>(void_this);
         return thread_this->run(thread_this->params);
    }
    void wait(){
	pthread_join (threadId, NULL);
	}
private:
    pthread_t threadId;
    //LAPPThread * thread_this;
    void *params;
};



#endif //  LAPPTHREAD_H_

