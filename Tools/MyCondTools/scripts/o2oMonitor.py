#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
import commands
from stat import *
from ConfigParser import ConfigParser

from ROOT import *

import datetime
import dateutil.parser

import shutil


import Tools.MyCondTools.monitorStatus as monitorStatus
import Tools.MyCondTools.tier0WMADasInterface as tier0DasInterface
import Tools.MyCondTools.gtTools as gtTools
import Tools.MyCondTools.dbTools as dbTools
import Tools.MyCondTools.o2oMonitoringTools as o2oMonitoringTools
import Tools.MyCondTools.RunRegistryTools as RunRegistryTools
import Tools.MyCondTools.popcon_monitoring_last_updates as popConLog
import Tools.MyCondTools.color_tools as colorPrintTools
import Tools.MyCondTools.RunInfo as RunInfo
import Tools.MyCondTools.tableWriter as tableWriter
import ConfigParser as ConfigParser
#from ConfigParser import ConfigParser





# read a global configuration file
cfgfile = ConfigParser.ConfigParser()
cfgfile.optionxform = str

CONFIGFILE = "GT_branches/pclMonitoring.cfg"
print 'Reading configuration file from ',CONFIGFILE
cfgfile.read([ CONFIGFILE ])

passwdfile                  = cfgfile.get('Common','passwdfile')
tier0DasSrc                 = cfgfile.get('Common','tier0DasSrc')
referenceDataset            = cfgfile.get('Common','referenceDataset')
gtconnstring                = cfgfile.get('Common','gtconnstring')
runinfoTag                  = cfgfile.get('Common','runinfoTag')

taskName                    = cfgfile.get('O2OMonitor','taskName')
monitoredrecords            = cfgfile.get('O2OMonitor','monitoredrecords')
weburl                      = cfgfile.get('O2OMonitor','weburl')
webArea                     = cfgfile.get('O2OMonitor','webArea')
cacheFileName               = cfgfile.get('O2OMonitor','cacheFileName')
rrDatasetName               = cfgfile.get('O2OMonitor','rrDatasetName')
rrRunClassName              = cfgfile.get('O2OMonitor','rrRunClassName')
o2oLogfileList              = cfgfile.get('O2OMonitor','o2oLogfileList')
thresholdLastWrite          = cfgfile.get('O2OMonitor','thresholdLastWrite')
thresholdLastSince          = cfgfile.get('O2OMonitor','thresholdLastSince')
firstMonitoredRun           = int(cfgfile.get('O2OMonitor','firstMonitoredRun'))

def runBackEnd():

    # this will store the exit status for the json report
    retValues = 0, "OK"
    # flag in case we miss the info for some runs 
    unknownRun = False
    unknownRunMsg = ""

    gtName = ''
    tier0Das = tier0DasInterface.Tier0DasInterface(tier0DasSrc) 
    try:
        nextPromptRecoRun = tier0Das.firstConditionSafeRun()
        print "Tier0 DAS next run for prompt reco:",nextPromptRecoRun
        gtName = tier0Das.promptGlobalTag(referenceDataset)
        print "      GT for dataset: ", referenceDataset, "run:", str(nextPromptRecoRun), ":", gtName
    except Exception as error:
        print '*** Error: Tier0-DAS query has failed'
        print error
        return 102, "Error: Tier0-DAS query has failed: " + str(error)

    
    
    

    # create the collection of tags
    tagCollection = gtTools.getGTCollection(gtName)

    tagsTomonitor = []

    print "Tags to be monitored: "
    for record in monitoredrecords.split(','):
        label = ''
        if ':' in record:
            label = record.split(':')[1]
            record = record.split(':')[0]
        rcdId =  gtTools.RcdID([record, label])
        if not tagCollection.hasRcdID(rcdId):
            print "Error: rcd: " + str(rcdId) + " not found in GT: " + gtName
        else:
            print '   ', tagCollection.getByRcdID(rcdId)
            tagsTomonitor.append(tagCollection.getByRcdID(rcdId))


    # --------------------------------------------------------------------------------
    # --- read the cache
    allCachedRuns = o2oMonitoringTools.readCache(cacheFileName)
    cachedRuns = allCachedRuns[0]
    runReports = allCachedRuns[1]

    unknownRun = False # this is set to true only if one run can not be processed
    unknownRunMsg = ''
    # --------------------------------------------------------------------------------
    # --- get the last cached run
    if len(cachedRuns) != 0:
        cachedRuns.sort()
    else:
        cachedRuns.append(firstMonitoredRun)

    lastCachedRun = cachedRuns[len(cachedRuns)-1]
    #lastCachedRun = 191419
    print "last cached run #: " + str(lastCachedRun)

    # --------------------------------------------------------------------------------
    # --- get the list of collision runs from RR (only for the runs not yet cached)
    runList = []
    try:
        # FIXME: do we need to restrict to Collision12?
        #runList = RunRegistryTools.getRunListRR3(lastCachedRun+1,"Online", "Commissioning12")
        runList = RunRegistryTools.getRunListRR3(lastCachedRun+1, rrDatasetName, rrRunClassName)

    except Exception as error:
        print '*** Error 1: RR query has failed'
        print error
        return 101, "Error: failed to get collision runs from RunRegistry: " + str(error)

    print runList


    # --------------------------------------------------------------------------------
    # --- check O2O and DB tag status for each record
    threshold = datetime.timedelta(hours=int(thresholdLastWrite))
    thresholdSince = datetime.timedelta(hours=int(thresholdLastSince))

    today = datetime.datetime.today()
    fromUTCToLocal = datetime.timedelta(hours=2)
    recordandlastsince = {}

    tableTitle = ["# run", "start-time", "end-time"]

    rcdJson = o2oMonitoringTools.O2ORecordJson("o2oMonitor")

    for entry in tagsTomonitor:
        print "- Tag:", entry
        
        tagName = entry.tag_name

        recordName = entry.record
        accountName = 'CMS_CONDITIONS'
        tableTitle.append(recordName)

        # create the report for this given record
        rcdRep = o2oMonitoringTools.RecordReport(recordName)
        rcdRep.setTagName(tagName)

        
        nDays = 1
        nSec = nDays*24*60*60
        popLog = popConLog.PopCon_Monitoring_last_updates(interval=nSec)

        # 0. get the last time the O2O run
        o2oLogfiles = {}

        for rcdEntry in o2oLogfileList.split(','):
            key = rcdEntry.split(':')[0]
            logFileForKey = rcdEntry.split(':')[1]
            o2oLogfiles[key] = logFileForKey
        jobData = popLog.PopConJobRunTime(authfile=passwdfile + "/authentication.xml",
                                          logFile=o2oLogfiles[recordName])

        if len(jobData) != 0:
            lastO2ORun = jobData[0][0] + fromUTCToLocal
            previouO2ORun = jobData[0][1] + fromUTCToLocal
            runO2OAge = today - lastO2ORun

            statusForRpt = "OK"

            print "  - Last O2O run on: " + str(lastO2ORun) + " (" + str(runO2OAge) + " ago)"
            if  runO2OAge > 2*(lastO2ORun - previouO2ORun):
                print "      " + colorPrintTools.error("Error") + ": the O2O for rcd " + recordName + " is not running since a while (" + str(runO2OAge) + ")"
                statusForRpt = "ERROR"
                if 2050 > retValues[0]:
                    retValues = 2050, "Error: the O2O for rcd " + recordName + " is not running since a while (" + str(runO2OAge) + ")"

            rcdRep.setLastO2ORun(lastO2ORun, runO2OAge, statusForRpt)
        else:
            print "Error: No O2O job logs for tag: " + tagName + " could be found in the PopConLogs"
            if 2051 > retValues[0]:
                retValues = 2051, "Error: no O2O job logs found for rcd: " + recordName



        # 1. get the last updates from PopConLogger
        # FIXME: the auth.xml can it be read from a central place?
        logData = popLog.PopConRecentActivityRecorded(authfile=passwdfile + "/authentication.xml",
                                                      account='CMS_CONDITIONS',
                                                      iovtag=tagName)

        

        if len(logData['data']) != 0:
            datestring = logData['data'][0][1]
            status = logData['data'][0][6]
            token =  logData['data'][0][8]
            #datelastupdate = datetime.datetime.strptime(datestring,"%B, %dnd %Y  %H:%M:%S") + fromUTCToLocal
            datelastupdate = dateutil.parser.parse(datestring) + fromUTCToLocal

            updateage = today - datelastupdate
            statusForRpt = "OK"
            print "  - Last O2O wrote on: " + str(datelastupdate) + " (" +  str(updateage) + " ago)"
            print "    status:",status, "payload token:", token.split("<br>")[4]
            if updateage > threshold:
                print "      " + colorPrintTools.warning("Warning") + ": O2O is not writing since a while!"
                statusForRpt = "OLD"
                if 2001 > retValues[0]:
                    retValues = 2001, "Warning: the O2O for rcd: " + recordName + " is not writing since a while!"
            if status != 'OK':
                print "      Warning: O2O status is: " + status + "!"
                statusForRpt = "ERROR"
                if 2002 > retValues[0]:
                    retValues = 2002, "Error: the O2O status for rcd: " + recordName + " is " + status + "!"
                
            rcdRep.setLastO2OWrite(datelastupdate, updateage, statusForRpt)
        else:
            print "Error: No O2O updates to tag: " + tagName + " in account: " + accountName + " could be found in the PopConLogs"
            if 2010 > retValues[0]:
                retValues = 2010, "Error: no O2O updates logged for rcd: " + recordName

            #rcdRep.setLastO2OWrite(datelastupdate, updateage, "ERROR")

        


            
        # 2. check the status of the tag
        #FIXME: handle the connection string correctly
        iovtable = dbTools.getIOVTag_CondDBV2('pro', tagName, passwdfile)
        datesince = iovtable.lastIOV.since
        sinceage = today - datesince
        print "  - Last IOV since:", datesince, "(" + str(sinceage),"ago)"
        print "    with token: [" + iovtable.lastIOV.payloadHash +"]"#.split("][")[4]
        recordandlastsince[recordName] = datesince
        #print iovtable.lastIOV()
        stat = "OK"
        if sinceage > thresholdSince:
            stat = "OLD"
            if 2101 > retValues[0]:
                retValues = 2101, "Error: the last IOV of rcd: " + recordName + " is OLD (since: " + str(datesince) + ")!"
        rcdRep.setLastSince(datesince, sinceage, stat)


        rcdJson.addRcd(gtTools.RcdID([recordName,""]), rcdRep)


    # --------------------------------------------------------------------------------
    # --- Write the Rcd status to cache
    rcdJson.writeJsonFile(webArea)
    

    # --------------------------------------------------------------------------------
    # --- check the status for each of the Collision runs
    for run in runList:
        if run == 167551:continue
        print "-- run #: " + colorPrintTools.blue(str(run))            
        #print run
        # get the information from runInfo
        runInfo = None
        try: 
            runInfo = RunInfo.getRunInfoStartAndStopTime(runinfoTag, "", run)
        except Exception as error:
            print '*** Error XXX: RunInfo query failed!'
            print error
            unknownRun = True
            unknownRunMsg = "Error: can not get report for run: " + str(run) + ", since run-info query failed: " + str(error)
            print unknownRunMsg
            continue
            
        rRep = o2oMonitoringTools.RunReportTagCheck()
        rRep.setRunNumber(runInfo.run())
        #rRep.setStartTime(runInfo.startTime())
        rRep.setRunInfoContent(runInfo)
        deltaTRun = runInfo.stopTime() - runInfo.startTime()
        deltaTRunH = deltaTRun.seconds/(60.*60.)


        print "   start: " + str(runInfo.startTime()) + " stop: " + str(runInfo.stopTime()) + " lenght (h): " + str(deltaTRunH)
        #pageWriter.setNextPromptReco(runInfo.run(), runInfo.startTime(), runInfo.stopTime(), deltaTRunH)
        for entry in tagsTomonitor:
            recordName = entry.record()
            datesince = recordandlastsince[recordName]
            if runInfo.stopTime() <= datesince:
                print "   rcd: ", recordName,":",colorPrintTools.ok("OK")
                rRep.addRecordAndStatus(recordName, 0)
            elif runInfo.startTime()  < datesince and runInfo.stopTime() > datesince:
                print "   rcd: ", recordName,":",colorPrintTools.warning("partially covered!")
                rRep.addRecordAndStatus(recordName, 0.5)
            else:
                print "   rcd: ", recordName,":",colorPrintTools.error("not covered!")
                rRep.addRecordAndStatus(recordName, 1)

        runReports.append(rRep)
        # print "---------------------------------------------------------"
        #print gtEntry,
        #print "  # of updates:", len(logData['data'])
        #if gtEntry.updateType() != 1:
        #    listofchanges.append(str(gtEntry) +  "  # of updates: " + str(len(logData['data'])))
        #else:
        #    listofchangesO2O.append(str(gtEntry) +  "  # of updates: " + str(len(logData['data'])))



    # --------------------------------------------------------------------------------
    # --- write to cache and to log
    runReports.sort(key=lambda rr: rr._runnumber)

    tableForCache =[]
    tableForCache.append(tableTitle)
    tableForLog =[]
    tableForLog.append(tableTitle)

    for rep in runReports:
        if int(rep.runNumber()) < int(nextPromptRecoRun):
            tableForCache.append(rep.getList())            
        tableForLog.append(rep.getList()) 


    #out = sys.stdout
    print "writing cache file: " + cacheFileName
    cacheFile = file(cacheFileName,"w")
    tableWriter.pprint_table(cacheFile, tableForCache)
    cacheFile.close()

    out = sys.stdout
    logFile = file(webArea + "log.txt","w")
    tableWriter.pprint_table(logFile, tableForLog)
    logFile.close()


    status = retValues[0]
    message = retValues[1]
    if status == 0 and unknownRun:
        status = 10
        message = unknownRunMsg
    return status, message
    








if __name__     ==  "__main__":

    # start here
    status = monitorStatus.MonitorStatus(taskName)
    status.setWebUrl(weburl)
    statAndMsg = None
    #try:
    statAndMsg = runBackEnd()
    
    status.setStatus(statAndMsg[0],statAndMsg[1])
    #print datetime.datetime.today()
    status.setUpdateTime(datetime.datetime.today())
    status.writeJsonFile(webArea + "status.json")


    sys.exit(0)
