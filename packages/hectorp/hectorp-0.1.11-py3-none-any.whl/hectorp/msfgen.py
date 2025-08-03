# -*- coding: utf-8 -*-
#
# msfgen.py
#
# Create msf-json files
#
# Example:
# --------
# msfgen -ji meta.json -di imu.dat -o drone_flight1.msf
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
# Subroutines
#===============================================================================

def open_file(fname):
    """ Simply test if file exists and open it

    Args:
        fname (string) : name of file to be tested
    """

    try:
        fp = open(fname,'r') 
    except IOError: 
        print('Error: File {0:s} cannot be opened for reading.'.format(fname))
        sys.exit()

    return fp

#===============================================================================
# Main program
#===============================================================================


def main():

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Create msf-json file')

    #--- List arguments that can be given 
    parser.add_argument('-ji', action='store', required=True,
                           dest='fname_header',help='json file with metadata')
    parser.add_argument('-di', action='store',required=True,
                           dest='fname_data',help='ASCII data file')
    parser.add_argument('-o', action='store', required=True,
                           dest='fname_out',help='output binary json file')

    args = parser.parse_args()

    #--- parse command-line arguments
    fname_header = args.fname_header
    fname_data   = args.fname_data
    fname_out    = args.fname_out

    #--- Create instance of MSF class
    msf = MSF()

    #--- Read metadata
    fp = open_file(fname_header)
    header = json.loads(fp.read()) 
    fp.close()

    #--- Do we have a valid msf header?
    if msf.verify_header(header) == False:
        sys.exit()

    #--- Already create the arrays we are going to fill
    data = {}
    column_names = header['column_names']
    for i in range(0,len(column_names)):
        data[column_names[i]] = []

    #--- Read the data
    fp = open_file(fname_data) 
    for line in fp:
        if not line.startswith('#'):
            cols = line.split()
            if not len(cols)==len(column_names):
                print('Ooops, number of columns is : {0:d}'.format(len(cols)))
                sys.exit()
            for i in range(0,len(column_names)):
                data[column_names[i]].append(float(cols[i]))

    #--- Write compressed dictionary to file
    msf.write(fname_out,header,data)


if __name__ == "__main__":
    main()
