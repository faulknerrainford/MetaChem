class Particle:

    def __init__(self):
        """
        Class for defining particles which have the correct parameters to be used by different templates. Definition
        of properties must be done in the subclass.

        Defines
        -------
        id
            A unique identifier used to track reactions in loggers
        location
            For templates with spacial interactions this is used to store a particles current location
        atom
            Boolean which indicates if a particle is atomic and can not be broken down or a composite made of several
            other particles
        located
            Boolean indicating if the Particle has or is supposed to have a location.
        """
        self.id = None
        self.location = None
        self.atom = False
        self.located = False