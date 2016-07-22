from collections import defaultdict
from random import randint

keys = defaultdict(list)
keys["weather"].append((["погода", "в"], "word"))
keys["weather"].append((["погоду", "в"], "word"))

keys["format"].append((["формат"], "regexp"))

keys["clear"].append((["(?:о|по)чист"], "regexp"))

keys["paint"].append((["кра[сш]"], "regexp"))
keys["paint"].append((["свет"], "regexp"))

keys["hello"].append((["привет"], "word"))
keys["hello"].append((["хай"], "word"))
keys["hello"].append((["здорово"], "word"))
keys["hello"].append((["здравствуй"], "word"))
keys["hello"].append((["здравствуйте"], "word"))
keys["hello"].append((["o/"], "word"))
keys["hello"].append((["\o/"], "word"))
keys["hello"].append((["ку"], "word"))
keys["hello"].append((["hello"], "word"))
keys["hello"].append((["hi"], "word"))

keys["bye"].append((["пока"], "word"))
keys["bye"].append((["бб"], "word"))
keys["bye"].append((["o/"], "word"))
keys["bye"].append((["\o/"], "word"))
keys["bye"].append((["bye"], "word"))

keys["quit"].append((["пошёл", "вон"], "word"))
keys["quit"].append((["проваливай"], "word"))
keys["quit"].append((["уходи"], "word"))
keys["quit"].append((["уйди"], "word"))
keys["quit"].append((["выйди"], "word"))

keys["store"].append((["запоми?н"], "regexp"))
keys["store"].append((["учи"], "regexp"))

keys["print"].append((["покажи"], "word"))
keys["print"].append((["выв[ое]д"], "regexp"))

keys["end"].append((["конец"], "word"))
keys["end"].append((["закончи"], "word"))
keys["end"].append((["кончай"], "word"))
keys["end"].append((["заканчивай"], "word"))
keys["end"].append((["не", "надо"], "word"))
keys["end"].append((["хватит"], "word"))
keys["end"].append((["стоп"], "word"))

keys["text"].append((["текст"], "regexp"))
keys["text"].append((["файл"], "regexp"))

keys["string"].append((["строч?ка"], "regexp"))
keys["string"].append((["предложение"], "regexp"))
keys["string"].append((["фраз"], "regexp"))
keys["string"].append((["выражен"], "regexp"))

keys["all"].append((["все"], "regexp"))
keys["all"].append((["here"], "word"))
keys["all"].append((["there"], "word"))
keys["all"].append((["guys"], "word"))

hello = [
    "o/",
    "привет"
]

bye = [
    "o/",
    "пока"
]


def rand_hello() -> str:
    return hello[randint(0, len(hello) - 1)]


def rand_bye() -> str:
    return bye[randint(0, len(bye) - 1)]
