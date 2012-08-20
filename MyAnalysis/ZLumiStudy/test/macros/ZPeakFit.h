
#ifndef ZPeakFit_H
#define ZPeakFit_H

#include "RooGlobalFunc.h"

#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooCategory.h"
#include "RooArgList.h"
#include "RooDataHist.h"
#include "RooFormulaVar.h"
#include "RooHistPdf.h"
#include "RooGenericPdf.h"
#include "RooAddPdf.h"
#include "RooSimultaneous.h"
#include "RooGaussian.h"
#include "RooNLLVar.h"
#include "RooConstVar.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "RooExponential.h"
#include "RooFFTConvPdf.h"
#include "RooWorkspace.h"
#include "RooPlot.h"
#include "TCanvas.h"

class ZPeakFit {
public:
	ZPeakFit(TH1* h);


	RooPlot* fitVExpo();
	RooPlot* fit2VExpo();
	RooPlot* fit2VExpoMin70();
	
	void getResult();


	void save(RooPlot* frame);

private:
	RooRealVar mass;
	RooDataHist data;
	RooFitResult* result;

	RooPlot* fit(RooWorkspace w);
};
#endif