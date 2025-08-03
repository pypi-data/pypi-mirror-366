# observations.py
#
# A simple interface that reads and writes mom-files and stores
# them into a Python class 'observations'.
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
#  31/1/2019  Machiel Bos, Santa Clara
#   1/5/2020  David Bugalho
# 29/12/2021  Machiel Bos, Santa Clara
#  7/ 2/2022  Machiel Bos, Santa Clara
# 10/ 7/2022  Machiel Bos, Santa Clara
#==============================================================================

import pandas as pd
import numpy as np
import os
import sys
import math
import re
from hectorp.control import Control
from hectorp.control import SingletonMeta
from hectorp.msf import MSF
from pathlib import Path

#==============================================================================
# Class definition
#==============================================================================

class Observations(metaclass=SingletonMeta):
    """Class to store my time series together with some metadata
    
    Methods
    -------
    momread(fname)
        read mom-file fname and store the data into the mom class
    momwrite(fname)
        write the momdata to a file called fname
    msfread(fname)
        read msf-file fname and store the data into the mom class
    msfwrite(fname)
        write the msfdata to a file called fname
    genread(fname)
        read general text-file (t,y) fname and store the data into the mom class
    genwrite(fname)
        write the general data (t,y) to a file called fname
    make_continuous()
        make index regularly spaced + fill gaps with NaN's
    """
    
    def __init__(self):
        """This is my time series class
        
        This constructor defines the time series in pandas DataFrame data,
        list of offsets and the sampling period (unit days)
        
        """

        #--- Get control parameters (singleton)
        control = Control()
        try:
            self.verbose = control.params['Verbose']
        except:
            self.verbose = True

        #--- Scale factor
        try:
            self.scale_factor = float(control.params['ScaleFactor'])
        except:
            self.scale_factor = 1.0

        #--- For displaying in output, get Physical and Time unit
        try:
            self.phys_unit = control.params['PhysicalUnit']
        except:
            self.phys_unit = 'unkown'
        try:
            self.time_unit = control.params['TimeUnit']
        except:
            self.time_unit = 'unkown'

        #--- class variables
        self.data = pd.DataFrame()
        self.offsets = []
        self.postseismicexp = []
        self.postseismiclog = []
        self.ssetanh = []
        self.sampling_period = 0.0
        self.F = None
        self.percentage_gaps = None
        self.m = 0
        self.column_name=''

        self.ZIPJSON_KEY = 'base64(zip(o))'


        #--- Read filename with observations and the directory
        try:
            self.datafile = control.params['DataFile']
            self.directory = Path(control.params['DataDirectory'])
            fname = str(self.directory / self.datafile)
        except Exception as e:
            fname = self.datafile = 'None'
            self.directory = ''

        #--- Which format?
        try:
            self.ts_format = control.params['TS_format']
        except:
            self.ts_format = 'mom'

        if self.ts_format == 'mom':  
            if not (self.time_unit=='unknown' or self.time_unit=='days'):
                print('TimeUnit should be days, not {0:s}!'.format(self.time_unit))
                sys.exit()
            if not fname=='None':
                self.momread(fname)
        elif self.ts_format == 'msf':   
            if not (self.time_unit=='unknown' or self.time_unit=='seconds'):
                print('TimeUnit should be seconds, not {0:s}!'.format(self.time_unit))
                sys.exit()
            #--- Are there columns with estimated trajectory models
            try:
                self.use_residuals = control.params['UseResiduals']
            except:
                self.use_residuals = False
            #--- Which column
            try:
                self.column_name = control.params['ColumnName']
            except Exception as e:
                print(e)
                sys.exit()
            if not fname=='None':
                self.msfread(fname)
        elif self.ts_format == 'gen':  
            if not fname=='None':
                self.genread(fname)
        else:
            print('Unknown format: {0:s}'.format(self.ts_format))
            sys.exit()

        #--- Inform the user
        if self.verbose==True:
            print("\nFilename                   : {0:s}".format(fname))
            print("TS_format                  : {0:s}".format(self.ts_format))
            print("TimeUnit                   : {0:s}".format(self.time_unit))
            print("PhysicalUnit               : {0:s}".format(self.phys_unit))
            print("ScaleFactor                : {0:f}".\
                                                    format(self.scale_factor))
            if self.ts_format == 'msf':   
                print("Column Name                : {0:s}".\
                                             format(self.column_name))
                print("Use Residuals              : {0:}".\
                                                    format(self.use_residuals))
            if not fname=='None':
                print("Number of observations+gaps: {0:d}".format(self.m))
                print("Percentage of gaps         : {0:5.1f}".\
			                           format(self.percentage_gaps))



    def create_dataframe_and_F(self,t,obs,mod,period):
        """ Convert np.arrays into Panda DataFrame and create matrix F

        Args:
            t (np.array): array with MJD or sod
            obs (np.array): array with observations
            mod (np.array): array with modelled values
            period (floatt): sampling period (unit is days or seconds)
        """
        
        #--- Store sampling period in this class
        self.sampling_period = period

        #---- Create pandas DataFrame
        self.data = pd.DataFrame({'obs':np.asarray(obs)}, \
                                              index=np.asarray(t))
        if len(mod)>0:
            self.data['mod']=np.asarray(mod)
            
        #--- Create special missing data matrix F
        self.m = len(self.data.index)
        n = self.data['obs'].isna().sum()
        self.F = np.zeros((self.m,n))
        j=0
        for i in range(0,self.m):
            if np.isnan(self.data.iloc[i,0])==True:
                self.F[i,j]=1.0
                j += 1

        #--- Compute percentage of gaps
        self.percentage_gaps = 100.0 * float(n) /float(self.m)



    def momread(self,fname):
        """Read mom-file fname and store the data into the mom class
        
        Args:
            fname (string) : name of file that will be read
        """
        #--- Constants
        TINY = 1.0e-6

        #--- Check if file exists
        if os.path.isfile(fname)==False:
            print('File {0:s} does not exist'.format(fname))
            sys.exit()
        
        #--- Read the file (header + time series)
        t = []
        obs = []
        mod = []
        mjd_old = 0.0
        with open(fname,'r') as fp:
            for line in fp:
                cols = line.split()
                if line.startswith('#')==True:
                    if len(cols)>3:
                        if cols[1]=='sampling' and cols[2]=='period':
                            self.sampling_period = float(cols[3])
                    if len(cols)>2:
                        if cols[0]=='#' and cols[1]=='offset':
                            self.offsets.append(float(cols[2]))
                        elif cols[0]=='#' and cols[1]=='exp':
                            mjd = float(cols[2])
                            T   = float(cols[3])
                            self.postseismicexp.append([mjd,T])
                        elif cols[0]=='#' and cols[1]=='log':
                            mjd = float(cols[2])
                            T   = float(cols[3])
                            self.postseismiclog.append([mjd,T])
                        elif cols[0]=='#' and cols[1]=='tanh':
                            mjd = float(cols[2])
                            T   = float(cols[3])
                            self.ssetanh.append([mjd,T])
                else:
                    if len(cols)<2 or len(cols)>3:
                        print('Found illegal row: {0:s}'.format(line))
                        sys.exit()
                    
                    mjd = float(cols[0])
                    #--- Fill gaps with NaN's
                    if mjd_old>0.0:
                        while abs(mjd-mjd_old-self.sampling_period)>TINY:
                            mjd_old += self.sampling_period
                            t.append(mjd_old)
                            obs.append(np.nan)
                            if len(cols)==3:
                                mod.append(float(np.nan))
                            if mjd_old>mjd-TINY:
                                print('Someting is very wrong here....')
                                print('mjd={0:f}'.format(mjd))
                                sys.exit()
                    t.append(mjd)
                    mjd_old = mjd
                    obs.append(self.scale_factor * float(cols[1]))
                    if len(cols)==3:
                        mod.append(self.scale_factor * float(cols[2]))
        
        self.create_dataframe_and_F(t,obs,mod,self.sampling_period)



    def msfread(self,fname):
        """Read msf-file fname and store the data into the Observation class
        
        Args:
            fname (string) : name of file that will be read
        """

        TINY = 1.0e-7
        msf  = MSF()

        #--- Read header and data
        [header,data] = msf.read(fname)

        #--- Extract required info from header
        self.sampling_period = header['sampling_period']
        column_names = header['column_names']
        if not self.column_name in column_names:
            print('Could not find column {0:s}'.format(self.column_name))
            sys.exit()
        if self.use_residuals==True:
            mod_column_name = 'mod_' + self.column_name
            if not mod_column_name in column_names:
                print('Could not find column {0:s}'.format(mod_column_name))
                sys.exit()
        all_offsets = header['offsets']
        if self.column_name in all_offsets.keys():
            self.offsets = all_offsets[self.column_name]
        else:
            self.offsets = []
             
        #--- Select specified column data
        sod = data['sod']
        if self.use_residuals==True:
            y = np.array(data[self.column_name]) - \
		np.array(data[mod_column_name])
        else:
            y = data[self.column_name]
   
        sod_old = sod[0]
        t = [sod[0]]
        obs = [y[0]]
        for i in range(1,len(sod)):
            while sod[i]-sod_old-self.sampling_period>TINY:
                sod_old += self.sampling_period
                t.append(sod_old)
                obs.append(np.nan)
            if sod_old>sod[i]-TINY:
                 print('Someting is very wrong here....')
                 print(' sod={0:f}'.format(sod[i]))
                 sys.exit()
            t.append(sod[i])
            sod_old = sod[i]
            obs.append(self.scale_factor * y[i])

        #---- Create pandas DataFrame
        self.create_dataframe_and_F(t,obs,[],self.sampling_period)



    def genread(self,fname):
        """Read gen-file fname and store the data into the mom class
        
        Args:
            fname (string) : name of file that will be read
        """
        #--- Constants
        TINY = 1.0e-6

        #--- Check if file exists
        if os.path.isfile(fname)==False:
            print('File {0:s} does not exist'.format(fname))
            sys.exit()

        #--- Read the file (header + time series)
        t = []
        obs = []
        mod = []
        first_observation = True
        with open(fname,'r') as fp:
            for line in fp:
                cols = line.split()
                if line.startswith('#')==True:
                    if len(cols)>3:
                        if cols[1]=='sampling' and cols[2]=='period':
                            self.sampling_period = float(cols[3])
                    if len(cols)>2:
                        if cols[0]=='#' and cols[1]=='offset':
                            self.offsets.append(float(cols[2])) 
                else:
                    if len(cols)<2 or len(cols)>3:
                        print('Found illegal row: {0:s}'.format(line))
                        sys.exit()

                    tt = float(cols[0])
                    #--- Fill gaps with NaN's
                    if not first_observation:
                        while abs(tt-tt_old-self.sampling_period)>TINY:
                            tt_old += self.sampling_period
                            t.append(tt_old)
                            obs.append(np.nan)
                            if len(cols)==3:
                                mod.append(float(np.nan))
                            if tt_old>tt-TINY:
                                print('Someting is very wrong here....')
                                print('tt={0:f}'.format(tt))
                                sys.exit()
                    else:
                        first_observation = False

                    t.append(tt)
                    tt_old = tt
                    obs.append(self.scale_factor * float(cols[1]))
                    if len(cols)==3:
                        mod.append(self.scale_factor * float(cols[2]))

        self.create_dataframe_and_F(t,obs,mod,self.sampling_period)

        
        
    def momwrite(self,fname):
        """Write the momdata to a file called fname
        
        Args:
            fname (string) : name of file that will be written
        """
        #--- Try to open the file for writing
        try:
            fp = open(fname,'w') 
        except IOError: 
           print('Error: File {0:s} cannot be opened for written.'. \
                                                         format(fname))
           sys.exit()
        if self.verbose==True:
            print('--> {0:s}'.format(fname))
        
        #--- Write header
        fp.write('# sampling period {0:f}\n'.format(self.sampling_period))
                
        #--- Write header offsets
        for i in range(0,len(self.offsets)):
            fp.write('# offset {0:10.4f}\n'.format(self.offsets[i]))
        #--- Write header exponential decay after seismic event
        for i in range(0,len(self.postseismicexp)):
            [mjd,T] = self.postseismicexp[i]
            fp.write('# exp {0:10.4f} {1:5.1f}\n'.format(mjd,T))
        #--- Write header logarithmic decay after seismic event
        for i in range(0,len(self.postseismiclog)):
            [mjd,T] = self.postseismiclog[i]
            fp.write('# exp {0:10.4f} {1:5.1f}\n'.format(mjd,T))
        #--- Write header slow slip event
        for i in range(0,len(self.ssetanh)):
            [mjd,T] = self.sshtanh[i]
            fp.write('# tanh {0:10.4f} {1:5.1f}\n'.format(mjd,T))
 
        #--- Write time series
        for i in range(0,len(self.data.index)):
            if not math.isnan(self.data.iloc[i,0])==True:
                fp.write('{0:12.6f} {1:13.6f}'.format(self.data.index[i],\
                                                  self.data.iloc[i,0]))
                if len(self.data.columns)==2:
                    fp.write(' {0:13.6f}\n'.format(self.data.iloc[i,1]))
                else:
                    fp.write('\n')
            
        fp.close()
        


    def msfwrite(self,fname,header={}):
        """Write the msf data to a file called fname
        
        Args:
            fname (string) : name of file that will be written

        """

        #--- Create instance of msf
        msf = MSF()

        #--- Do some checking
        mod_column_name = ''
        if self.datafile=='None' and header=={}:
            print('Both DataFile in ctl-file and header are not specified!')
            sys.exit()
        elif not self.datafile=='None' and not header=={}:
            print('Both DataFile in ctl-file and header are specified!')
            sys.exit()
        elif not self.datafile=='None':
            [header,data] = msf.read(str(self.directory / self.datafile))

        #--- Start with new data dictionary
        data_new = {}
        for column_name in header['column_names']:
            data_new[column_name] = []

        #--- Do we need to add another column?
        if len(self.data.columns)==2:
            mod_column_name = 'mod_' + self.column_name
            if not mod_column_name in header['column_names']:
                header['column_names'].append(mod_column_name)
                data_new[mod_column_name] = []                
        

        #--- Add sod & observations
        j = 0
        for i in range(0,self.m):
            y = self.data.iloc[i,0]
            if not np.isnan(y):
                for k in range(0,len(header['column_names'])):
                    cname = header['column_names'][k]
                    if cname == self.column_name:
                        data_new[cname].append(y)
                    elif cname == mod_column_name:
                        data_new[cname].append(self.data.iloc[i,1])
                    else:
                        data_new[cname].append(data[cname][j])

                #--- row had values, we can increase j for next rount
                j += 1

        #--- Finally, write header + data_new to file
        msf.write(fname,header,data_new)

        
        
    def genwrite(self,fname):
        """Write the gendata to a file called fname
        
        Args:
            fname (string) : name of file that will be written
        """
        #--- Try to open the file for writing
        try:
            fp = open(fname,'w') 
        except IOError: 
           print('Error: File {0:s} cannot be opened for written.'. \
                                                         format(fname))
           sys.exit()
        if self.verbose==True:
            print('--> {0:s}'.format(fname))
        
        #--- Write header
        fp.write('# sampling period {0:f}\n'.format(self.sampling_period))
        fp.write('# TimeUnit     {0:s}\n'.format(self.time_unit))
        fp.write('# PhysicalUnit {0:s}\n'.format(self.phys_unit))
                
        #--- Write header offsets
        for i in range(0,len(self.offsets)):
            fp.write('# offset {0:10.4f}\n'.format(self.offsets[i]))
 
        #--- Write time series
        for i in range(0,len(self.data.index)):
            if not math.isnan(self.data.iloc[i,0])==True:
                fp.write('{0:12.6f} {1:13.6f}'.format(self.data.index[i],\
                                                  self.data.iloc[i,0]))
                if len(self.data.columns)==2:
                    fp.write(' {0:13.6f}\n'.format(self.data.iloc[i,1]))
                else:
                    fp.write('\n')
            
        fp.close()
        


    def show_results(self,output):
        """ add info to json-ouput dict
        """
        
        output['N'] = self.m
        output['gap_percentage'] = self.percentage_gaps 
        output['TimeUnit'] = self.time_unit
        output['PhyiscalUnit'] = self.phys_unit



    def add_offset(self,t):
        """ Add time t to list of offsets
        
        Args:
            t (float): modified julian date or second of day of offset
        """

        EPS   = 1.0e-6
        found = False
        i     = 0
        while i<len(self.offsets) and found==False:
            if abs(self.offsets[i]-t)<EPS:
                found = True
            i += 1
        if found==False:
            self.offsets.append(t)



    def set_NaN(self,index):
        """ Set observation at index to NaN and update matrix F

        Args:
            index (int): index of array which needs to be set to NaN
        """

        self.data.iloc[index,0] = np.nan 
        dummy = np.zeros(self.m)
        dummy[index] = 1.0
        self.F = np.c_[ self.F, dummy ] # add another column to F



    def add_mod(self,xhat):
        """ Add estimated model as column in DataFrame

        Args:
            xhat (array float) : estimated model
        """

        self.data['mod']=np.asarray(xhat)



    def write(self,fname):
        """ Select correct subroutine for writing to file

        Args:
            fname (string): complete name of file
        """

        if self.ts_format=='mom':
            self.momwrite(fname)
        elif self.ts_format=='msf':
            self.msfwrite(fname)
        elif self.ts_format=='gen':
            self.genwrite(fname)
        else:
            print('unknown ts_format: {0:s}'.format(self.ts_format))
            sys.exit()
