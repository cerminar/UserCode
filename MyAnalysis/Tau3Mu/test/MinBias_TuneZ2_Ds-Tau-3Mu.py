# Auto generated configuration file
# using: 
# Revision: 1.303.2.7 
# Source: /cvs_server/repositories/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: MinBias_TuneZ2_7TeV_pythia6_cff.py -s GEN --geometry DB --datatier GEN-SIM-RAW --conditions MC_42_V15B --eventcontent RAWSIM --no_exec
import FWCore.ParameterSet.Config as cms

process = cms.Process('GEN')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic7TeV2011Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100000)
)

# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.303.2.7 $'),
    annotation = cms.untracked.string('MinBias_TuneZ2_7TeV_pythia6_cff.py nevts:1'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    fileName = cms.untracked.string('MinBias_TuneZ2_Ds-Tau-3Mu.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('GEN-SIM-RAW')
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    )
)

# Additional output definition

# Other statements
process.GlobalTag.globaltag = 'START42_V15B::All'

#customized generator settings:
# - load custom decay for tau to 3mu (phase space) and force to this decay
# - modify pythia cards for Ds decay to force Ds->Tau

process.generator = cms.EDFilter("Pythia6GeneratorFilter",
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(7000.0),
    crossSection = cms.untracked.double(71260000000.0),
    maxEventsToPrint = cms.untracked.int32(0),
   
    PythiaParameters = cms.PSet(
        pythiaUESettings = cms.vstring('MSTU(21)=1     ! Check on possible errors during program execution', 
            'MSTJ(22)=2     ! Decay those unstable particles', 
            'PARJ(71)=10 .  ! for which ctau  10 mm', 
            'MSTP(33)=0     ! no K factors in hard cross sections', 
            'MSTP(2)=1      ! which order running alphaS', 
            'MSTP(51)=10042 ! structure function chosen (external PDF CTEQ6L1)', 
            'MSTP(52)=2     ! work with LHAPDF', 
            'PARP(82)=1.832 ! pt cutoff for multiparton interactions', 
            'PARP(89)=1800. ! sqrts for which PARP82 is set', 
            'PARP(90)=0.275 ! Multiple interactions: rescaling power', 
            'MSTP(95)=6     ! CR (color reconnection parameters)', 
            'PARP(77)=1.016 ! CR', 
            'PARP(78)=0.538 ! CR', 
            'PARP(80)=0.1   ! Prob. colored parton from BBR', 
            'PARP(83)=0.356 ! Multiple interactions: matter distribution parameter', 
            'PARP(84)=0.651 ! Multiple interactions: matter distribution parameter', 
            'PARP(62)=1.025 ! ISR cutoff', 
            'MSTP(91)=1     ! Gaussian primordial kT', 
            'PARP(93)=10.0  ! primordial kT-max', 
            'MSTP(81)=21    ! multiple parton interactions 1 is Pythia default', 
            'MSTP(82)=4     ! Defines the multi-parton model'),
        processParameters = cms.vstring('MSEL=1         ! User defined processes', # or put 0 and use next lines for indiv processes 
         #   'MSUB(11)=1     ! Min bias process', 
         #   'MSUB(12)=1     ! Min bias process', 
         #   'MSUB(13)=1     ! Min bias process', 
         #   'MSUB(28)=1     ! Min bias process', 
         #   'MSUB(53)=1     ! Min bias process', 
         #   'MSUB(68)=1     ! Min bias process', 
         #   'MSUB(92)=1     ! Min bias process, single diffractive', 
         #   'MSUB(93)=1     ! Min bias process, single diffractive', 
         #   'MSUB(94)=1     ! Min bias process, double diffractive', 
         #   'MSUB(95)=1     ! Min bias process'
	 #,# D_s decays
       'MDME(818,1)=1    ! D_s+ -> tau nutau',
       'MDME(819,1)=0    ! ',
       'MDME(820,1)=0    ! ',
       'MDME(821,1)=0    ! D_s+ -> phi e nu',
       'MDME(822,1)=0    ! ',
       'MDME(823,1)=0    ! ',
       'MDME(824,1)=0    ! ',
       'MDME(825,1)=0    ! ',
       'MDME(826,1)=0    ! D_s+ -> phi mu nu',
       'MDME(827,1)=0    ! ',
       'MDME(828,1)=0    ! ',
       'MDME(829,1)=0    ! ',
       'MDME(830,1)=0    ! ',
       'MDME(831,1)=0    ! D_s+ -> phi pi',
       'MDME(832,1)=0    ! ',
       'MDME(833,1)=0    ! ',
       'MDME(834,1)=0    ! D_s+ -> phi ro',
       'MDME(835,1)=0    ! ',
       'MDME(836,1)=0    ! ',
       'MDME(837,1)=0    ! ',
       'MDME(838,1)=0    ! ',
       'MDME(839,1)=0    ! ',
       'MDME(840,1)=0    ! ',
       'MDME(841,1)=0    ! ',
       'MDME(842,1)=0    ! ',
       'MDME(843,1)=0    ! ',
       'MDME(844,1)=0    ! ',
       'MDME(845,1)=0    ! ',
       'MDME(846,1)=0    ! ',
       'MDME(847,1)=0    ! D_s+ ->phi K',
       'MDME(848,1)=0    ! ',
       'MDME(849,1)=0    ! ',
       'MDME(850,1)=0    ! '
					),
        parameterSets = cms.vstring('pythiaUESettings', 
            'processParameters')
    ),
				 
				     ExternalDecays = cms.PSet(
	EvtGen = cms.untracked.PSet(
	  operates_on_particles = cms.vint32(431,15), # 15=only tau
	  use_default_decay = cms.untracked.bool(False),
	  decay_table = cms.FileInPath('GeneratorInterface/ExternalDecays/data/DECAY_NOLONGLIFE.DEC'),
	  particle_property_file = cms.FileInPath('GeneratorInterface/ExternalDecays/data/evt.pdl'),
	  user_decay_file = cms.FileInPath('GeneratorInterface/ExternalDecays/data/Ds_tau_mumumu.dec'),
	  list_forced_decays = cms.vstring('Mytau+','Mytau-','MyD_s+','MyD_s-')
	  ),
	parameterSets = cms.vstring('EvtGen')
	),

)

# filter to select events with a Ds
process.Dfilter = cms.EDFilter("PythiaFilter",
       Status = cms.untracked.int32(2),
       MaxEta = cms.untracked.double(3),
       MinEta = cms.untracked.double(-3),
       MinPt = cms.untracked.double(5),
       ParticleID = cms.untracked.int32(431)  #D_s 
   )
#optionally, insert next filter to check all events have tau from Ds
process.taufromDfilter = cms.EDFilter("PythiaFilter",
       Status = cms.untracked.int32(2),
       MaxEta = cms.untracked.double(1000),
       MinEta = cms.untracked.double(-1000),
       MinPt = cms.untracked.double(0),
       ParticleID = cms.untracked.int32(15),  #tau  
       MotherID = cms.untracked.int32(431)    #D_s
   )
# mu from tau: filter used but basically no acceptance cut (one muon only required)
process.mufromtaufilter = cms.EDFilter("PythiaFilter",
       Status = cms.untracked.int32(1),
       MaxEta = cms.untracked.double(2.5),
       MinEta = cms.untracked.double(-2.5),
       MinPt = cms.untracked.double(1.0),
       ParticleID = cms.untracked.int32(13),  #mu  
       MotherID = cms.untracked.int32(15)    #tau
   )

# ask 3 muons in the acceptance

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
    )


process.ProductionFilterSequence = cms.Sequence(process.generator)

# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen*process.Dfilter)#*process.mufromtaufilter)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RAWSIMoutput_step)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path)._seq = process.ProductionFilterSequence * getattr(process,path)._seq 
