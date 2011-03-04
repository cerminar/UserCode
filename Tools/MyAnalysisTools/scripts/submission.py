#!/usr/bin/env python

import os
import sys
import commands
import shutil
from optparse import OptionParser, Option, OptionValueError
from ConfigParser import ConfigParser

import FWCore.ParameterSet.Config as cms


def createJobSetups(inputCfg, inputDir, outputDir, outputBaseName, JobName, nFilesPerJob, queue):

    JobName += "/"

    pwd = os.environ["PWD"]

    submissionArea = pwd + "/" + JobName


    outputBaseName = outputBaseName

    if not os.path.exists(JobName):
        print " directory " + JobName + " doesn't exist: creating it"
        os.mkdir(JobName)


    #shutil.copy(inputCfg, "input_cfg.py")
    shutil.copy(inputCfg, JobName + "input_cfg.py")

    os.chdir(submissionArea)
    sys.path.append(submissionArea)
    # list the files in the dir
    castorDir_cmd = "rfdir " + inputDir
    castorDir_out = commands.getstatusoutput(castorDir_cmd)
    if castorDir_out[0] != 0:
        print castorDir_out[1]
        sys.exit(1)

    # check the output dir
    outCastorDir_cmd = "rfdir " + outputDir
    outCastorDir_out = commands.getstatusoutput(outCastorDir_cmd)
    if outCastorDir_out[0] != 0:
        print outCastorDir_out[1]
        sys.exit(1)



    castorFileList = []
    storeDir = inputDir.split("cern.ch/cms")[1]
    #storeDir = "rfio://" + inputDir
    for castorFileLine in castorDir_out[1].split("\n"):
        castorFile = castorFileLine.split()[8]
        if "root" in castorFile:

            #print castorFile
            castorFileList.append(storeDir + castorFile)

    print "Input dir: " + inputDir
    print "# fo files: " + str(len(castorFileList))

    toNFiles = len(castorFileList)
    if len(castorFileList) < nFilesPerJob:
        nFilesPerJob = len(castorFileList)




    from input_cfg import process
    process.source.fileNames = cms.untracked.vstring()

    # do the manipulatio on output and input files
    indexPart = 0
    indexTot  = 0
    indexJob = 0
    for inputFile in castorFileList:

        process.source.fileNames.append(inputFile)
        indexPart+=1
        indexTot+=1


        #print inputFile
        if indexPart == nFilesPerJob or indexTot == toNFiles:
            print "Writing cfg file for job # " + str(indexJob) + "...."
            outputFileName = outputBaseName + "_" + str(indexJob) + ".root"
            process.out.fileName = outputFileName
            # write the previous cfg
            cfgfilename = "expanded_" + str(indexJob) + "_cfg.py"
            # dump it
            expanded = process.dumpPython()
            expandedFile = file(cfgfilename,"w")
            expandedFile.write(expanded)
            expandedFile.close()
            print "Writing submission script for job # " + str(indexJob) + "...."
            scriptname = "SubmissionJob_" +  str(indexJob) + ".csh"
            scriptfile = open(scriptname, 'w')
            scriptfile.write("#!/bin/tcsh\n")
            scriptfile.write("#BSUB -j " + JobName + "\n")
            scriptfile.write("#BSUB -q " + queue + "\n")
            scriptfile.write("setenv runningDir $PWD\n")
            scriptfile.write("cd " +  submissionArea + "\n")
            scriptfile.write("eval `scram runtime -csh`\n")
            scriptfile.write("cp " + cfgfilename + " $runningDir\n")
            scriptfile.write("cd $runningDir\n")
            scriptfile.write("cmsRun " + cfgfilename + "\n")
            scriptfile.write("rfcp " + outputFileName + " " + outputDir + "\n")
            scriptfile.write("rfcp histograms.root " + outputDir + "/histograms_" +  str(indexJob) + ".root\n")
            scriptfile.write("\n")
            scriptfile.close()
            os.chmod(scriptname, 0777)

            indexJob += 1
            # reset the linst of input files    
            process.source.fileNames = cms.untracked.vstring()
        
            indexPart = 0

    os.chdir(pwd)

if __name__     ==  "__main__":
    # --- set the command line options
    parser = OptionParser()

    parser.add_option("-q", "--queue", dest="queue",
                      help="queue", type="str", metavar="<queue>")
    parser.add_option("-s", "--split", dest="split",
                      help="# files per job", type="int", metavar="<split>", default=100)
    parser.add_option("-c", "--cfg", dest="config",
                      help="configuration file", type="str", metavar="<config>")
    parser.add_option("-i", "--input-dir", dest="inputdir",
                      help="input directory", type="str", metavar="<input dir>")
    parser.add_option("-o", "--output-dir", dest="outputdir",
                      help="output directory", type="str", metavar="<output dir>")
    parser.add_option("-j", "--job-name", dest="jobname",
                      help="job name", type="str", metavar="<job name>")
    parser.add_option("-f", "--file-basename", dest="basename",
                      help="file basename", type="str", metavar="<file basename>")

    parser.add_option("--submit", action="store_true",dest="submit",default=False, help="submit the jobs")
    parser.add_option("--file", dest="file",
                      help="submission config file", type="str", metavar="<file>")


    (options, args) = parser.parse_args()


    if options.submit:
        #
        pwd = os.environ["PWD"]

        if options.queue == None:
            print "no queue specified!"
            sys.exit(1)

        for job in args:
            if not os.path.exists(job):
                print "Dir: " + job + " doesn't exist!"
            else:
                os.chdir(job)
                fileList = os.listdir(".")
                for filename  in fileList:
                    if "SubmissionJob" in filename:
                        print "Submitting: " + filename + "..."
                        submit_cmd = "bsub -o tmp.tmp -q " + options.queue + " -J " + job + " " + filename
                        submit_out = commands.getstatusoutput(submit_cmd)
                        print submit_out[1]
                os.chdir(pwd)
                
    elif options.file != None:
        # read a global configuration file
        cfgfile = ConfigParser()
        cfgfile.optionxform = str

        print 'Reading configuration file from ',options.file
        cfgfile.read([options.file ])

        # get the releases currently managed
        listOfJobs = cfgfile.get('General','jobsToSubmit').split(',')
        flag = cfgfile.get('General','selFlag')
        configFile = cfgfile.get('General','configFile')
        filesPerJob = int(cfgfile.get('General','filesPerJob'))
        outputDirBase = cfgfile.get('General','outputDirBase')
        fileBaseName = cfgfile.get('General','fileBaseName')
        queue = cfgfile.get('General','queue')

        for job in listOfJobs:
            inputDir = cfgfile.get(job,'inputDir')
            outputDir = outputDirBase + "/" + flag + "/" + job + "/"
            mkdir_cmd = "rfmkdir -p " + outputDir
            mkdir_out =  commands.getstatusoutput(mkdir_cmd)
            print mkdir_out[1]
            createJobSetups(configFile, inputDir, outputDir, fileBaseName, flag + "_" + job, filesPerJob , queue)
    else:

        if options.queue == None:
            print "no queue specified!"
            sys.exit(1)
        if options.config == None:
            print "no cfg specified!"
            sys.exit(1)
        if options.inputdir == None:
            print "no input dir. specified!"
            sys.exit(1)
        if options.outputdir == None:
            print "no output dir. specified!"
            sys.exit(1)
        if options.jobname == None:
            print "no job name specified!"
            sys.exit(1)
        if options.basename == None:
            print "no fine basename specified!"
            sys.exit(1)

        # -----------------------------------------------------------------------
        inputCfg = options.config
        inputDir = options.inputdir
        outputDir = options.outputdir
        outputBaseName = options.basename
        JobName  = options.jobname
        nFilesPerJob = options.split
        queue = options.queue
        # -----------------------------------------------------------------------

        createJobSetups(inputCfg, inputDir, outputDir, outputBaseName, JobName, nFilesPerJob, queue)

sys.exit(0)
    
