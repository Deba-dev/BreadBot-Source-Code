import random

easy = [
    'rain',
    'ran'
    'hello',
    'sea',
    'ocean',
    'fish',
    'space',
    'mill',
    'sweet',
    'red',
    'date',
    'feed',
    'wheel',
    'clerk',
    'pass',
    'false',
    'beef',
    'child',
    'party',
    'cheek',
    'flu',
    'cane',
    'gold',
    'tense',
    'herb',
    'spite',
    'keep',
    'abbey',
    'sharp',
    'real',
    'faint',
    'mess',
    'blast',
    'room',
    'moral',
    'dark',
    'rifle',
    'book',
    'dairy',
    'so',
    'coal',
    'uncle',
    'game',
    'beg',
    'nest',
    'time',
    'ratio',
    'dip',
    'swarm',
    'kill',
    'stock',
    'final',
    'stage',
    'grief',
    'word',
    'oil',
    'duke',
]

coding = [
    "python",
    "javascript",
    "coding",
    "developer",
    "IDE",
    "html",
    "github"
]

animals = [
    "dog",
    "bone",
    "woof",
    "ball",
    "cat",
    "frog",
    "chew toy"
]

tools = [
    "hammer",
    "mallet",
    "ratchet",
    "nail",
    "bolt",
    "wrench",
    "screwdriver"
]

nature = [
    "grass",
    "tree",
    "sap",
    "leaves",
    "rocks",
    "cave",
    "water",
    "volcano"
]

def randtopic():
    rand = random.choice([nature, tools, animals, coding])
    return rand