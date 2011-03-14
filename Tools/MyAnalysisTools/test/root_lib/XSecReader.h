#ifndef XSecReader_H
#define XSecReader_H

/** \class XSecReader
 *  Reads the Xsection.txt and the Luminosity.txt files which 
 *  store the Xsections for the different MC samples and the luminosity
 *  for the different data samples. 
 *
 *  $Date: 2008/01/11 15:26:10 $
 *  $Revision: 1.3 $
 *  \author G. Cerminara - NEU Boston & INFN Torino
 */

#include <map>

class TString;


class XSecReader {
public:
  /// Constructor
  XSecReader(const TString& xsecFileName, const TString& lumiFileName);

  /// Destructor
  virtual ~XSecReader();
  
  // Operations
  // Get the weight = lumi*xsec*BR/# initial events 
  double getWeight(const TString& sampleName, const TString& epoch,
		   const TString& finalState, const bool dqApplied) const;
  // Get the weight = lumi*xsec*BR/# initial events 
  double getInitNEv(const TString& sampleName, const TString& finalState) const;
  
  double getLuminosity(const TString& epoch, const TString& finalState, const bool dqApplied) const;


  
protected:

private:
  std::map<TString, double> theWeightMapDimu;
  std::map<TString, double> theWeightMapDiem;
  std::map<TString, double> theInitialNEvDiem;
  std::map<TString, double> theInitialNEvDimu;

  std::map<TString, std::map<TString, double> > theLumiMapDQ;
  std::map<TString, std::map<TString, double> > theLumiMapNoDQ;

};
#endif

