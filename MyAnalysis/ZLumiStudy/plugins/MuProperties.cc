/** \class MuProperties
 *
 *  No description available.
 *
 *  $Date: 2012/07/16 13:42:48 $
 *  $Revision: 1.2 $
 */

#include <FWCore/Framework/interface/Frameworkfwd.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include <FWCore/Framework/interface/Event.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Framework/interface/ESHandle.h>

#include <DataFormats/PatCandidates/interface/Muon.h>
#include <Muon/MuonAnalysisTools/interface/MuonEffectiveArea.h>
#include "DataFormats/VertexReco/interface/Vertex.h"

#include <ZZAnalysis/AnalysisStep/interface/CutSet.h>
#include <ZZAnalysis/AnalysisStep/interface/LeptonIsoHelper.h>
#include <ZZAnalysis/AnalysisStep/interface/MCHistoryTools.h>
#include <ZZAnalysis/AnalysisStep/interface/SIPCalculator.h>

#include <vector>
#include <string>

using namespace edm;
using namespace std;
using namespace reco;


class MuProperties : public edm::EDProducer {
 public:
  /// Constructor
  explicit MuProperties(const edm::ParameterSet&);
    
  /// Destructor
  ~MuProperties(){};  

 private:
  virtual void beginJob(){};  
  virtual void produce(edm::Event&, const edm::EventSetup&);
  virtual void endJob(){};

  const edm::InputTag theCandidateTag;
  int sampleType;
  int setup;
  const StringCutObjectSelector<pat::Muon, true> cut;
  const CutSet<pat::Muon> flags;
  SIPCalculator *sipCalculator_;


};


MuProperties::MuProperties(const edm::ParameterSet& iConfig) :
  theCandidateTag(iConfig.getParameter<InputTag>("src")),
  sampleType(iConfig.getParameter<int>("sampleType")),
  setup(iConfig.getParameter<int>("setup")),
  cut(iConfig.getParameter<std::string>("cut")),
  flags(iConfig.getParameter<edm::ParameterSet>("flags"))
{
  sipCalculator_ = new SIPCalculator();
  produces<pat::MuonCollection>();
}


void
MuProperties::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  //--- Get leptons and rho
  edm::Handle<pat::MuonRefVector> muonHandle;
  iEvent.getByLabel(theCandidateTag, muonHandle);

  InputTag theRhoTag = LeptonIsoHelper::getMuRhoTag(sampleType, setup);
  edm::Handle<double> rhoHandle;
  iEvent.getByLabel(theRhoTag, rhoHandle);
  double rho = *rhoHandle;

  edm::Handle<vector<Vertex> >  vertexs;
  iEvent.getByLabel("offlinePrimaryVertices",vertexs);

  //Initialize SIP calculator
  sipCalculator_->initialize(iSetup);


  // Output collection
  auto_ptr<pat::MuonCollection> result( new pat::MuonCollection() );

  for (unsigned int i = 0; i< muonHandle->size(); ++i){
    //---Clone the pat::Muon
    pat::Muon l(*((*muonHandle)[i].get()));


    //--- PF ISO
    float PFChargedHadIso   = l.chargedHadronIso();
    float PFNeutralHadIso   = l.neutralHadronIso();
    float PFPhotonIso       = l.photonIso();
    
    float combRelIsoPF = LeptonIsoHelper::combRelIsoPF(sampleType, setup, rho, l);

    //--- SIP, dxy, dz
    float IP      = fabs(l.dB(pat::Muon::PV3D));
    float IPError = l.edB(pat::Muon::PV3D);
    float SIP     = IP/IPError;
    if(vertexs->size()>0) {
      SIP=sipCalculator_->calculate(l,vertexs->front());
    }

    float dxy = 999.;
    float dz  = 999.;
    const Vertex* vertex = 0;
    if (vertexs->size()>0) {
      vertex = &(vertexs->front());
      dxy = fabs(l.innerTrack()->dxy(vertex->position()));
      dz  = fabs(l.innerTrack()->dz(vertex->position()));
    }

    //--- Trigger matching
    bool HLTMatch = ((!l.triggerObjectMatchesByFilter("hltSingleMu13L3Filtered17").empty())||
		     ((!l.triggerObjectMatchesByFilter("hltSingleMu13L3Filtered13").empty()) && 
		      (l.triggerObjectMatchesByFilter("hltSingleMu13L3Filtered13").at(0).pt()>17)) || 
		     ((!l.triggerObjectMatchesByFilter("hltDiMuonL3PreFiltered5").empty()) && 
		      (l.triggerObjectMatchesByFilter("hltDiMuonL3PreFiltered5").at(0).pt()>17)) || 
		     ((!l.triggerObjectMatchesByFilter("hltDiMuonL3PreFiltered7").empty()) && 
		      (l.triggerObjectMatchesByFilter("hltDiMuonL3PreFiltered7").at(0).pt()>17)));
    //FIXME


    
    
    //--- Embed user variables
    l.addUserFloat("PFChargedHadIso",PFChargedHadIso);
    l.addUserFloat("PFNeutralHadIso",PFNeutralHadIso);
    l.addUserFloat("PFPhotonIso",PFPhotonIso);
    l.addUserFloat("combRelIsoPF",combRelIsoPF);
    l.addUserFloat("SIP",SIP);
    l.addUserFloat("dxy",dxy);
    l.addUserFloat("dz",dz);
    l.addUserFloat("HLTMatch", HLTMatch);
    // l.addUserCand("MCMatch",genMatch); // FIXME

    //--- isPFMuon flag - in old samples, l.isPFMuon() is not functional, so this has to be filled
    //    beforehand with the module PATPFMuonEmbedder.
    if(!l.hasUserFloat("isPFMuon")) {
      l.addUserFloat("isPFMuon",l.isPFMuon());
    }
    
    //--- MC parent code 
    MCHistoryTools mch(iEvent);
    if (mch.isMC()) {
      int MCParentCode = 0;//FIXME: does not work on cmg mch.getParentCode((l.genParticleRef()).get());
      l.addUserFloat("MCParentCode",MCParentCode);
    }

    //--- Check selection cut. Being done here, flags are not available; but this way we 
    //    avoid wasting time on rejected leptons.
    if (!cut(l)) continue;

    //--- Embed flags (ie flags specified in the "flags" pset)
    for(CutSet<pat::Muon>::const_iterator flag = flags.begin(); flag != flags.end(); ++flag) {
     l.addUserFloat(flag->first,int((*(flag->second))(l)));
    }
    
    result->push_back(l);
  }
  iEvent.put(result);
}


#include <FWCore/Framework/interface/MakerMacros.h>
DEFINE_FWK_MODULE(MuProperties);

