import os
import sys
from ConfigParser import ConfigParser
from copy import copy
from optparse import OptionParser, Option, OptionValueError
#import coral
#from CondCore.TagCollection import Node,tagInventory,CommonUtils,entryComment
from operator import itemgetter
#import datetime
from datetime import datetime
try:
    from CondCore.Utilities.timeUnitHelper import *
except ImportError:
    print "CondCore.Utilities.timeUnitHelper not found"


# tools for color printout
from color_tools import *

import commands




class GTEntry:
    """
    Object representing every single entry of the GT configuration file. In practice each GTEntry corresponds to an IOV tag.
    """
    def __init__(self, rcdId, tagName):
        self.tag_name = tagName
        self.record_id = rcdId
        return

    @property
    def record(self):
        """
        Return the record
        """
        return self.record_id[0]

    def updateType(self):
        """
        Access the tag category (o2o or manual)
        """
        return self._updateType

    #FIXME: remove
    def tagName(self):
        """
        Return the tag name
        """
        print '[GTEntry::tagName] DEPRECATED'
        return self.tag_name

    def __eq__(self, other):
        """
        Check for identity of the most important parameters 
        """
        return  self.tag_name == other.tag_name and self.record_id == other.record_id

    def __str__(self):
        """
        Prints some minimal info about the tag
        """
        return 'tag: \'' + self.tag_name + "\' " + str(self.record_id)


    def printTag(self):
        print 'Tag: ' + self.tag_name
        return

    
    def rcdID(self):
        """
        Retunrs a RcdId object 
        """
        print '[GTEntry::rcdID] DEPRECATED'
        return self.record_id


class RcdID(tuple):
    """
    Tuple of Record + label used to index the GTEntries in the GT
    """
    def __new__(cls, *args, **kw):
        return tuple.__new__(cls, *args, **kw)

    def __str__(self):
        return "rcd: \'" + tuple.__getitem__(self,0) + "\' label: \'" + tuple.__getitem__(self,1) + "\'"






class GTEntryCollection:
    """This is a collection of globalTag entries ('GTEntries') and as such it represents an entire global tag.
    It contains all the needed information and can be used to read a GT and loop over it.
    See in gtCompare.py for an example on how to use it."""
    def __init__(self,gtName):
        self.gt_name = gtName
        # the actual list of GTEntries
        self._tagList = []
        # mapping by tag: this is a dictionary of the actual idexes of _tagList organized by 'tag'
        self._tagByTag = dict()
        # mapping by record-label: this is a dictionary of the actual indexes of _tagList organized by 'rcdId'
        self._tagByRcdAndLabelId = dict()
        # keeps track of the order in the conf file

        return

    @property
    def size(self):
        """
        Returns the size (= # of entries) of the GT
        """
        return len(self._tagList)
    
    def addEntry(self, tag):
        """
        Insert a new GTEntry in the collection.
        The ENTRY is not added if the same tag or the same RcdId are already in the GT.
        """
        # check that the tagname and/or the rcdId are not yet in the collection
        if tag.tag_name in self._tagByTag or tag.record_id in self._tagByRcdAndLabelId:
            print error("***Error"),"adding entry:", tag
            othertagid = -1
            if tag.tag_name in self._tagByTag:
                othertagid = self._tagByTag[tag.tag_name]
            else:
                othertagid = self._tagByRcdAndLabelId[tag.record_id]
                
            print "     same tag or Record for: ",self._tagList[othertagid]
            print ""
            raise ValueError, "***Error: entry has same tag or RcdId than another one in the collection!" 

        # Actually add the GTEntry to the _tagList
        self._tagList.append(tag)
        # Save the index to use it in the various dictionaries to retrieve the entry by tag/by Rcdid and to preserve the order
        index = len(self._tagList) - 1
        self._tagByTag[tag.tag_name] = index
        self._tagByRcdAndLabelId[tag.record_id] = index

        return

    def getByTag(self, tag):
        """
        Returns the 'GTEntry' matching the 'tag' name in input
        """
        return self._tagList[self._tagByTag[tag]]

    def getByRcdID(self, id):
        """
        Returns the 'GTEntry' matching the RcdId in input
        """
        return self._tagList[self._tagByRcdAndLabelId[id]]

    def hasTag(self, tag):
        return tag in self._tagByTag

    def hasRcdID(self, anid):
        return anid in self._tagByRcdAndLabelId






def getGTCollection(gtName):
    collection = GTEntryCollection(gtName)

    gt_list_cmd = 'conddb list %s' % gtName
    gt_list_out = commands.getstatusoutput(gt_list_cmd)
    if gt_list_out[0] == 0:
        lines = gt_list_out[1].split('\n')
        for line_idx in range(2, len(lines)-1):
            line = lines[line_idx]
            items = line.split()

            label = ''
            if items[2] != '-':
                label = items[2]
            tag = GTEntry(RcdID((items[0], label)), items[4])
            print tag
            collection.addEntry(tag)
    else:
        print '[gtTools::getGTCollection] list GT failed for %s' % gtName
        print  gt_list_out[1]

    return collection


