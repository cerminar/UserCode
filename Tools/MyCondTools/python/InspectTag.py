import datetime

import os,sys, DLFCN
sys.setdlopenflags(DLFCN.RTLD_GLOBAL+DLFCN.RTLD_LAZY)


import pluginCondDBPyInterface as condDB
import CondCore.Utilities.iovInspector as iovInspector




"""
Module providing tools to inspect IOV tags in the DB

$Date: 2012/11/06 09:51:29 $
$Revision: 1.8 $

"""




def getSummaries(tagName, dbName, since, till, logName = 'oracle://cms_orcon_adg/CMS_COND_31X_POPCONLOG', passwdFile = '/afs/cern.ch/cms/DB/conddb/ADG'):
    """
    Builds a RunInfoContent for a given run. Input parameters are the RunInfo tag name, connection string and run #
    """


    try:
        fwkInc = condDB.FWIncantation()
        rdbms = condDB.RDBMS(passwdFile)
        rdbms.setLogger(logName)

        db = rdbms.getDB(dbName)


        db.startTransaction()
        log = db.lastLogEntry(tagName)
        iovs = iovInspector.Iov(db,tagName, since,till)
        db.commitTransaction()
    except Exception:
        raise 
    else:
        for iovSummary in iovs.summaries():
            print "----- OID: " + iovSummary[0] + " since: " + str(iovSummary[1]) + " till: " + str(iovSummary[2])
            print "Summary:"
            print iovSummary[3]
        return iovs.summaries()

    return None




if __name__ == "__main__":
    getSummaries(tagName = "SiStripDetVOff_v6_prompt",\
                 dbName = "oracle://cms_orcon_adg/CMS_COND_31X_STRIP",\
                 since = 5813170907986667904,\
                 till = 5813170907986667904)




