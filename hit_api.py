from googletrans import Translator
from nltk.corpus import stopwords
import string
import re

filename = "VerneVoyage_short.txt"
source_language = "fr"
lexicon = []

file = open(filename, 'rt')
text = file.read()
file.close()

def process(text: str) -> list:
    output = clean(text)
    output = to_unique_list(output)
    return output

def clean(text: str) -> str:
    output = text.lower()
    output = remove_punctuation(output)
    output = remove_stop_words(output)
    output = normalize_whitespace(output)
    return output

def normalize_whitespace(text: str) -> str:
    whitespace = re.compile('\s+')
    output = whitespace.sub(' ', text)
    return output

def remove_stop_words(text: str) -> str:
    output = [word for word in text.split() if word not in stopwords.words('french')]
    # output.remove("")
    return " ".join(output)

def remove_punctuation(text: str) -> str:
    not_letters = re.compile(r'[^a-zäàâçéèêëîïôöûùüÿñæœß ]')
    return not_letters.sub(' ', text)

def to_unique_list(text: str) -> list:
    words = to_list(text)
    words = normalize(words)
    return words

def to_list(text: str) -> str:
    text_list = text.split()
    return text_list

def normalize(words: list) -> list:
    sorted_words = sorted(list(set(words)))
    return sorted_words

# text = "Le 24 mai 1863, un dimanche, mon oncle, le professeur Lidenbrock, revint précipitamment vers sa petite maison située au numéro 19 de König-strasse, l'une des plus anciennes rues du vieux quartier de Hambourg."

words = process(text)

# text_nopunct = re.sub(r'[^a-zäàâçéèêëîïôöûùüÿñæœß ]', ' ', text, flags=re.I)

# words = text_nopunct.split() # split on whitespace

# words = sorted(list(set(words)))

# filtered_words = [word for word in words if word not in stopwords.words('french')]

def query_one_word(word: str, source_language: str) -> dict:
    translator = Translator()
    result = translator.translate(word, src=source_language)
    return result




for word in words:
    # result = translator.translate(word, src=source_language)
    result = query_one_word(word, "fr")
    if hasattr(result, "extra_data"):
        if "all-translations" in result.extra_data and result.extra_data["all-translations"] is not None:
            for translation in result.extra_data["all-translations"]:
                part_of_speech = translation[0]
                target = translation[1][0]
                single_translation = {
                    "Source": word,
                    "PartOfSpeech": part_of_speech,
                    "Target": target
                }
                lexicon.append(single_translation)
        else:
            single_translation = {
                "Source": word,
                "PartOfSpeech": "?",
                "Target": "???"
            }
            lexicon.append(single_translation)
            

for line in lexicon:
    print(f"{line['Source']} ({line['PartOfSpeech']}) - {line['Target']}")



# paragraph = " ".join(text)

# for word in words:
#     print(word)
