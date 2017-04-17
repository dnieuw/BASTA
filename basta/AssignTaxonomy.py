#!/usr/bin/env python

import sys
import os
import logging

# Quick'n'Dirty! Change!
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from basta import FileUtils as futils
from basta import TaxTree as ttree
from basta import DBUtils as db



############
#
#   Class for classification
#
####
#   COPYRIGHT DISCALIMER:
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
#   Author: Tim Kahlke, tim.kahlke@audiotax.is
#   Date:   April 2017
#



class Assigner():

    def __init__(self,evalue,alen,ident,num,minimum,lazy,method,directory):
        self.evalue = evalue
        self.alen = alen
        self.identity = ident
        self.num = num
        self.minimum = minimum
        self.lazy = lazy
        self.logger = logging.getLogger()
        self.method = method
        self.directory=directory
        


    def _assign_sequence(self,blast,output,db_file):
        self.logger.info("Initializing taxonomy database")
        tax_lookup = db._init_db(os.path.join(self.directory,"complete_taxa"))
        self.logger.info("Initializing mapping database")
        map_lookup = db._init_db(os.path.abspath(os.path.join(self.directory,db_file)))
        out_fh = open(output,"w")
        self.logger.info("Assigning taxonomies ...")
        for seq_hits in futils.hit_gen(blast,self.alen,self.evalue,self.identity):
            taxa = []
            for seq in seq_hits:
                for hit in seq_hits[seq]:
                    taxon_id = map_lookup.get(hit['id'])
                    if not taxon_id:
                        self.logger.warning("[WARNING] No mapping found for %s in %s" % (hit['id'],db_file))
                        continue
                    tax_string = tax_lookup.get(taxon_id)
                    if not tax_string:
                        self.logger.warning("[WARNING] No taxon found for %d in %s" % (int(taxon_id),os.path.join(self.directory,"complete_taxa")))
                        continue

                    taxa.append(tax_string)
            lca = self._getLCS(taxa)
            out_fh.write("%s\t%s\n" % (seq,lca))
        out_fh.close()



    def _assign_single(self,blast,db_file):
        tax_lookup = db._init_db(os.path.join(self.directory,"complete_taxa"))
        map_lookup = db._init_db(os.path.abspath(os.path.join(self.directory,db_file)))
        taxa = []
        for seq_hits in futils.hit_gen(blast,self.alen,self.evalue,self.identity):
            for seq in seq_hits:
                for hit in seq_hits[seq]:
                    taxon_id = map_lookup.get(hit['id'])
                    if not taxon_id:
                        self.logger.warning("[WARNING] No mapping found for %s in %s" % (hit['id'],db_file))
                        continue
                    tax_string = tax_lookup.get(taxon_id)
                    if not tax_string:
                        self.logger.warning("[WARNING] No taxon found for %d in %s" % (int(taxon_id),os.path.join(self.directory,"complete_taxa")))
                        continue

                taxa.append(tax_string)
        lca = self._getLCS([x for x in taxa if x])
        return lca



    def _assign_multiple(self,blast_dir,out,db_file):
        out_fh = open(output,"w")
        out_fh.write("#File\tLCA\n")
        for bf in os.listdir(blast_dir):
            self.logger.info("- Estimating Last Common Ancestor for file  %s" % (str(bf)))
            lca = _assign_single(os.path.join(blast_dir,bf),db_file)
            out_fh.write("%s\t%s\n" %(bf,lca))
        out_fh.close() 



    def _getLCS(self,l):
        tree = self._getTT(l)
        minimum = 0;
        if self.lazy:
            minimum = min(self.minimum,len(l))
        else:
            minimum = self.minimum
        taxon = tree.lca(minimum,len(l),self.method)
        return taxon


    def _getTT(self,l):
        tt = ttree.TTree()
        for item in l:
            tt.add_taxon(tt.tree,item)
        return tt



    def _get_db(self,n):
        if n == "prot":
            return "prot_mapping.db"
        elif n == "gss":
            return "gss_mapping.db"
        elif n == "gb":
            return "gb_mapping.db"
        elif n == "wgs":
            return "wgs_mapping.db"
        elif n == "est":
            return "est_mapping.db"
        elif n == "pdb":
            return "pdb_mapping.db"
        else:
            print("Unknown type %s" % (n))
            exit(1)
