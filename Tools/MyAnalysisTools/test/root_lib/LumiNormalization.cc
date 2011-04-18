
/*
 *  See header file for a description of this class.
 *
 *  $Date: 2011/03/14 18:05:53 $
 *  $Revision: 1.1 $
 *  \author G. Cerminara - NEU Boston & INFN Torino
 */

#include "LumiNormalization.h"

#include <iostream>

#include "TH1F.h"
#include "TFile.h"
#include "TSystem.h"
#include "XSecReader.h"
#include "SampleGroup.h"

using namespace std;



LumiNormalization::LumiNormalization(const TString& xsecFileName, const TString& lumiFileName,
				     const TString& epoch, const TString& finalState,
				     bool dqApplied,
				     const TString& inputDir) : nData(0),
								nMC(0),
								theInputDir(inputDir),
								theEpoch(epoch),
								theFinalState(finalState),
								theNormHistoName("zmass_restricted_1"),
								isDqApplied(dqApplied),
								additionalScale(1.),
								normalizeToZ(true) {

  xsecRead = new XSecReader(xsecFileName, lumiFileName);
  
}




LumiNormalization::~LumiNormalization(){
  delete xsecRead;
}


// Add data to the count of events to be used for data/MC normalization
// the histo used to get the count is zmass_restricted_1
// the default file for this histo is: histos_zzanalysis_data_FINALSTATE.root
void LumiNormalization::addData() {
  TString fileName = theInputDir+"/histos_zzanalysis_data_"+theFinalState+".root";
  addData(fileName);
}


// Add data to the count of events to be used for data/MC normalization
// the histo used to get the count is zmass_restricted_1
// This method allows to specify the name of the file which contains this histo
void LumiNormalization::addData(const TString& filename) {
  FileStat_t buffer;
  if(gSystem->GetPathInfo(filename.Data(),buffer) != 0) {
    cout << "[LumiNormalization]*** Error: Input file: " <<  filename << " doesn't exist!" << endl;
    return;
  }
  TFile file(filename.Data());
  TH1F *hZPeak = (TH1F *) file.Get(theNormHistoName.Data());
  if(hZPeak == 0) {
    cout << "[LumiNormalization]*** Error: histo: " << theNormHistoName << " not valid!" << endl;
    return;
  }
  nData += hZPeak->Integral();
  cout << "# ev. in data is " << nData << endl;
}


// Add MC sample to the count of events to be used for data/MC normalization
// the histo used to get the count is zmass_restricted_1
// the default file for this histo is: theInputDir+"/histos_zzanalysis_mc_"+sampleName+"_"+theFinalState+".root"
void LumiNormalization::addMC(const TString& sampleName) {
  TString fileName = theInputDir+"/histos_zzanalysis_mc_"+sampleName+"_"+theFinalState+".root";
  addMC(sampleName, fileName);
}


void LumiNormalization::addMC(const TString& sampleName, const TString& filename) {
  TFile file(filename.Data());
  TH1F *hZPeak = (TH1F *) file.Get(theNormHistoName.Data());
  double scale =  additionalScale * xsecRead->getWeight(sampleName, theEpoch, theFinalState, isDqApplied);
  double unscIntg = hZPeak->Integral();
  hZPeak->Scale(scale);
  cout << "# ev. in sample " << sampleName << " is: " 
       << unscIntg << " (not scaled) and " 
       << hZPeak->Integral() << " (scaled)" << endl;
  cout << "  # of entries: " << hZPeak->GetEntries() << endl;
  nMC += hZPeak->Integral();
}




double LumiNormalization::getNormalizationFactor() const {
  double ret = 1;
  if(normalizeToZ == true && nData !=0 && nMC != 0) {
    ret = nData/nMC;
  }
//   cout << "Lumi normalization factor: " << ret << endl;
  return ret;
}




double LumiNormalization::getScaleFactor(const TString& sampleName) const {
  if(dataSamples.find(sampleName) != dataSamples.end()) return 1.;
  double zPeakNorm = getNormalizationFactor();
//   zPeakNorm = 1;
//   cout << "[LumiNormalization]***WARNING: overall normaliz. factor set to 1!!!" << endl; // FIXME
  return additionalScale * zPeakNorm *
    xsecRead->getWeight(sampleName, theEpoch, theFinalState, isDqApplied);
}


void LumiNormalization::setAdditionalScale(double scale) {
  additionalScale = scale;
}


void LumiNormalization::normalizeToZPeak(bool doNormalize) {
  normalizeToZ = doNormalize;
}

void LumiNormalization::setNormalizHistoName(const TString& histoname) {
  theNormHistoName = histoname;
}

Number  LumiNormalization::getInitialNEv(const TString& sampleName) const {
  return Number(getScaleFactor(sampleName)*xsecRead->getInitNEv(sampleName, theFinalState),0);
}

void  LumiNormalization::addMC(const vector<TString>& sampleNames) {
  for(vector<TString>::const_iterator name = sampleNames.begin(); name != sampleNames.end();
      ++name) {
    addMC(*name);
  }
}


double LumiNormalization::getLuminosity() const {
  return xsecRead->getLuminosity(theEpoch, theFinalState, isDqApplied);
}


void LumiNormalization::addDataGroup(const SampleGroup& group) {
  vector<TString> samples = group.samples();
  for(vector<TString>::const_iterator sample = samples.begin();
      sample != samples.end(); ++sample) {
    dataSamples.insert(*sample);
  }
}

