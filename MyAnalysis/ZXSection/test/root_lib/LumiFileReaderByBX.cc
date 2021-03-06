
/*
 *  See header file for a description of this class.
 *
 *  $Date: 2011/08/27 12:45:55 $
 *  $Revision: 1.1 $
 *  \author G. Cerminara - INFN Torino
 */

#include "TFile.h"
#include "TTree.h"
#include "LumiFileReaderByBX.h"
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <math.h>

using namespace std;

static const unsigned int NBXMAX = 3650;


LumiFileReaderByBX::LumiFileReaderByBX(const TString& dirBaseName) : theDirBaseName(dirBaseName),
								   cachedRun(-1) {}

LumiFileReaderByBX::~LumiFileReaderByBX(){}


bool LumiFileReaderByBX::readFileForRun(const int run) {
  if(run != cachedRun) {
    // clean the cache
    theLumiByBXMap.clear();
    theLumiTable.clear();
    Long_t runN = run;

    // put together the file name
    TString fileName = theDirBaseName + runN + TString(".csvt");

    cout << "--- read a new file for run: " << runN << endl;


    TString rootFileName = theDirBaseName + runN +  TString(".root");
    // read the file
    if(!readRootFile(rootFileName,run, run+1)) {
      readFileNew(fileName, run, run+1);
      //readFile(fileName, run, run+1);
      convertToRootFile();
    }

    // add to the bins and total integrals
    //FIXME: ???

    
    // reassing the last cached run
    cachedRun = run;

    return true;
  }
  return false;

}


bool LumiFileReaderByBX::checkCache(int run) const {
  if(run != cachedRun) return true;
  return false;
    
}

// Operations
void LumiFileReaderByBX::readFile(const TString& fileName, int runMin, int runMax) {

  cout << "    txt file: " << fileName << endl;

  ifstream file(fileName.Data());
  string line;

  int nLines = 0;

  while (getline(file,line)) {
    if( line == "" || line[0] == '#' || line[0] == 'r'   ) continue; // Skip comments and empty lines
    //cout << line << endl;
    nLines ++;
    
    stringstream linestr;
    linestr << line;

    int run = -1;
    int ls = -1;
    float delLumi = -1;
    float recLumi = -1;
    int bx = -1;
    float bxDelLumi = -1.;
    float bxRecLumi = -1.;

    string cell;
    int cellCounter = 0;
    float ratioRecDel = 1.;

    float sumBxDel = 0;
    float sumBxRec = 0;


    while(getline(linestr, cell, ',')) {
      stringstream cellstream;
      cellstream << cell;
      if(cellCounter == 0) {
	cellstream >> run;
// 	cout << "---------------------------------------------------" << endl;
// 	cout << "run: " << run << endl;
	if(!(runMin == -1 && runMax == -1 ) && !(run >= runMin && run <= runMax)) return;

      } else if(cellCounter == 1) {
	cellstream >> ls;
// 	cout << "---------" << endl;
// 	cout << "ls: " << ls << endl;
	
      }  else if(cellCounter == 2) {
	cellstream >> delLumi;
      } else if(cellCounter == 3) {
	cellstream >> recLumi;
	ratioRecDel = recLumi/delLumi;
      } else if(cellCounter % 2 == 0) { // if pari
	cellstream >> bx;
      } else if(cellCounter % 2 == 1) { // if dispari
	cellstream >> bxDelLumi;
	sumBxDel += bxDelLumi;
	bxRecLumi = ratioRecDel*bxDelLumi;
	sumBxRec += bxRecLumi;
// 	cout << "BX: " << bx << " del luvi: " << bxDelLumi << " rec lumi: " << bxRecLumi << endl;
	theLumiByBXMap[RunLumiBXIndex(run, ls, bx)] = make_pair(bxDelLumi, bxRecLumi);

      }

      cellCounter++;
      
    }
    if(fabs(sumBxRec*23. - recLumi)/recLumi > 0.05) {
      
      cout << "WARNING: ls: " << ls
	   << " sum BX del: " << sumBxDel*23. << " sumBxRec: " << sumBxRec*23.
	   << " total del: " << delLumi << " total rec: " << recLumi << endl;
    }
  }

  // cout << "# lines in the file: " << nLines << endl;
  cout << "File: " << fileName << " # of entries (run,ls) = " << theLumiByBXMap.size() << endl;
  

}



// Operations
void LumiFileReaderByBX::readFileNew(const TString& fileName, int runMin, int runMax) {
  cout << "    txt file: " << fileName << endl;
   
  bool debug = false;

  // open the txt file for a given run
  ifstream file(fileName.Data());
  int theRun = -1;


  // container of vector of lumis by BX for each LS
  vector< vector<float> > lsContainer;


  // loop over lines: each line corresponds to a LS
  int nLines = 0;
  string line;
  while (getline(file,line)) { // loop over lines
    if( line == "" || line[0] == '#' || line[0] == 'r'   ) continue; // Skip comments and empty lines

    if(debug) cout << line << endl;
    
    // count the # of lines
    nLines ++;
    
    stringstream linestr;
    linestr << line;


    // now read the content of the line: each field is separated by a comma and the
    // position determines its meaning
    int run = -1;
    int ls = -1;
    float delLumi = -1;
    float recLumi = -1;
    int bx = -1;
    float bxDelLumi = -1.;
    float bxRecLumi = -1.;
    float ratioRecDel = 1.;
    float sumBxDel = 0;
    float sumBxRec = 0;

    // cells are storing the various values and are separeted by commas
    string cell;
    int cellCounter = 0;

    // vector of lumis values by BX
    // element 0 stores the ratio del/rec the other store the recorded value for each BX
    vector<float> lumiByBx(NBXMAX);
    

    while(getline(linestr, cell, ',')) { // loop over cells
      stringstream cellstream;
      cellstream << cell;

      if(cellCounter == 0) { // this is the "run" field
	cellstream >> run;
	if(debug) {
	  cout << "---------------------------------------------------" << endl;
	  cout << "run: " << run << endl;
	}
	if(!(runMin == -1 && runMax == -1 ) && !(run >= runMin && run <= runMax)) return;
	theRun = run;

      } else if(cellCounter == 1) { // LS field
	cellstream >> ls;
	if(debug) {
	  cout << "---------" << endl;
	  cout << "ls: " << ls << endl;
	}
	// FIXME: there are many 0 in LumiCal2 files...
	if(ls == 0) {
	  cout << "ERROR: lumi 0 found, skipping" << endl;
	  break;
	}
	
      }  else if(cellCounter == 2) { // delivered lumi in this LS
	cellstream >> delLumi;

      } else if(cellCounter == 3) { // recorded lumi in this LS
	cellstream >> recLumi;

	// ratio of del/rec -> this is used to scale all the BX lumis
	ratioRecDel = recLumi/delLumi;
	// store it in the first element of the vector
	lumiByBx[0] = ratioRecDel;
      } else if(cellCounter % 2 == 0) { // even -> BX #
	cellstream >> bx;

      } else if(cellCounter % 2 == 1) { // odd -> del lumi in this BX
	cellstream >> bxDelLumi;
	bxRecLumi = ratioRecDel*bxDelLumi;

	// sum over all the BX in the LS
	sumBxDel += bxDelLumi;
	sumBxRec += bxRecLumi;
	
	if(debug) cout << "BX: " << bx << " del luvi: " << bxDelLumi << " rec lumi: " << bxRecLumi << endl;

	// store it in the vector
	lumiByBx[bx] = bxRecLumi;
      }

      cellCounter++;
    }


    if(ls == 0) {
      cout << "skipping LS 0" << endl;
      continue;
    }
    // now push back the vector with the BX lumis in the LS container
    int lastLumi = lsContainer.size();
    if(debug) cout << "last analyzed LS was: " << lastLumi << " now adding: " << ls << endl;

    // we fill also missing LSs with an empty vector
    for(int nMiss = lastLumi + 1; nMiss <= ls; ++nMiss) {
      if(debug) cout << "  add  empty LS: " << nMiss << endl;
      vector<float> empty;
      lsContainer.push_back(empty);
    }

    // sanity check: compare the sum of the BXs with the integral in the lumi
    // FIXME: is the integral taking into account ONLY the colliding BXs?? (check!)
    if(fabs(sumBxRec*23. - recLumi)/recLumi > 0.05) {
      cout << "WARNING: ls: " << ls
	   << " sum BX del: " << sumBxDel *23.<< " sumBxRec: " << sumBxRec*23.
	   << " total del: " << delLumi << " total rec: " << recLumi << endl;
      // in this case we SKIP the LS so that it won'tbe used for the computation of the 
    } else {
      if(debug)  cout << "add filled LS: " << ls << " new size: " << lsContainer.size() << endl;
      lsContainer[ls - 1] = lumiByBx;
    }

  }

  theLumiTable[theRun] = lsContainer;
  cout << "    run: " << theRun << " # ls: " << lsContainer.size() << endl;

}


bool LumiFileReaderByBX::readRootFile(const TString& fileName, int runMin, int runMax) {

  TFile *file = new TFile(fileName.Data(),"r");

  if(file->IsZombie()) return false;


  cout << "  ROOT file: " << fileName << endl;

  TTree *tree = (TTree*) file->Get("lsTree");
  

  int run = -1;
  int ls = -1;
  float ratio = -1;
  float bxLumiValues[NBXMAX] = {0};
    


  tree->SetBranchAddress("run", &run);
  tree->SetBranchAddress("ls", &ls);
  tree->SetBranchAddress("ratio", &ratio);
  tree->SetBranchAddress("bxValues", bxLumiValues);

  vector< vector<float> > lsContainer(tree->GetEntries());
  for(int entry = 0; entry != tree->GetEntries(); ++entry) {
    tree->GetEntry(entry);
    if(ratio != -1) {
      vector<float> lumiByBx(bxLumiValues,bxLumiValues+NBXMAX );
      lsContainer[ls -1] = lumiByBx;
    } else {
      vector<float> lumiByBx;
      lsContainer[ls -1 ]  = lumiByBx ;
    }

  }

  cout << "   run: " << run << " # ls: " << lsContainer.size() << endl;
  theLumiTable[run] = lsContainer;
  file->Close();
  return true;
}


  
float LumiFileReaderByBX::getDelLumi(const RunLumiIndex& runAndLumi) const {
  return getLumi(runAndLumi).first;
}

float LumiFileReaderByBX::getRecLumi(const RunLumiIndex& runAndLumi) const {
  return getLumi(runAndLumi).second;
}
  
float LumiFileReaderByBX::getAvgInstLumi(const RunLumiIndex& runAndLumi) const {
  return getDelLumi(runAndLumi)/23.;
}

  
float LumiFileReaderByBX::computeAvgInstLumi(float delLumi) const {
  return delLumi/23.;
}



float LumiFileReaderByBX::getDelIntegral(const RunLumiIndex& from, const RunLumiIndex& to) const {
  float sum = 0;
  for(map<RunLumiIndex, pair<float, float> >::const_iterator lumiInfo = theLumiMap.begin();
      lumiInfo != theLumiMap.end();
      ++lumiInfo) {
    if(from < (*lumiInfo).first && (*lumiInfo).first < to) {
      sum += (*lumiInfo).second.first;
    }
  }
  return sum;
}



float LumiFileReaderByBX::getRecIntegral(const RunLumiIndex& from, const RunLumiIndex& to) const {
  float sum = 0;
  for(map<RunLumiIndex, pair<float, float> >::const_iterator lumiInfo = theLumiMap.begin();
      lumiInfo != theLumiMap.end();
      ++lumiInfo) {
    if(from < (*lumiInfo).first && (*lumiInfo).first < to) {
      sum += (*lumiInfo).second.second;
    }
  }
  return sum;
}



pair<float, float> LumiFileReaderByBX::getRecIntegralInLumiBin(float instLumiMin, float instLumiMax) const {
  float sum = 0;
  
  float avgInstDelSum = 0;
  int couter = 0;
  
  for(map<RunLumiIndex, pair<float, float> >::const_iterator lumiInfo = theLumiMap.begin();
      lumiInfo != theLumiMap.end();
      ++lumiInfo) {
//     if((*lumiInfo).first.run() != 163817) continue; //FIXME
    if(computeAvgInstLumi((*lumiInfo).second.first) >= instLumiMin && computeAvgInstLumi((*lumiInfo).second.first) < instLumiMax) {
      
      sum += (*lumiInfo).second.second;
      avgInstDelSum += (*lumiInfo).second.first/23.;
      couter++;
    }
  }
  
  float meanAvgInstDel = avgInstDelSum/couter;
  return make_pair(sum, meanAvgInstDel);
}




pair<float, float> LumiFileReaderByBX::getLumi(const RunLumiIndex& runAndLumi) const {
  if(theLumiMap.find(runAndLumi) != theLumiMap.end()) {
    return (*(theLumiMap.find(runAndLumi))).second;
  } else {
    cout << "Warning: run:ls " << runAndLumi.run() << ":" << runAndLumi.lumiSection() << " not found!" << endl;
  }
  return make_pair(-1,-1);
}

  

//-------------------------------------------------------



  
float LumiFileReaderByBX::getDelLumi(const RunLumiBXIndex& runAndLumiAndBx) const {
  return getLumi(runAndLumiAndBx).first*23.;
}

float LumiFileReaderByBX::getRecLumi(const RunLumiBXIndex& runAndLumiAndBx) const {
  return getLumi(runAndLumiAndBx).second*23.;
}
  
float LumiFileReaderByBX::getAvgInstLumi(const RunLumiBXIndex& runAndLumiAndBx) const {
  return getLumi(runAndLumiAndBx).first;
}


pair<float, float> LumiFileReaderByBX::getLumi(const RunLumiBXIndex& runAndLumiAndBx) const {
  // check which table was filled
  if(theLumiByBXMap.find(runAndLumiAndBx) != theLumiByBXMap.end()) {
    return (*(theLumiByBXMap.find(runAndLumiAndBx))).second;
  } 

  // get the vector of LSs for this run
  map<int, vector< vector<float> > >::const_iterator lsContainer =
    theLumiTable.find(runAndLumiAndBx.run());

  // check if the run is actually found
  if(lsContainer != theLumiTable.end()) { // run exists
    
    if((*lsContainer).second.size() >= runAndLumiAndBx.lumiSection()) { // run contains this LS
      //cout << "r: " << runAndLumiAndBx.run() << " ls: " << runAndLumiAndBx.lumiSection() << " bx: " << runAndLumiAndBx.bx() << endl;
      
      //cout << " # BX: " << (*lsContainer).second[runAndLumiAndBx.lumiSection() - 1].size() << endl;
      if((*lsContainer).second[runAndLumiAndBx.lumiSection() - 1].size() != 0) { // the vector of lumis by BX is filled

	float ratio = (*lsContainer).second[runAndLumiAndBx.lumiSection() - 1][0];
	//cout << "ratio: " << ratio << endl;
	if(ratio != 0 && ratio != -1) {
	  float recLumi = (*lsContainer).second[runAndLumiAndBx.lumiSection() - 1][runAndLumiAndBx.bx()];
	  float delLumi = recLumi/ratio;
	  return make_pair(delLumi, recLumi);
	}
      }
    } 

    
  } 

  cout << "Warning: run:ls " << runAndLumiAndBx.run() << ":" << runAndLumiAndBx.lumiSection() << " not found!" << endl;
  
  return make_pair(-1,-1);
}



float LumiFileReaderByBX::getDelIntegral(const RunLumiBXIndex& from, const RunLumiBXIndex& to) const {
  float sum = 0;
  for(map<RunLumiBXIndex, pair<float, float> >::const_iterator lumiInfo = theLumiByBXMap.begin();
      lumiInfo != theLumiByBXMap.end();
      ++lumiInfo) {
    if(from < (*lumiInfo).first && (*lumiInfo).first < to) {
      sum += (*lumiInfo).second.first;
    }
  }
  return sum;
}



float LumiFileReaderByBX::getRecIntegral(const RunLumiBXIndex& from, const RunLumiBXIndex& to) const {
  float sum = 0;
  for(map<RunLumiBXIndex, pair<float, float> >::const_iterator lumiInfo = theLumiByBXMap.begin();
      lumiInfo != theLumiByBXMap.end();
      ++lumiInfo) {
    if(from < (*lumiInfo).first && (*lumiInfo).first < to) {
      sum += (*lumiInfo).second.second;
    }
  }
  return sum;
}



// pair<float, float> LumiFileReaderByBX::getRecIntegralInLumiBin(float instLumiMin, float instLumiMax) const {
//   float sum = 0;
  
//   float avgInstDelSum = 0;
//   int couter = 0;
  
//   for(map<RunLumiBXIndex, pair<float, float> >::const_iterator lumiInfo = theLumiByBXMap.begin();
//       lumiInfo != theLumiByBXMap.end();
//       ++lumiInfo) {
// //     if((*lumiInfo).first.run() != 163817) continue; //FIXME
//     if(computeAvgInstLumi((*lumiInfo).second.first) >= instLumiMin && computeAvgInstLumi((*lumiInfo).second.first) < instLumiMax) {
      
//       sum += (*lumiInfo).second.second;
//       avgInstDelSum += (*lumiInfo).second.first/23.;
//       couter++;
//     }
//   }
  
//   float meanAvgInstDel = avgInstDelSum/couter;
//   return make_pair(sum, meanAvgInstDel);
// }

TH1F * LumiFileReaderByBX::getRecLumiBins(int nbins, float min, float max) const {
  cout << "Fill the integrated lumi for run " << cachedRun << endl;
  cout << "     # bins: " << nbins << " min: " << min << " max: " << max << endl;
  Long_t runN = cachedRun;
  TString hName = TString("hRec_") + runN;
  TH1F *histo = new TH1F(hName.Data(), "test", nbins, min, max);
  
  // old format
  for(map<RunLumiBXIndex, pair<float, float> >::const_iterator lumiInfo = theLumiByBXMap.begin();
      lumiInfo != theLumiByBXMap.end();
      ++lumiInfo) {
    //    cout << "BX: "  << lumiInfo->first.bx() << " del: " << (*lumiInfo).second.first << " rec: " << (*lumiInfo).second.second << endl;
    //     cout << (*lumiInfo).second.second << endl;
    histo->Fill((*lumiInfo).second.first, (*lumiInfo).second.second*23.);
  }
  
  // new format
  for(map<int, vector< vector<float> > >::const_iterator run = theLumiTable.begin();
      run != theLumiTable.end(); ++run) {
    vector< vector<float> > lsContainer = (*run).second;
    for(vector< vector<float> >::const_iterator bxValues =  lsContainer.begin();
	bxValues != lsContainer.end(); ++bxValues) {
      vector<float> values = (*bxValues);
      if(values.size() != 0) {
	float ratio = values[0];
	for(unsigned int index = 1; index != values.size(); ++index) {
	  float recLumi = values[index];
	  float delLumi = 0;
	  if(ratio != 0) {
	    delLumi = recLumi/ratio;
	  }
	  //cout << "BX: " << index << " del: " << delLumi << " rec: " << recLumi << endl;
	  histo->Fill(delLumi, recLumi*23.);
	}
      }
    }
  }

  return histo;
  


}



void LumiFileReaderByBX::convertToRootFile() const {

   for(map<int, vector< vector<float> > >::const_iterator run = theLumiTable.begin();
       run != theLumiTable.end(); ++run) { // loop over runs

     stringstream str;
     str << theDirBaseName << (*run).first << ".root";
     TString fileName;
     str >> fileName;
     cout << "converting the lumi table to ROOT file: " << fileName << endl;

     TFile rootFile(fileName.Data(),"recreate");
     rootFile.cd();
     TTree *tree = new TTree("lsTree","The tree");
     
     int runn = (*run).first;
     int ls = -1;
     float bxLumiValues[NBXMAX] = {0};
     float ratio = -1;
     
     tree->Branch("run", &runn,"run/I"); 
     tree->Branch("ls", &ls,"ls/I"); 
     tree->Branch("bxValues", bxLumiValues,"bxValues[3650]/F"); 
     tree->Branch("ratio", &ratio,"ratio/F"); 
     

     vector< vector<float> > lsContainer = (*run).second;
     for(vector< vector<float> >::const_iterator bxValues =  lsContainer.begin();
	 bxValues != lsContainer.end(); ++bxValues) { // loop over LSs
       ls = bxValues - lsContainer.begin() + 1;
       ratio = -1;
       bxLumiValues[0] = -1;
       vector<float> values = (*bxValues);
//        cout << values.size() << endl;
       if(values.size() != 0) {
	 
	 ratio = values[0];
	 bxLumiValues[0] = values[0];
	 for(unsigned int index = 1; index != values.size(); ++index) {
	   float recLumi = values[index];
	   //	   float delLumi = recLumi/ratio;
	   bxLumiValues[index] = recLumi;
	   //cout << "BX: " << index << " del: " << delLumi << " rec: " << recLumi << endl;
	   //	   histo->Fill(delLumi, recLumi*23.);
	 }
	 // FIXME: should become a variable size array
	 for(unsigned index = values.size(); index != NBXMAX; ++index) {
	   bxLumiValues[index] = 0;
	 }


       }
       tree->Fill();
     }
     tree->Write();
     rootFile.Close();
   }
   


}
