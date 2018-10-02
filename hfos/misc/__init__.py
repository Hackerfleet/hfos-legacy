import gettext
import json

import os

from datetime import datetime
from uuid import uuid4

from hashlib import sha512
from random import choice

from hfos.logger import hfoslog, verbose, warn

localedir = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'locale'))


def l10n_log(*args, **kwargs):
    """Log as L10N emitter"""

    kwargs.update({'emitter': 'L10N', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


def all_languages():
    """Compile a list of all available language translations"""

    rv = []

    for lang in os.listdir(localedir):
        base = lang.split('_')[0].split('.')[0].split('@')[0]
        if 2 <= len(base) <= 3 and all(c.islower() for c in base):
            if base != 'all':
                rv.append(lang)
    rv.sort()
    rv.append('en')
    l10n_log('Registered languages:', rv, lvl=verbose)

    return rv


def language_token_to_name(languages):
    """Get a descriptive title for all languages"""

    result = {}

    with open(os.path.join(localedir, 'languages.json'), 'r') as f:
        language_lookup = json.load(f)

    for language in languages:
        language = language.lower()
        try:
            result[language] = language_lookup[language]
        except KeyError:
            l10n_log('Language token lookup not found:', language, lvl=warn)
            result[language] = language

    return result


class Domain:
    """Gettext domain capable of translating into all registered languages"""

    def __init__(self, domain):
        self._domain = domain
        self._translations = {}

    def _get_translation(self, lang):
        """Add a new translation language to the live gettext translator"""

        try:
            return self._translations[lang]
        except KeyError:
            # The fact that `fallback=True` is not the default is a serious design flaw.
            rv = self._translations[lang] = gettext.translation(self._domain, localedir=localedir, languages=[lang],
                                                                fallback=True)
            return rv

    def get(self, lang, msg):
        """Return a message translated to a specified language"""

        return self._get_translation(lang).gettext(msg)


def print_messages(domain, msg):
    """Debugging function to print all message language variants"""

    domain = Domain(domain)
    for lang in all_languages():
        print(lang, ':', domain.get(lang, msg))


def i18n(msg, event=None, lang='en', domain='backend'):
    """Gettext function wrapper to return a message in a specified language by domain

    To use internationalization (i18n) on your messages, import it as '_' and use as usual.
    Do not forget to supply the client's language setting."""

    if event is not None:
        language = event.client.language
    else:
        language = lang

    domain = Domain(domain)
    return domain.get(language, msg)


def std_hash(word, salt):
    """Generates a cryptographically strong (sha512) hash with this nodes
    salt added."""

    try:
        password = word.encode('utf-8')
    except UnicodeDecodeError:
        password = word

    word_hash = sha512(password)
    word_hash.update(salt)
    hex_hash = word_hash.hexdigest()

    return hex_hash


def std_now():
    """Return current (UTC) timestamp in ISO format"""

    return datetime.now().isoformat()


def std_uuid():
    """Return string representation of a new UUID4"""

    return str(uuid4())


colors = [
    'Red', 'Orange', 'Yellow', 'Green', 'Cyan', 'Blue', 'Violet', 'Purple'
]

adjectives = [
    'abundant', 'adorable', 'agreeable', 'alive', 'ancient', 'angry', 'beautiful',
    'better', 'bewildered', 'big', 'bitter', 'boiling', 'brave', 'breeze', 'brief',
    'broad', 'broken', 'bumpy', 'calm', 'careful', 'chilly', 'chubby', 'clean',
    'clever', 'clumsy', 'cold', 'colossal', 'cooing', 'cool', 'creepy', 'crooked',
    'crooked', 'cuddly', 'curly', 'curved', 'damaged', 'damp', 'dead', 'deafening',
    'deep', 'defeated', 'delicious', 'delightful', 'dirty', 'drab', 'dry', 'dusty',
    'eager', 'early', 'easy', 'elegant', 'embarrassed', 'empty', 'faint',
    'faithful', 'famous', 'fancy', 'fast', 'fat', 'few', 'fierce', 'filthy',
    'flaky', 'flat', 'fluffy', 'freezing', 'fresh', 'full', 'gentle', 'gifted',
    'gigantic', 'glamorous', 'greasy', 'great', 'grumpy', 'handsome', 'happy',
    'heavy', 'helpful', 'helpless', 'high', 'hissing', 'hollow', 'hot', 'hot',
    'huge', 'icy', 'immense', 'important', 'inexpensive', 'itchy', 'jealous',
    'jolly', 'juicy', 'kind', 'large', 'late', 'lazy', 'light', 'little', 'lively',
    'long', 'long', 'loose', 'loud', 'low', 'magnificent', 'mammoth', 'many',
    'massive', 'melodic', 'melted', 'miniature', 'modern', 'mushy', 'mysterious',
    'narrow', 'nervous', 'nice', 'noisy', 'numerous', 'nutritious', 'obedient',
    'obnoxious', 'odd', 'old', 'old-fashioned', 'old-fashioned', 'panicky',
    'petite', 'plain', 'powerful', 'prickly', 'proud', 'puny', 'purring', 'quaint',
    'quick', 'quiet', 'rainy', 'rapid', 'raspy', 'relieved', 'repulsive', 'rich',
    'rotten', 'round', 'salty', 'scary', 'scrawny', 'screeching', 'shallow',
    'short', 'short', 'shy', 'silly', 'skinny', 'slow', 'small', 'sparkling',
    'sparse', 'square', 'steep', 'sticky', 'straight', 'strong', 'substantial',
    'sweet', 'swift', 'tall', 'tart', 'tasteless', 'teeny', 'teeny-tiny', 'tender',
    'thankful', 'thoughtless', 'thundering', 'tiny', 'ugliest', 'uneven',
    'uninterested', 'unsightly', 'uptight', 'vast', 'victorious', 'voiceless',
    'warm', 'weak', 'wet', 'wet', 'whispering', 'wide', 'wide-eyed', 'witty',
    'wooden', 'worried', 'wrong', 'young', 'yummy', 'zealous'
]

animals = [
    'Aardvark', 'Abyssinian', 'Affenpinscher', 'Akbash', 'Akita', 'Albatross',
    'Alligator', 'Angelfish', 'Ant', 'Anteater', 'Antelope', 'Armadillo', 'Avocet',
    'Axolotl', 'Baboon', 'Badger', 'Balinese', 'Bandicoot', 'Barb', 'Barnacle',
    'Barracuda', 'Bat', 'Beagle', 'Bear', 'Beaver', 'Beetle', 'Binturong', 'Bird',
    'Birman', 'Bison', 'Bloodhound', 'Bobcat', 'Bombay', 'Bongo', 'Bonobo',
    'Booby', 'Budgerigar', 'Buffalo', 'Bulldog', 'Bullfrog', 'Burmese',
    'Butterfly', 'Caiman', 'Camel', 'Capybara', 'Caracal', 'Cassowary', 'Cat',
    'Caterpillar', 'Catfish', 'Centipede', 'Chameleon', 'Chamois', 'Cheetah',
    'Chicken', 'Chihuahua', 'Chimpanzee', 'Chinchilla', 'Chinook', 'Chipmunk',
    'Cichlid', 'Coati', 'Cockroach', 'Collie', 'Coral', 'Cougar', 'Cow', 'Coyote',
    'Crab', 'Crane', 'Crocodile', 'Cuscus', 'Cuttlefish', 'Dachshund', 'Dalmatian',
    'Deer', 'Dhole', 'Dingo', 'Discus', 'Dodo', 'Dog', 'Dolphin', 'Donkey',
    'Dormouse', 'Dragonfly', 'Drever', 'Duck', 'Dugong', 'Dunker', 'Eagle',
    'Earwig', 'Echidna', 'Elephant', 'Emu', 'Falcon', 'Ferret', 'Fish', 'Flamingo',
    'Flounder', 'Fly', 'Fossa', 'Fox', 'Frigatebird', 'Frog', 'Gar', 'Gecko',
    'Gerbil', 'Gharial', 'Gibbon', 'Giraffe', 'Goat', 'Goose', 'Gopher', 'Gorilla',
    'Grasshopper', 'Greyhound', 'Grouse', 'Guppy', 'Hamster', 'Hare', 'Harrier',
    'Havanese', 'Hedgehog', 'Heron', 'Himalayan', 'Hippopotamus', 'Horse', 'Human',
    'Hummingbird', 'Hyena', 'Ibis', 'Iguana', 'Impala', 'Indri', 'Insect',
    'Jackal', 'Jaguar', 'Javanese', 'Jellyfish', 'Kakapo', 'Kangaroo',
    'Kingfisher', 'Kiwi', 'Koala', 'Kudu', 'Labradoodle', 'Ladybird', 'Lemming',
    'Lemur', 'Leopard', 'Liger', 'Lion', 'Lionfish', 'Lizard', 'Llama', 'Lobster',
    'Lynx', 'Macaw', 'Magpie', 'Maltese', 'Manatee', 'Mandrill', 'Markhor',
    'Mastiff', 'Mayfly', 'Meerkat', 'Millipede', 'Mole', 'Molly', 'Mongoose',
    'Mongrel', 'Monkey', 'Moorhen', 'Moose', 'Moth', 'Mouse', 'Mule',
    'Newfoundland', 'Newt', 'Nightingale', 'Numbat', 'Ocelot', 'Octopus', 'Okapi',
    'Olm', 'Opossum', 'Orang-utan', 'Ostrich', 'Otter', 'Oyster', 'Pademelon',
    'Panther', 'Parrot', 'Peacock', 'Pekingese', 'Pelican', 'Penguin', 'Persian',
    'Pheasant', 'Pig', 'Pika', 'Pike', 'Piranha', 'Platypus', 'Pointer', 'Poodle',
    'Porcupine', 'Possum', 'Prawn', 'Puffin', 'Pug', 'Puma', 'Quail', 'Quetzal',
    'Quokka', 'Quoll', 'Rabbit', 'Raccoon', 'Ragdoll', 'Rat', 'Rattlesnake',
    'Reindeer', 'Rhinoceros', 'Robin', 'Rottweiler', 'Salamander', 'Saola',
    'Scorpion', 'Seahorse', 'Seal', 'Serval', 'Sheep', 'Shrimp', 'Siamese',
    'Siberian', 'Skunk', 'Sloth', 'Snail', 'Snake', 'Snowshoe', 'Somali',
    'Sparrow', 'Sponge', 'Squid', 'Squirrel', 'Starfish', 'Stingray', 'Stoat',
    'Swan', 'Tang', 'Tapir', 'Tarsier', 'Termite', 'Tetra', 'Tiffany', 'Tiger',
    'Tortoise', 'Toucan', 'Tropicbird', 'Tuatara', 'Turkey', 'Uakari', 'Uguisu',
    'Umbrellabird', 'Vulture', 'Wallaby', 'Walrus', 'Warthog', 'Wasp', 'Weasel',
    'Whippet', 'Wildebeest', 'Wolf', 'Wolverine', 'Wombat', 'Woodlouse',
    'Woodpecker', 'Wrasse', 'Yak', 'Zebra', 'Zebu', 'Zonkey', 'Zorse'
]

alphabet = [
    'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel',
    'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
    'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray',
    'Yankee', 'Zulu'
]

places = [
    'airport', 'aquarium', 'bakery', 'bar', 'bridge', 'building', 'bus-stop',
    'cafe', 'campground', 'church', 'city', 'embassy', 'florist', 'gym', 'harbour',
    'hospital', 'hotel', 'house', 'island', 'laundry', 'library', 'monument',
    'mosque', 'museum', 'office', 'park', 'pharmacy', 'plaza', 'restaurant',
    'road', 'school', 'spa', 'stable', 'stadium', 'store', 'street', 'theater',
    'tower', 'town', 'train-station', 'university', 'village', 'wall', 'zoo']

attributes = [
    'Chaos', 'Hate', 'Adventure', 'Anger', 'Anxiety', 'Beauty', 'Beauty',
    'Being', 'Beliefs', 'Birthday', 'Brilliance', 'Career', 'Charity', 'Childhood',
    'Comfort', 'Communication', 'Confusion', 'Courage', 'Culture', 'Curiosity',
    'Death', 'Deceit', 'Dedication', 'Democracy', 'Despair', 'Determination',
    'Energy', 'Failure', 'Faith', 'Fear', 'Freedom', 'Friendship', 'Future',
    'Generosity', 'Grief', 'Happiness', 'Holiday', 'Honesty', 'Indifference',
    'Interest', 'Joy', 'Knowledge', 'Liberty', 'Life', 'Love', 'Luxury',
    'Marriage', 'Misery', 'Motivation', 'Nervousness', 'Openness', 'Opportunity',
    'Pain', 'Past', 'Patience', 'Peace', 'Perseverance', 'Pessimism', 'Pleasure',
    'Sacrifice', 'Sadness', 'Satisfaction', 'Sensitivity', 'Sorrow', 'Stress',
    'Sympathy', 'Thought', 'Trust', 'Warmth', 'Wisdom'
]


def std_human_uid(kind=None):
    """Return a random generated human-friendly phrase as low-probability unique id"""

    kind_list = alphabet

    if kind == 'animal':
        kind_list = animals
    elif kind == 'place':
        kind_list = places

    name = "{color} {adjective} {kind} of {attribute}".format(
        color=choice(colors),
        adjective=choice(adjectives),
        kind=choice(kind_list),
        attribute=choice(attributes)
    )

    return name


def std_table(rows):
    """Return a formatted table of given rows"""

    result = ""
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([x[i] for x in rows] + [headers[i]],
                                key=lambda x: len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        result += hpattern % tuple(headers) + " \n"
        result += separator + "\n"

        for line in rows:
            result += pattern % tuple(t for t in line) + "\n"
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields, key=lambda x: len(x)))
        for i in range(len(row)):
            result += "%*s = %s" % (hwidth, row._fields[i], row[i]) + "\n"

    return result


def std_salt(length=16, lowercase=True):
    """Generates a cryptographically sane salt of 'length' (default: 16) alphanumeric
    characters
    """

    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if lowercase is True:
        alphabet += "abcdefghijklmnopqrstuvwxyz"

    chars = []
    for i in range(length):
        chars.append(choice(alphabet))

    return "".join(chars)
