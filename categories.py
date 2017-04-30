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

colors = [Color.RED, Color.GREEN, Color.BLUE]

class Religion(Enum):
    LPANTH = "Loose Pantheon"
    TPANTH = "Tight Pantheon"
    CULT = "Cult"
    MONO = "Monotheism"
    DUAL = "Dualism"
    ANIM = "Animism"
    NONE = "Godless"

class Governments(Enum):
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
