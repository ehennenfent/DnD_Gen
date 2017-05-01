from enum import Enum

class Terrain(Enum):
    PLAIN = "Plains"
    MOUNTAIN = "Mountains"
    WATER = "Water"
    CITY = "City"
    ICE = "Ice"
    DESERT = "Desert"

class Color(Enum):
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    ORANGE = "#FFA500"
    PURPLE = "#800080"
    BROWN = "#8B4513"
    GOLD = "#FFD700"
    PINK = "#FFC0CB"
    SILVER = "#778899"

colors = [c for c in Color]

class Religion(Enum):
    LPANTH = "Loose Pantheon"
    TPANTH = "Tight Pantheon"
    CULT = "Cult"
    MONO = "Monotheism"
    DUAL = "Dualism"
    ANIM = "Animism"
    NONE = "Godless"

religions = [c for c in Religion]

class Icon(Enum):
    CASTLE = "castle"
    CATHEDRAL = "cathedral"
    CITY = "city"
    VILLAGE = "cottage"
    CAPITOL = "crown"
    MONSTER = "dragon"
    MOUNTAIN = "mountain"
    CSTATE = "tower"

class Government(Enum):
    AUTO = "Autocracy"
    BURO = "Bureaucracy"
    CONF = "Confederacy"
    DEMO = "Democracy"
    DICT = "Dictatorship"
    FEUD = "Feudalism"
    GERO = "Gerontocracy"
    HIER = "Hierarchy"
    KLEP = "Kleptocracy"
    MAGO = "Magocracy"
    MATY = "Matriarchy"
    PATY = "Patriarchy"
    MERI = "Meritocracy"
    MILI = "Militocracy"
    MONA = "Monarchy"
    OLIG = "Oligarchy"
    PLUT = "Plutocracy"
    REPB = "Republic"
    SATR = "Satrapy"
    THEO = "Theocracy"
