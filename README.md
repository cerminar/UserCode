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
   git remote add g-usercode git@github.com:cerminar/UserCode.git
   git clone g-usercode AlCaMonitoring_74X_v0
   git checkout AlCaMonitoring_74X_v0
   ln -s Alca/GT_branches/ .
   ```
   
   * edit the configuration file to point to your AFS based web area:
   
   Snippet of ```GT_branches/pclMonitoring.cfg```:
   
   ```
   [O2OMonitor]
   taskName               = O2OMonitor-dev
   ....
   webArea                = /afs/cern.ch/user/<m>/<myusername>/www/Monitoring-dev/PCLO2O/
   ```
   
