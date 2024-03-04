from source import node
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
    """
    Sampler that extracts the boids in the neighbourhood of a selected boid.

    Parameters
    ----------
    containersin : Tank
        The tank containing the neighbours of the boid.

    containersout : Sample
        The sample to put the set of neighbours into.

    readcontainers : Sample
        The sample container containing the boid we need to find the neighbours of.

    """

    def __init__(self, containersin, containersout, readcontainers=None):
        super(NeighbourSampler, self).__init__(containersin, containersout, readcontainers)
        self.Neighbours = []
        self.boid = None

    def read(self):
        """
        Read in the boid and the tank and sort through the results of the tank to find the boids in the neighbourhood
        around the given boid based on boid sensing radius. These are stored internally.

        """
        self.boid = self.readcontainers.read()[0]
        self.Neighbours = [neighbour for neighbour in self.containersin.read() if
                           self.boid.currentPosition[0]-self.boid.R <= neighbour.currentPosition[0]
                           <= self.boid.currentPosition[0]+self.boid.R and self.boid.currentPosition[1]-self.boid.R
                           <= neighbour.currentPosition[1] <= self.boid.currentPosition[1]+self.boid.R]

    def pull(self):
        """
        Remove the selection of neighbours from the tank to use in flocking.
        """
        self.containersin.remove(self.Neighbours)

    def push(self):
        """
        Puts the neighbours into the sample container.
        """
        self.containersout.add(self.Neighbours)


# BUILD Observer to generate averages of neighbours (check if this needs to include boid itself)
class NeighbourObserver(node.Observer):
    """
    Checks content of neighbourhood and generate the needed averages from that set.

    Parameters
    ----------
    containerin : List<Environment>
        Two item list of  the Environment containing neighbourhood variables and the Environment containing the number of
        boids in the neighbourhood.

    containerout : ContainerNode
        Two item list of  the Environment containing neighbourhood variables and the Environment containing the number of
        boids in the neighbourhood.

    readcontainers : List<ContainerNode>
        List of containers inorder: sample containing boid of interest, environment with position of nodes, environment with velocity of nodes.


    """
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
        """
        Reads in the boid, a placeholder for the neighbours position and velocity and the old values in the output
        Environments.

        """
        self.boid = self.readcontainers[0].read()[0]
        self.NeighPos = self.readcontainers[1].read()[-1]
        self.NeighVel = self.readcontainers[2].read()[-1]
        self.Oldav = self.containersin[0].read()
        self.count = self.containersin[1].read()

    def pull(self):
        """
        Clears the output Environments.

        """
        self.containersin[0].remove(self.Oldav)
        self.containersin[1].remove(self.count)

    def process(self):
        """
        Searches through the positions of all the boids to find those in the boid's neighbourhood, Then generates the
        average position, velocity, separation and count of the neighbourhood.

        """
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
        """
        Pushes the position, velocity and separation of the neighbourhood to the Averages Environment and the count to
        the neighbourhood count environment.

        """
        self.containersout[0].add([self.posAv, self.volAv, self.sepTot])
        self.containersout[1].add(self.count)

# BruteSampler to return neighbours

# flocking action and decision nodes.rst COME BACK TO THESE

# decision for flock or wander
# Flock
# a cohesion


class CohesionAction(node.Action):
    """
    Performs the cohesion action by updating the acceleration.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    readcontainers : Environment
        Environment containing neighbourhood averages.
    """

    def __init__(self, writesample, readsample, readcontainers):
        super(CohesionAction, self).__init__(writesample, readsample, readcontainers)
        self.avPos = None
        self.boid = None

    def read(self):
        """
        Reads in the boid and the average positions of boids in the neighbourhood.

        """
        self.avPos = self.readcontainers.read()[0]
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(CohesionAction, self).check()

    def pull(self):
        """
        Removes the boid from the sample.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids acceleration based on average position neighbours and parameters of boid.

        """
        self.boid.acceleration = self.boid.c1*(self.avPos - self.boid.currentposition)

    def push(self):
        """
        Puts updated boid back in the sample.

        """
        self.writesample.add(self.boid)


# align
class AlignAction(node.Action):
    """
    Performs the alignment action by updating the acceleration.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    readcontainers : Environment
        Environment containing neighbourhood averages.
    """

    def __init__(self, writesample, readsample, readcontainers):
        super(AlignAction, self).__init__(writesample, readsample, readcontainers)
        self.avVel = None
        self.boid = None

    def read(self):
        """
        Reads in the boid and the average velocities of boids in the neighbourhood.

        """
        self.avVel = self.readcontainers.read()[1]
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(AlignAction, self).check()

    def pull(self):
        """
        Removes the boid from the sample.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids acceleration based on average velocity neighbours and parameters of boid.

        """
        self.boid.acceleration = self.boid.acceleration+self.boid.c2*(self.avVel - self.boid.currentvelocity)

    def push(self):
        """
        Puts updated boid back in the sample.

        """
        self.writesample.add(self.boid)


# seperation
class SeperationAction(node.Action):
    """
    Performs the seperation action by updating the acceleration.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    readcontainers : Environment
        Environment containing neighbourhood averages.
    """

    def __init__(self, writesample, readsample, readcontainers):
        super(SeperationAction, self).__init__(writesample, readsample, readcontainers)
        self.totSep = None
        self.boid = None

    def read(self):
        """
        Reads in the boid and the separation of boids in the neighbourhood.

        """
        self.totSep = self.readcontainers.read()[2]
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(SeperationAction, self).check()

    def pull(self):
        """
        Removes the boid from the sample.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids acceleration based on seperation of neighbours and parameters of boid.

        """
        self.boid.acceleration = self.boid.acceleration+self.boid.c3*self.totSep

    def push(self):
        """
        Puts updated boid back in the sample.

        """
        self.writesample.add(self.boid)


# whim
class WhimAction(node.Action):
    """
    Performs the whim action by updating the acceleration.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    """

    def __init__(self, writesample, readsample):
        super(WhimAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        """
        Reads in the boid.

        """
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(WhimAction, self).check()

    def pull(self):
        """
        Removes boid from the sample for editing.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids acceleration with a  small amount of random movement.

        """
        self.boid.acceleration = self.boid.acceleration + np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        """
        Adds updated boid back into the sample.

        """
        self.writesample.add(self.boid)


# random
# random walk
class RWalkAction(node.Action):
    """
    Applies random walk to boid.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    """

    def __init__(self, writesample, readsample):
        super(RWalkAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        """
        Reads in the boid.

        """
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(RWalkAction, self).check()

    def pull(self):
        """
        Removes boid from the sample for editing.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids acceleration with a  random walk.

        """
        self.boid.acceleration = np.array([random.random()-0.5, random.random()-0.5])

    def push(self):
        """
        Adds updated boid back into the sample.

        """
        self.writesample.add(self.boid)


# pacekeeping
class UpdateVAction(node.Action):
    """
    Updates the boids velocity based on acceleration.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.
    """

    def __init__(self, writesample, readsample):
        super(UpdateVAction, self).__init__(writesample, readsample)
        self.boid = None

    def read(self):
        """
        Reads in the boid.

        """
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(UpdateVAction, self).check()

    def pull(self):
        """
        Removes boid from the sample for editing.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids velocity by adding the acceleration and then normalizing the velocity and ensure the new
        velocity is within limits.

        """
        self.boid.newvelocity = self.boid.currentvelocity + self.boid.acceleration
        self.boid.newvelocity = np.dot(min(self.boid.Vm / np.linalg.norm(self.boid.newvelocity), 1),
                                       self.boid.newvelocity)
        self.boid.newvelocity = self.boid.c5 * np.array(np.dot(self.boid.Vn / np.linalg.norm(self.boid.currentvelocity),
                                                               self.boid.newvelocity)
                                                        ) + (1 - self.boid.c5) * np.array(self.boid.currentvelocity)

    def push(self):
        """
        Adds updated boid back into the sample.

        """
        self.writesample.add(self.boid)

# Ordered Sampler works with ordered containers, always adds to end and removes from start. Mostly done by using a
# type of ordered container.

# clock observer

# counter decision

# ordered sampler from above

# action update position and velocity


class UpdatePAction(node.Action):
    """
    Updates the boids position based on velocity.

    Parameters
    -----------
    writesample : Sample
        Sample containing boid of interest, same as readsample.
    readsample : Sample
        Sample containing boid of interest, same as writesample.

    """

    def __init__(self, writesample, readsample, bounds):
        super(UpdatePAction, self).__init__(writesample, readsample)
        self.boid = None
        self.bounds = bounds
        self.shift0 = -bounds[0] if bounds[0]<0 else bounds[0]
        self.shift1 = -bounds[2] if bounds[2]<0 else bounds[2]
        self.mod0 = bounds[1]-bounds[0]
        self.mod1 = bounds[3]-bounds[2]



    def read(self):
        """
        Reads in the boid.

        """
        self.boid = self.readsample.read()[0]

    def check(self):
        """
        Uses default.

        """
        return super(UpdatePAction, self).check()

    def pull(self):
        """
        Removes boid from the sample for editing.

        """
        self.readsample.remove(self.boid)

    def process(self):
        """
        Updates the boids position by adding the velocity and then normalizing the velocity and ensure the new positions
        is within bounds.

        """
        self.boid.currentvelocity = np.squeeze(self.boid.newvelocity)
        self.boid.currentposition = np.squeeze(self.boid.currentposition + self.boid.currentvelocity)
        self.boid.currentposition[0] = (self.boid.currentposition[0] + self.shift0)%self.mod0 - self.shift0
        self.boid.currentposition[1] = (self.boid.currentposition[1] + self.shift1)%self.mod1 - self.shift1

    def push(self):
        """
        Adds updated boid back into the sample.

        """
        self.writesample.add(self.boid)


# ordered sampler from above

# clock observer

# counter decision

# Collision nodes.rst

#   Collision observer
class CollisionObserver(node.Observer):
    """
    Checks boid's distance to other boids to find collisions and outputs a list of collisions.

    Parameters
    -----------
    containersin : Environment
        Stores list of collisions
    containersout : Environment
        Stores list of collisions
    readcontainers : Tank
        Tank container we are checking for collisions
    index : int
        default set to 0, not used in observer.
    coll_dist : int
        The collision distance within which a collisions is deemed to have occured.
    """

    def __init__(self, containersin, containersout, readcontainers=None, index=0, coll_dist=1):
        super(CollisionObserver, self).__init__(containersin, containersout, readcontainers, index)
        self.coll_dist = coll_dist
        self.coll_list = []
        self.tank = None
        self.oldColl = []

    def read(self):
        """
        Reads in tank and the old collision list.

        """
        super(CollisionObserver, self).read()
        self.tank = self.readcontainers.read()
        self.oldColl = self.containersin.read()

    def pull(self):
        """
        Cleans out the collision list Environment.

        """
        super(CollisionObserver, self).pull()
        self.containersin.remove(self.oldColl)

    def process(self):
        """
        Finds collisions for each node and adds them to a list of collision ids.

        """
        for boid in self.tank:
            self.tank = self.tank[1:]
            for neigh in self.tank:
                if (boid.currentposition - neigh.currentposition).all < self.coll_dist:
                    self.coll_list.append(np.ndarray([boid.id, neigh.id]))

    def push(self):
        """
        Push the collision list to the output Environment

        """
        self.containersout.add(self.coll_list)


#   Collision Sampler
class CollisionSampler(node.Sampler):
    """
    Sampler to extract the particles involved in a collision from a tank.

    Parameters
    ----------
    containersin : Tank
        The tank containing the colliding particles.
    containersout: Sample
        The sample for the particles to be processed for the collision.
    readcontainers: Environment
        The container containing the list of collisions.
    """
    def __init__(self, containersin, containersout, readcontainers):
        super(CollisionSampler, self).__init__(containersin, containersout, readcontainers)
        self.coll = None
        self.tank = None

    def read(self):
        """
        Reads in the first collision in the collision list and the contents of the tank.

        """
        super(CollisionSampler, self).read()
        self.coll = self.readcontainers.read()[0]
        self.tank = self.containersin.read()

    def pull(self):
        """
        Selects the boids involved in the collision from the tank and removes them.

        """
        self.sample = [boid for boid in self.tank if boid.id in self.coll]
        self.containersin.remove(self.sample)

    def push(self):
        """
        Places the needed boids into the sample container.

        """
        self.containersout.add(self.sample)


#   Collision action
class CollisionAction(node.Action):
    """
    Processes the effect of the collision by randomly selecting a number of parameters and swapping them between the boids.

    Parameters
    -----------
    containersin : Sample
        The sample containing the particles involved, should be the same as the containersout.
    containersout: Sample
        The sample for the return of the particles to the tank, should be the same as the containersin.
    """

    def __init__(self, containersin, containersout):
        super(CollisionAction, self).__init__(containersin, containersout)
        self.tank = containersin[0]
        self.containersout = containersout
        self.boid1 = None
        self.boid2 = None
        self.collenv = containersin[1]
        self.coll = None

    def read(self):
        """
        Reads in the boids involved in collision from the sample and the collision from the Environment.

        """
        [self.boid1, self.boid2] = self.tank.read()
        self.coll = self.collenv.read()

    def pull(self):
        """
        Empties out the sample and removes the first collision from the Environment.

        """
        self.tank.remove([self.boid1, self.boid2])
        self.collenv.remove(1)

    def check(self):
        return super(CollisionAction, self).check()

    def process(self):
        """
        Selects a number of parameters, 0-7, at random and then selects without replacement which of the 8 parameters
        will be swapped. These are then exchanged.

        """
        inds = random.sample(range(8), random.randrange(9))
        [self.boid2.r, self.boid1.r] = [self.boid1.r, self.boid2.r] if 0 in inds else False
        [self.boid2.vn, self.boid1.vn] = [self.boid1.vn, self.boid2.vn] if 1 in inds else False
        [self.boid2.vm, self.boid1.vm] = [self.boid1.vm, self.boid2.vm] if 2 in inds else False
        [self.boid2.c1, self.boid1.c1] = [self.boid1.c1, self.boid2.c1] if 3 in inds else False
        [self.boid2.c2, self.boid1.c2] = [self.boid1.c2, self.boid2.c2] if 4 in inds else False
        [self.boid2.c3, self.boid1.c3] = [self.boid1.c3, self.boid2.c3] if 5 in inds else False
        [self.boid2.c4, self.boid1.c4] = [self.boid1.c4, self.boid2.c4] if 6 in inds else False
        [self.boid2.c5, self.boid1.c5] = [self.boid1.c5, self.boid2.c5] if 7 in inds else False

    def push(self):
        """
        Puts the modified particles back in the sample.

        """
        self.containersout.add([self.boid1, self.boid2])


# observation logger - does all the things.
class VizLoggerObserver(node.Observer):
    """
    Combines the logging of visual information (The contents of the tank, positions and velocity of boids) and the
    clock tick.

    Parameters
    -----------
    containersin : Environment
        The clock environment containing the time variable.
    containersout : List<Environment>
        The Environment used to log the: tank, positions, velocities and the clock environment.
    readcontainers: Tank
        The current tank of particles being logged.
    """

    def __init__(self, containersin, containersout, readcontainers=None, index=None):
        super(VizLoggerObserver, self).__init__(containersin, containersout, readcontainers, index)
        self.tank = None
        self.positions = []
        self.velocities = []
        self.time = None

    def read(self):
        """
        Reads in the current state of the tank and the clock.

        """
        self.tank = self.readcontainers.read()
        self.time = self.containersin.read()[0]

    def pull(self):
        """
        Clears the clock variable.

        """
        super(VizLoggerObserver, self).pull()
        self.positions = []
        self.velocities = []
        self.containersin.remove([self.time])

    def process(self):
        """
        Get the position and velocity for each boid in the tank. Increment the time.

        """
        self.tank.sort()
        self.positions = [boid.currentposition for boid in self.tank]
        self. velocities = [boid.currentvelocity for boid in self.tank]
        self.time = self.time + 1

    def push(self):
        """
        Push out the tank, list of positions and velocities and the updated time to the correct environment.

        """
        self.containersout[0].add(tuple(self.tank))
        self.containersout[1].add(tuple(self.positions))
        self.containersout[2].add(tuple(self.velocities))
        self.containersout[3].add(self.time)


class VisualizerObserver(node.Observer):
    """
    Generates the graphs from each of the generations boid positions and puts them together into an animation.

    Parameters
    ----------

    readcontainers: Environment
        The environment container providing the positions of all the boids at each time step.
    bounds : List<int>
        The 4 item list x_min, x_max, y_min, y_max dictating the limited of the boids position and the size of graph.
    boid_size : float
        The size of the boid marker in the graph.
    gen_time : int
        Total number of generations in system.
    ani_steps : int
        Number of frames to produce per generation (dictates animation speed)
    writefile : string
        Name of save file for animation.
    """

    def __init__(self, readcontainers, bounds, boid_size, gen_time, ani_steps, writefile):
        super(VisualizerObserver, self).__init__(None, None, readcontainers)
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

    def read(self):
        """
        Reads in the boid positions and generates the Surface used to build the animation and ensures the coordinates
        are correctly formated.
        Returns
        -------

        """
        super(VisualizerObserver, self).read()
        self.world = Surface(self.readcontainers, self.particles, self.bounds, self.boid_size, self.ani_steps)
        self.viz_gens = self.readcontainers.read()
        for gen in self.viz_gens:
            for coord in gen:
                while isinstance(coord[0], list) or isinstance(coord[0], np.ndarray):
                    coord = coord[0]

    def pull(self):
        super(VisualizerObserver, self).pull()

    def process(self):
        """
        Creates a swarm animation based on the Surface and parameters given and converts it to a general animation.

        """
        super(VisualizerObserver, self).process()
        self.sa = SwarmAnimation(self.world, self.rect, self.viz_gens, self.gen_time, self.fig, self.ax, self.dt,
                                 self.boid_size)
        self.anim = animation.FuncAnimation(self.fig, self.sa.animate,
                                            frames=self.gen_time*self.ani_steps-self.ani_steps, interval=10, blit=True,
                                            init_func=self.sa.init)

    def push(self):
        """
        Saves and displays animation.

        """
        super(VisualizerObserver, self).push()
        Writer = animation.writers['ffmpeg']
        writer_inst = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        self.anim.save(self.file, writer=writer_inst)
        plt.show()


class Surface:
    """
    Builds the background and moving parts of the animation.

    Parameters
    -----------
    viz_gen : List<List<List<int>>>
        The list of positions of boids in each generation
    particles : plot marker
        The marker to be used to represent boids in the graph animation
    bounds : list<int>
        The min and max values for x and y for the graph edges.
    boid_size : int
        The size of the marker to be used for the particles.
    ani_steps : int
        the number of frames to be used per time step.
    """
    #    """init_state is an [N x 4] array, where N is the number of boids:
    #        [[x1, y1, vx1, vy1],
    #            [x2,y2,vx2,vy2],
    #            ...             ]
    #
    #        bounds is the size of the box: [xmin, xmax, ymin, ymax]
    #    """
    def __init__(self, viz_gen, particles, bounds=tuple([-150, 150, -150, 150]), boid_size=0.4, ani_steps=1):
        # generat initial state of swarm.rst from boids
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
        """
        The transition from one time step to the next to generate the next set of frames.

        Parameters
        ----------
        viz_gens : List<List<List<int>>>
            Positions of boid at each time step.
        i : int
            Current generation

        """
        # update velocities taken from swarm.rst and passed into surface/gen_time to give smoother generations
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
        """
        The definition of a transition change, takes the number of time steps to take for each animation step.

        Parameters
        ----------
        dt : int
            Number of time steps to take for each animation step.

        """
        # generation is defined as gen_time time steps
        self.time_elapsed = dt


class SwarmAnimation:
    """
    Runs the animation setup on the surface.

    Parameters
    ----------

    world : Surface
        The set up for the animation.
    rect : List<int>
        The set of x and y limits for a rectangle around the plot points.
    viz_gen : List<List<List<int>>>
        The positions of each boid at each time step.
    gen_time : int
        The number of generations that will need to be visualized.
    fig : plot
        Figure plot set up to take the graph of the boids
    ax : plot
        The axes for the plot.
    dt : int
        The number of generations to include in each animation step.
    boid_size: float
        The size of the boid marker on the graph.

    """

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
        """
        Sets up the animation.

        """
        self.world.particles.set_data([], [])
        self.rect.set_edgecolor('none')
        return self.world.particles, self.rect

    def animate(self, i):
        """
        Runs the animation for each step of size i.

        Parameters
        ----------
        i : int
            size of time step to take.

        Returns
        -------
        particles
            The set of markers for a graph.
        rect
            The rectangle which contains all the markers.

        """
        self.world.updatestep(self.viz_gens, i)
        self.ms = int(self.fig.dpi * 2 * self.world.size * self.fig.get_figwidth() / np.diff(self.ax.get_xbound())[0])
        self.rect.set_edgecolor('k')
        self.world.particles.set_data(self.world.state[:, 0], self.world.state[:, 1])
        self.world.particles.set_markersize(self.boid_size)
        return self.world.particles, self.rect
