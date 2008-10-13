// Author: David Lawrence  August 8, 2007
//
//

#include <JANA/JEventProcessor.h>
#include <JANA/JEventLoop.h>
using namespace jana;

#include <map>
using std::map;

class JEventProcessorJANARATE:public JEventProcessor
{
	public:
		jerror_t init(void);							///< Called once at program start.
		jerror_t brun(JEventLoop *loop, int runnumber);	///< Called everytime a new run number is detected.
		jerror_t evnt(JEventLoop *loop, int eventnumber);	///< Called every event.
		jerror_t erun(void);	///< Called everytime run number changes, provided brun has been called.
		jerror_t fini(void);							///< Called after last event of last event source has been processed.		

		pthread_mutex_t mutex;
		bool initialized;
		bool finalized;
		
		struct itimerval start_tmr;
		struct itimerval end_tmr;
		struct itimerval last_tmr;
		
		unsigned int Ncalls;
		unsigned int last_Ncalls;
		unsigned int PERIOD_EVENTS;
		
		typedef struct{
			double rate;
			double delta_sec;
			double last_sec;
			unsigned int Ncalls;
		}rate_t;
		
		rate_t rate;
		
		TTree *rate_tree;
};
