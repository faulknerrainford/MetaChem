import abc
import random


class ParticleFactory:

    def __init__(self):
        self.seed = 0
        self.generator_size = 0

    @abc.abstractmethod
    def createParticle(self, seed=None):
        if seed:
            self.seed = seed
            random.seed(self.seed)

    def createParticles(self, numParticles, seed=None):
        if seed:
            self.seed = seed
            random.seed(seed)
        self.generator_size = numParticles
        return [self.createParticle() for _ in range(self.generator_size)]
