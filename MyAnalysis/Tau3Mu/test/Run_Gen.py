import FWCore.ParameterSet.Config as cms

process = cms.Process('GenLevel')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.Services_cff')
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.GlobalTag.globaltag = 'GR_P_V37::All'


process.MessageLogger = cms.Service("MessageLogger",
     cout = cms.untracked.PSet(
         threshold = cms.untracked.string('WARNING')
     ),
     destinations = cms.untracked.vstring('cout')
)

# Source
process.source = cms.Source("PoolSource",
fileNames = cms.untracked.vstring(
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_10_1_If0.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_10_1_N8t.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_10_1_oAu.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_11_1_GYM.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_12_1_1pH.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_13_1_4A7.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_14_1_p6N.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_15_1_8KK.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_16_1_wen.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_17_1_3eP.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_18_1_R5r.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_19_1_88c.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_1_1_1tl.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_1_1_JEN.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_1_1_Pfb.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_1_1_jDk.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_20_1_BQM.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_21_1_PXv.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_22_1_Em3.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_23_1_kEV.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_24_1_xXy.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_25_1_vzK.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_26_1_yfv.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_27_1_LUg.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_28_1_jSg.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_29_1_NRk.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_2_1_cTO.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_2_1_mDQ.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_2_1_yrK.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_30_1_lEM.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_3_1_TbI.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_3_1_fkX.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_4_1_Y5X.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_4_1_sA3.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_5_1_8Kc.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_5_1_lzv.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_5_1_nbS.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_6_1_Fqs.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_6_1_Y80.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_6_1_agm.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_7_1_43M.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_7_1_iQM.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_7_1_kSf.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_8_1_H9U.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_8_1_jbD.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_8_1_tf6.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_9_1_kpZ.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_9_1_sGe.root",
"/store/caf/user/guiducci/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/MinBias_TuneZ2_DsPhiTo2MuPhi_v1/91497683f71fb3fd1629db65b303c81d/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_9_1_wC3.root"
    
#"file:/tmp/fiori/MinBias_TuneZ2_DsPhiTo2MuPhi_2Mu_cff_py_GEN_FASTSIM_HLT_PU_9_1_wC3.root"
#"/store/data/Run2012B/MuOnia/AOD/PromptReco-v1/000/194/315/70FF96EF-E8A1-E111-8B8B-001D09F27003.root"
#"/store/data/Run2012A/MuOnia/AOD/PromptReco-v1/000/190/934/FC8803E0-CE85-E111-AF7C-001D09F34488.root"
    #"/store/data/Run2012A/MuOnia/AOD/PromptReco-v1/000/191/024/98F7ED7D-2C86-E111-AE56-0025901D623C.root"

#
)
)


#process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange('190645:10-190645:110')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(50))

process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.ana = cms.EDAnalyzer('GenAnalysis',

OutFileName=cms.string("OUT_Gen.root"),
HLT_paths = cms.vstring( # noting means passtrough
#"HLT_Dimuon0_Omega_Phi_v3",
#"HLT_Dimuon0_Omega_Phi_v4"
"HLT_Tau2Mu_ItTrack"
),

HLT_process = cms.string("HLT")


)

process.analysisPath = cms.Path(process.ana)