#!/usr/bin/env python

import os
import sys
from ConfigParser import ConfigParser
from copy import copy
from optparse import OptionParser, Option, OptionValueError
#import coral
#from CondCore.TagCollection import Node,tagInventory,CommonUtils,entryComment
from operator import itemgetter


import commands

# tools for color printout
from Tools.MyCondTools.color_tools import *
from Tools.MyCondTools.gt_tools import *
from Tools.MyCondTools.odict import *

def dump2XML(pfn, tag, passwd, begin):
    scratch = os.environ["SCRATCH"]
    print scratch 
    command = "cd " + scratch + " ; cmscond_2XML -c " + pfn + " -t " + tag + " -b " + str(begin) + " -P " + passwd 

    outandstat = commands.getstatusoutput(command)
    if outandstat[0] != 0:
        print outandstat[1]
    return scratch + "/" + tag + ".xml"

def diffXML(filename1, filename2):
    command = "diff " + filename1 + " " + filename2
    outandstat = commands.getstatusoutput(command)
                  
    difflines  = outandstat[1].split('\n')
    nLines = len(difflines)
    # print self._tagName
    for line in difflines:
        if "root setup=" in line:
            continue
        if "XmlKey name" in line:
            continue
        if "2,3c2,3" in line:
            continue
        if "---" in line:
            continue
        #print line
        return False
    return True

def resetQueue(cfgName, cfgFile, newVersion):
    # print confirmation message
    print fg
    warning("*** Warning, reset GT conf file: " + cfgName)
    confirm = raw_input('Proceed? (y/N)')
    confirm = confirm.lower() #convert to lowercase
    if confirm != 'y':
        return

    print "Resetting: " + cfgName
            
    newconfig = ConfigParser(dict_type=OrderedDict)
    newconfig.optionxform = str
    # starting tag
    newconfig.add_section("Common")
    newconfig.set("Common",'OldGT', cfgFile.get('Common','NewGT'))

    # new GT name
    newgtname = cfgFile.get('Common','NewGT').split('_V')[0] + '_V' + newVersion

    if newgtname == cfgFile.get('Common','NewGT'):
        print "New tag : " + newgtname + " equal to old tag: " + cfgFile.get('Common','NewGT') + " skipping the reset"
        return
            
    newconfig.set("Common",'NewGT', newgtname)
    newconfig.set("Common",'Passwd', cfgFile.get('Common','Passwd'))
    newconfig.set("Common",'Environment', cfgFile.get('Common','Environment'))
    newconfig.set("Common",'GTType', cfgFile.get('Common','GTType'))
            
    newconfig.add_section("Tags")
    newconfig.add_section("Connect")
    newconfig.add_section("Account")
    newconfig.add_section("AddRecord")
    newconfig.add_section("RmRecord")

    newconfig.add_section("TagManipulation")
    newconfig.set("TagManipulation",'check', 'new')

    newconfig.add_section("Comments")
    newconfig.set("Comments","Release",cfgFile.get("Comments","Release"))
    newconfig.set("Comments","Scope",cfgFile.get("Comments","Scope"))
    newconfig.set("Comments","Changes",'')
    
    newconfig.add_section("Pending")
    if cfgFile.has_section("Pending"):
        for item in cfgFile.items("Pending"):
            newconfig.set("Pending",item[0],item[1])
            
            
    # write the file
    configfile = open(cfgName, 'wb')
    newconfig.write(configfile)
    configfile.close()
    cvsCommit(cfgName,'reset for new GT')
    return


def getEntryByTag(gtCollection, tagName, entry):
    if not tagCollection.hasTag(tagName):
        print warning("***Warning ") + "tag " + tagName + " not found in this GT"
        return False
    # get the old entry for this tag
    print tagCollection.getByTag(tagName)
    entry = tagCollection.getByTag(tagName)
    print entry
    return True


def getEntryByRcd(gtCollection, rcdAndLabel, entry):
    rcdandlbl = options.record.split(',')
    if len(rcdandlbl) == 1:
        rcdandlbl.append('')
    rcdId = RcdID ([rcdandlbl[0],rcdandlbl[1]])
    if not tagCollection.hasRcdID(rcdId):
        print warning("***Warning ") + str(rcdId) + " not found in this GT"
        return False
    print tagCollection.getByRcdID(rcdId)
    entry = tagCollection.getByRcdID(rcdId)
    print entry
    return True

def checkIOV(newentry, gttype, isOnline, passwd):              
    # list IOV            
    outputAndStatus = listIov(newentry.getOraclePfn(isOnline), newentry.tagName(), passwd)
    if outputAndStatus[0] != 0:
        print ' -----'
        print error("***Error:") + " list IOV failed for tag: " + str(newentry)
        print "         account: " + newentry._account
        print outputAndStatus[1]
        print ''
        sys.exit(1)
    else:
        iovtable = IOVTable()
        iovtable.setFromListIOV(outputAndStatus[1])
        iovtable.checkConsitency(gttype)
        print "tag check: done"


if __name__     ==  "__main__":

    # ---------------------------------------------------------
    # --- set the command line options
    parser = OptionParser()

    parser.add_option("--dump", action="store_true",dest="dump",default=False, help="dump the entry in the GT")
    
#     parser.add_option("-s", "--scenario", dest="scenario",
#                       help="GT scenario: ideal - mc - startup - data - craft09",
#                       type="str", metavar="<scenario>",action="append")
#     parser.add_option("-r", "--release", dest="releases",
#                       help="CMSSW release", type="str",
#                       metavar="<release>",action="append")
#     # to substitute a tag or a record you need to specify one of these
#     parser.add_option("-t", "--tag", dest="oldtag",
#                       help="tag", type="str", metavar="<tag>",default="NONE")
#     parser.add_option("--rcd", dest="record",
#                       help="record and optionally label", type="str", metavar="<record>[,<label>]",default="NONE")
    

#     parser.add_option("--new-tag", dest="newtag",
#                       help="new tag", type="str", metavar="<new-tag>",default="NONE")
#     parser.add_option("--new-connect", dest="newconnect",
#                       help="new connect", type="str", metavar="<new-connect>",default="NONE")
#     parser.add_option("--new-account", dest="newaccount",
#                       help="new account", type="str", metavar="<new-account>",default="NONE")
#     parser.add_option("--new-rcd", dest="newrecord",
#                       help="new record", type="str", metavar="<new-record>",default="NONE")
#     parser.add_option("--new-object", dest="newobject",
#                       help="new object", type="str", metavar="<new-object>",default="NONE")
#     parser.add_option("--new-leaf", dest="newleaf",
#                       help="new leaf", type="str", metavar="<new-leaf>",default="NONE")
#     parser.add_option("--new-label", dest="newlabel",
#                       help="new label", type="str", metavar="<new-label>",default="")



#     parser.add_option("-c", "--comment", dest="comment",
#                       help="comment", type="str", metavar="<comment>",default="NONE")

    
#     parser.add_option("--dump", action="store_true",dest="list",default=False, help="dump the entry in the GT")
#     parser.add_option("--check", action="store_true",dest="check",default=False, help="check the IOV of the tag")
#     parser.add_option("--reset", action="store_true",dest="reset",default=False, help="clean the queue")
#     parser.add_option("-v", "--version", dest="version",
#                       help="version of the new GT (used with --reset)", type="str", metavar="<version>",default="NONE")

    
    
    #    parser.add_option("-t", "--globaltag", dest="gt",
    #                      help="Global-Tag", type="str", metavar="<globaltag>")
    #parser.add_option("--local", action="store_true",dest="local",default=False)

    (options, args) = parser.parse_args()

    print args
    
    # read a global configuration file
    cfgfile = ConfigParser()
    cfgfile.optionxform = str


    # FIXME: configure this
    CONFIGFILE = "GT_branches/Common.cfg"
    print 'Reading configuration file from ',CONFIGFILE
    cfgfile.read([ CONFIGFILE ])
    passwdfile             = cfgfile.get('Common','Passwd')


    globaltag1 = args[0]
    globaltag2 = args[1]
    
    #print "Compare "
    #print "      GT 1: " + globaltag1 + " with GT 2: " + globaltag2

    filename1 = globaltag1 + '.conf'
    filename2 = globaltag2 + '.conf'

    # create the collection of tags
    tagCollection1 = GTEntryCollection()
    tagCollection2 = GTEntryCollection()

    # --------------------------------------------------------------------------
    # fill the collection
    fillGTCollection(filename1, globaltag1, tagCollection1)
    fillGTCollection(filename2, globaltag2, tagCollection2)


    # compare the # of records in the GT
#     print "    GT " + globaltag1 + " has " + str(tagCollection1.size()) + " entries"
#     print "    GT " + globaltag2 + " has " + str(tagCollection2.size()) + " entries"

    firstCollection = tagCollection1
    secondCollection = tagCollection2
    
    if tagCollection1.size() <  tagCollection2.size():
        firstCollection = tagCollection2
        secondCollection = tagCollection1
        print "    GT 1: " + globaltag2 + " has " + str(tagCollection2.size()) + " entries"
        print "    GT 2: " + globaltag1 + " has " + str(tagCollection1.size()) + " entries"
    else:
        print "    GT 1: " + globaltag1 + " has " + str(tagCollection1.size()) + " entries"
        print "    GT 2: " + globaltag2 + " has " + str(tagCollection2.size()) + " entries"


    nchanges = 0

    # loop over all records and compare the tag names and the # of payloads
    for index in range(0, len(firstCollection._tagOrder)):
        entry1 = firstCollection._tagList[firstCollection._tagOrder[index]]

        # FIXME: check that record is in the GT
        if not secondCollection.hasRcdID(entry1.rcdID()):
            print " Rcd: " + str(entry1.rcdID()) + " not in GT 2!!!"
            continue
        
        entry2 = secondCollection.getByRcdID(entry1.rcdID())

        runnumber = 300000

        if entry1.tagName() != entry2.tagName():

            match = False

            if options.dump:
                outputAndStatus1 = listIov(entry1.getOraclePfn(False), entry1.tagName(), passwdfile)
                outputAndStatus2 = listIov(entry2.getOraclePfn(False), entry2.tagName(), passwdfile)

                if outputAndStatus1[0] == 0 and outputAndStatus2[0] == 0: 
                    iovtable1 = IOVTable()
                    iovtable1.setFromListIOV(outputAndStatus1[1]) 
                    lastiov1 = iovtable1.lastIOV()

                    iovtable2 = IOVTable()
                    iovtable2.setFromListIOV(outputAndStatus2[1]) 
                    lastiov2 = iovtable2.lastIOV()


                    # 1 - Check the tokens fo the last IOV
                    if lastiov1.token() == lastiov2.token():
                        match = True

                    # 2 - Dump the last IOV in xml and compare
                    else:                     
                        if entry1.rcdID()[0] != "SiPixelGainCalibrationOfflineRcd" and entry1.rcdID()[0] != "DQMReferenceHistogramRootFileRcd":
                            difffile1 = dump2XML(entry1.getOraclePfn(False), entry1.tagName(), passwdfile, lastiov1.since() + 1)
                            difffile2 = dump2XML(entry2.getOraclePfn(False), entry2.tagName(), passwdfile, lastiov2.since() + 1)

                            if diffXML(difffile1, difffile2):
                                match = True
                                os.remove(difffile1)
                                os.remove(difffile2)

                        




            

                    
            if not match:
                print entry1.rcdID()
                print "     tag 1: " + entry1.tagName() + " -> 2: " + entry2.tagName()
                nchanges += 1
                
             
#         else:
#             # check the # of IOVs
#             outputAndStatus1 = listIov(entry1.pfn(), entry1.tagName(), passwdfile)
#             outputAndStatus2 = listIov(entry2.pfn(), entry2.tagName(), passwdfile)

#             iovtable1 = IOVTable()
#             iovtable1.setFromListIOV(outputAndStatus1[1])

#             iovtable2 = IOVTable()
#             iovtable2.setFromListIOV(outputAndStatus2[1])

#             if iovtable1.size() != iovtable2.size():
#                 print entry1.rcdID()
#                 print "     # IOVs 1: " + str(iovtable1.size()) + " -> 2: " + str(iovtable2.size()) + "   delta = " + str(iovtable2.size() - iovtable1.size())

    print "# of changes: " + str(nchanges)

    sys.exit(1)
    

    # get the releases currently managed
    known_releases         = cfgfile.get('Common','Releases').split(',')
    gtconnstring           = cfgfile.get('Common','GTConnectString')
    passwdfile             = cfgfile.get('Common','Passwd')

    # read the cfg file containing comments
    commentfile = ConfigParser(dict_type=OrderedDict)
    commentfile.optionxform = str
    COMMENTFILENAME = "GT_branches/Comments.cfg"
    cvsUpdate(COMMENTFILENAME)
    print 'Reading updated comment file from ',COMMENTFILENAME
    commentfile.read([ COMMENTFILENAME ])

    # ---------------------------------------------------------------------------
    # --- check options and expand wildcards and aliases

    # force comments to be added for new tags
    if options.newtag != 'NONE' and options.comment == 'NONE':
        # check that the comment has not yet been entered
        if not commentfile.has_option("TagComments",options.newtag):
            print warning("***Warning") + " no comments for tag: " + options.newtag

 
    basedir = "GT_branches/"
    gtConfList = []

    for conffile in args:
        gtConfList.append(conffile)
    

    #print "------------------------"
    if options.scenario != None and options.releases != None:
        # wild card for scenarios
        if 'all' in options.scenario:
            options.scenario = ['DESIGN','MC','START',"GR_R","CRAFT09"]
        elif 'mc' in options.scenario:
            options.scenario = ['DESIGN','MC','START']


        # wild-card for releases
        if 'all' in options.releases:
            options.releases = known_releases


        for gttype in options.scenario:
            for release in options.releases:
                print "--- Scenario: " + gttype + " release: " + release
                gtConf = 'GT_' + release + "_" + gttype + ".cfg"
                CONFIGFILE = basedir + gtConf            
                if os.path.isfile(CONFIGFILE):
                    print '    configuration file: ',CONFIGFILE
                    gtConfList.append(CONFIGFILE)
                else:
                    print "    cfg: " + CONFIGFILE + " doesn't exist!"



    # loop on the configuration files and update them
    for cfg in gtConfList:
        if not os.path.isfile(cfg):
            print "Cfg: " + CONFIGFILE + " doesn't exist!"
            sys.exit(1)

            
        diffconfig = ConfigParser(dict_type=OrderedDict)
        diffconfig.optionxform = str

        print "---------------------------------------------------------------"
        print 'Reading configuration file from ',cfg
        cvsUpdate(cfg)
        diffconfig.read(cfg)

        # get the old GT name
        OLDGT = diffconfig.get('Common','OldGT')
        nextGT = diffconfig.get('Common','NewGT')

        oldfilename = OLDGT + '.conf'
        print "--- Original GT: " + OLDGT
        print '        Next GT: ' + nextGT
        # create the collection of tags
        tagCollection = GTEntryCollection()

        # --------------------------------------------------------------------------
        # fill the collection
        fillGTCollection(oldfilename, OLDGT, tagCollection)

        # 1. Manipulate an existing entry
        if options.oldtag != "NONE" or options.record != "NONE":
            # original entry
            oldentry = GTEntry()
            
            if options.oldtag != "NONE":
                tagName = options.oldtag
                if not tagCollection.hasTag(tagName):
                    print warning("***Warning ") + "tag " + tagName + " not found in this GT"
                    continue
                oldentry = tagCollection.getByTag(tagName)

            elif options.record != "NONE":
                rcdandlbl = options.record.split(',')
                if len(rcdandlbl) == 1:
                    rcdandlbl.append('')
                rcdId = RcdID ([rcdandlbl[0],rcdandlbl[1]])
                if not tagCollection.hasRcdID(rcdId):
                    print warning("***Warning ") + str(rcdId) + " not found in this GT"
                    continue
                oldentry = tagCollection.getByRcdID(rcdId)
            
            # A -> dump the entry
            if options.list:
                # some useful printout for this tag
                print " -- List: " + str(oldentry)
                print "     cfg string:"
                print "     " + oldentry.getCfgFormat()

            
            # B -> modify the entry
            if  options.newtag != 'NONE' or  options.newconnect != 'NONE' or  options.newaccount != 'NONE':
                # check that the GT is not already in oracle
                if gtExists(nextGT, gtconnstring, passwdfile):
                    print error("***Error: GT: " + nextGT + " is already in oracle: cannot be modified!!!")
                    continue
                    
                # modify the relevant properties
                newentry = oldentry
                if  options.newtag != 'NONE':
                    newentry.setTagName(options.newtag)
                if options.newconnect != 'NONE':
                    newentry.setConnect(options.newconnect)
                if options.newaccount != 'NONE':
                    newentry.setAccount(options.newaccount)

                # check the tag
                isOnline = False
                if  diffconfig.get('Common','Environment') != 'offline':
                    isOnline = True
                passwdfile =  diffconfig.get('Common','Passwd')
                gttype =  diffconfig.get('Common','GTType')

                checkIOV(newentry, gttype, isOnline, passwdfile)

                # add the new entry to the collection
                diffconfig.set('AddRecord',newentry.tagName(), newentry.getCfgFormat())

                # write the comment to the file
                cvscomment = ''
                if options.comment != 'NONE':
                    if options.newtag != 'NONE':
                        if (not commentfile.has_option("TagComments",options.newtag)):
                            # this is a comment saved in the central file since associated to a tag
                            commentfile.set("TagComments",options.newtag,options.comment)
                    else:
                        # this comment is added only to the particular scenario file
                        prevcomment = diffconfig.get("Comments", "Changes")
                        diffconfig.set("Comments", "Changes",prevcomment + "<br> - " + options.comment)
                    cvscomment = options.comment

                configfile = open(cfg, 'wb')
                diffconfig.write(configfile)
                configfile.close()
                cvsCommit(cfg,cvscomment)


            # B -> check IOV
            if options.check:
                isOnline = False
                if  diffconfig.get('Common','Environment') != 'offline':
                    isOnline = True
                passwdfile =  diffconfig.get('Common','Passwd')
                gttype =  diffconfig.get('Common','GTType')
                print "--- list IOV: " 
                outputAndStatus = listIov(oldentry.getOraclePfn(isOnline), oldentry.tagName(), passwdfile)
                iovtable = IOVTable()
                iovtable.setFromListIOV(outputAndStatus[1])
                iovtable.printList()

        # 2. Reset the queue
        elif options.reset:

            if options.version == 'NONE':
                print error("***Error:") + " new version not specified, use -v option!"
                sys.exit(1)
            resetQueue(cfg, diffconfig, options.version)

        # 3. Add a new entry to the GT
        else:
            # no old entry is specified: a new tag must be created from command line options
            if options.newtag == 'NONE' or options.newconnect == 'NONE' or options.newaccount == 'NONE' or options.newobject == 'NONE' or options.newrecord == 'NONE'  or options.newleaf == 'NONE':
                print error("***Error:") + " specify <newtag> <newrecord> <newconnect> <newaccount> <newobject> <newleaf> [ <newlabel> ] to create a new entry!"
                sys.exit(1)


            # check that the GT is not already in oracle
            if gtExists(nextGT, gtconnstring, passwdfile):
                print error("***Error: GT: " + nextGT + " is already in oracle: cannot be modified!!!")
                continue

            # create the new entry
            newentry = GTEntry()
            newentry.setEntry( options.newtag, 'Calibration', options.newconnect,
                              options.newaccount, options.newobject, options.newrecord,
                              options.newleaf, options.newlabel)
            # check the tag
            isOnline = False
            if  diffconfig.get('Common','Environment') != 'offline':
                isOnline = True
            passwdfile =  diffconfig.get('Common','Passwd')
            gttype =  diffconfig.get('Common','GTType')
            outputAndStatus = listIov(newentry.getOraclePfn(isOnline), newentry.tagName(), passwdfile)
            if outputAndStatus[0] != 0:
                print ' -----'
                print error("***Error:") + " list IOV failed for tag: " + str(newentry)
                print outputAndStatus[1]
                print ''
                sys.exit(1)
            else:
                iovtable = IOVTable()
                iovtable.setFromListIOV(outputAndStatus[1])
                iovtable.checkConsitency(gttype)
                print "tag check: done"

            diffconfig.set('AddRecord',newentry.tagName(), newentry.getCfgFormat())
                
            print newentry

            # write the file
            configfile = open(cfg, 'wb')
            diffconfig.write(configfile)
            configfile.close()
            cvsCommit(cfg,'new record added')


            # write the comment to the file
            if options.comment != 'NONE':
                if options.newtag != 'NONE':
                    if (not commentfile.has_option("TagComments",options.newtag)):
                        # this is a comment saved in the central file since associated to a tag
                        commentfile.set("TagComments",options.newtag,options.comment)
                else:
                    # this comment is added only to the particular scenario file
                    prevcomment = diffconfig.get("Comments", "Changes")
                    diffconfig.set("Comments", "Changes",prevcomment + "<br> - " + options.comment)




        # write the comment file
        commfile = open(COMMENTFILENAME, 'wb')
        commentfile.write(commfile)
        commfile.close()
        cvsCommit(COMMENTFILENAME, '')
            

        
# TODO:
# 1. leggi da cfg file
# 4. update del cfg file da cvs e il commit dopo la modifica
# 8. meccanismo per rimuovere un record
# 10. shortcuts per connect string: fprep fprod oprep oprod pprod fonline

