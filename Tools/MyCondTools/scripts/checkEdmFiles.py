#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
import commands
from stat import *
from ConfigParser import ConfigParser

from datetime import date
from datetime import datetime

import shutil


if __name__     ==  "__main__":
    
    # set the command line options
    parser = OptionParser()
    
    #    parser.add_option("-t", "--globaltag", dest="gt",
    #                      help="Global-Tag", type="str", metavar="<globaltag>")
    #     parser.add_option("-r", "--release", dest="release",
    #                       help="CMSSW release", type="str", metavar="<release>")
    #parser.add_option("--local", action="store_true",dest="local",default=False)

    (options, args) = parser.parse_args()
    #print "OPTIONS: ", options
    #print "ARGS: ", args


    # check that the dir does not yet exist
    releasearea = ''
    try:
    print "Looking for CMSSW environment....",
        releasearea = os.environ["CMSSW_BASE"]
    except:
        print "no release area found"
        sys.exit(1)
        
    topdirname = releasearea + "/src/"

    os.chdir(topdirname)

    
    CONFIGFILE = 'gtValid.cfg'

    if not os.path.isfile(CONFIGFILE):
        print error("*** Error:") + " cfg file: " + CONFIGFILE + " doesn't exist!"
        sys.exit(1)


    diffconfig = ConfigParser()
    diffconfig.optionxform = str

    print 'Reading configuration file from ',CONFIGFILE
    diffconfig.read(CONFIGFILE)


    globaltagsandWfIds = dict()
    if diffconfig.has_section('Tags'):
        globaltagsandWfIds = dict(diffconfig.items('Tags'))

    gts = globaltagsandWfIds.keys()

    
    fileList = os.listdir(topdirname)
    for filename in fileList:
        if os.path.isdir(filename) == True:
            for gt in gts:
                if gt in filename:
                    # list the root files in the directory
                    print "GT: " + gt + " relval: " + globaltagsandWfIds[gt]
                    
                    print filename





    sys.exit(0)












    





    if os.path.exists(topdirname):
            print " directory", topdirname," doesn't exist: creating it"
            os.mkdir(topdirname)

    

    releasearea = os.environ["CMSSW_BASE"]

    # create the top level directory
    today = date.today()
    topdirname = str(today)

    CONFIGFILE = 'gtValid.cfg'

    if not os.path.isfile(CONFIGFILE):
        print error("*** Error:") + " cfg file: " + CONFIGFILE + " doesn't exist!"
        sys.exit(1)

    diffconfig = ConfigParser()
    diffconfig.optionxform = str

    print 'Reading configuration file from ',CONFIGFILE
    diffconfig.read(CONFIGFILE)


    globaltagsandWfIds = dict()
    if diffconfig.has_section('Tags'):
        globaltagsandWfIds = dict(diffconfig.items('Tags'))

    #print globaltagsandWfIds

    # arguments: list of GTS, might be all
    gts = []
    if 'all' in args:
        gts = globaltagsandWfIds.keys()
    else:
        gts = args



    outputvalues = dict()



    outfilename = "loadAllTest_"
    if options.local:
        outfilename = outfilename + "local.out"
    else:
        outfilename = outfilename + "frontier.out"
    
    outfile = open(outfilename,'w')
    outfile.write("Date: " + str(datetime.today()) + "\n")
    print "Date: " + str(datetime.today())
    for gt in gts:
        # reaqd from sqlite file
        loadallscript_local_name = "./test_loadAll_" + gt + "_local.csh"
        loadallscript_frontier_name = "./test_loadAll_" + gt + "_frontier.csh"
        command = ''
        if options.local:
            #print loadallscript_local_name
            command = loadallscript_local_name
        else:
            #print loadallscript_frontier_name
            command = loadallscript_frontier_name

        outandstat = commands.getstatusoutput(command)
        if outandstat[0] != 0:
            print " GT " + gt + " failed load-all test:"
            print outandstat[1]
            outfile.write("GT: " + gt + ": failed!\n")
        else:
            print " GT "  + gt + ": \033[92mOK\033[0m" 
            outfile.write("GT " + gt + ": OK\n")
        outputvalues[gt] =  outandstat[0]

    outfile.close()
    sys.exit(0)
        

    
