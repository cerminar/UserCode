#ifndef RunLumiIndex_H
#define RunLumiIndex_H

/** \class RunLumiIndex
 *  No description available.
 *
 *  $Date: $
 *  $Revision: $
 *  \author G. Cerminara - CERN
 */

class RunLumiIndex {
public:
  /// Constructor
  RunLumiIndex();

  RunLumiIndex(int run, int ls);

  /// Destructor
  virtual ~RunLumiIndex();

  // Operations
  bool operator<(const RunLumiIndex& anIndex) const;

  int run() const;

  int lumiSection() const;

protected:

private:
  
  int theRun;
  int theLS;


};
#endif

