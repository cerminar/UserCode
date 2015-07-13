# UserCode

## How to setup a working area

   * setup a CMSSW working area
   
   ```
   scram proj CMSSW CMSSW_7_4_5
   cd CMSSW_7_4_5/src/
   cmsenv
   ```
   
   * clone this repo and setup the area
   
   ```
   git init
   git remote add g-usercode git@github.com:cerminar/UserCode.git
   git fetch g-usercode
   git checkout g-usercode/AlCaMonitoring_74X_v0
   git branch AlCaMonitoring_74X_v0
   git checkout AlCaMonitoring_74X_v0
   ln -s Alca/GT_branches/ .
   scram b -j 4
   ```
   
   * edit the configuration file to point to your AFS based web area:
   
   Snippet of ```GT_branches/pclMonitoring.cfg```:
   
   ```
   [O2OMonitor]
   taskName               = O2OMonitor-dev
   ....
   webArea                = /afs/cern.ch/user/<m>/<myusername>/www/Monitoring-dev/PCLO2O/
   ```
   
   * run the application:
  
   ```
   o2oMonitor.py
   ```
   
