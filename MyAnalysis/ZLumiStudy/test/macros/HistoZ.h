#ifndef HistoZ_H
#define HistoZ_H


#include "TH1F.h"
#include "TH2F.h"


#include <iostream>
using namespace std; 

class HistoZ {
public:

  
  HistoZ(std::string name, std::string title) : theName(name), theTitle(title) {
    hMass = new TH1F("Mass_" + theName, theTitle + ";Mass [GeV]; Events", 75,50,125);
    hMass->Sumw2();
  }


  HistoZ() : theName("") {
    hMass = 0;
  }


  HistoZ(std::string name, std::string dir, TFile *file) : theName(name) {
    if(dir != "") {
      dir = dir + "/";
    }

    hMass = (TH1F *) file->Get(TString(dir) + theName+"_hMass");
  }


  void Scale(double scaleFact) {
    if(hMass != 0) hMass->Scale(scaleFact);
  }


  void Write() {
    //if(hMass != 0) 
      hMass->Write();
  }
  
  void Fill(double mass, double weight) {
    hMass->Fill(mass, weight);
  }

  /// Destructor
  virtual ~HistoZ() {}

  // Operations
  TString theName;
  TString theTitle;

  TH1F *hMass;

};


#endif
