#!/bin/tcsh

source /afs/cern.ch/user/c/cerminar/scripts/gtEnv.csh

cd  ${GT_DIR}/${GT_CMSSW_VERSION}/src
cmsenv;
gtBuild.py -r 44X -s all  --nightly


