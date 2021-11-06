import http.client
import json
import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import scipy.stats as stat

def pCandy(housePrice):
    p_max = 1000000
    p_min = 100000
    curve = 0.01
    p = curve*np.exp(6.5*np.log(2)/(p_max-p_min)*(housePrice-p_min))-curve
    return np.clip(p, 0, 1)

def pDist(houseAcre):
    dist = np.sqrt(houseAcre*4840/2)
    d_min = 20
    d_max = 200
    m = -1/(d_max-d_min)
    p_dist = m*(dist-d_max)
    return np.clip(p_dist,0,1)