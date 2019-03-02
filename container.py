# Set of generic classes for general use in Artificial Chemistries

import node

# Basic containers using lists/nested lists


class ListTank(node.Tank):

    def __init__(self):
        super(ListTank, self).__init__()
        self.list = None
        pass

    def read(self):
        return self.list[:]

    def add(self, particles=None):
        if self.list:
            # print len(particles)
            self.list = self.list + particles
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        # print self.list
        # print particles
        if self.list and isinstance(self.list[0], list) and not isinstance(particles[0], list):
            self.list.remove(particles)
        elif self.list:
            [self.list.remove(part) for part in particles]
        return self.list


class ListSample(node.Sample):

    def __init__(self):
        super(ListSample, self).__init__()
        self.list = None
        pass

    def read(self):
        return self.list[:]

    def add(self, particles=None):
        if self.list:
            # print len(particles)
            self.list = self.list + particles
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        [self.list.remove(part) for part in particles]
        return self.list


class ListEnvironment(node.Environment):

    def __init__(self):
        super(ListEnvironment, self).__init__()
        self.list = None
        pass

    def read(self):
        return self.list[:]

    def add(self, variables=None):
        if self.list:
            self.list.append(variables)
        elif isinstance(variables, list):
            self.list = variables
        else:
            self.list = [variables]
        return self.list

    def remove(self, variables=None):
        self.list.remove(variables)
        return self.list
