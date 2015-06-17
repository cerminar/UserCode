import commands
from datetime import datetime
from CondCore.Utilities.timeUnitHelper import *
import re

def listIov_CondDBV1(connect, tag, passwd):
    """
    Interface to cmscond_list_iov command (CondDBv1)
    """
    # FIXME: this need to be migrated to CondDBv2 and also TNS_ADMIN should be configurable
    listiovCommand = 'export TNS_ADMIN=/data/secrets/conddb/oracle/admin; cmscond_list_iov -c ' + connect + '  -t ' + tag
    # listiovCommand = 'setenv TNS_ADMIN /afs/cern.ch/cms/DB/conddb; cmscond_list_iov -c ' + connect + '  -t ' + tag
    # listiovCommand = 'cmscond_list_iov -c ' + connect + '  -t ' + tag
    if passwd != 'None' and passwd != '':
        listiovCommand = listiovCommand + ' -P ' + passwd
    statusAndOutput = commands.getstatusoutput(listiovCommand)
    if statusAndOutput[0] != 0:
        print "Warning: listiov for tag: " + tag + " failed!"
        print listiovCommand
        print statusAndOutput[1]

    return statusAndOutput


def listIov_CondDBV2(connect, tag, passwd):
    """
    Interface to 'conddb list' command (CondDBv2)
    """
    dbAlias = ''

    # check for online connection strings
    #FIXME: should actually be orapro, but need to figure out how to provide the pwd
    if 'oracle://cms_orcon_prod' in connect:
        dbAlias = 'pro'
        connect = dbAlias        
    elif 'oracle://cms_orcoff_prep' in connect:
        dbAlias = 'dev'
        connect = dbAlias

    
    #FIXME: should add handling of the password
    conddb_list_command = 'conddb --db %s list --limit 10000 %s' % (connect, tag)
    conddb_list_return = commands.getstatusoutput(conddb_list_command)

    if conddb_list_return[0] != 0:
        print "Warning: listiov for tag: " + tag + " failed!"
        print conddb_list_command
        print conddb_list_return[1]

    return conddb_list_return


def getIOVTag_CondDBV1(connect, tag, passwd):
    ret = IOVTag()
    listiov_oracle = listIov_CondDBV1(connect, tag, passwd)
    if listiov_oracle[0] == 0:
        ret.setFromListIOV_CondDBV1(listiov_oracle[1])
    else:
        print listiov_oracle[1]
        raise RuntimeError("[getIOVTag_CondDBV1] list iov failed for tag %s in %s!" % (tag, connect))
    return ret

def getIOVTag_CondDBV2(connect, tag, passwd):
    ret = IOVTag()
    listiov_oracle = listIov_CondDBV2(connect, tag, passwd)
    if listiov_oracle[0] == 0:
        ret.setFromListIOV_CondDBV2(tag, listiov_oracle[1])
    else:
        print listiov_oracle[1]
        raise RuntimeError("[getIOVTag_CondDBV2] list iov failed for tag %s in %s!" % (tag, connect))
    return ret


class IOVEntry:
    def __init__(self, timetype = "runnumber"):
        self.since = None
        self.payloadHash = None
        self.insertionTime = None
        self.timeType = timetype


    def setFromSqlite3_CondDBV2(self, values):
        if self.timeType == 'timestamp':
            #FIXME: move unpack here and remove the dependency on cmssw
            #self.since = datetime.strptime(timeStamptoDate(int(values[1])),"%a %b %d %H:%M:%S  %Y")
            #print values[1]
            #print unpack(values[1])[0]
            #print datetime.utcfromtimestamp(unpack(values[1])[0])
            # FIXME: should use the first as soon as we migrate also conddb to use UTC
            #self.since = datetime.utcfromtimestamp(unpack(values[1])[0])
            self.since = datetime.fromtimestamp(unpack(values[1])[0])

        elif self.timeType == 'lumiid':
            self.since = self.unpackLumiid(int(values[1]))
        elif self.timeType == 'runnumber':
            self.since = int(values[1])
        else:
            raise ValueError("[IOVEntry::setFromSqlite3_CondDBV2] timetype %s is not valid!" % self.timeType)

        self.payloadHash = values[3]

        #FIXME: the insertion time is not yet handled
        #formatdate = "%Y-%m-%d %H:%M:%S"

        #if len(listofentries[3]) != 8:
        #        formatdate = "%Y-%m-%d %H:%M:%S.%f"
        
        return

        
    def setFromListIOV_CondDBV1(self, line, timetype = "runnumber"):
        listofentries = line.split()
        # print "listofentries =", listofentries
        if self.timeType == 'timestamp':
            self.since = datetime.strptime(timeStamptoDate(int(listofentries[0])),"%a %b %d %H:%M:%S  %Y")
            if int(listofentries[3]) != 18446744073709551615:
                self.payloadHash = listofentries[6]
            else:
                self.payloadHash = listofentries[5]
        elif self.timeType == 'lumiid':
            self.since = self.unpackLumiid(int(listofentries[0]))
            self.payloadHash = listofentries[6]
        elif self.timeType == 'runnumber':
            self.since = int(listofentries[0])
            self.payloadHash = listofentries[2]
        else:
            raise ValueError("[IOVEntry::setFromListIOV] timetype %s is not valid!" % self.timeType)

        return

    def setFromListIOV_CondDBV2(self, line, timetype = "runnumber"):
        listofentries = line.split()
        formatdate = "%Y-%m-%d %H:%M:%S"
        if self.timeType == 'timestamp':
            # in the current version of conddb tools this is local
            self.since = datetime.strptime(listofentries[0] +' ' + listofentries[1],"%Y-%m-%d %H:%M:%S")
            #print "dt: ", dt
            #import pytz
            #utc = pytz.utc
            #zurich = pytz.timezone('Europe/Zurich')

            #zurich_time = zurich.localize(dt)
            #print "zt: ",zurich_time
            #utc_time = zurich_time.astimezone(utc)
            #print "utc: ",utc_time
            # we convert it to timestamp
            #timestamp = (dt - datetime(1970,1,1)).total_seconds()
            #print timestamp
            #self.since = datetime.fromtimestamp(timestamp)
            if len(listofentries[3]) != 8:
                formatdate = "%Y-%m-%d %H:%M:%S.%f"
            self.insertionTime = datetime.strptime(listofentries[2] + ' ' + listofentries[3], formatdate)
            self.payloadHash = listofentries[4]

        elif self.timeType == 'lumiid':
            self.since = (int(listofentries[0]), int(listofentries[2]))
            if len(listofentries[4]) != 8:
                formatdate = "%Y-%m-%d %H:%M:%S.%f"
            self.insertionTime = datetime.strptime(listofentries[3] + ' ' + listofentries[4], formatdate)
            self.payloadHash = listofentries[5]
        elif self.timeType == 'runnumber':
            self.since = int(listofentries[0])
            if len(listofentries[2]) != 8:
                formatdate = "%Y-%m-%d %H:%M:%S.%f"
            self.insertionTime = datetime.strptime(listofentries[1] + ' ' + listofentries[2], formatdate)
            self.payloadHash = listofentries[3]
        else:
            raise ValueError("[IOVEntry::setFromListIOV] timetype %s is not valid!" % self.timeType)

    
        return


    def __str__(self):
        return str(self.since) + '\t' + '\t' + self.payloadHash

        
    def unpackLumiid(self, lumiid):
        kLowMask = 0XFFFFFFFF
        run = lumiid >> 32
        lumi = lumiid & kLowMask
        return (run, lumi)


#      ===========================================================
#      Tag: XMLFILE_Geometry_44YV1_Ideal_mc
#              ===========================================================
#              TimeType: runnumber
#                      Since         Till          Payload token  Payload Class
#                              ------------  ------------  -------------  ----------------
#                                                 1    4294967295  0007-0000000A          FileBlob

#                                                         Total # of payload objects: 1
                                                        


class IOVTag:
    def __init__(self):
        self.iovList = []
        self.tagName = None
        self.timeType = None
        self.containerName = ""
        return

    @property
    def _iovList(self):
        """ This is needed for backward compatibility with previous implementation of IOVTable
        which is cached in the DB"""
        return self.iovList

    def addIOVEntry(self, entry):
        # print "Add IOV : " + str(entry)
        self.iovList.append(entry)
    

    def setFromListIOV_CondDBV1(self, listiovOutput):
        listiovlines  = listiovOutput.split('\n')
        nLines = len(listiovlines)
        for line in listiovlines:
            if "=========" in line or "------------" in line:
                continue
            linewords = line.split()
            if len(linewords) != 0:
                #print line
                if 'Tag' in linewords[0]:
                    self.tagName = linewords[1]
                elif 'TimeType' in linewords[0]:
                    self.timeType = linewords[1]
                elif 'PayloadContainerName' in linewords[0]:
                    self.containerName = linewords[1]

                    
        #print self.tagName
        for line in range(6, nLines-1):
            # print "listiovlines =", listiovlines[line]
            # if "Since" in listiovlines[line] or "------------" in listiovlines[line] or listiovlines[line] == "":
            if "Since" in listiovlines[line] or "------------" in listiovlines[line] or listiovlines[line] == "" or "TimeType" in listiovlines[line]:
                continue
            # print "after continue listiovlines =", listiovlines[line]
            ioventry = IOVEntry(self.timeType)
            if self.containerName == "":
                items = listiovlines[line].split()
                self.containerName = items[len(items)-1]
            ioventry.setFromListIOV_CondDBV1(listiovlines[line])
            self.addIOVEntry(ioventry)


    def setFromListIOV_CondDBV2(self, tagname, listiovOutput):
        listiovlines  = listiovOutput.split('\n')
        nLines = len(listiovlines)
        self.tagName = tagname
        
        for idx in range(3,nLines-1):
            ansi_escape = re.compile(r'\x1b[^m]*m')
            line = ansi_escape.sub('', listiovlines[idx])

            # execute only once
            if idx == 3:
                linewords = line.split()
                nFields = len(linewords)
                if nFields == 6:
                    self.timeType = 'timestamp'
                elif nFields == 7:
                    self.timeType = 'lumiid'
                elif nFields == 5:
                    self.timeType = 'runnumber'
                else:
                    raise ValueError("[IOVTag::setFromListIOV_CondDBV2] unknown # of fields %s!" % str(nFields))

                self.containerName = linewords[-1]
                
            ioventry = IOVEntry(self.timeType)
            ioventry.setFromListIOV_CondDBV2(line)
            self.addIOVEntry(ioventry)



    # def checkConsitency(self, tagType):
    #     if tagType == "mc":
    #         if len(self.iovList) != 1:
    #             print warning("***Warning") + " MC tag: " + self.tagName + " contains: " + str(len(self.iovList)) + " IOVs"
    #         else:
    #             if self.iovList[0].since() != 1 or self.iovList[0].till() != 4294967295:
    #                 print warning("***Warning") + " MC tag: " + self.tagName + " has IOV: " + str(self.iovList[0])
    #     elif tagType == "data":
    #         if self.iovList[0].sinceR() != 1 or self.iovList[len(self.iovList) - 1].tillR() != 4294967295:
    #             print warning("***Warning") + " data tag: " + self.tagName + " is not covering the whole range 1 - inf"
    #             #self.printList()
    #             return
    #         if len(self.iovList) != 1:
    #             for index in range(0, len(self.iovList)-1):
    #                 if (self.iovList[index+1].sinceR() - self.iovList[index].tillR()) > 1:
    #                     print warning("***Warning") + " data tag: " + self.tagName + " has an hole in the IOVs:"
    #                     print self.iovList[index]
    #                     print self.iovList[index+1]
    #                     #self.printList()
    #                     return

    def printList(self):
        print "Tag " + self.tagName
        print "TimeType " + self.timeType
        print "PayloadContainerName " + self.containerName
        print "since    payloadToken"
        for iov in self.iovList:
            print iov
        print "Total # of payload objects: " + str(len(self.iovList))
        return
    
    @property    
    def lastIOV(self):
        return  self.iovList[len(self.iovList)-1]

    @property
    def size(self):
        return len(self.iovList)

    def searchIOV(self, iov):
        # FIXME: in CondDBv2 the IOVs are not unique The algorithm should give the lower match and than look for the payloadHash
        # this however needs the sqlite to be in CondDBv2
        since = iov.since
        hi = self.size
        lo = 0
        while lo < hi:
            mid = (lo+hi)//2
            midval = self.iovList[mid]
            
            if midval.since < since:
                lo = mid+1
            elif midval.since > since:
                hi = mid
            else:
                if iov.payloadHash ==  midval.payloadHash:
                    return True, midval
                return False, midval
        return False, None


    def search(self, since, iov):
        """ OBSOLETE, should migrate the DB schema and get rid of this"""
        hi = self.size
        lo = 0
        while lo < hi:
            mid = (lo+hi)//2
            midval = self.iovList[mid]
            if midval.since < since:
                lo = mid+1
            elif midval.since > since:
                hi = mid
            else:
                #iov = midval
                iov.since = midval.since
                iov.payloadHash = midval.payloadHash
                iov.timeType = midval.timeType
                #print midval
                return True
        return False


if __name__ == "__main__":
    index = 4

    if index == 1:
        tag = 'SiStripBadChannel_PCL_v1_offline'
        connect = 'frontier://FrontierPrep/CMS_COND_STRIP'
        passwd = ''
        res = listIov_CondDBV1(connect, tag, passwd)
        table = IOVTag()
        table.setFromListIOV_CondDBV1(res[1])
        table.printList()

    elif index == 2:
        tag = 'EcalLaserAPDPNRatios_prompt'
        connect = 'frontier://FrontierProd/CMS_COND_42X_ECAL_LAS'
        passwd = ''
        res = listIov_CondDBV1(connect, tag, passwd)
        table = IOVTag()
        table.setFromListIOV_CondDBV1(res[1])
        table.printList()

    elif index == 3:
        tag = 'BeamSpotObjects_PCL_byLumi_v1_prompt'
        connect = 'frontier://FrontierProd/CMS_COND_31X_BEAMSPOT'
        passwd = ''
        res = listIov_CondDBV1(connect, tag, passwd)
        table = IOVTag()
        table.setFromListIOV_CondDBV1(res[1])
        table.printList()

    elif index == 4:
        tag = 'SiStripBadChannel_PCL_v1_offline'
        connect = 'dev'
        passwd = ''
        table = getIOVTag_CondDBV2(connect, tag, passwd)
        table.printList()
        iov = IOVEntry()
        if table.search(238412, iov):
            print "found"
        else:
            print "not found"
        
    elif index == 5:

        tag = 'BeamSpotObjects_PCL_byLumi_v1_prompt'
        connect = 'pro'
        passwd = ''
        table = getIOVTag_CondDBV2(connect, tag, passwd)
        table.printList()

    elif index == 6:

        tag = 'EcalLaserAPDPNRatios_prompt'
        connect = 'pro'
        passwd = ''
        table = getIOVTag_CondDBV2(connect, tag, passwd)
        table.printList()
