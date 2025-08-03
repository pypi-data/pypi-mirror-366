# -*- coding: utf-8 -*-
#
# msfdump.py
#
# Create text file from msf-json file
#
# Example:
# --------
# msfdump -i drone_flight1.msf -o data.txt
#
# This file is part of HectorP 0.1.11.
#
# HectorP is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# HectorP is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# HectorP. If not, see <https://www.gnu.org/licenses/>.
#
# 19/5/2023 Machiel Bos, Santa Clara
#
# (c) Copyright 2023 TeroMovigo, all rights reserved.
#===============================================================================

import os
import sys
import argparse
import numpy as np
import json
from hectorp.msf import MSF

#===============================================================================
# Main program
#===============================================================================


def main():

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Dump msf-json file')

    #--- List arguments that can be given 
    parser.add_argument('-i', action='store', required=True,
                           dest='fname_in',help='binary json file')
    parser.add_argument('-jo', action='store', required=True,
                           dest='fname_json_out',help='output json file')
    parser.add_argument('-do', action='store', required=True,
                           dest='fname_data_out',help='output data text file')

    args = parser.parse_args()

    #--- parse command-line arguments
    fname_in       = args.fname_in
    fname_json_out = args.fname_json_out
    fname_data_out = args.fname_data_out

    #--- Create instance of MSF class
    msf = MSF()

    #--- Read file
    [header,data] = msf.read(fname_in)

    #--- Dum Json
    with open(fname_json_out,'w') as fp:
        json.dump(header, fp, indent=4)
    
    #--- Dump data
    fp_out = open(fname_data_out,'w')
    fp_out.write('# sampling period {0:f}\n'.format(header['sampling_period']))
    fp_out.write('#\n# mjd: {0:f}\n'.format(header['mjd']))
    fp_out.write('#\n# Observations\n# ------------\n')
    j = 0
    for i in range(0,len(header['column_names'])):
        if not header['column_names'][i].startswith('mod_'):
            fp_out.write('# {0:d}. {1:s}\n'.format(i+1, \
						    header['column_names'][i]))
            j += 1

    if j<len(header['column_names']):
        fp_out.write('#\n# Models\n# ------\n')
        for i in range(0,len(header['column_names'])):
            if header['column_names'][i].startswith('mod_'):
                fp_out.write('# {0:d}. {1:s}\n'.format(i+1,\
						    header['column_names'][i]))
					       

    if 'Offsets' in header.keys():
        fp_out.write('#\n# Offsets\n# -------\n')
        offsets = header['offsets']
        for cname in offsets.keys():
            i = header['column_names'].index(cname)
            sods = offsets[cname]
            for k in range(0,len(sods)):
                fp_out.write('# {0:d}. {1:f}\n'.format(i,sods[k]))

    fp_out.write('#\n#=========================================' + \
                  		'======================================\n')


    for i in range(0,len(data['sod'])):
        fp_out.write('{0:9.3f}'.format(data['sod'][i]))
        for j in range(1,len(header['column_names'])):
             cname = header['column_names'][j]
             fp_out.write(' {0:11.7f}'.format(data[cname][i]))
        fp_out.write('\n')

    fp_out.close()
    


if __name__ == "__main__":
    main()
