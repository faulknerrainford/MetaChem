from unittest import TestCase
from metachem.RBNworld import WatsonRBNParticleFactory, RBNParticle
import pickle


class TestWatsonRBNParticleFactory(TestCase):
    def test_create_particle(self):
        # generate a particle
        fact = WatsonRBNParticleFactory(8, 2)
        part = fact.createParticle()
        self.assertIsInstance(part, RBNParticle, "Did not produce particle")
        # generate a tank of 2
        particles = fact.createParticles(2)
        self.assertEqual(2, len(particles), "Did not produce 2 particles")
        # generate a tank of 100
        particles = fact.createParticles(100)
        self.assertEqual(100, len(particles), "Did not produce 100 particles")
        file = open("data/test_data_RBNparticles.pickle", "wb")
        pickle.dump(particles, file)
        file.close()
        # TODO: Set up seeds to work correctly for regenerating
        # # TODO: generate a tanks with a seed
        # particles1 = fact.createParticles(100, 4)
        # # TODO: generate a tank with the same seed
        # particles2 = fact.createParticles(100, 4)
        # self.assertListEqual(particles1, particles2, "Lists with same seed not the same")
