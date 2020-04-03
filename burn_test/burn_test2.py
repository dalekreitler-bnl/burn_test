# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import math


class BurnModel:
    def __init__():
        pass
    
    def trimNoise(self, trimNoiseStrategy):
        pass
    
    def calculateDecayRate(self, decayRateStrategy):
        pass

class BurnObject:
    def __init__():
        pass
    
class ResShell:
    def __init__(self, d_min=0, d_max=1000):
        self.d_min = d_min
        self.d_max = d_max

class ArrayHandler:
    
    @staticmethod
    def readSPOTXDStoNpArray(fileName="SPOT.XDS"):
        npArray = np.genfromtxt(fileName)
        return npArray
    
    @staticmethod
    def correctForDetCenter(npArray, beam_x, beam_y):
        npArray[:,0] = npArray[:,0] - beam_x
        npArray[:,1] = npArray[:,1] - beam_y
        return npArray
    
    @staticmethod
    def addResolutionColumn(centeredNpArray, wavelength, detDistance):
        x = centeredNpArray[:,0]
        y = centeredNpArray[:,1]
        rPixels = (x**2 + y**2)**0.5
        rResolution = ResolutionTools.detPixelstoRes(rPixels, 0.9, 150)
        resNpArray = np.c_[centeredNpArray, rPixels, rResolution]
        return resNpArray
    
class ResolutionTools:
    
    @staticmethod
    def resShellBounds(N_shells, r_min):
        resShellBoundsList = list()
        resShellBoundsList.append(1)
        for k in range(1, N_shells+1):
            r = r_min*math.sqrt(float(k)/N_shells)
            resShellBoundsList.append(r)
        return resShellBoundsList
    
    @staticmethod
    def detPixelstoRes(r, wavelength=0.9, detDistance=150, pixelSize=0.075):
        #distance from beam center converted from det pixels
        #to resolution
        r = r*pixelSize
        denom = 2*np.sin(0.5*np.arctan(r/detDistance))
        resolution = wavelength/denom
        return resolution
        
def main():
    test = ArrayHandler.readSPOTXDStoNpArray()
    test = ArrayHandler.correctForDetCenter(test, 1600, 1600)
    test = ArrayHandler.addResolutionColumn(test, 0.9, 150)
    np.savetxt("testfile.txt",test)
    
if __name__ == "__main__":
    main()
    
        