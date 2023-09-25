# Set of generic classes for general use in Artificial Chemistries

import metachem.CoreNode as CoreNode


# Basic containers using lists/nested lists


class ListTank(CoreNode.Tank):
    """
    Tank which stores particles in a list.

    """

    def __init__(self, graph):
        super(ListTank, self).__init__(graph)
        self.list = None
        pass

    def read(self):
        """
        Returns copy of full tank.

        Returns
        -------
        list: List<>
            List of particles

        """
        if self.list:
            return self.list[:]
        else:
            return self.list

    def add(self, particles=None):
        """
        Adds particles to end of tank list.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be appended to existing internal list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            self.list = self.list + particles
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        Removes the listed particles from the tank.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be found and removed from tank list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if self.list and isinstance(self.list[0], list) and not isinstance(particles[0], list):
            self.list.remove(particles)
        elif not isinstance(particles, list):
            self.list.remove(particles)
        elif self.list:
            [self.list.remove(part) for part in particles]
        return self.list


class ListSample(CoreNode.Sample):
    """
    Sample which stores particles in a list.

    """

    def __init__(self, graph):
        super(ListSample, self).__init__(graph)
        self.list = []
        pass

    def read(self):
        """
        Returns copy of full sample.

        Returns
        -------
        list: List<>
            List of particles

        """
        return self.list[:]

    def add(self, particles=None):
        """
        Adds particles to end of sample list.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be appended to existing internal list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            if isinstance(particles, list):
                self.list = self.list + particles
            else:
                self.list.append(particles)
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        Removes the listed particles from the sample.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be found and removed from sample list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if particles == self.list:
            self.list = []
        elif not isinstance(particles, list):
            self.list.remove(particles)
        else:
            [self.list.remove(part) for part in particles]
        return self.list


class ListEnvironment(CoreNode.Environment):
    """
    Environment which stores variables in a list.

    """

    def __init__(self, graph):
        super(ListEnvironment, self).__init__(graph)
        self.list = []
        pass

    def read(self):
        """
        Returns copy of full environment.

        Returns
        -------
        list: List<>
            List of variables

        """
        return self.list[:]

    def add(self, variables=None):
        """
        Adds variables to end of environment list.

        Parameters
        ----------
        variables: List<Variable>
            List of variables to be appended to existing internal list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            self.list.append(variables)
        elif isinstance(variables, list):
            self.list = variables
        else:
            self.list = [variables]
        return self.list

    def remove(self, variables=None):
        """
        Removes the listed variables from the environment.

        Parameters
        ----------
        variables : List<Variable>
            List of variables to be found and removed from the Environment list.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if variables and isinstance(variables, list):
            [self.list.remove(var) for var in variables]
        elif variables:
            self.list.remove(variables)
        return self.list


class StackTank(ListTank):
    """
    A tank which uses a stack for storage of particles.
    """

    def __init__(self, graph):
        super(StackTank, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the tank.

        Returns
        -------
        List<Particle>

        """
        return super(StackTank, self).read()

    def add(self, particles=None):
        """
        Pushes list of particles onto the top of the tank stack.

        Parameters
        ----------
        particles : List<Particle>
            Particles to be added to stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            self.list = particles + self.list
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        The length n of the particle list is used to pop the top n particles from the stack, removing them from the
        container.

        Parameters
        ----------
        particles : List<Particle>
            particles list length of which is to be used to remove particles from stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class StackSample(ListSample):
    """
    A sample which uses a stack for storage of particles.
    """

    def __init__(self, graph):
        super(StackSample, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the sample.

        Returns
        -------
        List<Particle>

        """
        return super(StackSample, self).read()

    def add(self, particles=None):
        """
        Pushes list of particles onto the top of the sample stack.

        Parameters
        ----------
        particles : List<Particle>
            Particles to be added to stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            self.list = particles + self.list
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        The length n of the particle list is used to pop the top n particles from the stack, removing them from the
        container.

        Parameters
        ----------
        particles : List<Particle>
            particles list length of which is to be used to remove particles from stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class StackEnvironment(ListEnvironment):
    """
    An Environment which uses a stack for storage of variables.
    """

    def __init__(self, graph):
        super(StackEnvironment, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the environment.

        Returns
        -------
        List<Particle>

        """
        return super(StackEnvironment, self).read()

    def add(self, variables=None):
        """
        Pushes list of variables onto the top of the environment stack.

        Parameters
        ----------
        variables : List<Variable>
            Variables to be added to stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(variables)
            self.list = variables + self.list
        elif isinstance(variables, list):
            self.list = variables
        else:
            self.list = [variables]
        # print len(self.list)
        return self.list

    def remove(self, variables=None):
        """
        The length n of the variable list is used to pop the top n variables from the stack, removing them from the
        container.

        Parameters
        ----------
        variables : List<Variable>
            variables list length of which is to be used to remove particles from stack.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(variables, list):
            self.list = self.list[len(variables):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueTank(ListTank):
    """
    Tank using a queue for storage
    """

    def __init__(self, graph):
        super(QueueTank, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the queue.

        Returns
        -------
        List<particles>
            list of the queue contents.

        """
        return super(QueueTank, self).read()

    def add(self, particles=None):
        """
        Add the given particles to the end of the queue.

        Parameters
        ----------
        particles : List<Particle>
            particles to be added to the container.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            self.list = self.list + particles
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        Remove particles from front of queue equal in number to length of particles.

        Parameters
        ----------
        particles : List<Particle>
            list of particles, length of which is used for removing particles from the queue

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueSample(ListSample):
    """
    Sample using a queue for storage
    """

    def __init__(self, graph):
        super(QueueSample, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the queue.

        Returns
        -------
        List<particles>
            list of the queue contents.

        """
        return super(QueueSample, self).read()

    def add(self, particles=None):
        """
        Add the given particles to the end of the queue.

        Parameters
        ----------
        particles : List<Particle>
            particles to be added to the container.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(particles.rst)
            self.list = self.list + particles
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        """
        Remove particles from front of queue equal in number to length of particles.

        Parameters
        ----------
        particles : List<Particle>
            list of particles, length of which is used for removing particles from the queue

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueEnvironment(ListEnvironment):
    """
    Environment using a queue for storage
    """

    def __init__(self, graph):
        super(QueueEnvironment, self).__init__(graph)

    def read(self):
        """
        Returns a full copy of the queue.

        Returns
        -------
        List<Variable>
            list of the queue contents.

        """
        return super(QueueEnvironment, self).read()

    def add(self, variables=None):
        """
        Add the given variables to the end of the queue.

        Parameters
        ----------
        variables : List<Variable>
            variables to be added to the container.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        if self.list:
            # print len(variables)
            self.list = self.list + variables
        elif isinstance(variables, list):
            self.list = variables
        else:
            self.list = [variables]
        # print len(self.list)
        return self.list

    def remove(self, variables=None):
        """
        Remove variables from front of queue equal in number to length of variables.

        Parameters
        ----------
        variables : List<Variable>
            list of variables, length of which is used for removing variables from the queue

        Returns
        --------
        Returns storage to confirm successful change.

        """
        # print self.list
        # print particles.rst
        if isinstance(variables, list):
            self.list = self.list[len(variables):]
        else:
            self.list = self.list[1:]
        return self.list


class DictionaryTank(CoreNode.Tank):
    """
    Environment which stores variables by name value pair in a dictionary.

    """
    def __init__(self, graph):
        super(DictionaryTank, self).__init__(graph)
        self.dict = {}
        pass

    def read(self):
        """
        Returns copy of environment dictionary.

        Returns
        -------
        dict: Dictionary<>
            Dictionary of variables.

        """
        return self.dict.copy()

    def add(self, particles=None):
        """
        Adds variables to dictionary.

        Parameters
        ----------
        particles : Dictionary<Sting, Value>
            Dictionary of name value pair variables to be added to environment dictionary.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        self.dict = self.dict | particles
        # print len(self.list)
        return self.dict

    def remove(self, particles=None):
        """
        Removes the listed variables from the environment.

        Parameters
        ----------
        particles : List<String>
            List of variable names for variables to be removed from dictionary

        Returns
        --------
        Returns storage to confirm successful change.

        """
        for p in particles:
            if p in self.dict.keys():
                del self.dict[p]
        return self.dict


class DictionaryEnvironment(CoreNode.Environment):
    """
    Environment which stores variables by name value pair in a dictionary.

    """

    def __init__(self, graph):
        super(DictionaryEnvironment, self).__init__(graph)
        self.dict = {}
        pass

    def read(self):
        """
        Returns copy of environment dictionary.

        Returns
        -------
        dict: Dictionary<>
            Dictionary of variables.

        """
        return self.dict.copy()

    def add(self, variables=None):
        """
        Adds variables to dictionary.

        Parameters
        ----------
        variables : Dictionary<Sting, Value>
            Dictionary of name value pair variables to be added to environment dictionary.

        Returns
        --------
        Returns storage to confirm successful change.

        """
        self.dict = self.dict | variables
        # print len(self.list)
        return self.dict

    def remove(self, variables=None):
        """
        Removes the listed variables from the environment.

        Parameters
        ----------
        variables : List<String>
            List of variable names for variables to be removed from dictionary

        Returns
        --------
        Returns storage to confirm successful change.

        """
        for var in variables:
            if var in self.dict.keys():
                del self.dict[var]
        return self.dict


class LinkTank(CoreNode.Tank):
    """
    Link tanks are used to declare subgraphs which can be linked into templates. They act as a forwarding system.
    They have a dynamic link to another containers and all requests are forwarded to that container.

    Parameters
    ----------
    graph   :   nx.DiGraph
        The graph the link node is to be added to.
    """
    def __init__(self, graph):
        super(LinkTank, self).__init__(graph)
        self.linknode = None

    def read(self):
        return self.linknode.read()

    def add(self, particles=None):
        return self.linknode.add(particles)

    def remove(self, particles=None):
        return self.linknode.remove(particles)

    def set_linknode(self, link):
        self.linknode = link

    def clear_linknode(self):
        self.linknode = None


class LinkSample(CoreNode.Sample):
    """
    Link samples are used to declare subgraphs which can be linked into templates. They act as a forwarding system.
    They have a dynamic link to another containers and all requests are forwarded to that container.

    Parameters
    ----------
    graph   :   nx.DiGraph
        The graph the link node is to be added to.
    """
    def __init__(self, graph):
        super(LinkSample, self).__init__(graph)
        self.linknode = None

    def read(self):
        return self.linknode.read()

    def add(self, particles=None):
        return self.linknode.add(particles)

    def remove(self, particles=None):
        return self.linknode.remove(particles)

    def set_linknode(self, link):
        self.linknode = link

    def clear_linknode(self):
        self.linknode = None


class LinkEnvironment(CoreNode.Environment):
    """
    Link environments are used to declare subgraphs which can be linked into templates. They act as a forwarding system.
    They have a dynamic link to another containers and all requests are forwarded to that container.

    Parameters
    ----------
    graph   :   nx.DiGraph
        The graph the link node is to be added to.
    """
    def __init__(self, graph):
        super(LinkEnvironment, self).__init__(graph)
        self.linknode = None

    def read(self):
        return self.linknode.read()

    def add(self, variables=None):
        return self.linknode.add(variables)

    def remove(self, variables=None):
        return self.linknode.remove(variables)

    def set_linknode(self, link):
        self.linknode = link

    def clear_linknode(self):
        self.linknode = None


class NestedGridTank(DictionaryTank):
    """

    """
    def __init__(self, graph, gridrows=1, gridcols=1):
        super(NestedGridTank, self).__init__(graph)
        self.gridrows = gridrows
        self.gridcols = gridcols

    def add(self, particles=None, full=False, tank=None, append=False):
        if full:
            for i in range(0, len(particles)):
                self.dict[i] = particles[i]
        elif append:
            self.dict[len(self.dict.keys())] = particles
        elif tank is not None:
            if self.dict[tank] and isinstance(particles, list):
                # print len(particles.rst)
                self.dict[tank] = self.dict[tank] + particles
            elif self.dict[tank]:
                self.dict[tank].append(particles)
            elif isinstance(particles, list):
                self.dict[tank] = particles
            else:
                self.dict[tank] = [particles]
            # print len(self.list)
            return self.dict[tank]
        else:
            self.dict[len(self.dict.keys())] = particles

    def remove(self, particles=None, full=False, tank=None, append=False):
        if full:
            self.dict = {}
        elif tank is not None:
            if particles == self.dict[tank]:
                self.dict[tank] = []
            else:
                if self.dict[tank] and not isinstance(particles[0], list):
                    self.dict[tank].remove(particles[0])
                elif not isinstance(particles, list):
                    self.dict[tank].remove(particles)
                elif self.dict[tank]:
                    [self.dict[tank].remove(part) for part in particles]
        else:
            for key in self.dict.keys():
                if self.dict[key] == particles:
                    self.dict[key] = []
        return self.dict
