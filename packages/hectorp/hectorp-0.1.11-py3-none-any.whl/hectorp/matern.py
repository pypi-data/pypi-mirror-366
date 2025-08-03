# -*- coding: utf-8 -*-
#
# This class implements the Matérn noise model. Eqs. are taken from
# Lilly et al. (2017) "Fractional Brownian motion, the Matérn process, and 
# stochastic modeling of turbulent dispersion", Nonlinear Processes in 
# Geophysics, 24: 481-514 
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
# 18/8/2022 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
import sys
import math
from scipy.special import kv
from hectorp.control import Control

#==============================================================================
# Subroutines
#==============================================================================


class Matern:

    def __init__(self,d_fixed=math.nan):
        """ initialise class
        """

        #--- Get control parameters
        control = Control()

        #--- Remember the d value used to instantiate this class
        self.d_fixed = d_fixed

        #--- Check if 1-phi is given in control file
        try:
            self.lambda_fixed = control.params['lambda_fixed']
        except:
            self.lambda_fixed = math.nan

        #--- Number of noise parameters
        self.Nparam = 2
        if not math.isnan(self.d_fixed):
            self.Nparam -= 1
            alpha_fixed = 2.0*self.d_fixed
            print('alpha fixed to : {0:f}'.format(self.alpha_fixed))
        else:
            alpha_fixed = math.nan

        if not math.isnan(self.lambda_fixed):
            self.Nparam -= 1



    def get_Nparam(self):
        """ Return the number of parameters in GGM noise model
        
        Returns:
            self.Nparam (int) : total number of parameters (free)
        """

        return self.Nparam



    def backward(self,a,b,c,z,F,Fp1):
        """ Compute backward recursion

        Args:
            a,b,c,z (double) : Hypergeometric function 2F1(a,b;c;z)
            Fp1 (double)     : 2F1(a+1,b;c+1;z)

        Returns:
            2F1(a-1,b;c-1;z)
        """

        return ((1.0-c+(b-a)*z)*F + (a*(c-b)*z)*Fp1/c)/(1.0-c)


    
    def create_t(self,m,k,param):
        """ Create first row of covariance matrix of power-law noise
    
        Args:
            m (int) : length of time series
            k (int) : index of param
            param (array float) : spectral index
        
        Returns:
            t (row (m,1)) : first row Toeplitz covariance matrix 
            k_new (int)   : shifted index in param array
        """

        #--- Constant
        EPS = 1.0e-12
        threshold = 100.0

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)
        
        #--- extract parameters to readable variables
        if self.Nparam==0:
            d     = self.d_fixed
            alpha = 2.0*d
            lamba = self.lambda_fixed
            k_new = k
        elif self.Nparam==1:
            if math.isnan(self.alpha_fixed)==True:
                d     = param[k]
                lamba = self.lambda_fixed
            else:
                d     = 0.5*self.alpha_fixed
                lamba = param[k]
            k_new = k+1
        else:
            d     = param[k]
            lamba = param[k+1]
            k_new = k+2
        alpha = 2.0*d

        #--- Constant
        c0 = 2.0/(math.gamma(alpha-0.5) * pow(2.0, alpha-0.5))

        #--- Use Modified Bessel Function, second order
        t[0] = 1.0 #-- check Eq. (62) and set tau=0
        i = 1
        tau = float(i)
        while i<m:
            if tau>threshold/lamba:
                #--- Eq. (61)
                t[i] = c0*math.sqrt(math.pi/2.0)*pow(lamba*tau,alpha-0.5)\
                                                        * math.exp(-lamba*tau)
            else:
                #--- Eq. (60)
                t[i] = c0*pow(lamba*tau,alpha-0.5) * kv(alpha-0.5,lamba*tau)
                
            #--- Next tau
            i += 1
            tau = float(i)

        return t, k_new 



    def penalty(self,k,param):
        """ Computes penalty for power-law noise

        Args:
            k (int) : index of param
            param (array float) : spectral index
        
        Returns:
            penalty (float)
        """

        LARGE = 1.0e8
        penalty = 0.0 

        if self.Nparam==0:
            penalty = 0.0 
        else:
            if self.Nparam==2 or (self.Nparam==1 and \
                                        math.isnan(self.alpha_fixed))==True:
                if param[k]>0.7499:
                    penalty += (param[k]-0.7499)*LARGE
                    param[k] = 0.7499
                elif param[k]<0.251:
                    penalty += (0.251-param[k])*LARGE
                    param[k] = 0.251
            if self.Nparam==2 or (self.Nparam==1 and \
                                        math.isnan(self.labda_fixed))==True:
                if self.Nparam==2:
                    k += 1
                if param[k]<1.0e-6:
                    penalty += (1.0e-6 - param[k])*LARGE
                    param[k] = 1.0e-6

        return penalty



    def show_results(self,output_single,k,noise_params,sigma):
        """ show estimated noiseparameters

        Args:
            output_single (dictionary) : where values for json file are saved
            k (int) : index where we should start reading noise_params
            noise_params (float-array) : fractions + noise model parameters
            sigma (float) : noise amplitude of power-law noise
        """
      
        #--- Get some info from other classes
        control = Control() 
        unit = control.params['PhysicalUnit']
        try:
            verbose = control.params['Verbose']
        except:
            verbose = True

        if self.Nparam==0:
            d = self.d_fixed
            kappa = -2.0*d
            lamba = self.lambda_fixed
        else:
            d     = noise_params[k]
            kappa = -2.0*d
            if self.Nparam==1:
                lamba = self.lambda_fixed
            else:
                lamba = noise_params[k+1]

        if verbose==True:
            print('sigma     = {0:7.4f} {1:s}'.format(sigma,unit))

            if self.Nparam==0:
                print('d         = {0:7.4f} (fixed)'.format(d))
                print('kappa     = {0:7.4f} (fixed)'.format(kappa))
                print('lambda    = {0:7.4f} (fixed)\n'.format(lamba))
            elif self.Nparam==1:
                print('d         = {0:7.4f}'.format(d))
                print('kappa     = {0:7.4f}'.format(kappa))
                print('lambda    = {0:7.4f} (fixed)\n'.format(lamba))
            else:
                print('d         = {0:7.4f}'.format(d))
                print('kappa     = {0:7.4f}'.format(kappa))
                print('lambda    = {0:7.4f}\n'.format(lamba))

        output_single['d']      = d
        output_single['kappa']  = kappa
        output_single['lambda'] = lamba
        output_single['sigma']  = sigma

        return k+self.Nparam
