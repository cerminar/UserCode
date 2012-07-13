### ----------------------------------------------------------------------
###
### Example analayzer
###
###----------------------------------------------------------------------


try:
    IsMC
except NameError:
    IsMC = True

try:
    LEPTON_SETUP
except NameError:
    LEPTON_SETUP = 2012 # define the set of effective areas, rho corrections, etc.

try:
    PD
except NameError:
    PD = ""             # "" for MC, "DoubleEle", "DoubleMu", or "MuEG" for data 

try:
    MCFILTER
except NameError:
    MCFILTER = ""


# Get absolute path
import os
PyFilePath = os.environ['CMSSW_BASE'] + "/src/MyAnalysis/ZLumiStudy/test/"

### ----------------------------------------------------------------------
### Standard sequence
### ----------------------------------------------------------------------

#execfile(PyFilePath + "MasterPy/ZZ4lAnalysisPRL2011.py")         # 2011 reference analysis
execfile(PyFilePath + "MasterPy/ZLumiStudyMaster.py")         # 2012 reference analysis


### ----------------------------------------------------------------------
### Replace parameters
### ----------------------------------------------------------------------
process.source.fileNames = cms.untracked.vstring(

#        'root://cmsphys05//data/b/botta/V5_2_0/cmgTuple_H120Fall11_noSmearing.root' #Fall11 H120 for May, 21 synch exercise
#        'root://cmsphys05//data/b/botta/V5_4_0/cmgTuple_H120Fall11_noSmearing.root' #Fall11 H120 for FSR synch
         'root://cmsphys05//data/b/botta/V5_4_0/cmgTuple_H126Summer12.root' #Summer12 H126 for FSR synch        
    )


# from CMGTools.Production.datasetToSource import *
# process.source = datasetToSource(
#    'cmgtools',
#    '/GluGluToHToZZTo4L_M-120_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM/V5/PAT_CMG_V5_2_0/',
#    'patTuple.*.root'
#    )

process.maxEvents.input = -1
#process.options.wantSummary = False


#Add my own cuts
#process.EEMMCand.flags +=
# SIPcut = cms.string("userFloat('SIP4')<4.")


### ----------------------------------------------------------------------
### Output root file (monitoring histograms)
### ----------------------------------------------------------------------
process.TFileService=cms.Service('TFileService',
                                fileName=cms.string('ZLumiStudy.root')
                                )





#Count events with at least 1 Z
# process.ZFiltered = cms.EDFilter("PATCompositeCandidateRefSelector",
#     src = cms.InputTag("ZCand"),
#     cut = cms.string("userFloat('GoodLeptons')")
# )
# process.sStep4 = cms.EDFilter("CandViewCountFilter",
#                               src = cms.InputTag("ZFiltered"),
#                               minNumber = cms.uint32(1)
#                               )
#process.step4 = cms.Path(process.SkimSequence + process.ZFiltered + process.sStep4 )


#Count events with at least 1 ZZ
# process.ZZFiltered = cms.EDFilter("PATCompositeCandidateRefSelector",
#     src = cms.InputTag("ZZCand"),
#     cut = cms.string("userFloat('GoodLeptons')")
# )
# process.sStep5 = cms.EDFilter("CandViewCountFilter",
#                                 src = cms.InputTag("ZZFiltered"),
#                                 minNumber = cms.uint32(1)
#                             )
#process.step5 = cms.Path(process.SkimSequence + process.ZZFiltered + process.sStep5 )


### ----------------------------------------------------------------------
### Analyzer for Trees
### ----------------------------------------------------------------------

TreeSetup = cms.EDAnalyzer("ZTreeMaker",
                                   channel = cms.untracked.string('aChannel'),
                                   CandCollection = cms.untracked.string('aCand'),
                                   fileName = cms.untracked.string('candTree'),
                                   isMC = cms.untracked.bool(IsMC),
                                   sampleType = cms.int32(SAMPLE_TYPE),
                                   setup = cms.int32(LEPTON_SETUP),
                                   skimPaths = cms.vstring(SkimPaths),
                                   PD = cms.string(PD),
                                   MCFilterPath = cms.string(MCFILTER),
                                   skipEmptyEvents = cms.bool(True),
                                   )

process.Z2muTree = TreeSetup.clone()
process.Z2muTree.channel = 'MM'
process.Z2muTree.CandCollection = 'MMCand'



# # Debug
# #Define candidates to be dumped
# process.ZZFiltered = cms.EDFilter("PATCompositeCandidateRefSelector",
#                                   src = cms.InputTag("ZZCand"),
#                                   cut = cms.string("userFloat('isBestCand')")
#                                   )
# ### Select only events with one such candidate
# process.ZZSelection= cms.EDFilter("CandViewCountFilter",
#                                   src = cms.InputTag("ZZFiltered"),
#                                   minNumber = cms.uint32(1)
#                                   )


# process.dumpUserData =  cms.EDAnalyzer("dumpUserData",
#      dumpTrigger = cms.untracked.bool(True),
#      muonSrc = cms.InputTag("appendPhotons:muons"), 
#      electronSrc = cms.InputTag("appendPhotons:electrons"),
#      candidateSrcs = cms.PSet(
#         Zmm   = cms.InputTag("MMCand"),
#         Zee   = cms.InputTag("EECand"),
#         Z     = cms.InputTag("ZCand"),                                          
#         MMMM  = cms.InputTag("MMMMCand"),
#         EEEE  = cms.InputTag("EEEECand"),
#         EEMM  = cms.InputTag("EEMMCand"),
#      )
# )

# if (not IsMC):
#     process.dump = cms.Path(process.ZZFiltered + process.ZZSelection + process.dumpUserData)

# process.p = cms.EndPath( process.Plots4mu + process.Plots4e + process.Plots2e2mu + process.PlotsCRZLL + process.PlotsCRZMM + process.PlotsCRZEE + process.PlotsCRZLLHiSIP + process.PlotsCRZLLHiSIPMM + process.PlotsCRZLLHiSIPKin + process.PlotsCRMMEEss + process.PlotsCREEMMss + process.PlotsCRMMMMss + process.PlotsCREEEEss + process.PlotsCRMMEEos + process.PlotsCREEMMos + process.PlotsCRMMMMos + process.PlotsCREEEEos )
process.trees = cms.EndPath( process.Z2muTree)

