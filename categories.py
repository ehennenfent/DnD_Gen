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
    DRAGON = "dragon"
    CRYPT = "crypt"
    FOREST = "forest"
    GRIFFIN = "griffin"
    HELMET = "helmet"
    AXE = "axe"
    HYDRA = "hydra"
    MANTICORE = "manticore"
    OGRE = "ogre"
    SWORDS = "swords"
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


governments = [government for government in Government]


class Ruler(Enum):
    POLITICAL = "Political"
    RELIGIOUS = "Religious"
    MILITARY = "Militaristic"
    CRIME = "Criminal"
    CULTURE = "Cultural"
    WISDOM = "Wise"
    NONE = "Anarchy"


rulers = [ruler for ruler in Ruler]


class Organization(Enum):
    THIEVES = "Thieves Guild"
    SUN = "Cult of the Sun"
    MOON = "Moon Cult"
    SHADOW = "Cult of Shadows"
    MERCHANTS = "Merchant's guild"
    PALADINS = "Paladin's Guild"
    YALE = "Skull and Bones"
    SAINTS = "Church of the Forgotten Saints"
    DRAGON = "Order of the Dragon"
    ASSASSIN = "League of Assassins"
    TEMPLAR = "Knight's Templar"
    LIGHT = "Brotherhood of Light"
    ZEAL = "Sicarii"
    PRIORY = "Priory of Sion"
    OWL = "Court of Owls"
    SCIENCE = "Council of Dark Scientists"
    PHOENIX = "Sect of the Phoenix"
    BIRD = "Organization of Miscellanious Fantastic Birds"
    BATTLE = "V-Battalion"
    NUMBER = "22 Society"
    KNIGHT = "Knights of Hromada"
    POLITIC = "National Action Party"
    MINING = "Mining Interests Alliance"


organizations = [org for org in Organization]
