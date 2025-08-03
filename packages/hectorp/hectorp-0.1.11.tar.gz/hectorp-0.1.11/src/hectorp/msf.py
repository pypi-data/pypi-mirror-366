# -*- coding: utf-8 -*-
#
# msf.py
#
# A simple class that helps to read and write msf-files
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
#  19/05/2023  Machiel Bos, Santa Clara
#==============================================================================

import os
import sys
import zlib, json
import base64
#from base64 import b64encode, b64decode

#==============================================================================
# Class definition
#==============================================================================

class MSF():
    """Class to handle msf-files
    """
    
    def __init__(self):
        """ Define some class variables """
        
        self.ZIPJSON_KEY = 'base64(zip(o))'



    def read(self,fname):
        """Read msf-file fname and store the data into the Observation class
        
        Args:
            fname (string) : name of file that will be read
        """

        #--- Check if file exists
        if os.path.isfile(fname)==False:
            print('File {0:s} does not exist'.format(fname))
            sys.exit()

        with open(fname, 'r') as fp:
            json_object = json.load(fp)

        j = self.json_unzip(json_object) 

        header = j['header']
        data   = j['data']

        return [header,data]
        
        
        
    def json_zip(self,j):
        """ Convert dictionary into json -> binary -> base64 string

        Args:
            j (dictionary) : data + metadata we want to store
        
        Return
            base64 string
        """

        j = {
            self.ZIPJSON_KEY: base64.b64encode(
                zlib.compress(
                    json.dumps(j).encode('utf-8')
                )
            ).decode('ascii')
        }

        return j



    def json_unzip(self,j, insist=True):
        """ Unpack a dictionary with a binary string into useable dictionary

        Args:
            j : dictionary with binary string
            insist : option to ignore errors
        
        Return:
            dictionary
        """

        try:
            assert (j[self.ZIPJSON_KEY])
            assert (set(j.keys()) == {self.ZIPJSON_KEY})
        except:
            if insist:
                raise RuntimeError("JSON not in the expected format {"\
				    + str(self.ZIPJSON_KEY) + ": zipstring}")
            else:
                return j

        try:
            j = zlib.decompress(base64.b64decode(j[self.ZIPJSON_KEY]))
        except:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            j = json.loads(j)
        except: 
            raise RuntimeError("Could interpret the unzipped contents")

        return j



    def write(self,fname,header,data):
        """Write the msf data to a file called fname
        
        Args:
            fname (string) : name of file that will be written
            header (dictionary) : metadata
            data (dictionary)   : data
        """

        self.verify_header(header)
        j = {}
        j['header'] = header
        j['data'] = data

        with open(fname, "w") as fp:
            json.dump(self.json_zip(j), fp) 



    def verify_header(self,header):
        """ Verify if the dictionary has all the required variables

        Args:
            header (dictionary)

        Returns:
            True if passed
        """

        #print(header)
        assert 'sampling_period' in header.keys()
        assert 'mjd' in header.keys()
        assert 'column_names' in header.keys()
        assert 'offsets' in header.keys()

        return True
