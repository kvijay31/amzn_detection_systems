
import string
import contractions
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.tokenize import word_tokenize
import nltk.data
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import words
import re
import spacy
from spacy_language_detection import LanguageDetector
from spacy.language import Language
import fasttext



#### Cleaning text

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('words')
nltk.download('punkt')
nltk.download('omw-1.4')


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer.sent_end_chars=(':','.',',',';')
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS)) - set(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'elven', 'twelve' ])




def basic_cleaning(text:string, punctuation:bool) -> str:
    """
    This function does some basic data cleaning.
    """
    for a_sign in ['\\n', '\\t', '☐', '☒', '\xa0', '●', '“', '”']:
        text = text.replace(a_sign," ")

    if punctuation:
        for a_punc in string.punctuation:
            text = text.replace(a_punc, " ")
    else:
        text =  re.sub(', ', ' ', text).strip()
    
    text = re.sub('\s+'," ", text).lower()
    return text.strip() 


def split_into_sentences(text:str) -> list:
    #.
    text = re.sub(r'([a-zA-Z)])\.([a-zA-Z-])', r'\1. \2', text)
    text = re.sub(r"([\d)])\.([a-zA-Z-])", r"\1. \2", text)
    text = re.sub(r"([a-zA-Z)])\.(\d)", r"\1. \2", text)
    #.
    text = re.sub(r'([a-zA-Z)])\!([a-zA-Z-])', r'\1! \2', text)
    text = re.sub(r"([\d)])\!([a-zA-Z-])", r"\1! \2", text)
    text = re.sub(r"([a-zA-Z)])\!(\d)", r"\1! \2", text)
    #?
    text = re.sub(r'([a-zA-Z)])\?([a-zA-Z-])', r'\1? \2', text)
    text = re.sub(r"([\d)])\?([a-zA-Z-])", r"\1? \2", text)
    text = re.sub(r"([a-zA-Z)])\?(\d)", r"\1? \2", text)
    #:
    text = re.sub(r'([a-zA-Z)])\:([a-zA-Z-])', r'\1: \2', text)
    text = re.sub(r"([\d)])\:([a-zA-Z-])", r"\1: \2", text)
    text = re.sub(r"([a-zA-Z)])\:(\d)", r"\1: \2", text)
    #;
    text = re.sub(r'([a-zA-Z)])\;([a-zA-Z-])', r'\1; \2', text)
    text = re.sub(r"([\d)])\;([a-zA-Z-])", r"\1; \2", text)
    text = re.sub(r"([a-zA-Z)])\;(\d)", r"\1; \2", text)
    return tokenizer.tokenize(text)

def remove_special_characters(text:str):
    text = re.sub(r"%", ' percent ', text)
    return re.sub(r"[^A-Za-z0-9\s!.,?]+", '', text)


def remove_stop_words(text:string):
    text = ' '.join([word for word in text.split() if word not in stop])
    return text 

def clean_contractions(text:string):
    text = contractions.fix(text).lower()
    text = re.sub('can t', ' cannot ', text).strip()
    text = re.sub(' ll ', ' will ', text).strip()
    text = re.sub(' +', ' ', text).strip()
    text = re.sub(r' [^\w\s] ', '', text)
    return text

def removing_numbers(text:string):
    text = re.sub('(?<=\d),(?=\s)', '', text)
    text = re.sub('(?<=\d).(?=\d)', '', text)
    text = re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", text)
    #text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s([?.!,"](?:\s|$))', r'\1', text)
    text = re.sub(' +', ' ', text).strip()
    return text

def removing_non_english(text:string):
    text = ' '.join([word for word in text.split() if word in words.words()])
    return text

def lammatize_text(text:string):
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split() ])
    return text

def stem_text(text:string):
    text = ' '.join([ stemmer.stem(word) for word in text.split() ])
    return text

def replace_words(text, word_list: dict):
    for word in list(word_list):
        text = text.replace(word, word_list[word])
    return text

def text_cleaner(text:string, punctuation:bool, special_char: bool, stop_words:bool, contractions:bool, numbers:bool, non_english:bool, lammatize:bool, stem:bool, replacements:dict ):
    text = basic_cleaning(text, punctuation)
    if replacements != None:
        text = replace_words(text, replacements)
    if special_char:
        text = remove_special_characters(text)
    if contractions:
        text = clean_contractions(text)
    if numbers:
        text = removing_numbers(text)
    if non_english:
        text = removing_non_english(text)
    if lammatize:
        text = lammatize_text(text)
    if stem:
        text = stem_text(text)
    if stop_words:
        text = remove_stop_words(text)
    return text



#### Creating N-grams

def creating_bigrams(text:str):
    ''' This function returns bigrams. '''
    sentences = tokenizer.tokenize(text)
    bigrams = []
    for sentence in sentences:
        bigrams.extend(list(nltk.bigrams(sentence.split())))
    return bigrams

def creating_unigrams(text:str):
    ''' This function returns unigrams. '''
    return text.split()


#### Detect Language

class language_detection_spacy():
    def __init__(self):
        def get_lang_detector(nlp, name):
                return LanguageDetector(seed=42)  # We use the seed 42

        self.nlp_model = spacy.load("en_core_web_sm")
        Language.factory("language_detector", func=get_lang_detector)
        self.nlp_model.add_pipe('language_detector', last=True)

    def detect_language(self, text:str):
        ''' This function detects the language of the text. '''
        doc = self.nlp_model(text)
        language = doc._.language
        return language['language'], language['score']


class languate_detection_fasttext():

    def __init__(self):
        pretrained_lang_model = "/Volumes/Research/e01_Amazon/02_empirics/00_data/external/lid.176.bin"
        self.model = fasttext.load_model(pretrained_lang_model)

    def detect_language(self, text):
        predictions = self.model.predict(text, k=1) # returns top 2 matching languages
        return predictions[0][0].replace('__label__', ''), predictions[1][0]



