import FWCore.ParameterSet.Config as cms

### USAGE:
###    cmsRun fitTrigger_Z.py <scenario>
### scenarios:
###   - data_all:    will fit tnpJPsi_Data.root with bins suitable for the current data
###   - datalike_mc: will fit tnpJPsi_{JPsiMuMu,ppMuX}_Spring10_0.117pb.root MC but
###                  with same config as data

import sys
args = sys.argv[1:]
if (sys.argv[0] == "cmsRun"): args =sys.argv[2:]
scenario = "data_all"
if len(args) > 0: scenario = args[0]
print "Will run scenario ", scenario 

process = cms.Process("TagProbe")

process.load('FWCore.MessageService.MessageLogger_cfi')

process.source = cms.Source("EmptySource")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.TnP_Trigger = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
    NumCPU = cms.uint32(1),
    SaveWorkspace = cms.bool(False),

    InputFileNames = cms.vstring('/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_9_1_1Iu_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_82_2_eSg_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_84_2_jrg_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_85_2_Yoi_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_86_2_spN_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_87_1_7Nl_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_88_1_ll4_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_89_1_RMZ_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_8_1_NYr_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_90_1_Wym_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_91_1_ZsV_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_92_1_F88_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_93_1_oox_sorted_lumi.root',
'/data1/ZLumiStudy/TagAndProbe/TPV0/SingleMu_Run2012B-PromptReco-v1_lumi/tnpZ_Data_94_1_pKE_sorted_lumi.root',
                                 ),
    InputTreeName = cms.string("fitter_tree"),
    InputDirectoryName = cms.string("tpTree"),
    OutputFileName = cms.string("TnP_Z_Trigger_%s.root" % scenario),

    Variables = cms.PSet(
        mass = cms.vstring("Tag-Probe Mass", "50", "130", "GeV/c^{2}"),
        pt     = cms.vstring("Probe p_{T}", "0", "1000", "GeV/c"),
        eta    = cms.vstring("Probe |#eta|", "-2.5", "2.5", ""),
        abseta = cms.vstring("Probe |#eta|", "0", "2.5", ""),
        tag_pt = cms.vstring("Tag p_{T}", "2.6", "1000", "GeV/c"),
    ),

    Categories = cms.PSet(
        Calo = cms.vstring("POG_Glb",  "dummy[pass=1,fail=0]"),
        Glb  = cms.vstring("POG_Glb",  "dummy[pass=1,fail=0]"),
        VBTF = cms.vstring("VBTFLike", "dummy[pass=1,fail=0]"),
        Isol = cms.vstring("MC true",  "dummy[pass=1,fail=0]"),
        DoubleMu17Mu8_Mu17  = cms.vstring("DoubleMu17Mu8_Mu17",  "dummy[pass=1,fail=0]"),
    ),

    PDFs = cms.PSet(
        gaussPlusExpo = cms.vstring(
            "Voigtian::signal(mass, mean[90,80,100], width[2.495], sigma[3,1,20])",
            "Exponential::backgroundPass(mass, lp[0,-5,5])",
            "Exponential::backgroundFail(mass, lf[0,-5,5])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        )
    ),

    Efficiencies = cms.PSet(), # will be filled later
)


#DoubleMu17Mu8_Mu17
# ==================================================================================================
# Here I define the different categories (or BINS) for wich I want to compute the efficiency
# NOTE: when inclusive, I consider min pt > 25 GeV -> this should match what is used in the analysis
triggerName = "DoubleMu17Mu8_Mu17"
minPtCut = 25.
instLumiBins = cms.vdouble()


BARREL_ONLY = cms.PSet(
    pt = cms.vdouble(minPtCut, 100),
    abseta = cms.vdouble( 0, 1.2)
    )

ALL2P1 = cms.PSet(
    pt = cms.vdouble(minPtCut, 100),
    abseta = cms.vdouble( 0, 2.1)
    )

ALL2P4 = cms.PSet(
    pt = cms.vdouble(minPtCut, 100),
    abseta = cms.vdouble( 0, 2.4)
    )

PT_BINS_ALL2P1 = ALL2P1.clone(pt = cms.vdouble(15, 25, 35, 100))
ETA_BINS_ALL2P1 = ALL2P1.clone(abseta = cms.vdouble(0, 1.2, 2.1))


if scenario == "data_all":
    process.TnP_Trigger.binsForMassPlots = cms.uint32(20)

if scenario == "datalike_mc":
    process.TnP_Trigger.InputFileNames = [ "tnpZ_MC.root", ]


ALLBINS=[("all2p1",ALL2P1)]
for (T,M) in [ ("DoubleMu17Mu8_Mu17","Track")]:
        print "--------------"
        print "Trigger: " + T
        print "From: " + M
        for BN,BV in ALLBINS:
            print "   Bin Name: " + BN
            print "   Bins: " + str(BV)
            BINNEDVARS = BV.clone()
            if M == "VBTF_Isol":
                setattr(BINNEDVARS, "VBTF", cms.vstring("pass"))
                setattr(BINNEDVARS, "Isol", cms.vstring("pass"))
            elif M != "Track": 
                setattr(BINNEDVARS, M, cms.vstring("pass"))
            setattr(process.TnP_Trigger.Efficiencies, M+"_To_"+T+"_"+BN, cms.PSet(
                EfficiencyCategoryAndState = cms.vstring(T,"pass"),
                UnbinnedVariables = cms.vstring("mass"),
                BinnedVariables = BINNEDVARS,
                BinToPDFmap = cms.vstring("gaussPlusExpo")
            ))
# for  X,B in ALLBINS:
#     setattr(process.TnP_Trigger.Efficiencies, "Track_To_VBTF_Mu9_"+X, cms.PSet(
#         EfficiencyCategoryAndState = cms.vstring("VBTF","pass","Mu9","pass"),
#         UnbinnedVariables = cms.vstring("mass"),
#         BinnedVariables = B,
#         BinToPDFmap = cms.vstring("gaussPlusExpo")
#     ))
#     setattr(process.TnP_Trigger.Efficiencies, "Track_To_VBTF_Isol_Mu9_"+X, cms.PSet(
#         EfficiencyCategoryAndState = cms.vstring("VBTF","pass","Isol","pass","Mu9","pass"),
#         UnbinnedVariables = cms.vstring("mass"),
#         BinnedVariables = B,
#         BinToPDFmap = cms.vstring("gaussPlusExpo")
#     ))


process.p = cms.Path(
    process.TnP_Trigger
)

f = file('fitTrigger_byLumi_dump.py', 'w')
f.write(process.dumpPython())
f.close()

