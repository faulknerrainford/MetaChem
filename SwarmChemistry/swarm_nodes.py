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

    def __init__(self):
        super(NeighbourSampler, self).__init__()
        self.Neighbours = []
        self.boid = None

    def read(self, info):
        super(NeighbourSampler, self).read(info)
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

    def __init__(self):
        super(NeighbourObserver, self).__init__()
        self.boid = None
        self.NeighPos = []
        self.NeighVel = []
        self.Oldav = []
        self.posAv = None
        self.volAv = None
        self.sepTot = None
        self.count = 0

    def read(self, info):
        super(NeighbourObserver, self).read(info)
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
            currentrecord = self.NeighPos[i]
            currentvel = self.NeighVel[i]
            if self.boid.currentposition[0]-self.boid.r <= currentrecord[0] <= \
                    self.boid.currentposition[0]+self.boid.r and self.boid.currentposition[1]-self.boid.r <= \
                    currentrecord[1] <= self.boid.currentposition[1]+self.boid.r:
                neighbour = neighbour + [(currentrecord, currentvel)]
        if neighbour:
            self.posAv = [np.mean([boid[0][0] for boid in neighbour]),
                          np.mean([boid[0][1] for boid in neighbour])]
            self.volAv = [np.mean([boid[1][0] for boid in neighbour]),
                          np.mean([boid[1][1] for boid in neighbour])]
            self.sepTot = sum(np.array([(self.boid.currentposition-n[0:1]) /
                                        (np.absolute(np.linalg.norm(self.boid.currentposition-n[0:1]))**2)for n in
                                        neighbour if np.all(np.array(self.boid.currentposition-n[0:1]) != 0)]))
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

    def __init__(self):
        super(CohesionAction, self).__init__()
        self.avPos = None
        self.boid = None

    def read(self, info):
        super(CohesionAction, self).read(info)
        self.avPos = self.readcontainers.read()[0]
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(CohesionAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.c1*(self.avPos - self.boid.currentposition)

    def push(self):
        self.containersout.add(self.boid)


# align
class AlignAction(node.Action):

    def __init__(self):
        super(AlignAction, self).__init__()
        self.avVel = None
        self.boid = None

    def read(self, info):
        super(AlignAction, self).read(info)
        self.avVel = self.readcontainers.read()[1]
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(AlignAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration+self.boid.c2*(self.avVel - self.boid.currentvelocity)

    def push(self):
        self.containersout.add(self.boid)


# seperation
class SeperationAction(node.Action):

    def __init__(self):
        super(SeperationAction, self).__init__()
        self.totSep = None
        self.boid = None

    def read(self, info):
        super(SeperationAction, self).read(info)
        self.totSep = self.readcontainers.read()[2]
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(SeperationAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration+self.boid.c3*self.totSep

    def push(self):
        self.containersout.add(self.boid)


# whim
class WhimAction(node.Action):

    def __init__(self):
        super(WhimAction, self).__init__()
        self.boid = None

    def read(self, info):
        super(WhimAction, self).read(info)
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(WhimAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.acceleration = self.boid.acceleration + np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        self.containersout.add(self.boid)


# random
# random walk
class RWalkAction(node.Action):

    def __init__(self):
        super(RWalkAction, self).__init__()
        self.boid = None

    def read(self, info):
        super(RWalkAction, self).read(info)
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(RWalkAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.acceleration = np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        self.containersout.add(self.boid)


# pacekeeping
class UpdateVAction(node.Action):

    def __init__(self):
        super(UpdateVAction, self).__init__()
        self.boid = None

    def read(self, info):
        super(UpdateVAction, self).read(info)
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(UpdateVAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.newvelocity = self.boid.currentvelocity + self.boid.acceleration
        self.boid.newvelocity = np.dot(min(self.boid.Vm / np.linalg.norm(self.boid.newvelocity), 1),
                                       self.boid.newvelocity)
        self.boid.newvelocity = self.boid.c5 * np.array(np.dot(self.boid.Vn / np.linalg.norm(self.boid.currentvelocity),
                                                               self.boid.newvelocity)
                                                        ) + (1 - self.boid.c5) * np.array(self.boid.currentvelocity)

    def push(self):
        self.containersout.add(self.boid)

# Ordered Sampler works with ordered containers, always adds to end and removes from start. Mostly done by using a
# type of ordered container.

# clock observer

# counter decision

# ordered sampler from above

# action update position and velocity


class UpdatePAction(node.Action):

    def __init__(self, bounds):
        super(UpdatePAction, self).__init__()
        self.boid = None
        self.bounds = bounds
        self.shift0 = -bounds[0] if bounds[0] < 0 else bounds[0]
        self.shift1 = -bounds[2] if bounds[2] < 0 else bounds[2]
        self.mod0 = bounds[1]-bounds[0]
        self.mod1 = bounds[3]-bounds[2]

    def read(self, info):
        super(UpdatePAction, self).read(info)
        self.boid = self.containersin.read()[0]

    def check(self):
        return super(UpdatePAction, self).check()

    def pull(self):
        self.containersin.remove(self.boid)

    def process(self):
        self.boid.currentvelocity = np.squeeze(self.boid.newvelocity)
        self.boid.currentposition = np.squeeze(self.boid.currentposition + self.boid.currentvelocity)
        self.boid.currentposition[0] = (self.boid.currentposition[0] + self.shift0) % self.mod0 - self.shift0
        self.boid.currentposition[1] = (self.boid.currentposition[1] + self.shift1) % self.mod1 - self.shift1

    def push(self):
        self.containersout.add(self.boid)


# ordered sampler from above

# clock observer

# counter decision

# Collision nodes

#   Collision observer
class CollisionObserver(node.Observer):

    def __init__(self, index=0, coll_dist=1):
        super(CollisionObserver, self).__init__(index)
        self.coll_dist = coll_dist
        self.coll_list = []
        self.tank = None

    def read(self, info):
        super(CollisionObserver, self).read(info)
        self.tank = self.readcontainers.read()

    def pull(self):
        super(CollisionObserver, self).pull()

    def process(self):
        for boid in self.tank:
            self.tank = self.tank[1:]
            for neigh in self.tank:
                if (boid.currentposition - neigh.currentposition).all < self.coll_dist:
                    self.coll_list.append(np.ndarray([boid.id, neigh.id]))

    def push(self):
        self.containersout.add(self.coll_list)


#   Collision Sampler
class CollisionSampler(node.Sampler):

    def __init__(self):
        super(CollisionSampler, self).__init__()
        self.coll = None
        self.tank = None

    def read(self, info):
        super(CollisionSampler, self).read(info)
        self.coll = self.readcontainers.read()[0]
        self.tank = self.containersin.read()

    def pull(self):
        self.sample = [boid for boid in self.tank if boid.id in self.coll]
        self.containersin.remove(self.sample)

    def push(self):
        self.containersout.add(self.sample)


#   Collision action
class CollisionAction(node.Action):

    def __init__(self):
        super(CollisionAction, self).__init__()
        self.tank = None
        self.boid1 = None
        self.boid2 = None
        self.coll = None
        self.collenv = None

    def read(self, info):
        super(CollisionAction, self).read(info)
        self.tank = self.containersin[0]
        self.collenv = self.containersin[1]
        [self.boid1, self.boid2] = self.tank.read()
        self.coll = self.collenv.read()

    def pull(self):
        self.tank.remove([self.boid1, self.boid2])
        self.collenv.remove(1)

    def check(self):
        return super(CollisionAction, self).check()

    def process(self):
        inds = random.sample(range(7), random.randrange(7))
        [self.boid2.r, self.boid1.r] = [self.boid1.r, self.boid2.r] if 0 in inds else False
        [self.boid2.vn, self.boid1.vn] = [self.boid1.vn, self.boid2.vn] if 1 in inds else False
        [self.boid2.vm, self.boid1.vm] = [self.boid1.vm, self.boid2.vm] if 2 in inds else False
        [self.boid2.c1, self.boid1.c1] = [self.boid1.c1, self.boid2.c1] if 3 in inds else False
        [self.boid2.c2, self.boid1.c2] = [self.boid1.c2, self.boid2.c2] if 4 in inds else False
        [self.boid2.c3, self.boid1.c3] = [self.boid1.c3, self.boid2.c3] if 5 in inds else False
        [self.boid2.c4, self.boid1.c4] = [self.boid1.c4, self.boid2.c4] if 6 in inds else False
        [self.boid2.c5, self.boid1.c5] = [self.boid1.c5, self.boid2.c5] if 7 in inds else False

    def push(self):
        self.containersout.add([self.boid1, self.boid2])


# observation logger - does all the things.
class VizLoggerObserver(node.Observer):

    def __init__(self, index=None):
        super(VizLoggerObserver, self).__init__(index)
        self.tank = None
        self.positions = []
        self.velocities = []
        self.time = None

    def read(self, info):
        super(VizLoggerObserver, self).read(info)
        self.tank = self.readcontainers.read()
        self.time = self.containersin.read()[0]

    def pull(self):
        super(VizLoggerObserver, self).pull()
        self.positions = []
        self.velocities = []
        self.containersin.remove([self.time])

    def process(self):
        self.tank.sort()
        self.positions = [boid.currentposition for boid in self.tank]
        self. velocities = [boid.currentvelocity for boid in self.tank]
        self.time = self.time + 1

    def push(self):
        self.containersout[0].add(tuple(self.tank))
        self.containersout[1].add(tuple(self.positions))
        self.containersout[2].add(tuple(self.velocities))
        self.containersout[3].add(self.time)


class VisualizerObserver(node.Observer):

    def __init__(self, bounds, boid_size, gen_time, ani_steps, writefile):
        super(VisualizerObserver, self).__init__()
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
        self.ani_steps = ani_steps
        self.file = writefile

    def read(self, info):
        super(VisualizerObserver, self).read(info)
        self.world = Surface(self.readcontainers, self.particles, self.bounds, self.boid_size, self.ani_steps)
        self.viz_gens = self.readcontainers.read()
        for gen in self.viz_gens:
            for coord in gen:
                while isinstance(coord[0], list) or isinstance(coord[0], np.ndarray):
                    coord = coord[0]

    def pull(self):
        super(VisualizerObserver, self).pull()

    def process(self):
        super(VisualizerObserver, self).process()
        self.sa = SwarmAnimation(self.world, self.rect, self.viz_gens, self.gen_time, self.fig, self.ax, self.dt,
                                 self.boid_size)
        self.anim = animation.FuncAnimation(self.fig, self.sa.animate,
                                            frames=self.gen_time*self.ani_steps-self.ani_steps, interval=10, blit=True,
                                            init_func=self.sa.init)

    def push(self):
        super(VisualizerObserver, self).push()
        Writer = animation.writers['ffmpeg']
        writer_inst = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        self.anim.save(self.file, writer=writer_inst)
        plt.show()


class Surface:
    #    """init_state is an [N x 4] array, where N is the number of boids:
    #        [[x1, y1, vx1, vy1],
    #            [x2,y2,vx2,vy2],
    #            ...             ]
    #
    #        bounds is the size of the box: [xmin, xmax, ymin, ymax]
    #    """
    def __init__(self, viz_gen, particles, bounds=tuple([-150, 150, -150, 150]), boid_size=0.4, ani_steps=1):
        # generat initial state of swarm from boids
        init_state = np.array(viz_gen)
        self.init_state = np.array(init_state)
        self.boid_size = boid_size
        self.state = self.init_state.copy()
        self.time_elapsed = 0
        self.bounds = bounds
        self.gen_time = 100
        self.size = 0.04
        self.particles = particles
        self.ani_steps = ani_steps

    def updatestep(self, viz_gens, i):
        # update velocities taken from swarm and passed into surface/gen_time to give smoother generations
        if not i % self.ani_steps:
            formerstate = viz_gens[i/self.ani_steps]
            newstate = viz_gens[i/self.ani_steps + 1]
            state = list(formerstate)
            for g in range(len(formerstate)):
                state[g] = (newstate[g] - formerstate[g]) * ((1 / self.ani_steps)*(i % self.ani_steps)) + state[g]
        else:
            state = viz_gens[i/self.ani_steps]
        # for coord in state:
        #     while isinstance(coord[0], list) or isinstance(coord[0], np.ndarray):
        #         coord = np.squeeze(coord)
        self.state = np.squeeze(state)

    def step(self, dt):
        # generation is defined as gen_time time steps
        self.time_elapsed = dt


class SwarmAnimation:

    def __init__(self, world, rect, viz_gens, gen_time, fig, ax, dt, boid_size):
        self.world = world
        self.rect = rect
        self.viz_gens = viz_gens
        self.gen_time = gen_time
        self.fig = fig
        self.ax = ax
        self.dt = dt
        self.boid_size = boid_size
        self.ms = None

    def init(self):
        self.world.particles.set_data([], [])
        self.rect.set_edgecolor('none')
        return self.world.particles, self.rect

    def animate(self, i):
        self.world.updatestep(self.viz_gens, i)
        self.ms = int(self.fig.dpi * 2 * self.world.size * self.fig.get_figwidth() / np.diff(self.ax.get_xbound())[0])
        self.rect.set_edgecolor('k')
        self.world.particles.set_data(self.world.state[:, 0], self.world.state[:, 1])
        self.world.particles.set_markersize(self.boid_size)
        return self.world.particles, self.rect
