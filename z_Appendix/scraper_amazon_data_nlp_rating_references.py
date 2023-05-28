########################## Setting up paths ############################

import sys
import os 

def setting_up_code_directory():
    paths = ["/Users/ohegers/Github/Amazon/01_Clean_WP_1/"]
    check = False
    for path in paths:
        if os.path.exists(path):
            sys.path.append(path)
            check = True
            break 
    if check:
        print(f"The root directory is: {path}")
    else: 
        print("Could not identify a root directoy")

setting_up_code_directory()

######################### Importing modules #############################

import json
from pandas import DataFrame
import re
import datetime
import pycountry
import Libs.nlp.text_cleaning as text_cleaning
import os
import pickle
import Libs.global_functions as global_functions
import pandas as pd
import numpy as np
from p_tqdm import p_imap

language_detection = text_cleaning.languate_detection_fasttext()

AMAZON_DATA = global_functions.code_file_basics(storage_name= "amazon_data") #Add data directories to libs.gobal_functions
AMAZON_DATA.print_paths()


def clean_reviews_rating_references(amazon_reviews:DataFrame, max_reviews = None) -> DataFrame:
    '''
    This function takes a DataFrame containing reviews, splits the review in sentences, looks for references to rating or reviews, and returns a new DataFrame.
    If desired, maximum number of reviews can be set. 
    '''
    amazon_reviews = amazon_reviews[(amazon_reviews["language"] == 'en') ].sample(frac  =1,  random_state=1).to_dict(orient = "records")
    if max_reviews:
        print(f"Process only {max_reviews} of {len(amazon_reviews)}")
        amazon_reviews = amazon_reviews[0:max_reviews]
    else:
        print(f"Process all {len(amazon_reviews)}.")

    def processing_reviews(chunk:list):
        amazon_review_cleaned = []
        for review in chunk:
            senteces = text_cleaning.split_into_sentences(text = review['text'])
            for sentence in senteces:
                temp = {"asin": review["asin"], 'review_id': review["review_id"], 'reviewer_id': review["reviewer_id"], 'date': review["date"], 'YYWW': review["YYWW"], "full_review": review["text"] }
                temp['sentence'] =  sentence
                temp['text_clean'] = text_cleaning.text_cleaner(text = sentence, non_english= False,  punctuation= True, special_char= True, stop_words= True, contractions= True, numbers= False, lammatize= True, stem = True, replacements= None)
                temp['text_unigrams'] = text_cleaning.creating_unigrams(temp['text_clean'])
                temp['rating_reference'] =  1 if ("rate" in temp['text_unigrams']) else 0
                temp['star_reference'] =  1 if ("star" in temp['text_unigrams']) else 0
                temp['review_reference'] =  1 if ("review" in temp['text_unigrams']) else 0
                amazon_review_cleaned.append(temp)
                del temp
        return amazon_review_cleaned

    print("Start multi-processing!")
    chunk_size = 100
    chunks = [amazon_reviews[i:i + chunk_size] for i in range(0, len(amazon_reviews), chunk_size)]
    multi_processing_output = [ x for x in p_imap(processing_reviews, chunks ) ]

    return DataFrame([item for sublist in multi_processing_output  for item in sublist]) 
    


######  Office Products ##########

with open(AMAZON_DATA.directory_processing + "office_indvidual_reviews.pkl", 'rb') as file:
    amazon_reviews = pickle.load(file)


amazon_reviews_df = clean_reviews_rating_references(amazon_reviews=amazon_reviews[amazon_reviews['rating'] <= 2 ])
amazon_reviews_df_temp = amazon_reviews_df[(amazon_reviews_df['rating_reference'] == 1) | (amazon_reviews_df['star_reference'] == 1) | (amazon_reviews_df['review_reference'] == 1)].reset_index(drop = True) 
amazon_reviews_df_temp["sentence"] = amazon_reviews_df_temp["sentence"].apply(lambda x: ' ' + x)
len(amazon_reviews_df_temp)

if 1 == 0:
    amazon_reviews_df_temp.to_pickle(AMAZON_DATA.directory_processing + "office_indvidual_reviews_reference.pkl")
    #Be mindful, do not override hand-coded classifications.
    amazon_reviews_df_temp.to_excel(AMAZON_DATA.directory_processing + "office_indvidual_reviews_reference.xlsx")



