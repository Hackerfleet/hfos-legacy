from datetime import datetime
from pprint import pprint
from uuid import uuid4
from hashlib import sha512
from random import choice

import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
translate = gettext.translation('hfos', localedir, fallback=True)
_ = translate.gettext


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
    """Return current timestamp in ISO format"""

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


def format_template(template, content):
    """Render a given pystache template
    with given content"""

    import pystache
    result = u""
    if True:  # try:
        result = pystache.render(template, content, string_encoding='utf-8')
    # except (ValueError, KeyError) as e:
    #    print("Templating error: %s %s" % (e, type(e)))

    # pprint(result)
    return result


def format_template_file(filename, content):
    """Render a given pystache template file with given content"""

    with open(filename, 'r') as f:
        template = f.read()
        if type(template) != str:
            template = template.decode('utf-8')

    return format_template(template, content)


def write_template_file(source, target, content):
    """Write a new file from a given pystache template file and content"""

    # print(formatTemplateFile(source, content))
    print(target)
    data = format_template_file(source, content)
    with open(target, 'w') as f:
        for line in data:
            if type(line) != str:
                line = line.encode('utf-8')
            f.write(line)


def insert_nginx_service(definition):  # pragma: no cover
    """Insert a new nginx service definition"""

    config_file = '/etc/nginx/sites-available/hfos.conf'
    splitter = "### SERVICE DEFINITIONS ###"

    with open(config_file, 'r') as f:
        old_config = "".join(f.readlines())

    pprint(old_config)

    if definition in old_config:
        print("Service definition already inserted")
        return

    parts = old_config.split(splitter)
    print(len(parts))
    if len(parts) != 3:
        print("Nginx configuration seems to be changed and cannot be "
              "extended automatically anymore!")
        pprint(parts)
        return

    try:
        with open(config_file, "w") as f:
            f.write(parts[0])
            f.write(splitter + "\n")
            f.write(parts[1])
            for line in definition:
                f.write(line)
            f.write("\n    " + splitter)
            f.write(parts[2])
    except Exception as e:
        print("Error during Nginx configuration extension:", type(e), e)


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
