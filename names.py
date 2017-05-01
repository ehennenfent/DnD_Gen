from random import choice

class nameGen(object):

    def __init__(self):
        self.people = []
        self.places = []

        with open('people.txt', 'r') as people_file:
            for line in people_file:
                self.people.append(line.strip())
        print("Read %s people" % len(self.people))

        with open('places.txt', 'r') as places_file:
            for line in places_file:
                self.places.append(line.strip())
        print("Read %s places" % len(self.places))

    def get_person(self):
        out = choice(self.people)
        self.people.remove(out)
        return out

    def get_place(self):
        out = choice(self.places)
        self.places.remove(out)
        return out
