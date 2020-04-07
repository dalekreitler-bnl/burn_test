# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import abc
import numpy as np
import math
import subprocess
from os import path


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
        
class FileReader(abc.ABC):
    
    @abc.abstractmethod
    def getDetector(self):
        pass
    
    @abc.abstractmethod
    def getDetDistance(self):
        pass
    
    @abc.abstractmethod
    def getPixelSize(self):
        pass
    
    @abc.abstractmethod
    def getExposureTime(self):
        pass
    
    @abc.abstractmethod
    def getWavelength(self):
        pass
    
    @abc.abstractmethod
    def getBeamx(self):
        pass
    
    @abc.abstractmethod
    def getBeamy(self):
        pass
    
    @abc.abstractmethod
    def getStartAngle(self):
        pass
    
    @abc.abstractmethod
    def getAngleIncrement(self):
        pass

class CbfReader(FileReader):
    
    def __init__(self):
        self._fileSystem = None
    
    def getDetector(self):
        pass
        
    def getPixelSize(self):
        pass

class FileReaderFactory:
    
    def getFileReader(self, format):
        if format == "cbf":
            return CbfReader()
        elif format == "hdf5" or format == "h5":
            return Hdf5Reader()

class ExpParams:
    
    def __init__(self):
        self._ExpReader = None
        return
        
class FileSystem:
    
    def __init__(self, workingDirectory="$PWD", firstFrame=None):
        self.workingDirectory = workingDirectory
        self.firstFrame = firstFrame
        self.checkInput()
        
    def checkInput(self):
        
        if path.isfile(self.firstFrame):
            pass
        else:
            print("first frame does not exist")

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
    FileSystem(firstFrame="burn_test2.py")
    
if __name__ == "__main__":
    main()
    
        