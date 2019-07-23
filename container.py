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
        elif not isinstance(particles,list):
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
        if particles == self.list:
            self.list = []
        elif not isinstance(particles, list):
            self.list.remove(particles)
        else:
            [self.list.remove(part) for part in particles]
        return self.list


class ListEnvironment(node.Environment):

    def __init__(self):
        super(ListEnvironment, self).__init__()
        self.list = []
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
        if variables and isinstance(variables, list):
            [self.list.remove(var) for var in variables]
        elif variables:
            self.list.remove(variables)
        return self.list


class StackTank(ListTank):

    def __init__(self):
        super(StackTank, self).__init__()

    def read(self):
        return super(StackTank, self).read()

    def add(self, particles=None):
        if self.list:
            # print len(particles)
            self.list = particles + self.list
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        # print self.list
        # print particles
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class StackSample(ListSample):

    def __init__(self):
        super(StackSample, self).__init__()

    def read(self):
        return super(StackSample, self).read()

    def add(self, particles=None):
        if self.list:
            # print len(particles)
            self.list = particles + self.list
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        # print self.list
        # print particles
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class StackEnvironment(ListEnvironment):

    def __init__(self):
        super(StackEnvironment, self).__init__()

    def read(self):
        return super(StackEnvironment, self).read()

    def add(self, variables=None):
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
        # print self.list
        # print particles
        if isinstance(variables, list):
            self.list = self.list[len(variables):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueTank(ListTank):

    def __init__(self):
        super(QueueTank, self).__init__()

    def read(self):
        return super(QueueTank, self).read()

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
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueSample(ListSample):

    def __init__(self):
        super(QueueSample, self).__init__()

    def read(self):
        return super(QueueSample, self).read()

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
        if isinstance(particles, list):
            self.list = self.list[len(particles):]
        else:
            self.list = self.list[1:]
        return self.list


class QueueEnvironment(ListEnvironment):

    def __init__(self):
        super(QueueEnvironment, self).__init__()

    def read(self):
        return super(QueueEnvironment, self).read()

    def add(self, variables=None):
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
        # print self.list
        # print particles
        if isinstance(variables, list):
            self.list = self.list[len(variables):]
        else:
            self.list = self.list[1:]
        return self.list
