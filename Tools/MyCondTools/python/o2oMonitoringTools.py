import datetime
import time
import os
import Tools.MyCondTools.RunInfo as RunInfo
import Tools.MyCondTools.tableWriter as tableWriter
import Tools.MyCondTools.color_tools as colorTools
#import Tools.MyCondTools.gt_tools as gtTools



class RunReportTagCheck:
    def __init__(self):
        self._runnumber = -1
        self._startTime = None
        self._stopTime = None
        self._recordList = []
        self._recordStatus = []
        
        return

    def runNumber(self):
        return self._runnumber


    def startTime(self):
        return self._startTime

    def stopTime(self):
        return self._stopTime

    def setRunNumber(self, number):
        self._runnumber = number

    def setStartTime(self, start):
        self._startTime = start

    def setStopTime(self, stop):
        self._stopTime = stop

    def setRunInfoContent(self, runInfo):
        self._startTime = runInfo.startTime()
        self._stopTime = runInfo.stopTime()
        #self._runInfo = runInfo

    # hours
    def runLenght(self):
        deltaTRun = self.stopTime() - self.startTime()
        return deltaTRun.days*24.0 + deltaTRun.seconds/(60.*60.)

    def __str__(self):
        return "--- run #: " + str(self._runnumber) + " start time: " + str(self.startTime())

    def getList(self):
             theList = [str(self._runnumber), str(self.startTime()), str(self.stopTime())]
             for index in range(0, len(self._recordList)):
                 #theList.append(self._recordList[index])
                 theList.append(self._recordStatus[index])
             return theList

    def addRecordAndStatus(self, record, status):
        if not record in  self._recordList:
            self._recordList.append(record)
            self._recordStatus.append(status)
        else:
            print "Record already registered!"


class RecordReport:
    def __init__(self, recordname):
        self._properties = {}
        self._properties['recordName'] = recordname
        self._properties['tagName'] = None
        self._properties['lastWrite'] = None
        self._properties['lastWriteAge'] = None
        self._properties['lastWriteStatus'] = None
        self._properties['lastRun'] = None
        self._properties['lastRunAge'] = None
        self._properties['lastRunStatus'] = None
        self._properties['lastSince'] = None
        self._properties['lastSinceAge'] = None
        self._properties['lastSinceStatus'] = None



    def getProperty(self, key):
        data = self._properties[key]
        if data:
            if key == 'lastSince' or key == 'lastWrite' or key == 'lastRun':
                return datetime.datetime.fromtimestamp(data)
            elif key == 'lastSinceAge' or key == 'lastWriteAge' or key == 'lastRunAge':
                return datetime.timedelta(days=data[0],seconds=data[1],microseconds=data[2])
        return data

        
    def setLastO2ORun(self, dateandtime, age, status):
        self._properties['lastRun'] = time.mktime(dateandtime.timetuple())
        self._properties['lastRunAge'] = [age.days, age.seconds, age.microseconds]
        self._properties['lastRunStatus'] = status

    def setLastO2OWrite(self, dateandtime, age, status):
        self._properties['lastWrite'] = time.mktime(dateandtime.timetuple())
        self._properties['lastWriteAge'] = [age.days, age.seconds, age.microseconds]
        self._properties['lastWriteStatus'] = status


    def setLastSince(self, dateandtime, age, status):
        self._properties['lastSince'] = time.mktime(dateandtime.timetuple())
        self._properties['lastSinceAge'] = [age.days, age.seconds, age.microseconds]
        #time.mktime(age.timetuple())
        self._properties['lastSinceStatus'] = status


    def setTagName(self, tag):
        self._properties['tagName'] = tag



def readCache(filename):
    # read the cache file and returns the list of the RunReports for all the cached files
    runReports = []
    runNumbers = []
    if os.path.exists(filename):
        print "reading cache file: " + filename
        cache = file(filename,"r")
        data = cache.readlines()
        for line in data:
            if line[0] != '#' and line != "":
                # read the relevant lines
                items = line.split()
                # get the  run #
                runCached = int(items[0])
                runNumbers.append(runCached)
                # create the report
                rRep = RunReportTagCheck()
                rRep.setRunNumber(runCached)
                
                startCached = RunInfo.getDate(items[1] + " " + items[2])
                rRep.setStartTime(startCached)

                stopCached = RunInfo.getDate(items[3] + " " + items[4])
                rRep.setStopTime(stopCached)
                
                remaining = len(items) - 5
                last = 4
                #print runCached
                while remaining >= 1:
                    record = data[0].split()[last]
                    status = items[last+1]
                    rRep.addRecordAndStatus(record,status)
                    #print data[0].split()
                    #print record, status
                    last += 1
                    remaining -= 1
                runReports.append(rRep)
        cache.close()                

    return runNumbers, runReports


def writeCacheAndLog(cachefilename, logfilename, runReports):
    last2days = datetime.timedelta(days=2)
    tableForCache =[]
    tableForCache.append(["# run", "start-time", "end-time", "PCL Run", "payload","upload","Tier0 OOO", "latency from start", "latency from end"])

    tableForLog =[]
    tableForLog.append(["# run", "start-time", "end-time", "PCL Run", "payload","upload","Tier0 OOO", "latency from start", "latency from end"])

    #print str(len(runReports))
    for rep in runReports:

        twdaysago = datetime.datetime.today() - last2days
        if rep.startTime() < twdaysago:
            #print "start: " + str(rep.startTime()) + " older than " + str(twdaysago)
            tableForCache.append(rep.getList())            
        tableForLog.append(rep.getList()) 

        
    #out = sys.stdout
    cacheFile = file(cachefilename,"w")
    tableWriter.pprint_table(cacheFile, tableForCache)
    cacheFile.close()

    #out = sys.stdout
    logFile = file(logfilename,"w")
    tableWriter.pprint_table(logFile, tableForLog)
    logFile.close()



def getRunReport(runinfoTag, run, promptCalibDir, fileList, iovtableByRun_oracle, iovtableByLumi_oracle):
    
    #print run
    # input: runInfoTag, run, fileList, iovlist
    runInfo = None
    try:
        runInfo = RunInfo.getRunInfoStartAndStopTime(runinfoTag, '', run)

    except Exception as error:
        print "*** Error can not find run: " + str(run) + " in RunInfo: " + str(error)
        raise Exception("Error can not find run: " + str(run) + " in RunInfo: " + str(error))

    rRep = RunReport()
    rRep.setRunNumber(runInfo.run())
    rRep.setRunInfoContent(runInfo)

    deltaTRun = runInfo.stopTime() - runInfo.startTime()
    deltaTRunH = deltaTRun.days*24. + deltaTRun.seconds/(60.*60.)

    print "-- run #: " + colorTools.blue(runInfo.run())            
    print "   start: " + str(runInfo.startTime()) + " stop: " + str(runInfo.stopTime()) + " lenght (h): " + str(deltaTRunH)

    # --- status flags for this run
    isFileFound = False
    emptyPayload = True
    isOutOfOrder = False
    allLumiIOVFound = False


    # --- look for the file on AFS
    fileName = ""
    fileForRun = []
    # find the files associated to this run:
    for dbFile in fileList:
        if str(run) in dbFile:
            fileForRun.append(dbFile)

    if len(fileForRun) == 0:
        print "   " + colorTools.warning("***Warning") + ": no sqlite file found!"
        isFileFound = False

    elif len(fileForRun) > 1:
        print "   " + colorTools.warning("***Warning") + ": more than one file for this run!"
        for dbFile in fileForRun:
            modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(promptCalibDir + dbFile))
            print '       ',dbFile,'time-stamp:',modifDate


    for dbFile in fileForRun:
        isFileFound = True
        if isFileFound and not emptyPayload and isFileFound:
            # in this case the file was already identified
            continue
        print "   file: " + dbFile
        modifDate = datetime.datetime.fromtimestamp(os.path.getmtime(promptCalibDir + dbFile))
        rRep.setJobTime(modifDate)

        #         # check this is not older than the one for the following run
        #         if isFirst or modifDate < lastDate:
        #             lastDate = modifDate
        #             isFirst = False
        #             isOutOfOrder = False

        #         else:
        #             print "   " + warning("Warning: ") + " this comes after the following run!!!"
        #             isOutOfOrder = True


        # delta-time from begin of run
        deltaTFromBegin = modifDate - runInfo.startTime()
        deltaTFromBeginH = deltaTFromBegin.days*24. + deltaTFromBegin.seconds/(60.*60.)

        # delta-time from end of run
        deltaTFromEndH = 0.01
        if(modifDate > runInfo.stopTime()): 
            deltaTFromEnd = modifDate - runInfo.stopTime()
            deltaTFromEndH = deltaTFromEnd.days*24. + deltaTFromEnd.seconds/(60.*60.)

        print "   file time: " + str(modifDate) + " Delta_T begin (h): " + str(deltaTFromBeginH) + " Delta_T end (h): " + str(deltaTFromEndH)

        rRep.setLatencyFromBeginning(deltaTFromBeginH)
        rRep.setLatencyFromEnd(deltaTFromEndH)

        # check the file size
        fileSize = os.path.getsize(promptCalibDir + dbFile)
        if fileSize == 1 or fileSize == 32768:
            emptyPayload = True
            print "   " + colorTools.warning("***Warning") + ": no payload in sqlite file!"
        else:
            emptyPayload = False

            # list the iov in the tag
            connect    = "sqlite_file:" + promptCalibDir + dbFile
            listiov_run_sqlite = gtTools.listIov(connect, tagRun, '')
            if listiov_run_sqlite[0] == 0:
                iovtableByRun_sqlite = gtTools.IOVTable()
                iovtableByRun_sqlite.setFromListIOV(listiov_run_sqlite[1])
                #iovtableByRun_sqlite.printList()
                for iov in iovtableByRun_sqlite._iovList:
                    iovOracle = gtTools.IOVEntry()
                    if iovtableByRun_oracle.search(iov.since(), iovOracle):
                        print "    runbased IOV found in Oracle!"
                        #print iovOracle
                    else:
                        print "    " + colorTools.warning("Warning:") + " runbased IOV not found in Oracle"
                

            missingIOV = False
            listiov_lumi_sqlite = gtTools.listIov(connect, tagLumi, '')
            if listiov_lumi_sqlite[0] == 0:
                iovtableByLumi_sqlite = gtTools.IOVTable()
                iovtableByLumi_sqlite.setFromListIOV(listiov_lumi_sqlite[1])
                #iovtableByLumi_sqlite.printList()
                counterbla = 0
                for iov in iovtableByLumi_sqlite._iovList:
                    iovOracle = gtTools.IOVEntry()
                    if not iovtableByLumi_oracle.search(iov.since(), iovOracle):
                        #print "    Lumi based IOV found in Oracle:"
                        #print iovOracle
                        counterbla += 1
                        print "    " + colorTools.warning("Warning:") + " lumibased IOV not found in Oracle for since: " + str(iov.since())
                        missingIOV = True
            else:
                raise Exception("Error can not list IOV for file",connect)
                
                
            if not missingIOV:
                allLumiIOVFound = True
                print "    All lumibased IOVs found in oracle!"
            else:
                allLumiIOVFound = False
                print "    " + colorTools.warning("Warning:") + " not all lumibased IOVs found in Oracle!!!"




    # fill the run-report for this run
    if not isFileFound:
        rRep.sqliteFound(False)
    else:
        rRep.sqliteFound(True)
        if isOutOfOrder:
            rRep.isOutoforder(True)
        else:
            rRep.isOutoforder(False)

        if emptyPayload:
            rRep.payloadFound(False)
        else:
            rRep.payloadFound(True)

        if not allLumiIOVFound:
            rRep.isUploaded(False)
        else:
            rRep.isUploaded(True)

    return rRep


import json


class O2ORecordJson:
    def __init__(self, name):
        self._name = name
        self._recordMap = {}

    #def rcdID(self):
    #    return RcdID([self._record,self._label])


    def addRcd(self, rcdId, rcdRep):
        self._recordMap[rcdId[0]] = rcdRep._properties

        
    def writeJsonFile(self, dirName):
        filename =  self._name + ".json"
        # get a string with JSON encoding the list
        #dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        dump = json.dumps(self._recordMap)
        file = open(dirName + '/' + filename, 'w')
        file.write(dump + "\n")
        file.close()

    def readJsonFile(self, dirName):
        filename = self._name + ".json"
        jsonData = open(dirName + '/' + filename)
        self._recordMap = json.load(jsonData)
        jsonData.close()

    def getRecordReport(self, rcdId):
        rcdRep = RecordReport(rcdId[0])
        rcdRep._properties = self._recordMap[rcdId]
        return rcdRep

    def getRecordIds(self):
        return self._recordMap.keys()







