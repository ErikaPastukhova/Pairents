from enum import Enum

class Sex(Enum):
    NOTHING = 0
    FEMALE = 1
    MALE = 2

class Profile:
    def __init__(self):
        self.name = ''
        self.surname = ''
        self.sex = Sex.NOTHING
        self.photo = None
        self.num_of_children = 0
        self.children = []

profile = Profile()
