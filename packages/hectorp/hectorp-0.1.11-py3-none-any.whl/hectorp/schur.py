# ammargrag.py
#
# Implementation of the fast method of Ammar and Grag / Musicus. 
# It provides a quick subroutine to
# perform least-squares given the design matrix H, the observations y and
# the first column of the Toeplitz covariance matrix C.
#
# Equations are taken from Bos et al. (2013), "Fast error analysis of 
# continuous GNSS observations with missing data", Journal of Geodesy,
# DOI 10.1007/s00190-012-0605-0.
#
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
# 11/12/2022  Machiel Bos, Santa Clara
#===============================================================================

import numpy as np
import math
import time
from numpy import fft
from numpy.linalg import inv
import datetime
from hectorp.control import SingletonMeta
from operator import add
from hectorp.powerlaw import Powerlaw
from numpy.linalg import inv
from math import sin,cos,pi
from itertools import zip_longest
import pyfftw


#===============================================================================
# Class definitions
#===============================================================================


class Schur():

    def __init__(self):
        """ Define Class variables
        """

        #pyfftw.config.NUM_THREADS = 4
        #pyfftw.config.NUM_THREADS = multiprocessing.cpu_count()
        #print('NUM_THREADS=',pyfftw.config.NUM_THREADS)
        #pyfftw.interfaces.cache.enable()
        #pyfftw.config.PLANNER_EFFORT = 'FFTW_PATIENT'

        n_max = 19
        self.Fx = [None]*n_max
        self.Fa = [None]*n_max
        self.Fb = [None]*n_max
        self.x  = [None]*n_max
        
        self.rfft_object = [None]*n_max
        self.irfft_object = [None]*n_max

        n = 2
        for i in range(1,n_max):
            print(i,', n=',n)
            self.x[i]  = pyfftw.empty_aligned(n, dtype='float64')
            self.Fx[i] = pyfftw.empty_aligned(n//2+1, dtype='complex128')
            self.Fa[i] = pyfftw.empty_aligned(n//2+1, dtype='complex128')
            self.Fb[i] = pyfftw.empty_aligned(n//2+1, dtype='complex128')
            #self.x[i]  = np.empty(n, dtype='float64')
            #self.Fx[i] = np.empty(n//2+1, dtype='complex128')
            #self.Fa[i] = np.empty(n//2+1, dtype='complex128')
            #self.Fb[i] = np.empty(n//2+1, dtype='complex128')
            
            self.rfft_object[i] = pyfftw.builders.rfft(self.x[i])
            self.irfft_object[i]= pyfftw.builders.irfft(self.Fx[i])


            n *= 2

        self.zeros = np.zeros(n)

        self.multiply = self.multiply_fftw



    def levinson(self,t):
        """ Use Durbin-Levinson algorithm to compute l1 and l2

        This subroutine is just listed here for testing and not
        used in production

        Args:
            t : array containing first column of Toeplitz matrix

        Returns:
            l1,l2 : arrays containing Schur polynomials
            delta : scale factor
        """

        #--- Durbin-Levinson to compute l1 and l2
        m = len(t)
        r = np.zeros(m-1)
        delta = t[0]
        for i in range(0,m-1):
            if i==0:
                gamma = -t[i+1]/delta
            else:
                gamma = -(t[i+1] + np.dot(t[1:i+1],r[0:i]))/delta
                r[1:i+1] = r[0:i] + gamma*r[i-1::-1]

            r[0] = gamma
            delta = t[0] + np.dot(t[1:i+2],r[i::-1])

        #--- create l1 & l2 using r
        l1 = np.zeros(m)
        l2 = np.zeros(m)

        l1[0]   = 1.0
        l1[1:m] = r[m-2::-1]
        l2[1:m] = r[0:m-1]

        return [l1,l2,delta]



    def multiply_fftw(self,a,b):
        """ Multiply 2 polynomials using Numpy FFT

        Args:
            a (array float) : polynomial a0, a1*t, a2*t^2, ...  
            b (array float) : polynomial b0, b1*t, b2*t^2, ...  

        Returns:
            c (array float) : a*b
        """
        #--- Determine which polynomial is longer
        if len(a)>len(b):
            m = len(a)
        else:
            m = len(b)

        #--- Algorithm only works for powers of 2 and zero padding
        n=1
        i=1
        while n<m:
            n *= 2
            i += 1
        n *= 2 #--- These are the extra cells for padding

        #--- forward transform to point value
        #self.x[i] = (ctypes.c_double*len(a)).from_address(id(a))
        self.x[i][0:len(a)] = a[:]
        self.x[i][len(a):n] = self.zeros[len(a):n]
        self.Fa[i][:] = self.rfft_object[i]()

        self.x[i][0:len(b)] = b[:]
        self.x[i][len(b):n] = self.zeros[len(b):n]
        self.Fb[i][:] = self.rfft_object[i]()

        #self.Fx[i][:] = self.Fa[i] * self.Fb[i]
        self.Fx[i][:] = np.multiply(self.Fa[i],self.Fb[i])

        c = self.irfft_object[i]().copy()

        m = len(a)+len(b)-1
        
        return c[0:m]



    def multiply_numpy(self,a,b):
        """ Multiply 2 polynomials using Numpy FFT

        Args:
            a (array float) : polynomial a0, a1*t, a2*t^2, ...  
            b (array float) : polynomial b0, b1*t, b2*t^2, ...  

        Returns:
            c (array float) : a*b
        """

        #--- Determine which polynomial is longer
        if len(a)>len(b):
            m = len(a)
        else:
            m = len(b)

        #--- Algorithm only works for powers of 2 and zero padding
        n=1
        while n<m:
            n *= 2
        n *= 2 #--- These are the extra cells for padding

        #--- forward transform to point value
        Fa = np.fft.rfft (a,n=n) # n=n takes care of zero padding of a[len(a):n]
        Fb = np.fft.rfft (b,n=n)

        #--- convolution
        Fc = Fa * Fb 

        #--- reverse transform to get back coefficients
        c = np.fft.irfft ( Fc )

        m = len(a)+len(b)-1
        
        return c[0:m]



    def generalised_schur(self,tm,p_0,q_0):
        """ Generalised Schur Algorithm

        """

        if tm==1:
            gamma = -p_0[0]/q_0[0]
            delta_tm = 1.0 - pow(gamma,2.0) 
            a_tm = np.array([0.0,1.0])
            c_tm = np.array([0.0,-gamma])
            return [a_tm,c_tm,delta_tm]
        else:
            m = tm//2
            [a_m,c_m,delta_m] = self.generalised_schur(m,p_0[0:m],q_0[0:m])
 
            #--- Construct b_m and d_m
            d_m = a_m[-1:0:-1].copy() 
            b_m = c_m[-1:0:-1].copy() 

            #--- Multiply polynomials
            #start_time = time.time()
            part1 =       self.multiply(d_m,p_0) 
            part2 =  -1 * self.multiply(b_m,q_0)
        
            p_m   = [sum(j) for j in zip_longest(part1,part2, fillvalue=0.0)]
      
            #start_time = time.time()
            part1 = -1 * self.multiply(c_m,p_0)
            part2 =      self.multiply(a_m,q_0)
     
            q_m   = [sum(j) for j in zip_longest(part1,part2, fillvalue=0.0)]
        
            [a_mtm,c_mtm,delta_mtm] = \
                                self.generalised_schur(m,p_m[m:tm],q_m[m:tm])

            #--- Multiply polynomials
            part1 = self.multiply(a_m,a_mtm)
            part2 = self.multiply(b_m,c_mtm)
            a_tm  = [sum(j) for j in zip_longest(part1,part2, fillvalue=0.0)]
        
            part1 = self.multiply(c_m,a_mtm)
            part2 = self.multiply(d_m,c_mtm)
            c_tm  = [sum(j) for j in zip_longest(part1,part2, fillvalue=0.0)]

            delta_tm = delta_m * delta_mtm
  
            return [a_tm,c_tm,delta_tm]


    def test(self):
        """ Perform test computation to check if everything is okay
        """

        #nn = 4*1024 + 1
        nn = 64*1024 + 1
        noise_model = Powerlaw()
        [t,k_new] = noise_model.create_t(nn,0,[-0.8])
  
        #--- Levinson-Durbin
        #print('\nLevingson-Durbin')
        #start_time = time.time()
        #[l1,l2,delta] = self.levinson(t)
        #print("Levinson : {0:12.6f} s n".format(float(time.time() - start_time)))
        #print("l1 = ",l1)

            #--- remember this one... gamma's are good
        xi  = np.zeros(nn-1)
        p_0 = np.zeros(nn)
        p_0[0:nn-1] = np.array(t[1:])
        q_0 = np.array(t)
        tm  = len(t)

        start_time = time.time()
        [a_tm,c_tm,delta_tm] = self.generalised_schur(tm-1,p_0,q_0)
        print("GSA : {0:12.6f} s n".format(float(time.time() - start_time)))
        print('delta_tm = ',delta_tm)
        for i in range(0,nn-1):
            xi[nn-2-i]=a_tm[i] - c_tm[i+1]
        print(xi)
