
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/Common/interface/Handle.h"

// #include "DataFormats/VertexReco/interface/Vertex.h"
// #include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"
#include "DataFormats/Candidate/interface/Particle.h"

#include "MyAnalysis/Tau3Mu/src/Histograms.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h" 
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"
//#include "DataFormats/MuonReco/interface/MuonEnergy.h" 

#include "DataFormats/L1Trigger/interface/L1MuonParticleFwd.h"
#include "DataFormats/L1Trigger/interface/L1MuonParticle.h"
#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h"
#include "DataFormats/Common/interface/TriggerResults.h"

#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"

#include "DataFormats/Math/interface/Error.h"
#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/GeometryCommonDetAlgo/interface/GlobalError.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidateFwd.h"

#include "DataFormats/HLTReco/interface/TriggerFilterObjectWithRefs.h"
#include "DataFormats/HLTReco/interface/TriggerRefsCollections.h"
#include "DataFormats/HLTReco/interface/TriggerEventWithRefs.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "FWCore/Common/interface/TriggerNames.h"

#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TLorentzVector.h"
#include <TMath.h>
#include <iostream>
#include <map>

using namespace std;
using namespace reco;


// USEFUL DOCUMENTS:
// https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookGenParticleCandidate#GenPCand
// http://pdg.lbl.gov/mc_particle_id_contents.html


//-----------------------------------------------------------------


// bool sortByPt(const reco::Candidate *part1, const reco::Candidate *part2) {

//   return part1->pt() > part2->pt();
// }

//////////////////////////////////////////////////////////////////
// generically maximum
template <class T> const T& max ( const T& a, const T& b ) {
  return (b<a)?a:b;     // or: return comp(b,a)?a:b; for the comp version
}


//-----------------------------------------------------------------
class TriggerProdAnalysis : public edm::EDAnalyzer {
public:
  explicit TriggerProdAnalysis(const edm::ParameterSet&);
  ~TriggerProdAnalysis();

private:
  virtual void beginJob() ;
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  virtual void endJob() ;


  edm::InputTag l1ExtraParticlesIntag;
  edm::InputTag inputTr;
  edm::InputTag DisplacedVertexTag_;
  edm::InputTag beamSpotTag_;
  edm::InputTag RegTrackCands_;
  edm::InputTag L3muCandLabel_;
  edm::InputTag L3muDisplVtxCandLabel_;
  edm::InputTag L2muCandLabel_;
  edm::InputTag L2muPreFilterCandLabel_ ;
  edm::InputTag mmkVtxLabel;

  HistoVertex *hHLTDiMuonVertex;
  HistoVertex *hHLTTriTrackVertex;

  HistoKinPair *hDiMuL2P,*hDiMuL2FilteredP,*hDiMuL3P,*hDiMuL3FilteredDispVtxP,*hDiMuL3Filtered3VtxP,*hDiMuL3TrkP;

  HistoKin *hL2;
  HistoKin *hL2Filtered;
  HistoKin *hL3;
  HistoKin *hL3FilteredDispVtx;
  HistoKin *hL3Filtered3Vtx;
  HistoKin *hAllTracks;
  HistoKin *hTracksTriVtx;
  HistoKin *hDiMuL2;
  HistoKin *hDiMuL2Filtered;
  HistoKin *hDiMuL3;
  HistoKin *hDiMuL3FilteredDispVtx;
  HistoKin *hDiMuL3Filtered3Vtx;
  HistoKin *hDiMuL3Trk;

  TH1F *hNVtxMuMuTrk;
  TH1F *hNVtxMuMu;
  TH1F *hNRegTracks;
  TH1F *hNL3Muons;
  TH1F *hNL2Muons;

  TH1F *hL2DxyB,*hL2DzB, *hL2DxySigB;
  TH1F *hL2DxyA,*hL2DzA, *hL2DxySigA;

  int counter;
  int countInAccept;
  int counterMoreThan3Muons;
  int counterMoreThanOneds;
  int counterTaus;

  bool debug;

};

//
// constants, enums and typedefs
//
//

TriggerProdAnalysis::TriggerProdAnalysis(const edm::ParameterSet& iConfig) {

  counter = 0;
  countInAccept = 0;
  counterMoreThan3Muons = 0;
  counterMoreThanOneds = 0;
  counterTaus = 0;

  l1ExtraParticlesIntag = iConfig.getUntrackedParameter<edm::InputTag>("l1ExtraParticles",
								       edm::InputTag("l1extraParticles",""));

  inputTr               = iConfig.getUntrackedParameter<edm::InputTag>("TriggerResults",
								       edm::InputTag("TriggerResults", "", "HLTX"));

  DisplacedVertexTag_   = iConfig.getUntrackedParameter<edm::InputTag>("diMuDisplacedVertex",
								       edm::InputTag("hltDisplacedmumuFilterDoubleMuTau2Mu"));

  L3muDisplVtxCandLabel_ = iConfig.getUntrackedParameter<edm::InputTag>("diMuDisplacedVertexFiltLabel",
									edm::InputTag("hltDisplacedmumuFilterTauTo2Mu::HLTX"));

  beamSpotTag_          = iConfig.getUntrackedParameter<edm::InputTag>("beamSpot",
								       edm::InputTag("hltOnlineBeamSpot::HLTX"));

  L3muCandLabel_        = iConfig.getUntrackedParameter<edm::InputTag>("l3MuonCands",
								       edm::InputTag("hltL3MuonCandidates::HLTX"));

  RegTrackCands_        = iConfig.getUntrackedParameter<edm::InputTag>("tracks",
								       edm::InputTag("hltTau3MuAllTracks::HLTX"));

  L2muCandLabel_        = iConfig.getUntrackedParameter<edm::InputTag>("l2MuonCands",
								       edm::InputTag("hltL2MuonCandidates::HLTX"));

  mmkVtxLabel           = iConfig.getUntrackedParameter<edm::InputTag>("mmkVtxLabel",
								       edm::InputTag("hltTau3MuMuMuTkFilter::HLTX"));

  debug                 = iConfig.getUntrackedParameter<bool>("debug", false);

  L2muPreFilterCandLabel_ = iConfig.getUntrackedParameter<edm::InputTag>("diMuL2FilterLabel",
								       edm::InputTag("hltDimuon0or33L2PreFiltered0::HLTX"));
}

TriggerProdAnalysis::~TriggerProdAnalysis() {}


//
// member functions
//

// ------------ method called to for each event  ------------
void TriggerProdAnalysis::analyze(const edm::Event& ev, const edm::EventSetup& iSetup) {
  float weight = 1.;

  // ------------------------------------------------------------------------------------------------
  // trigger analysis


  // some counters/flags from trigger info
  int nL1Muons=0;
  int nL1MuonsPt3p5=0;
  int nL1MuonsPt5=0;
  bool tau3MuTrig = false;
  bool tau2MuPixTrack = false;
  bool tau2MuRegionalPixTrack = false;
  bool tau2MuRegionalPixTrackTight = false;


  // count number of L1 Muons at correct BX
  // no matching to reco by now. it will require some attention for multiples match, and the phi at MS2
  /*
  edm::Handle<l1extra::L1MuonParticleCollection> l1Muon; 
  ev.getByLabel(l1ExtraParticlesIntag, l1Muon);

  for(l1extra::L1MuonParticleCollection::const_iterator it=l1Muon->begin(); it!=l1Muon->end(); it++){
    if (it->bx()==0){             
      double l1pt=it->et();
      //double eta=it->eta();
      //double phi=it->phi();
      //double charge=it->charge();
      nL1Muons++;
      if (l1pt>=3.5) nL1MuonsPt3p5++;
      if (l1pt>=5.0) nL1MuonsPt5++;
    }
  }
  if(debug) cout<<"Found "<<nL1Muons<<" L1 Muons"<<endl;
*/
  // check fired HLT paths
  edm::Handle<edm::TriggerResults> hltresults;
  ev.getByLabel(inputTr, hltresults);

  if (hltresults.isValid()) {
    const edm::TriggerNames TrigNames_ = ev.triggerNames(*hltresults);
    const int ntrigs = hltresults->size();
    for (int itr=0; itr<ntrigs; itr++){
      TString trigName=TrigNames_.triggerName(itr);
      if(debug) cout<<"Found HLT path "<< trigName<<endl;
      if (!hltresults->accept(itr)) continue;
      if(debug) cout << " accepted" << endl;
      // TString trigName=TrigNames_.triggerName(itr);

      // cout<<"Found HLT path "<< trigName<<endl;
      if(trigName=="HLT_Tau2Mu_L2MuonCandidates") tau3MuTrig=true;
       }
  }
  else
    { 
      cout<<"Trigger results not found"<<endl;
    }
  
  if (!tau3MuTrig) return;
  // Trigger products analysis

  // get displaced vertices formed by 2 L3 muons
  reco::VertexCollection displacedVertexColl;
  edm::Handle<reco::VertexCollection> displacedVertexCollHandle;
  bool foundVertexColl = ev.getByLabel(DisplacedVertexTag_, displacedVertexCollHandle);
  if(foundVertexColl) displacedVertexColl = *displacedVertexCollHandle;

 // get beam spot
  reco::BeamSpot vertexBeamSpot;
  edm::Handle<reco::BeamSpot> recoBeamSpotHandle;
  ev.getByLabel(beamSpotTag_,recoBeamSpotHandle);
  vertexBeamSpot = *recoBeamSpotHandle;

  hNVtxMuMu->Fill(displacedVertexColl.size());

  // loop over vertex collection
  for(reco::VertexCollection::iterator it = displacedVertexColl.begin(); it!= displacedVertexColl.end(); it++){
          reco::Vertex displacedVertex = *it;


	  float normChi2 = displacedVertex.normalizedChi2();
	  double vtxProb = 0.0;
	  if( (displacedVertex.chi2()>=0.0) && (displacedVertex.ndof()>0) ) vtxProb = TMath::Prob(displacedVertex.chi2(), displacedVertex.ndof() );


	  reco::Vertex::Point vpoint=displacedVertex.position();
	  //translate to global point, should be improved
	  GlobalPoint secondaryVertex (vpoint.x(), vpoint.y(), vpoint.z());

	  reco::Vertex::Error verr = displacedVertex.error();
	  // translate to global error, should be improved
	  GlobalError err(verr.At(0,0), verr.At(1,0), verr.At(1,1), verr.At(2,0), verr.At(2,1), verr.At(2,2) );

	  GlobalPoint displacementFromBeamspot( -1*((vertexBeamSpot.x0() -  secondaryVertex.x()) +
						    (secondaryVertex.z() - vertexBeamSpot.z0()) * vertexBeamSpot.dxdz()),
						-1*((vertexBeamSpot.y0() - secondaryVertex.y())+
						    (secondaryVertex.z() - vertexBeamSpot.z0()) * vertexBeamSpot.dydz()), 0);
        


          float lxy = displacementFromBeamspot.perp();
          float lxyerr = sqrt(err.rerr(displacementFromBeamspot));
        
	  float significance = lxy/lxyerr;

	  //calculate the angle between the decay length and the mumu momentum
	  Vertex::Point vperp(displacementFromBeamspot.x(),displacementFromBeamspot.y(),0.);
	  math::XYZTLorentzVectorD  p = displacedVertex.p4(0.);   
	  math::XYZVector pperp(p.x(),p.y(),0.);
	  cout << "----- Mass: " << p.mass() << " pt: " << p.Pt() << endl;
	  float cosAlpha = vperp.Dot(pperp)/(vperp.R()*pperp.R());

	  // FIXME: add plots lxy and signif vs Pt Ds
	  hHLTDiMuonVertex->Fill(normChi2, vtxProb, lxy, significance, 0, cosAlpha, p.mass(), weight);

  }

  //get all l2 mu cands
  edm::Handle<RecoChargedCandidateCollection> l2mucands;
  ev.getByLabel (L2muCandLabel_,l2mucands);
  if (l2mucands.isValid()){
    int l2s=l2mucands->size();
    hNL2Muons->Fill(l2s);
    for (int i=0; i<l2s; ++i){
      hL2->Fill((*l2mucands)[i].pt(), (*l2mucands)[i].eta(), (*l2mucands)[i].phi(), 0, weight);
      double DxyL2=(*l2mucands)[i].track()->dxy(vertexBeamSpot);
      double DxyEL2=(*l2mucands)[i].track()->dxyError();
      double DzL2=(*l2mucands)[i].track()->dz(vertexBeamSpot.position());
      hL2DxyB->Fill(DxyL2); hL2DzB->Fill(DzL2); hL2DxySigB->Fill(fabs(DxyL2/DxyEL2));
    }

    if (l2s>=2){
      TLorentzVector mu1p4=TLorentzVector((*l2mucands)[0].px(),(*l2mucands)[0].py(),(*l2mucands)[0].pz(),(*l2mucands)[0].energy());
      TLorentzVector mu2p4=TLorentzVector((*l2mucands)[1].px(),(*l2mucands)[1].py(),(*l2mucands)[1].pz(),(*l2mucands)[1].energy());
      TLorentzVector DiMu = mu1p4+mu2p4;
      double DiMuMass=(mu1p4+mu2p4).M();
      hDiMuL2->Fill(DiMu.Pt(),DiMu.Eta(),DiMu.Phi(),DiMu.M(),weight);
      hDiMuL2P->Fill(mu1p4.Pt(), mu2p4.Pt(), mu1p4.DeltaPhi(mu2p4),fabs(mu1p4.Eta()-mu2p4.Eta()), mu1p4.DeltaR(mu2p4),DiMu.M(),weight);

      cout<<endl;
      cout<<"Found L2 muons with mass "<<DiMuMass<<endl;
    }
  }

  // get the l2 candidates passing the prefilter
  edm::Handle<trigger::TriggerFilterObjectWithRefs> l2mufilt;
  ev.getByLabel(L2muPreFilterCandLabel_ ,l2mufilt);
  if (l2mufilt.isValid()){
    std::vector<RecoChargedCandidateRef> tr;
    l2mufilt->getObjects(trigger::TriggerMuon, tr);

    for (uint i=0; i<tr.size(); ++i){
      hL2Filtered->Fill(tr[i]->pt(), tr[i]->eta(), tr[i]->phi(), 0, weight);
      double DxyL2=tr[i]->track()->dxy(vertexBeamSpot);
      double DxyEL2=tr[i]->track()->dxyError();
      double DzL2=tr[i]->track()->dz(vertexBeamSpot.position());
      hL2DxyA->Fill(DxyL2); hL2DzA->Fill(DzL2); hL2DxySigA->Fill(fabs(DxyL2/DxyEL2));
    }
   
    if (tr.size()>=2){

      double DiMuMass=(tr[0]->p4()+tr[1]->p4()).mass();
      hDiMuL2Filtered->Fill((tr[0]->p4()+tr[1]->p4()).pt(),(tr[0]->p4()+tr[1]->p4()).eta(),(tr[0]->p4()+tr[1]->p4()).phi(),DiMuMass, weight);
      TLorentzVector m1=TLorentzVector(tr[0]->px(),tr[0]->py(),tr[0]->pz(),tr[0]->energy());
      TLorentzVector m2=TLorentzVector(tr[1]->px(),tr[1]->py(),tr[1]->pz(),tr[1]->energy());
      hDiMuL2FilteredP->Fill(m1.Pt(),m2.Pt(),m1.DeltaPhi(m2),fabs(m1.Eta()-m2.Eta()),m1.DeltaR(m2),DiMuMass,weight);
      cout<<"L2 muons passing  " << DiMuMass << endl;
      //      hDiMuInvMass1->Fill(DiMuMass);
    }
  }

  // get all l3 mu candidates
  edm::Handle<RecoChargedCandidateCollection> l3mucands;
  ev.getByLabel (L3muCandLabel_,l3mucands);
  if (l3mucands.isValid()){
    hNL3Muons->Fill(l3mucands->size());
    for (uint i=0; i<l3mucands->size(); ++i){
      hL3->Fill((*l3mucands)[i].pt(), (*l3mucands)[i].eta(), (*l3mucands)[i].phi(), 0, weight);
    }

    if (l3mucands->size()>=2) {
      //for (RecoChargedCandidateCollection::const_iterator mucand1=mucands->begin(), endCand1=mucands->end(); mucand1!=endCand1; ++mucand1) {
      TLorentzVector mu1p4=TLorentzVector((*l3mucands)[0].px(),(*l3mucands)[0].py(),(*l3mucands)[0].pz(),(*l3mucands)[0].energy());
      TLorentzVector mu2p4=TLorentzVector((*l3mucands)[1].px(),(*l3mucands)[1].py(),(*l3mucands)[1].pz(),(*l3mucands)[1].energy());
      TLorentzVector DiMu = mu1p4+mu2p4;
      double DiMuMass=(mu1p4+mu2p4).M();
      hDiMuL3->Fill(DiMu.Pt(),DiMu.Eta(),DiMu.Phi(),DiMu.M(),weight);
      hDiMuL3P->Fill(mu1p4.Pt(), mu2p4.Pt(), mu1p4.DeltaPhi(mu2p4),fabs(mu1p4.Eta()-mu2p4.Eta()), mu1p4.DeltaR(mu2p4),DiMu.M(),weight);
      cout<<endl;
      cout<<"Found L3 muons with mass "<<DiMuMass<<endl;
      //hDiMuInvMass0->Fill(DiMuMass);
    }
  }


  // get the l3 candidates passing the displaced vertex cut
  edm::Handle<trigger::TriggerFilterObjectWithRefs> l3muvtxcands;
  ev.getByLabel(L3muDisplVtxCandLabel_,l3muvtxcands);

  if (l3muvtxcands.isValid()){
    std::vector<RecoChargedCandidateRef> tr;
    l3muvtxcands->getObjects(trigger::TriggerMuon, tr);

    for (uint i=0; i<tr.size(); ++i){
      hL3FilteredDispVtx->Fill(tr[i]->pt(), tr[i]->eta(), tr[i]->phi(), 0, weight);
    }

    if (tr.size()>=2){
      double DiMuMass=(tr[0]->p4()+tr[1]->p4()).mass();
      hDiMuL3FilteredDispVtx->Fill((tr[0]->p4()+tr[1]->p4()).pt(),(tr[0]->p4()+tr[1]->p4()).eta(),(tr[0]->p4()+tr[1]->p4()).phi(),DiMuMass, weight);
      TLorentzVector m1=TLorentzVector(tr[0]->px(),tr[0]->py(),tr[0]->pz(),tr[0]->energy());
      TLorentzVector m2=TLorentzVector(tr[1]->px(),tr[1]->py(),tr[1]->pz(),tr[1]->energy());
      hDiMuL3FilteredDispVtxP->Fill(m1.Pt(),m2.Pt(),m1.DeltaPhi(m2),fabs(m1.Eta()-m2.Eta()),m1.DeltaR(m2),DiMuMass,weight);
      cout<<endl;
      cout<<"Found L3 muons with displaced vertex with mass "<<DiMuMass<<endl;
      //      hDiMuInvMass1->Fill(DiMuMass);
    }
  }

  //all regional reco tracks
  edm::Handle<RecoChargedCandidateCollection> tks;
  ev.getByLabel (RegTrackCands_,tks);
  if (tks.isValid()){
    cout << "All Tracks size " << tks->size() << endl;
    hNRegTracks->Fill(tks->size());
    for (uint i=0; i<tks->size(); ++i){
      hAllTracks->Fill((*tks)[i].pt(),(*tks)[i].eta(),(*tks)[i].phi(),0,weight);
    }
  }


  // get the L3 mu & track candidates passing the hltTau2MuTkMuMuTkFilter 
  edm::Handle<trigger::TriggerFilterObjectWithRefs> dimuAndTrackVtxCands;

  ev.getByLabel(mmkVtxLabel,dimuAndTrackVtxCands);

  if (dimuAndTrackVtxCands.isValid()){

    std::vector<RecoChargedCandidateRef> muons;

    dimuAndTrackVtxCands->getObjects(trigger::TriggerMuon, muons);
    cout << "# of L3 muons: " << muons.size() << endl;
    int ms=muons.size();

    math::XYZTLorentzVectorD  totMom;

    TLorentzVector DiMuMom;
    TLorentzVector TMom;

    for(int n = 0;
	n != ms; ++n) {
      cout << "muon pt " << muons[n]->pt()<< endl;
      hL3Filtered3Vtx->Fill( muons[n]->pt(), muons[n]->eta(), muons[n]->phi(),0,weight);
      totMom=totMom+muons[n]->p4();
    }
    if (ms>=2){
      TLorentzVector m1=TLorentzVector(muons[0]->px(),muons[0]->py(),muons[0]->pz(),muons[0]->energy());
      TLorentzVector m2=TLorentzVector(muons[1]->px(),muons[1]->py(),muons[1]->pz(),muons[1]->energy());
      hDiMuL3Filtered3VtxP->Fill(m1.Pt(),m2.Pt(),m1.DeltaPhi(m2),fabs(m1.Eta()-m2.Eta()),m1.DeltaR(m2),(m1+m2).M(),weight);
      hDiMuL3Filtered3Vtx->Fill((muons[0]->p4()+muons[1]->p4()).pt(),(muons[0]->p4()+muons[1]->p4()).eta(),(muons[0]->p4()+muons[1]->p4()).phi(),(muons[0]->p4()+muons[1]->p4()).mass(),weight);
      DiMuMom=m1+m2;
    }

    std::vector<RecoChargedCandidateRef> tracks;
    dimuAndTrackVtxCands->getObjects(trigger::TriggerTrack, tracks);
    cout << "# of tracks: " << tracks.size() << endl;
    int ts=tracks.size();
    for(int n = 0;
	n != ts; ++n) {
      hTracksTriVtx->Fill(tracks[n]->pt(),tracks[n]->eta(),tracks[n]->phi(),0,weight);
      cout << "track pt " << tracks[n]->pt()<< endl;
      totMom=totMom+tracks[n]->p4();
      if (ts>=1) TMom=TLorentzVector(tracks[0]->px(),tracks[0]->py(),tracks[0]->pz(),tracks[0]->energy()); 
    }

    if (ts>=1 && ms>=2){
      hDiMuL3Trk->Fill(totMom.Pt(),totMom.Eta(),totMom.Phi(),totMom.M(),weight);
      hDiMuL3TrkP->Fill(DiMuMom.Pt(),TMom.Pt(),DiMuMom.DeltaPhi(TMom), fabs(DiMuMom.Eta()-TMom.Eta()), DiMuMom.DeltaR(TMom),(DiMuMom-TMom).M(),weight);
    }
  }
  

  // get displaced vertices formed by 2 L3 muons + Track
  reco::VertexCollection threeTrackVertexColl;
  edm::Handle<reco::VertexCollection> threeTrackVertexCollHandle;
  edm::InputTag  threeTrackVertexTag("hltTau3MuMuMuTkFilter");
  bool found3trkVertexColl = ev.getByLabel(threeTrackVertexTag, threeTrackVertexCollHandle);
  if(found3trkVertexColl) {
    threeTrackVertexColl = *threeTrackVertexCollHandle;
    cout << "#of 3trk vertices: " << threeTrackVertexColl.size() << endl;
    hNVtxMuMuTrk->Fill(threeTrackVertexColl.size(),weight);
    // loop over vertex collection
    for(reco::VertexCollection::iterator it = threeTrackVertexColl.begin(); it!= threeTrackVertexColl.end(); it++){
      reco::Vertex vertex = *it;

      // get vertex position and error to calculate the decay length significance
      //      GlobalPoint secondaryVertex = vertex.position();
      // GlobalError err = vertex.positionError();
      reco::Vertex::Point vpoint=vertex.position();
      //translate to global point, should be improved
      GlobalPoint secondaryVertex (vpoint.x(), vpoint.y(), vpoint.z());

      reco::Vertex::Error verr = vertex.error();
      // translate to global error, should be improved
      GlobalError err(verr.At(0,0), verr.At(1,0), verr.At(1,1), verr.At(2,0), verr.At(2,1), verr.At(2,2) );

      //calculate decay length  significance w.r.t. the beamspot
      GlobalPoint displacementFromBeamspot( -1*((vertexBeamSpot.x0() -secondaryVertex.x()) +
						(secondaryVertex.z() - vertexBeamSpot.z0()) * vertexBeamSpot.dxdz()),
					    -1*((vertexBeamSpot.y0() - secondaryVertex.y())+
						(secondaryVertex.z() -vertexBeamSpot.z0()) * vertexBeamSpot.dydz()), 0);

      float lxy = displacementFromBeamspot.perp();
      float lxyerr = sqrt(err.rerr(displacementFromBeamspot));
      
      // get normalizes chi2
      float normChi2 = vertex.normalizedChi2();
      double vtxProb = 0.0;
      if( (vertex.chi2()>=0.0) && (vertex.ndof()>0) ) vtxProb = TMath::Prob(vertex.chi2(), vertex.ndof() );

      //calculate the angle between the decay length and the mumu momentum
      Vertex::Point vperp(displacementFromBeamspot.x(),displacementFromBeamspot.y(),0.);
      math::XYZTLorentzVectorD  p = vertex.p4(0.);   
      math::XYZVector pperp(p.x(),p.y(),0.);
      cout << "----- Mass: " << p.mass() << " pt: " << p.Pt() << endl;
      float cosAlpha = vperp.Dot(pperp)/(vperp.R()*pperp.R());
      
      hHLTTriTrackVertex->Fill(normChi2, vtxProb, lxy, lxy/lxyerr, 0, cosAlpha,  p.mass(), weight);
      // FIXME: add mass and pt of the 3 tracks
    }		
  }

}

// ------------ method called once each job just before starting event loop  ------------
void TriggerProdAnalysis::beginJob() {
  cout << "begin job" << endl;
  edm::Service<TFileService> fs;

  hHLTDiMuonVertex = new HistoVertex("HLTDiMuonVertex",*fs);
  hHLTTriTrackVertex = new HistoVertex("HLTTriTrackVertex",*fs);
  hL2=new HistoKin("L2Muons",*fs);
  hL2Filtered=new HistoKin("L2MuonsFiltered",*fs);
  hL3=new HistoKin("L3Muons",*fs);

  hL3FilteredDispVtx=new HistoKin("L3MuonsFilteredDispVtx",*fs);
  hL3Filtered3Vtx=new HistoKin("L3MuonsFiltered3Vtx",*fs);
  hAllTracks=new HistoKin("AllRegTracks",*fs);
  hTracksTriVtx=new HistoKin("TracksInVtx",*fs);
  hDiMuL2=new HistoKin("L2DiMuons",*fs);
  hDiMuL2Filtered=new HistoKin("L2DiMuonsFiltered",*fs);
  hDiMuL3=new HistoKin("L3DiMuons",*fs);
  hDiMuL3FilteredDispVtx=new HistoKin("L3DiMuonsFilteredDispVtx",*fs);
  hDiMuL3Filtered3Vtx=new HistoKin("L3DiMuonsFiltered3Vtx",*fs);
  hDiMuL3Trk=new HistoKin("L3DiMuonsTrack",*fs);

  hDiMuL2P=new HistoKinPair("L2DiMuonsPair",0,5,*fs);
  hDiMuL2FilteredP=new HistoKinPair("L2DiMuonsFilteredPair",0,5,*fs);
  hDiMuL3P=new HistoKinPair("L3DiMuonsPair",0,5,*fs);
  hDiMuL3FilteredDispVtxP=new HistoKinPair("L3DiMuonsFilteredDispVtxPair",0,5,*fs);
  hDiMuL3Filtered3VtxP=new HistoKinPair("L3DiMuonsFiltered3VtxPair",0,5,*fs);
  hDiMuL3TrkP=new HistoKinPair("L3DiMuonsTrackPair",0,5,*fs);

  hL2DxyB= fs->make<TH1F>("hL2DxyBeforeFilter", "# Dxy;# Dxy; # events", 250,0,0.5);
  hL2DzB = fs->make<TH1F>("hL2DzBeforeFilter", "# Dz;# Dz; # events", 250,0,0.5);
  hL2DxySigB = fs->make<TH1F>("hL2DxySigBeforeFilter", "# DxySig;# DxySig; # events", 100,0,50);

  hL2DxyA= fs->make<TH1F>("hL2DxyAfterFilter", "# Dxy;# Dxy; # events", 250,0,0.5);
  hL2DzA = fs->make<TH1F>("hL2DzAfterFilter", "# Dz;# Dz; # events", 250,0,0.5);
  hL2DxySigA = fs->make<TH1F>("hL2DxySigAfterFilter", "# DxySig;# DxySig; # events", 100,0,50);

  hNVtxMuMuTrk = fs->make<TH1F>("hNVtxMuMuTrk", "# vertices;# vertices; # events", 50,0,50);
  hNVtxMuMu = fs->make<TH1F>("hNVtxMuMu", "# vertices;# vertices; # events", 50,0,50);
  hNRegTracks = fs->make<TH1F>("hNRegTracks", "# RegTracks;# tracks; # events", 50,0,50);
  hNL3Muons= fs->make<TH1F>("hNL3", "# L3Muons;# muons; # events", 50,0,50);
  hNL2Muons= fs->make<TH1F>("hNL2", "# L2Muons;# muons; # events", 50,0,50);

}


// ------------ method called nce each job just after ending the event loop  ------------
void 
TriggerProdAnalysis::endJob() {
  cout << "Total # events: " << counter << endl;
}



#include "FWCore/Framework/interface/MakerMacros.h"  
DEFINE_FWK_MODULE( TriggerProdAnalysis );
