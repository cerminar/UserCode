#!/usr/bin/env python

from Tools.MyCondTools.gt_tools import *
from Tools.MyCondTools.color_tools import *
#from Tools.MyCondTools.Tier0LastRun import *
#from Tools.MyCondTools.RunValues import *

from Tools.MyCondTools.RunInfo import *


import Tools.MyCondTools.RunRegistryTools as RunRegistryTools
import Tools.MyCondTools.tier0WMADasInterface as tier0DasInterface
import Tools.MyCondTools.pclMonitoringTools as pclMonitoringTools

import Tools.MyCondTools.monitoring_config as config



import shutil









#os.putenv("CORAL_AUTH_PATH","/afs/cern.ch/cms/DB/conddb")






import datetime

# -- status must include:
# 1. errori nell'esecuzione -> exit code !=0 + messaggio di descrizione
# 2. problema PCL -> exit code !=0 + messaggio di descrizione
# 3. data update (controllata dal plugin di nagios)
# NOTE: il plugin di nagios deve anche controllare che l'url sia raggiungibile


def fill1DHisto(histo, xarray, yarray, labels = False):
    lastBin= int(len(xarray))
    counter = 0
    for runnumber in xarray:
#        print "run: " + str(runnumber)
#        print "bin: " + str(lastBin)
        histo.SetBinContent(lastBin, yarray[counter])
        if labels:
            histo.GetXaxis().SetBinLabel(lastBin, str(int(runnumber)))
        lastBin-=1
        counter+=1

    

def runBackEnd():


    # --- get the prompt reco status from Tier0-DAS
    tier0Das = tier0DasInterface.Tier0DasInterface(config.tier0DasSrc) 

    try:
        lastPromptRecoRun = tier0Das.firstConditionSafeRun()
        print "Tier0 DAS last run released for PROMPT:       ", lastPromptRecoRun
        #print "Tier0 DAS first run safe for condition update:", tier0Das.firstConditionSafeRun()
    except Exception as error:
        print '*** Error 2: Tier0-DAS query has failed'
        print error
        return 102, "Error: Tier0-DAS query has failed: " + str(error)

    # --------------------------------------------------------------------------------
    # find the file produced by PCL in the afs area
    fileList = os.listdir(config.promptCalibDir)

    # --------------------------------------------------------------------------------
    # create a dictionary to store cached IOV tables for target tags in ORACLE
    oracleTables = {}

    # --------------------------------------------------------------------------------
    # these will store the global outcome of the script
    tagsJson = pclMonitoringTools.PCLTagsJson('pclMonitor')

    retValues = 0, 'OK'
        

    for pclTag in config.pclTasks:
        print blue("---------------------------------------------------------------------")
        print "--- Check status for PCL workflow: " + blue(pclTag)

        tagReport = pclMonitoringTools.PclTagReport(pclTag)

        
        cacheFileName = 'pclMonitor_' + pclTag + '.cache'
        
        # --------------------------------------------------------------------------------
        # --- read the cache
        allCachedRuns = pclMonitoringTools.readCache(cacheFileName)
        cachedRuns = allCachedRuns[0]
        runReports = allCachedRuns[1]

        unknownRun = False # this is set to true only if one run can not be processed
        unknownRunMsg = ''

        # --------------------------------------------------------------------------------
        # --- get the last cached run
        if len(cachedRuns) != 0:
            cachedRuns.sort()
        else:
            cachedRuns.append(firstRunToMonitor)


        # get the list of runs to be refreshed (< 24h old)
        runsToBeRefreshed = []
        reportsToBeRefreshed = []
        last2days = datetime.timedelta(days=config.refreshDays)
        twdaysago = datetime.datetime.today() - last2days
        for rep in runReports:

            if rep.startTime >= twdaysago:
                runsToBeRefreshed.append(rep.runNumber)
                reportsToBeRefreshed.append(rep)
                #print rep.runNumber()
                #print "start: " + str(rep.startTime()) + " less than " + str(twdaysago)

        #remove the list of reports and runs to be refreshed from the cahced ones
        for rep in reportsToBeRefreshed:
            cachedRuns.remove(rep.runNumber)
            runReports.remove(rep)

        
        lastCachedRun = config.firstRunToMonitor
        if(len(cachedRuns) != 0):
            lastCachedRun = cachedRuns[len(cachedRuns)-1]
        runsToBeRefreshed.sort(reverse=True)
        print "last cached run #: " + str(lastCachedRun)
        print "runs to be refreshed: " + str(runsToBeRefreshed)


    
        # --------------------------------------------------------------------------------
        # --- get the list of collision runs from RR (only for the runs not yet cached)
        runList = []
        try:
            #runList = RunRegistryTools.getRunList(lastCachedRun+1)
            #runList2 = RunRegistryTools.getRunListRR3(lastCachedRun+1, "Express", "Collisions12")
            # FIXME: the run-types can be specialized "by tag"
            runList = RunRegistryTools.getRunListRR3(lastCachedRun+1, config.rrDatasetName, config.rrRunClassName)
            #print runList
            #print runList2
            runList.sort(reverse=True)
        except Exception as error:
            print '*** Error 1: RR query has failed'
            print error
            return 101, "Error: failed to get collision runs from RunRegistry: " + str(error)

        print "run list from RR: " + str(runList)
        if len(runList) < len(runsToBeRefreshed):
            print "Warning: list from RR is fishy...using the previous one!"
            retValues = 1, 'Warning: list from RR is fishy...using the previous one!'
            runList = runsToBeRefreshed



        # --------------------------------------------------------------------------------
        # run on runs not yet cached
        # FIXME: remove?
        lastUploadDate = None
        isLastProcessed = True
        for run in runList:
            statusValues = 0, 'OK'

            # get the run report for all the records run in PCL (dictionary)
            rRep = None 
            try:
                rRep = pclMonitoringTools.getRunReport(pclTag, run, fileList, oracleTables, lastUploadDate)
            except pclMonitoringTools.OngoingRunExcept as error:
                print error
            except Exception as error:
                unknownRun = True
                unknownRunMsg = "Error: can not get report for run: " + str(run) + ", reason: " + str(error)
                print unknownRunMsg
            else:

                runReports.append(rRep)

                # --- Assign the status for this run based on the RunReport
                # NOTE: the 'isLastProcessed' flag is meant not to flag as problematic runs that are just waiting to be processed.
                # as soon as a run is uploaded or Tier0 tries to uplaod it all the following runs should have the flag set to false
                # the same is true if the "age" of the run is > than 12h (time-out on the Tier0 side to launch PCL)
                # here the logic is based on the reverse order of the runs in the list
                if rRep.hasUpload or rRep.stopTimeAge() > 12:
                    isLastProcessed = False

                #print run, isLastProcessed

                # these are assigned before any other since they are only warning and they could in principle be overwritten by error statuses
                if rRep.multipleFiles:
                    statusValues = 998, "PCL run multiple times for run: " + str(rRep.runNumber)
                if rRep.isOutOfOrder:
                    statusValues = 999, "PCL run out of order for run: " + str(rRep.runNumber)


                # assign the status to this run
                if not rRep.pclRun:
                    if not isLastProcessed:
                        statusValues  =  1001, "PCL not run for run: " + str(rRep.runNumber)
                elif not rRep.hasPayload:
                    statusValues  =  1002, "PCL produced no paylaod for run: " + str(rRep.runNumber)
                elif not rRep.hasUpload:
                    if not isLastProcessed:
                        statusValues  =  1003, "PCL did not upload paylaod for run: " + str(rRep.runNumber)
                elif not rRep.uploadSucceeded:
                    statusValues = 1004, "Upload to DB failed for run: " + str(rRep.runNumber)

                # strore the status of the problemati runs only
                if statusValues[0] != 0:
                    tagReport.addRunStatus(rRep.runNumber, statusValues)



                #print statusValues


        runReports.sort(key=lambda rr: rr.runNumber)


        # -----------------------------------------------------------------
        # ---- cache the results for runs older than 48h and write the log for the web
        logFileName = '/log_' + pclTag + '.txt'
        pclMonitoringTools.writeCacheAndLog(cacheFileName, config.webArea + logFileName, runReports)

        # --- add the reports for this tag to the Json
        tagsJson.addTag(pclTag, tagReport)


    # --- write the reports for all the tags to a JSON
    tagsJson.writeJsonFile(config.webArea)
    

    # FIXME: find a logic for many records
    status = retValues[0]
    message = retValues[1]
    if status == 0 and unknownRun:
        status = 10
        message = unknownRunMsg



    return status, message

import Tools.MyCondTools.monitorStatus as monitorStatus


if __name__ == "__main__":

    # start here
    status = monitorStatus.MonitorStatus(config.taskName)
    status.setWebUrl(config.weburl)
    statAndMsg = None
    # FIXME: catch and report errors
    #try:
    statAndMsg = runBackEnd()
    #except:
    #    print "*** Error running back-end call"
    #    statAndMsg = 1000, "unknown error"
    
    status.setStatus(statAndMsg[0],statAndMsg[1])
    #print datetime.datetime.today()
    status.setUpdateTime(datetime.datetime.today())
    status.writeJsonFile(config.webArea + "status.json")

    sys.exit(0)
