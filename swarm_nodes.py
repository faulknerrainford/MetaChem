import node
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# import container
# standard load/ gen node (2 versions, generic load and a generator node specific)
# Brute sampler pregen boids put into a list container.
# default ordered sampler


# uses first boid in sample (or random in unordered container) for reference to pull neighbours
class NeighbourSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None):
        super(NeighbourSampler, self).__init__(containersin, containersout, readcontainers)
        self.Neighbours = []
        self.boid = None

    def read(self):
        self.boid = self.readcontainers.read()[0]
        self.Neighbours = [neighbour for neighbour in self.containersin.read() if
                           self.boid.currentPosition[0]-self.boid.R <= neighbour.currentPosition[0]
                           <= self.boid.currentPosition[0]+self.boid.R and self.boid.currentPosition[1]-self.boid.R
                           <= neighbour.currentPosition[1] <= self.boid.currentPosition[1]+self.boid.R]

    def pull(self):
        self.containersin.remove(self.Neighbours)

    def push(self):
        self.containersout.add(self.Neighbours)


# BUILD Observer to generate averages of neighbours (check if this needs to include boid itself)
class NeighbourObserver(node.Observer):

    def __init__(self, containersin, containersout, readcontainers=None):
        super(NeighbourObserver, self).__init__(containersin, containersout, readcontainers)
        self.boid = None
        self.NeighPos = []
        self.NeighVel = []
        self.Oldav = []
        self.posAv = None
        self.volAv = None
        self.sepTot = None
        self.count = 0

    def read(self):
        self.boid = self.readcontainers[0].read()[0]
        self.NeighPos = self.readcontainers[1].read()[-1]
        self.NeighVel = self.readcontainers[2].read()[-1]
        self.Oldav = self.containersin[0].read()
        self.count = self.containersin[1].read()

    def pull(self):
        self.containersin[0].remove(self.Oldav)
        self.containersin[1].remove(self.count)

    def process(self):
        neighbour = []
        for i in range(len(list(self.NeighPos))):
            # for each in the positions if they are a neighbour then add them to the listings.
            currentrecord =self.NeighPos[i]
            currentvel = self.NeighVel[i]
            while isinstance(currentrecord[0], list) or isinstance(currentrecord[0], np.ndarray):
                currentrecord = currentrecord[0]
                currentvel = currentvel[0]
            while isinstance(self.boid.currentposition[0], list) or isinstance( self.boid.currentposition[0], np.ndarray):
                self.boid.currentposition = self.boid.currentposition[0]
            print currentrecord[0]
            print self.boid.currentposition
            print self.boid.r
            if self.boid.currentposition[0]-self.boid.r <= currentrecord[0] <= \
                    self.boid.currentposition[0]+self.boid.r and self.boid.currentposition[1]-self.boid.r <= \
                    currentrecord[1] <= self.boid.currentposition[1]+self.boid.r:
                neighbour = neighbour + [tuple([currentrecord, currentvel])]
        if neighbour:
            self.posAv = [np.mean([boid[0][0] for boid in neighbour]),
                          np.mean([boid[0][1] for boid in neighbour])]
            self.volAv = [np.mean([boid[1][0] for boid in neighbour]),
                          np.mean([boid[1][1] for boid in neighbour])]
            print self.boid.currentposition-neighbour[0][0:1]
            print self.boid.currentposition
            print neighbour[0][0:1]
            self.sepTot = sum(np.array([(self.boid.currentposition-n[0:1]) / (np.absolute(np.linalg.norm(self.boid.currentposition-n[0:1]))**2)for n in neighbour if np.all(np.array(self.boid.currentposition-n[0:1])!= 0)]))
        self.count = len(neighbour)

    def push(self):
        self.containersout[0].add([self.posAv, self.volAv, self.sepTot])
        self.containersout[1].add(self.count)

# BruteSampler to return neighbours

# flocking action and decision nodes COME BACK TO THESE

# decision for flock or wander
# Flock
# a cohesion


class CohesionAction(node.Action):

    def __init__(self, writesample, readsample, readcontainers):
        super(CohesionAction, self).__init__(writesample, readsample, readcontainers)
        self.avPos = None
        self.boid = None

    def read(self):
        self.avPos = self.readcontainers.read()[0]
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(CohesionAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.c1*(self.avPos - self.boid.currentposition)

    def push(self):
        self.writesample.add(self.boid)


# align
class AlignAction(node.Action):

    def __init__(self, writesample, readsample, readcontainers):
        super(AlignAction, self).__init__(writesample, readsample, readcontainers)
        self.avVel = None
        self.boid = None

    def read(self):
        self.avVel = self.readcontainers.read()[1]
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(AlignAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration+self.boid.c2*(self.avVel - self.boid.currentvelocity)

    def push(self):
        self.writesample.add(self.boid)


# seperation
class SeperationAction(node.Action):

    def __init__(self, writesample, readsample, readcontainers):
        super(SeperationAction, self).__init__(writesample, readsample, readcontainers)
        self.totSep = None
        self.boid = None

    def read(self):
        self.totSep = self.readcontainers.read()[2]
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(SeperationAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration+self.boid.c3*self.totSep

    def push(self):
        self.writesample.add(self.boid)


# whim
class WhimAction(node.Action):

    def __init__(self, writesample, readsample):
        super(WhimAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(WhimAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration + np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        self.writesample.add(self.boid)


# random
# random walk
class RWalkAction(node.Action):

    def __init__(self, writesample, readsample):
        super(RWalkAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(RWalkAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.acceleration = np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        self.writesample.add(self.boid)


# pacekeeping
class UpdateVAction(node.Action):

    def __init__(self, writesample, readsample):
        super(UpdateVAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(UpdateVAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.newvelocity = self.boid.currentvelocity + self.boid.acceleration
        self.boid.newvelocity = np.dot(min(self.boid.Vm / np.linalg.norm(self.boid.newvelocity), 1),
                                       self.boid.newvelocity)
        self.boid.newvelocity = self.boid.c5 * np.array(np.dot(self.boid.Vn / np.linalg.norm(self.boid.currentvelocity),
                                                               self.boid.newvelocity)
                                                        ) + (1 - self.boid.c5) * np.array(self.boid.currentvelocity)

    def push(self):
        self.writesample.add(self.boid)

# Ordered Sampler works with ordered containers, always adds to end and removes from start. Mostly done by using a
# type of ordered container.

# clock observer

# counter decision

# ordered sampler from above

# action update position and velocity


class UpdatePAction(node.Action):

    def __init__(self, writesample, readsample):
        super(UpdatePAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        self.boid = self.readsample.read()[0]

    def check(self):
        return super(UpdatePAction, self).check()

    def pull(self):
        self.readsample.remove(self.boid)

    def process(self):
        self.boid.currentvelocity = self.boid.newvelocity
        self.boid.currentposition = self.boid.currentposition + self.boid.currentvelocity

    def push(self):
        self.writesample.add(self.boid)


# ordered sampler from above

# clock observer

# counter decision

# observation logger - does all the things.
class VizLoggerObserver(node.Observer):

    def __init__(self, containersin, containersout, readcontainers=None, index=None):
        super(VizLoggerObserver, self).__init__(containersin, containersout, readcontainers, index)
        self.tank = None
        self.positions = []
        self.velocities = []
        self.time = None

    def read(self):
        self.tank = self.readcontainers.read()
        self.time = self.containersin.read()[0]

    def pull(self):
        super(VizLoggerObserver, self).pull()
        self.positions = []
        self.velocities = []
        self.containersin.remove([self.time])

    def process(self):
        for boid in self.tank:
            self.positions.append(boid.currentposition)
            self.velocities.append(boid.currentvelocity)
        self.time = self.time + 1

    def push(self):
        self.containersout[0].add(tuple(self.tank))
        self.containersout[1].add(tuple(self.positions))
        self.containersout[2].add(tuple(self.velocities))
        self.containersout[3].add(self.time)


class VisualizerObserver(node.Observer):

    def __init__(self, containersin, bounds, boid_size, gen_time):
        super(VisualizerObserver, self).__init__(containersin, None)
        self.gen_time = gen_time
        self.bounds = bounds
        self.boid_size = boid_size
        self.world = None
        self.dt = 1
        self.fig = plt.figure()
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot(111, aspect='equal', autoscale_on=False, xlim=(bounds[0], bounds[1]),
                                       ylim=(bounds[2], bounds[3]))
        self.particles, = self.ax.plot([], [], 'bo', ms=6)
        self.rect = plt.Rectangle(self.bounds[::2], self.bounds[1] - self.bounds[0],
                                  self.bounds[3] - self.bounds[2], ec='none', lw=2, fc='none')
        self.ax.add_patch(self.rect)
        self.anim = None
        self.viz_gens = None
        self.sa = None

    def read(self):
        super(VisualizerObserver, self).read()
        self.world = Surface(self.containersin.read(), self.bounds, self.boid_size)
        self.viz_gens = self.containersin.read()

    def pull(self):
        super(VisualizerObserver, self).pull()

    def process(self):
        super(VisualizerObserver, self).process()
        self.sa = SwarmAnimation(self.world, self.rect, self.viz_gens, self.gen_time, self.fig, self.ax, self.dt)
        self.anim = animation.FuncAnimation(self.fig, self.sa.animate, frames=600, interval=10, blit=True,
                                            init_func=self.sa.init)
        plt.show()

    def push(self):
        super(VisualizerObserver, self).push()
        self.anim.save('swarmani.mp4', writer="mencoder", fps=30, extra_args=['-vcodec', 'libx263'])


class Surface:
    #    """init_state is an [N x 4] array, where N is the number of boids:
    #        [[x1, y1, vx1, vy1],
    #            [x2,y2,vx2,vy2],
    #            ...             ]
    #
    #        bounds is the size of the box: [xmin, xmax, ymin, ymax]
    #    """
    def __init__(self, viz_gen, bounds=tuple([-150, 150, -150, 150]), boid_size=0.4):
        # generat initial state of swarm from boids
        init_state = np.array(viz_gen)
        self.init_state = np.array(init_state)
        self.boid_size = boid_size
        self.state = self.init_state.copy()
        self.time_elapsed = 0
        self.bounds = bounds
        self.gen_time = 100
        self.size = 0.04

    def updatestep(self, viz_gens, i):
        # update velocities taken from swarm and passed into surface/gen_time to give smoother generations
        state = np.array(viz_gens[i])
        self.state = state

    def step(self, dt):
        # generation is defined as gen_time time steps
        self.time_elapsed = dt


class SwarmAnimation:

    def __init__(self, world, rect, viz_gens, gen_time, fig, ax, dt):
        self.world = world
        self.rect = rect
        self.viz_gens = viz_gens
        self.gen_time = gen_time
        self.fig = fig
        self.ax = ax
        self.dt = dt

    def init(self):
        self.world.particles.set_data([], [])
        self.rect.set_edgecolor('none')
        return self.world.particles, self.rect

    def animate(self):
        # self.swarm = self.world.updateStep(self.dt, self.gen_time, self.viz_gens, i)
        # self.ms = int(self.fig.dpi * 2 * self.world.size * self.fig.get_figwidth() / np.diff(self.ax.get_xbound())[0])
        self.rect.set_edgecolor('k')
        self.world.particles.set_data(self.world.state[:, 0], self.world.state[:, 1])
        self.world.particles.set_markersize(10)
        return self.world.particles, self.rect
