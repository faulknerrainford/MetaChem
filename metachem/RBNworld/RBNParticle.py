"""
rbn particle class taken from Meta-AChem by Issac Watson.
"""
import numpy as np
from numpy import *
import pickle
from metachem import ParticleFactory, Particle


class RBNParticle(Particle):

    def __init__(self, rbns, bonded_spikes, open_spikes, spike_type=None, maxSizeAtom=250):
        super(RBNParticle, self).__init__()
        if len(rbns) == 1:
            self.atom = True
        self.id = tuple([rbn.id for rbn in rbns])
        self.atoms = rbns
        self.open_spikes = open_spikes
        self.bonds = bonded_spikes
        self.spike_type = spike_type
        # work this value out
        self.maxSizeAtom = maxSizeAtom

    def checkSpikes(self):
        broken_bond = None
        # calculate intensity of all spikes in molecule
        self.calculateIntensitySpikes(self.atoms)
        # check stability of all bonds
        for bond in self.bonds:
            # compare intensity of spikes in each bond
            spike1, rbn1, spike2, rbn2 = bond
            newIntensitySpk1 = spike1.intensity
            newIntensitySpk2 = spike2.intensity
            # This used to handle situation in which cycle length could not be found
            if newIntensitySpk1 == 'a' or newIntensitySpk2 == 'a':
                broken_bond = bond
                break
            elif spike1.type == 3 and spike2.type == 3:
                if 2 >= newIntensitySpk1 + newIntensitySpk2 >= -2:
                    continue
                else:
                    broken_bond = bond
                    break
            elif (spike1.type == 2 and spike2.type == 2) or (spike1.type == 2 and spike2.type == 3) or (
                    spike1.type == 3 and spike2.type == 2):
                if 1 >= newIntensitySpk1 + newIntensitySpk2 >= -1:
                    continue
                else:
                    broken_bond = bond
                    break
            else:
                if newIntensitySpk1 + newIntensitySpk2 == 0:
                    continue
                else:
                    broken_bond = bond
                    break
        # return first unstable bond found
        # else return none
        return broken_bond

    def breakBond(self, bond):
        current_bonds = self.bonds
        current_bonds.remove(bond)
        spike1, rbn1, spike2, rbn2 = bond
        spike1.bondBreak()
        spike2.bondBreak()
        self.open_spikes = self.open_spikes + [[spike1, rbn1], [spike2, rbn2]]
        # create two new particles
        particle1_rbns = [rbn1]
        particle2_rbns = [rbn2]
        particle1_closed = []
        particle2_closed = []
        particle1_open = []
        particle2_open = []
        # split atoms and spikes into correct lists for the different particles
        while current_bonds:
            # check closed bonds and redistribute them to the two particles including rbns
            for closed in self.bonds:
                if closed[1] in particle1_rbns:
                    if closed[3] not in particle1_rbns:
                        particle1_rbns.append(closed[3])
                        particle1_closed.append(closed)
                        current_bonds.remove(closed)
                elif closed[3] in particle1_rbns:
                    if closed[1] not in particle1_rbns:
                        particle1_rbns.append(closed[1])
                        particle1_closed.append(closed)
                        current_bonds.remove(closed)
                if closed[1] in particle2_rbns:
                    if closed[3] not in particle2_rbns:
                        particle2_rbns.append(closed[3])
                        particle2_closed.append(closed)
                        current_bonds.remove(closed)
                elif closed[3] in particle2_rbns:
                    if closed[1] not in particle2_rbns:
                        particle2_rbns.append(closed[1])
                        particle2_closed.append(closed)
                        current_bonds.remove(closed)
            # check all rbns assigned to particle, if rbn is assigned to both particles return the full particle with
            # the bond broken, handles circular bonding
            for rbn in self.atoms:
                if rbn not in particle1_rbns:
                    if rbn not in particle2_rbns:
                        # TODO: handle missed rbn
                        pass
                elif rbn in particle2_rbns:
                    return [self]
            # assign all open spikes
            for spike in self.open_spikes:
                if spike[1] in particle1_rbns:
                    particle1_open.append(spike)
                else:
                    particle2_open.append(spike)
        # return particles
        particle1 = RBNParticle(particle1_rbns, particle1_closed, particle1_open)
        particle2 = RBNParticle(particle2_rbns, particle2_closed, particle2_open)
        return [particle1, particle2]

    def calculateIntensitySpikes(self, mol):
        """ This function calculates the intensity of every spike in the molecule, it does this by updating the molecule
            and then calculating the intensity of evey spike
        """
        origStates = []
        for i in range(len(mol)):
            origStates.append(mol[i].states)
            mol[i].zeroRBN()
            # print ("The state matrix for atom " + str(i) + " is: \n" + str(mol[i].states) + "\n")
        for i in range(self.maxSizeAtom + 30):
            self.updateMolecule(mol)
        self.analyseMolecule(mol)
        for i in range(len(mol)):
            mol[i].setState(origStates[i], np.size(origStates[i], 0) - 1)

    def analyseMolecule(self, molecule):
        """ This function goes through every Atom in a molecule and calculates the intensity of the spikes,
        this is needed as bonding and unbonding causes spike intensity values to change
        """
        for i in range(len(molecule)):
            self.analyseAtom(molecule[i])

    @staticmethod
    def analyseAtom(rbn):
        """ Recalculation of intensity of an atom """
        for i in range(np.size(rbn.spikeArray)):
            # print ("The value of i is: " + str(i) + "\n")
            rbn.spikeArray[i].calcMolIntenisty()

    @staticmethod
    def updateMolecule(molecule):
        """ This function updates every RBN in a molecule synchronously, it does this by updating an RBN then popping
            its new state, before moving on to the next RBN, this ensures that every RBN is updated synchronously with
            the other RBNs. After this update and pop loop the popped states are appended to the RBNs
        """
        poppedStates = []  # Stores the popped states
        for i in range(len(molecule)):
            molecule[i].updateRBN()
            poppedStates.append(molecule[i].popState())

        # After all updated states found add these states back to atoms
        for i in range(len(molecule)):
            molecule[i].appendState(poppedStates[i])


class WatsonRBNParticleFactory(ParticleFactory):

    def __init__(self, numNodes, numConnections, index_start=0, seed=0, maxSizeAtoms=100):
        super(WatsonRBNParticleFactory, self).__init__()
        self.atom_num_nodes = numNodes
        self.atom_num_connections = numConnections
        self.index = index_start
        self.seed = seed
        self.spikeType = "Watson"
        self.maxSizeAtoms = maxSizeAtoms

    def createParticle(self, seed=None):
        super(WatsonRBNParticleFactory, self).createParticle(seed)
        rbn = RBN(self.atom_num_nodes, self.atom_num_connections, self.index, self.spikeType)
        self.index = self.index + 1
        return RBNParticle([rbn], [], [(spike, rbn) for spike in rbn.spikeArray], self.spikeType, self.maxSizeAtoms)


class RBN:

    def __init__(self, numNodes, numConnections, rbnNumber, spikeType="Watson", seed=None):
        """
        Method which initializes the rbn by assigning internal variables there value and calling a method which
        creates the internal structure of the rbn

        Parameters
        ----------
        numNodes        :   int
            Number of nodes to be included in the rbn
        numConnections  :   int
            Number of incoming edges for each node
        rbnNumber       :   int
            ID number of rbn for tracking

        Returns
        -------
        RBN
            The generated rbn in its initial state with all nodes in state 0.
        """
        self.n = numNodes
        self.k = numConnections
        self.rbnNumber = rbnNumber
        self.nodeArray = array([], dtype=Node)  # Create array which can be filled with nodes
        self.spikeArray = array([], dtype=WatsonSpike)
        self.bonded = False  # Boolean used to indicate if rbn is bonded to another rbn
        self.bondedRBNs = []
        self.states = array([], dtype=int)  # Matrix to hold states of each node
        self.numIterations = 0  # Number of times rbn has been run
        self.activeSpikes = array([], dtype=int)  # Stores the spike numbers of the spikes which are currently
        # involved in bonds
        self.type = 0  # The type of rbn is determined by the number of spikes it has
        self.spikeType = spikeType
        self.seed = seed
        self.createRBN()
        self.generateSpikes()

    def createRBN(self):
        """
        This method creates a rbn by generating an array of nodes and assigning each node its connections to other
        nodes and its internal function
        """
        # First generate connection matrix
        con = apply_along_axis(random.permutation, 1, tile(range(self.n), (self.n, 1)))[:, 0:self.k]
        # print ("The original connection matrix is: " + str(con) + "\n")

        # Next generate boolean function matrix which maps how node reacts to inputs
        booleanFuncs = random.randint(0, 2, (self.n, 2 ** self.k))

        # Fill array with appropriate number of nodes and give each node its
        # connections
        for i in range(self.n):
            self.nodeArray = append(self.nodeArray, Node(i, self, booleanFuncs[i,], self.k))

        for i in range(self.n):
            # Generate a new node object
            # self.nodeArray = append(self.nodeArray,node.Node(i,self,booleanFuncs[i,],self.k))
            for j in range(self.k):
                # Add connections to newly generated node
                # print ("The node number to add is: " + str(con[i,j]) + "\n")
                self.nodeArray[i].addConnection(self.nodeArray[con[i, j]])
            self.states = append(self.states, self.nodeArray[i].state)  # Add state of node to create initial state

    def generateSpikes(self):
        if self.spikeType == "Watson":
            self.generateWatsonSpikes()

    def generateWatsonSpikes(self):
        """ This function generates the spikes that the rbn uses to bond with
            other RBNs, the function is split into two smaller functions
            one calculates the nodes in the spike and the other
            the properties of the spike
        """
        # Generates the spikes
        self.findSpikeNodes()
        # Finally spikes with zero intensity are removed as they are considered 'inert' and give each remaining spike a
        # fixed spike number
        self.intensityOfSpikes()
        self.removeZeroIntensitySpikes()
        for i in range(size(self.spikeArray)):
            self.type += 1
            self.spikeArray[i].setSpikeNum(i)

    def findSpikeNodes(self):
        """ This function finds the number of spikes and the nodes in them
            the algorithm to do this is described throughout this function
        """
        # First generate set of nodes by randomly sorting the list of node numbers
        setOfNodes = arange(self.n)

        random.shuffle(setOfNodes)

        # While the set of nodes is not empty
        while size(setOfNodes) != 0:
            # Next we select a node from this list
            node = setOfNodes[0]
            # Remove node from set
            setOfNodes = delete(setOfNodes, [0])
            # Generate a new spike
            self.spikeArray = append(self.spikeArray, WatsonSpike(0, self))
            # Append node to spike
            self.spikeArray[size(self.spikeArray) - 1].addNode(self.nodeArray[node])

            # Get list of node connections, note we can discard second row as all nodes will be bonded to this rbn
            inputList = self.nodeArray[node].returnConnections()
            # While there are still nodes in the input list
            while (size(inputList) != 0):
                # The next node is randomly selected from the input lis
                nextNodeIndex = random.randint(0, size(inputList))
                nextNode = inputList[nextNodeIndex]
                # The next node is then removed from the input list
                inputList = delete(inputList, nextNodeIndex)

                if nextNode.nodeNumber in setOfNodes:
                    indexToDelete = int(where(setOfNodes == nextNode.nodeNumber)[0])
                    setOfNodes = delete(setOfNodes, indexToDelete)
                    self.spikeArray[size(self.spikeArray) - 1].addNode(self.nodeArray[nextNode.nodeNumber])
                    node = nextNode
                    inputList = self.nodeArray[node.nodeNumber].returnConnections()

    def intensityOfSpikes(self):
        """ This function is used to calculate the intensity of each spike it works by going through each spike and
        calling a function in the spike class which calculates the intensity. Note the flashiness of each node is
        stored is the spike class so the only data that needs to be passed to it is the cycle length
        """
        for i in range(size(self.spikeArray)):
            self.spikeArray[i].calculateInitialIntensity()

    def removeZeroIntensitySpikes(self):
        """ This function scans through the list of spikes and removes the ones with zero intensity, this is done
            as zero intensity is considered an 'inert' spike which can't bond with anything
            also removes spikes with only one node as they cannot swap links with other spikes
        """
        spikesToBeDeleted = array([], dtype=int)
        for i in range(size(self.spikeArray)):
            if self.spikeArray[i].returnSize() == 1 or self.spikeArray[i].intensity == "a" or \
                    self.spikeArray[i].intensity == 0:
                spikesToBeDeleted = append(spikesToBeDeleted, i)
        for i in range(size(spikesToBeDeleted) - 1, -1, -1):
            self.spikeArray = delete(self.spikeArray, spikesToBeDeleted[i])

    def resetRBN(self):
        """ This function resets a rbn by giving the state matrix of the rbn
            the initial value of the State matrix and then resetting number of iterations
            after this the state of the nodes is reset
        """

        if ndim(self.states) > 1:
            # print ("Original states is: \n" + str(self.states) + "\n" )
            self.states = self.states[0,]
            # print (" New states is: \n" + str(self.states) + "\n" )
            self.numIterations = 0

            for i in range(size(self.n)):
                self.nodeArray[i].changeState(self.states[i])
        else:
            # print ("Original states is: \n" + str(self.states) + "\n" )
            self.states = self.states
            # print (" New states is: \n" + str(self.states) + "\n" )
            self.numIterations = 0

            for i in range(size(self.n)):
                self.nodeArray[i].changeState(self.states[i])

    def findCycleLength(self):
        """
        This calculates the cycle length of a rbn with starting conditions given by current state and connections of
        each node in the rbn, this function is called after a bond occurs as cycle length could change

        Returns
        --------
        int
            length of the attractor cycle of the rbn or -1 for an error in calculating the cycle length

        """
        #
        originalStateMatrix = self.states  # Store the original matrix
        originalNumIteration = self.numIterations
        numAttempts = self.n
        numRBNUpdate = self.n + 30
        # print ("The number of attempts is: " + str(numAttempts) + "\n")
        for i in range(numAttempts):
            for j in range(i):
                self.updateRBN()
            self.selectMostRecentState()
            # stateOfRBN = self.states
            # Run rbn for this number of time
            for k in range(1, numRBNUpdate):
                self.updateRBN()
                stateOfRBN = self.states
                # print ("The state of the rbn is now: " + str(spike.rbn.states) + "\n")
                # print ("The first row is: " + str(stateOfRBN[0,:]) + "\n")
                # print ("The last row is: " + str(stateOfRBN[k,:]) + "\n")
                if array_equal(stateOfRBN[0, :], stateOfRBN[k, :]):
                    self.popState()
                    #       print ("The cycle length is: " + str(spike.rbn.numIterations) + "\n")
                    # Need to pop last state
                    # for i in range(size(spike.nodeList)):
                    # print ("Node in spike: " + str(spike.nodeList[i].nodeNumber) + "\n")
                    # print ("The state matrix is: " + str(self.states) + "\n")
                    count = k
                    self.setState(originalStateMatrix, originalNumIteration)
                    return count
            self.zeroRBN()

        return -1

    def returnMostRecentNodeState(self, nodeNumber):

        if self.numIterations == 0:
            print("In the IF Statement \n")
            print("The node number is: " + str(nodeNumber) + "\n")
            print("The state matrix is: \n" + str(self.states) + "\n")

            return self.states[nodeNumber]
        else:
            # print ("In else statement \n")
            return self.states[self.numIterations, nodeNumber]

    def selectMostRecentState(self):
        """ This function resets the rbn, with the starting state being equal
            to the final state before the reset
        """

        # print ("Number of iteration before reset is: " + str(self.numIterations) + "\n")
        # print ("The rbn number is: " + str(self.rbnNumber) + "\n")
        self.numIterations = 0
        if self.states.ndim == 1:
            for i in range(self.n):
                self.nodeArray[i].state = self.states[i]
            # print ("In this area \n")
            return
        else:
            self.states = self.states[size(self.states, 0) - 1,]
        # print ("The state matrix is: "  + str(self.states) + "\n")

        for i in range(size(self.states)):
            self.nodeArray[i].state = self.states[i]

    def popState(self):
        """ This function removes state given by iterNumber and returns the state value
            and decrements the number of iterations
        """
        # print ("The number of rows is: " + str(size(self.states,0)) + "\n")
        # print ("The number of iterations is: " + str(self.numIterations) + "\n")
        state = self.states[size(self.states, 0) - 1,]
        self.states = delete(self.states, size(self.states, 0) - 1, 0)
        self.numIterations -= 1
        # print ("Number of iterations is: " + str(self.numIterations) + "\n")
        if self.numIterations == 0:
            self.states = self.states.flatten()
            for i in range(self.n):
                self.nodeArray[i].changeState(self.states[i])
        else:
            for i in range(self.n):
                self.nodeArray[i].changeState(self.states[size(self.states, 0) - 1, i])
        # print ("The state to be returned is: " + str(state) + "\n")
        return state

    def returnStateMatrix(self):
        """ This returns the state matrix associated with this rbn """
        return self.states

    def setState(self, stateMatrix, numIterations):
        # print ("New state is: " + str(stateMatrix) + "\n")
        # print ("New num iters is: " + str(numIterations) + "\n")
        self.numIterations = numIterations
        self.states = stateMatrix
        if self.states.ndim == 1:
            for i in range(self.n):
                self.nodeArray[i].changeState(stateMatrix[i])
        else:
            for i in range(self.n):
                # print ("States is: " + str(self.states) + "\n")
                # print ("Rows: " + str(size(self.states,0)) + "\n")
                self.nodeArray[i].changeState(stateMatrix[(size(self.states, 0) - 1), i])
        self.numIterations = size(self.states, 0) - 1

    def zeroRBN(self):
        self.states = array([], dtype=int)
        self.numIterations = 0
        for i in range(self.n):
            self.states = append(self.states, 0)
        for i in range(self.n):
            self.nodeArray[i].state = 0

    def updateRBN(self):
        """ This function works by calling the update state function for each
            node then appending thew new state of each node to a new
            row in the state matrix
        """
        # Generate new array to store the new state of node
        newStates = empty([self.n], dtype=int)
        for i in range(self.n):
            origState = self.nodeArray[i].state
            self.nodeArray[i].calculateState()
            # print ("Return state is: " + str(self.nodeArray[i].returnState()) + "\n")
            newStates[i] = self.nodeArray[i].state
            self.nodeArray[i].state = origState

        self.numIterations += 1
        # Append new states to state matrix
        self.states = vstack((self.states, newStates))

        # Update nodes with new state
        for i in range(self.n):
            self.nodeArray[i].state = newStates[i]

    def rbnBonded(self, spikeNum, bondedRBN):
        """ This function adds a spike to the list of spikes involved in a bond """
        self.bonded = True
        self.activeSpikes = append(self.activeSpikes, spikeNum)
        self.bondedRBNs.append(bondedRBN)

    def appendState(self, state):
        """ This function appends a state passed in as an argument and
            increments number of states and updates node values
        """
        self.states = vstack((self.states, state))

        # print ("The number of iterations is: " + str(self.numIterations) + "\n")
        for i in range(self.n):
            if self.states[size(self.states, 0) - 1, i] != 0 and self.states[size(self.states, 0) - 1, i] != 1:
                print("Error the most recent state is \n" + str(self.states) + "\n")
            self.nodeArray[i].changeState(self.states[size(self.states, 0) - 1, i])
        self.numIterations += size(self.states, 0) - 1

    def rbnUnbonded(self, spikeNum, bondedRBN):
        """ This function removes a spike from the list of spikes involved in a bond
            and if there are no more spikes in the active spike array then the state of
            the rbn is set to unbonded
        """
        # Need to remove spike num from list of active spikes
        # print ("Before spike removal: \n" + str(self.activeSpikes) + "\n")
        self.activeSpikes = setdiff1d(self.activeSpikes, spikeNum)  # This numpy function will remove spikeNUm
        # print ("After spike removal: \n" + str(self.activeSpikes) + "\n")

        if size(self.activeSpikes) == 0:
            self.bonded = False

        for i in range(len(self.bondedRBNs)):
            if self.bondedRBNs[i] == bondedRBN:
                self.bondedRBNs.pop(i)
                break


class Node:
    """ A node is a building block of a rbn it takes k number of connections from other nodes
        and has a boolean function which determines how the state of the node changes
        in response to the state of its inputs
    """

    def __init__(self, nodeNumber, rbn, boolFunc, numConnections):
        """ This method initializes the node object with its node number, rbnNumber
            and function
        """
        self.nodeNumber = nodeNumber
        self.rbn = rbn  # rbn node is part of
        self.state = random.randint(0, 2)
        self.boolFunc = boolFunc
        self.connections = array([], dtype=Node)

        self.numConnections = numConnections
        self.bonded = False  # This is triggered if the rbn is involved in a bond

    def addConnection(self, inputNode):
        """ This method adds an input to the node it takes the
            input node number and the rbn number the node is part of
        """
        self.connections = append(self.connections, inputNode)

    def calculateState(self):
        """ This function is used to determine how to calculate the state of the node
            if the node is involved with a bond a special function has to be called in order to calculate
            the state, if it is not involved in a bond then a simpler function can be called
        """
        sumOfStates = 0
        power_local = 1
        for i in range(self.numConnections):
            # print ("The value of i is: " + str(i) + "\n")
            connectedNode = self.connections[i]
            power_local = 2 ** i
            # print ("The value of power_local is: " + str(power_local) + "\n")
            mostRecentState = connectedNode.state
            if mostRecentState != 0 and mostRecentState > 1:
                mostRecentState = 1
                connectedNode.rbn.fixStateMatrix()
            sumOfStates = (power_local * mostRecentState) + sumOfStates

        # print ("The value of sum of states is: " + str(sumOfStates) + "\n")

        if sumOfStates >= size(self.boolFunc):
            print("Error occurring \n")
            print("The number of connections is: " + str(self.numConnections) + "\n")
            print("The node rbn number is: " + str(self.rbn.rbnNumber) + "\n")
            print("The power_local value is: " + str(power_local) + "\n")
            print("Connections and their rbn numbers \n")
            for i in range(size(self.connections)):
                print("The connected number is: " + str(self.connections[i].nodeNumber) + " the rbn is " + str(
                    self.connections[i].rbn.rbnNumber) + "\n")
            print("The boolean function is:\n" + str(self.boolFunc) + "\n")
            print("Actual number of connections is: " + str(size(self.connections)) + "\n")
            print("rbn State matrix is: \n")
            self.rbn.printStateMatrix()

            pickle_out = open("ErrorBond", "wb")
            pickle.dump(self.rbn, pickle_out)
            pickle_out.close()

        self.state = self.boolFunc[sumOfStates]
        return self.state

    def returnConnections(self):
        """ This method returns the matrix which shows the connections of the node and the RBNs those connections
            come from
        """
        return self.connections

    def changeState(self, newState):

        if newState != 1 and newState != 0:
            print("Error invalid state: " + str(newState) + "\n")
            newState = 1

        self.state = newState

    def changeConnection(self, changedConnection, newConnection):
        """ This function changes the connection list of the new node, this means that the node will now
            be receiving an input from somewhere else
        """
        # First have to find index of connection we are going to change
        for i in range(self.numConnections):
            if self.connections[i] == changedConnection:
                self.connections[i] = newConnection
                break

    def involvedInBond(self, changedConnection, newConnection):
        self.bonded = True
        # self.rbnArray = append(self.rbnArray,RBNOrigin) # Appends rbn node is part of to list
        # self.rbnArray = append(self.rbnArray,RBNNewConnection) # Appends rbn the node is bonded too to the list
        self.changeConnection(changedConnection, newConnection)

    def bondBroken(self, expectedNode):
        """ This function is called when the spike the node is in has a bond which becomes unstable, this function
        links the node up to another node passed in as an argument, this other node is located in the same rbn as
        this node. The nodes connection list is then changed
        """
        self.bonded = False

        # Search through bottom row of connection list until bonded rbn is found, as bond is breaking
        # we want to remove this connection to the other rbn

        for i in range(self.numConnections):
            if self.connections[i].rbn.rbnNumber != self.rbn.rbnNumber:  # Search until connection to other rbn is found
                # Once found replace the connection with the new node
                self.connections[i] = expectedNode


class WatsonSpike:
    """ The spike class is used by the rbn to determine whether the rbn should bond to another rbn
        bonding occurs when two spikes interact and share links between nodes. WatsonSpike class contains data such as
        nodes in spikes, rbn spike is part of and whether the spike is involved in a bond or not
    """

    def __init__(self, spikeNumber, rbn):
        self.intensity = None
        self.bondedSpikeNum = None
        self.nodeList = array([], dtype=Node)  # Stores nodes in the spike
        self.bonded = False  # Boolean to indicate if spike is involved in a bond or not initially all spikes are not
        # bonded
        self.RBN = rbn  # Stores the rbn the spike is part of

        self.spikeNumber = spikeNumber
        self.bondedRBN = 0
        self.checked = False  # This boolean is used to indicate whether the spike has been checked when
        # recalculating intensity
        self.danglingBonds = []  # This stores dangling bonds in the spike, dangling bonds are bonds not involved in
        # bonding
        self.numDanglingBonds = 0  # Stores number of dangling bonds

        # The type of node is dependent on the size of the spike
        self.type = 1

    def addNode(self, node):
        """ This function adds a node to the spike and adds the nodes
            flashiness to the flashiness array
        """
        self.nodeList = append(self.nodeList, node)
        # Check to see if type of spike can change
        if 5 <= len(self.nodeList) < 10:
            self.type = 2
        elif len(self.nodeList) >= 10:
            self.type = 3

        if self.bonded:
            print("called when bonded \n")

    def setSpikeNum(self, spikeNum):
        """ This function sets the spike number """
        self.spikeNumber = spikeNum

    def returnSpkNum(self):
        return self.spikeNumber

    def hasBonded(self, rbn, bondedSpikeNum):
        """ This function is called when spike is involved in a bond, it sets the boolean variable
            indicating whether spike has bonded to true
        """
        self.bonded = True  # Update bonding status of spike
        self.bondedRBN = rbn  # Store rbn  spike is bonded too
        self.bondedSpikeNum = bondedSpikeNum  # Stores the spike num the spike is bonded to
        # Update rbn that spike is part of with new bonding infor
        self.RBN.rbnBonded(self.spikeNumber, rbn)

    def addDanglingBonds(self, numDangleNodes):
        """ This function is called after a spike has bonded, it takes the number of dangling bonds the spike will
        have,dangling bonds are bonds  which has not been involved in the linking with another rbn, the function will
        then place the first nodes in the node array into the dangling bond array as these nodes will be the ones
        which are not involved in the bonding, the variable contains a number of bonds which will also be updated
        """
        # Add nodes to dangle bond array print ("The number of dangling nodes is: " + str(numDangleNodes) + "\n")
        # print ("The length of the spike is: " + str(size(self.nodeList)) + "\n") print ("The length of the bonded
        # spike is: " + str(size(self.bondedRBN.spikeArray[self.bondedSpikeNum].nodeList)) + "\n")
        self.danglingBonds = []
        for i in range(numDangleNodes):
            self.danglingBonds = append(self.danglingBonds, self.nodeList[i])

        self.numDanglingBonds = numDangleNodes  # update number

    def bondBreak(self):
        """ This function is called when the bond between two bonds breaks, this function works
            by starting at the bottom index of the list of nodes and connecting it to the node
            below. Finally, the bonding state of the node is set to false and the rbn is updated to
            reflect the fact that the bond has been broken
        """
        self.bonded = False  # Set the bonding status of the bond to false as spike is now unbonded

        # Next go through each node reconnecting it to the node after it in order to
        # reform the spike to the connection list it had before the bond formed
        for i in range(size(self.nodeList) - 1):
            self.nodeList[i].bondBroken(self.nodeList[i + 1])
        # print ("Before In the function intensity is: " + str (self.intensity) + "\n")
        # print ("The state of the the rbn is: \n")
        # self.rbn.printMostRecentState()
        # Need to recalculate intensity
        # self.recalculateIntensity()

        # print ("after In the function intensity is: " + str (self.intensity) + "\n")

        # Need to update rbn to inform it that bond has broken
        self.RBN.rbnUnbonded(self.spikeNumber, self.bondedRBN)
        # Need to update dangling bonds
        self.danglingBonds = []
        self.numDanglingBonds = 0

        # Can remove reference to bonded rbn as no longer needed
        self.bondedRBN = 0
        self.bondedSpikeNum = -1  # Set to -1 as invalid spike num

    def returnNodeArray(self):
        return self.nodeList

    def calculateInitialIntensity(self):
        """ This function calculates the initial intensity of the spike
           it works by calling a function which works by
           finding the cycle length of rbn (only stores states of nodes in spikes)
           the intensity is sum of weighted transitions, 0-1 transition is +1, 0-1 transition is -1
        """

        calculateIntensity(self)  # See function script for more detail
        # print ("The intensity is: " + str(self.intensity) + "\n")
        self.intensity = calculateIntensity(self)
        return self.intensity

    def recalculateIntensity(self):
        """ This function is used to recalculate the intensity of a spike after the spike has formed a bond
            it works in the same way as the function above but updates the other rbn when finding the cycle
        """
        self.intensity = calculateIntensity(self)  # See function script for more detail
        return self.intensity

    def calcMolIntenisty(self):
        self.intensity = findMolecularIntensity(self)

    def calcMolIntenistyDebug(self):
        self.intensity = findMolecularIntensityDebug(self)

    def returnIntensity(self):
        """ This function returns the intenisty of the spike """
        return self.intensity

    def changeNodeArray(self, newNodeArray):
        """ This function changes the nodes (or properties of the nodes), this is called when spike is involved in a
        bond """
        self.nodeList = newNodeArray

    def printNodeArray(self):
        print("The node list is: \n")
        for i in range(size(self.nodeList)):
            print(str(self.nodeList[i].nodeNumber))
            print("  ")

    def returnSize(self):
        """ Returns the number of nodes in the spike """
        return size(self.nodeList)

    def returnBondedRBN(self):
        """ Returns the rbn the spike is bonded to """
        return self.bondedRBN

    def setBondedRBN(self, rbn):
        """ Sets the rbn the spike is bonded to """
        self.bondedRBN = rbn


def calculateIntensity(spike):
    # First need to store the original state of rbn Nodes
    # print ("The original states: " + str(spike.rbn.states) + "\n")

    originalStateRBNNodes = spike.RBN.states
    origNumIters = spike.RBN.numIterations
    spike.RBN.zeroRBN()
    # print ("State rbn after reset is: " + str(spike.rbn.states) + "\n")
    intensity = findIntensity(spike)
    spike.RBN.setState(originalStateRBNNodes, origNumIters)

    # spike.bondedRBN.setState(originalStateBRBNNodes,origNumItersBonded)
    # print ("before resetting states: " + str(originalStateRBNNodes) + "\n")

    # print ("After resetting states: " + str(originalStateRBNNodes) + "\n")
    # print ("Returns back to here \n")
    return intensity


def findIntensity(spike):
    # First need to store the original state of rbn Nodes
    originalStateRBNNodes = []
    for i in range(spike.RBN.n):
        originalStateRBNNodes.append(spike.RBN.nodeArray[i].state)

    # Stores the state of nodes in each update
    stateNodes = zeros(spike.RBN.n, dtype=int)

    # Reset the rbn
    spike.RBN.resetRBN()

    # Add initial states to array
    for i in range(spike.RBN.n):
        stateNodes[i] = spike.RBN.states[i]

    stateNodes = findUnbondedAttractorCycle(spike)

    #   print ("After function state nodes is \n" + str(stateNodes) + "\n")

    # print ("The transposed array is: \n"  + str(trans) + "\n")

    intensity = newFinalStage(stateNodes, spike)
    # for i in range (len(spike.nodeList)):
    #   print ("Nodes in spike: " + str(spike.nodeList[i].nodeNumber) + "\n")
    # print ("The intensity is: " + str(intensity) + "\n")
    return intensity


def findMolecularIntensity(spike):
    stateNodes = findMolecularAttractorCycle(spike)
    intensity = newFinalStage(stateNodes, spike)
    # print ("The intensity is:\n " + str(intensity) + "\n")
    return intensity


def findMolecularAttractorCycle(spike):
    for i in range(size(spike.RBN.states, 0)):
        for j in range(i + 1, size(spike.RBN.states, 0)):
            # print ("The state matrix is currently: " + str(spike.rbn.states) + "\n")
            # print ("First row: " + str(spike.rbn.states[i,:]) + "\n")
            # print ("Second row: " + str(spike.rbn.states[j,:]) + "\n")
            if array_equal(spike.RBN.states[i, :], spike.RBN.states[j, :]):
                # print ("The spike number is: " + str(spike.spikeNumber) + "\n")
                # print ("The rbn number is: " + str(spike.rbn.rbnNumber) + "\n")
                # print ("Returning:\n" + str(spike.rbn.states[i:j,]) + "\n")
                return spike.RBN.states[i:j, ]


def findUnbondedAttractorCycle(spike):
    # We will run rbn for n + 30 times, where n is number of nodes in RBM

    numAttempts = spike.RBN.n
    numRBNUpdate = spike.RBN.n + 30
    # print ("The number of attempts is: " + str(numAttempts) + "\n")
    for i in range(numAttempts):
        # print ("Initial state is: " + str(stateOfRBN) + "\n")
        for j in range(i):
            # print ("Inside for loop \n")
            spike.RBN.updateRBN()
        spike.RBN.selectMostRecentState()
        # print ("The states are now: " + str(spike.rbn.states) + "\n")
        # print ("The other matrix has the value: " + str(stateOfRBN) + "\n")

        # Run rbn for this number of time
        for k in range(1, numRBNUpdate):
            spike.RBN.updateRBN()
            stateOfRBN = spike.RBN.states
            # print ("The state of the rbn is now: " + str(spike.rbn.states) + "\n")
            # print ("The first row is: " + str(stateOfRBN[0,:]) + "\n")
            # print ("The last row is: " + str(stateOfRBN[k,:]) + "\n")
            if array_equal(stateOfRBN[0, :], stateOfRBN[k, :]):
                spike.RBN.popState()
                # print ("The cycle length is: " + str(spike.rbn.numIterations) + "\n")

                # Need to pop last state
                # for i in range(size(spike.nodeList)):
                # print ("Node in spike: " + str(spike.nodeList[i].nodeNumber) + "\n")
                # print ("The states are: \n" + str(spike.rbn.states) + "\n")
                return spike.RBN.states

        spike.RBN.resetRBN()
        # print ("After fail states: " + str(spike.rbn.states) + " \n")


def newFinalStage(states, spike):
    # Fist store list node number
    nodeNumbers = []
    for i in range(size(spike.nodeList)):
        nodeNumbers.append(spike.nodeList[i].nodeNumber)
    # print ("The node numbers are: " + str(nodeNumbers) + "\n")
    # print ("Number of columns: " + str(size(states,1)) + "\n")
    # print ("Number of rows: " + str(size(states,0)) + "\n")
    # print ("The states are \n " + str(states) + "\n")
    # print ("Number of dimensions is: " + str(states.ndim) + "\n")

    # First check that a cycle has been found if not then return a string to indicate failure
    if states is None:
        return 'a'

    if states.ndim == 1:
        states = atleast_2d(states)
    intensity = 0
    # Go through each column
    for i in range(size(states, 1)):
        # Go through each row
        # print ("Column number " + str(i) +  "\n" )
        currentSum = 0
        if i in nodeNumbers:
            # print ("Starting value for sum: " + str(currentSum) + "\n")
            for j in range(size(states, 0)):
                # print ("State matrix is: " + str(states) + "\n")
                # print ("Row number " + str(j) +  "\n" )
                # print (" Element value is: " + str(states[j,i]) + "\n")
                if states[j, i] == 1:
                    currentSum += 1
                    # print ("Current sum value: " + str(currentSum) + "\n")
                else:
                    currentSum -= 1
                    # print ("Current sum value: " + str(currentSum) + "\n")

            # print ("Current sum final value: " + str(currentSum) + "\n")
            if currentSum == size(states, 0):
                intensity += 1
            elif currentSum == (size(states, 0) * -1):
                intensity -= 1

    # print ("The intensity is: " + str(intensity) + "\n")
    return intensity


def findMolecularIntensityDebug(spike):
    stateNodes = findMolecularAttractorCycleDebug(spike)
    intensity = newFinalStage(stateNodes, spike)
    print("The intensity being returned is: " + str(intensity) + "\n")
    return intensity


def findMolecularAttractorCycleDebug(spike):
    print("The starting matrix is: " + str(spike.RBN.states))
    for i in range(size(spike.RBN.states, 0)):
        for j in range(i + 1, size(spike.RBN.states, 0)):
            # print ("The state matrix is currently: " + str(spike.rbn.states) + "\n")
            # print ("First row: " + str(spike.rbn.states[i,:]) + "\n")
            # print ("Second row: " + str(spike.rbn.states[j,:]) + "\n")
            if array_equal(spike.RBN.states[i, :], spike.RBN.states[j, :]):
                print("Returning: " + str(spike.RBN.states[i:j, ]) + "\n")
                return spike.RBN.states[i:j, ]
