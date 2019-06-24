# import matplotlib.pyplot as plt
import numpy as np
# import networkx as nx
# import operator
import random
# import sys
import warnings

warnings.filterwarnings('error')


class Boid:

    def __init__(self, currentparams, bounds, colour='black'):
        [r, vn, vm, c1, c2, c3, c4, c5] = currentparams
        self.r = r
        self.Vn = vn
        self.Vm = vm
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        self.c5 = c5
        self.colour = colour
        self.currentvelocity = np.array([random.randrange(int(-vn), int(vn)), random.randrange(int(-vn), int(vn))])
        while np.linalg.norm(self.currentvelocity) == 0:
            self.currentelocity = np.array([random.randrange(int(-vn), int(vn)), random.randrange(int(-vn), int(vn))])
        self.currentposition = np.array([random.randrange(bounds[0] * 1000, bounds[1] * 1000, 5) * 0.001,
                                         random.randrange(bounds[2] * 1000, bounds[3] * 1000, 5) * 0.001])
        self.acceleration = None

    def updateparam(self, newparams):
        if newparams[0] < 0 or newparams[0] > 300:
            return BoidError('Radius')
        if newparams[1] < 0 or newparams[1] > 20:
            return BoidError('Vn')
        if newparams[2] < 0 or newparams[2] > 40:
            return BoidError('Vm')
        if newparams[3] < 0 or newparams[3] > 1:
            return BoidError('c1')
        if newparams[4] < 0 or newparams[4] > 1:
            return BoidError('c2')
        if newparams[5] < 0 or newparams[5] > 100:
            return BoidError('c3')
        if newparams[6] < 0 or newparams[6] > 0.5:
            return BoidError('c4')
        if newparams[7] < 0 or newparams[7] > 1:
            return BoidError('c5')
        else:
            [self.r, self.Vn, self.Vm, self.c1, self.c2, self.c3, self.c4, self.c5] = newparams
            # colour = colour


class BoidError:
    def __init__(self, errortype=''):
        self.etype = errortype

    def __str__(self):
        if self.etype == 'Radius':
            return 'Radius outside 0-300 range'
        elif self.etype == 'Vn':
            return 'Speed outside 0-20 range'
        elif self.etype == 'Vm':
            return 'Max speed outside 0-40 range'
        elif self.etype == 'c1':
            return 'Strength of cohesion outside 0-1 range'
        elif self.etype == 'c2':
            return 'Strength of alignment outside 0-1 range'
        elif self.etype == 'c3':
            return 'Strength of seperation outside 0-100 range'
        elif self.etype == 'c4':
            return 'Probability of random steering outside 0-0.5 range'
        elif self.etype == 'c5':
            return 'Tendancy of pacekeeping outside 0-1 range'
        elif self.etype == '':
            return 'Unknown Boid Error'


def initialise_swarm(initialparameters, bounds, size):
    swarm = []
    for i in range(len(initialparameters)):
        swarm = swarm + [Boid(initialparameters[i][1], bounds) for _ in range(size)]
    return swarm
