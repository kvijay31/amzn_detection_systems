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

class amazon_product_review():
    """
    This object contains an Amazon Product Review that is cleaned and usable.
    """

    def __init__(self, review:dict):
        self.review_id = review['review_id']
        self.text = review['review_body']
        self.title = review['review_title']
        self.account_name = review['account_name']
        self.account_link = review['account_link']
        self.purchase_type = review['purchase_type']
        self.helpful_votes = review['helpful_votes']
        self.location_date(review)
        self.clean_text_basic()
        self.clean_title()
        self.generate_reviewer_id()
        self.generate_helpful_votes()
        self.generate_verified_purchase()

        self.rating = float(review['rating'].replace(" out of 5 stars", ""))

       
    def location_date(self, review:dict):
        temp_string = re.search(r'on\s[A-Za-z]+\s\d{1,2},\s\d{4}', review['review_date'])[0]
        self.date = datetime.datetime.strptime(temp_string.replace("on ", ""), '%B %d, %Y').date()
        self.YYWW = str(self.date.isocalendar().year)+ "-" + str(self.date.isocalendar().week).zfill(2)

        raw_location =  review['review_date'].replace(temp_string, "")
        for country in pycountry.countries:
            if country.name in raw_location:
                self.location = country.name

    def clean_text_basic(self):
        if self.text:
            self.text = self.text.replace("\n", " ").strip()
            self.text = self.text.replace("\s+", " ")
    
    def clean_text_advanced(self):
        if self.text:
            self.cleaned =  text_cleaning.text_cleaner(text = self.text, punctuation = True, special_char = True, stop_words = True, contractions = True, numbers = True, non_english = False, lammatize = True, stem = False, replacements = None )
        else:
            self.cleaned = None

    def detect_language(self):
        if self.text:
            self.language, self.language_score = language_detection.detect_language(self.text)
        else:
            self.language = None
            self.language_score = None

    def clean_title(self):
        if self.title:
            self.title = self.title.replace("\n", " ").strip()
            self.title = self.title.replace("\s+", " ")

    def generate_reviewer_id(self):
        if self.account_link:
            self.reviewer_id = self.account_link.replace("/gp/profile/amzn1.account.", "").replace("/ref=cm_cr_arp_d_gw_btm?ie=UTF8", "")
        else:
            self.reviewer_id =  np.nan

    def generate_helpful_votes(self):
       
        if self.helpful_votes == 0:
            self.helpful_votes = 0 
        elif 'one person' in self.helpful_votes.lower():
            self.helpful_votes = 1
        else: 
            temp = re.findall(r'\d+', self.helpful_votes)
            self.helpful_votes = int(temp[0]) if temp else 0

    def generate_verified_purchase(self):
        self.verified_purchase = True if self.purchase_type == 'Verified Purchase' else False

class amazon_product():
    """
    This object contains an Amazon product that is cleaned and usable. 
    """
    def __init__(self, product:dict):

        #Rating distribution
        if product['rating_histogram']:
            rating_distribution = []
            for value in product['rating_histogram']:
                if value:
                    rating_distribution.append(int(re.search(r'\s\d{1,3}\%\s', value)[0].replace("%", "").strip()))
                else:
                    rating_distribution.append(0)
            self.rating_distribution = rating_distribution
        else: 
            self.rating_distribution = None
        #self.status_code = product['status_code']
        self.reviews = product['reviews']
        self.asin = product['asin']
        self.rating_global = product['rating']
        self.rating_count = product['rating_count']
        self.review_count = product['review_count']


### Import individual reviews 


def import_reviews_from_json(review_files:list) -> DataFrame:
    '''
    This function takes a list of paths to json files that contain scraped Amazon reviews, and processes the data to a DataFrame. The function returns two DataFrames (i.e., product and review level).
    '''
    def processing_reviews_from_json(file:str):
        print(file)
        amazon_reviews = []
        amazon_products = [] 
        counter = 0
        for line in open(AMAZON_DATA.directory_input + file , "r", encoding="utf-8"):
            counter += 1
            if counter % 10000 == 0:
                print(counter)
            temp_product =  json.loads(line)
            if 'rating_count' in temp_product:
                product = amazon_product(product = temp_product) 
                if product.reviews:
                    review_ratings = []  
                    for temp_review in product.reviews:
                        review = amazon_product_review(review= temp_review)
                        review.detect_language()
                        review_ratings.append(review.rating)
                        amazon_reviews.append({"file": file, "asin": product.asin, "review_id": review.review_id, "reviewer_id": review.reviewer_id, "rating": review.rating, "date": review.date, "YYWW": review.YYWW,  "location": review.location, "title": review.title, "text": review.text, "language": review.language, "votes": review.helpful_votes, "verified": review.verified_purchase})
                    review_distribution = [round((review_ratings.count(x) / len(review_ratings)) , 3) for x in range(5,0, -1) ]
                    plausi_check =  True if product.review_count == len(product.reviews) else False
                else:
                    review_distribution = np.nan
                    plausi_check = np.nan
                
                rating_distribution =  [percentage / 100 for percentage in product.rating_distribution] 
                
                amazon_products.append({"file": file, "asin": product.asin, "rating": product.rating_global, "rating_count": product.rating_count, "review_count": product.review_count, "distribution": rating_distribution, "review_distribution": review_distribution, "plausi_check": plausi_check})
        return {"amazon_products": amazon_products, "amazon_reviews": amazon_reviews}

    print("Start multi-processing!")
    multi_processing_output = [ x for x in p_imap(processing_reviews_from_json, review_files ) ]

    amazon_products = [x["amazon_products"] for x in multi_processing_output]
    amazon_products = [item for sublist in amazon_products  for item in sublist]

    amazon_reviews = [x["amazon_reviews"] for x in multi_processing_output]
    amazon_reviews = [item for sublist in amazon_reviews  for item in sublist]

    amazon_products = DataFrame(amazon_products)
    print(f"# Products {len(amazon_products)}")
    amazon_reviews = DataFrame(amazon_reviews)
    print(f"# Reviews {len(amazon_reviews)}")

    return amazon_products, amazon_reviews

review_files = [x for x in os.listdir(AMAZON_DATA.directory_input) if x[0] != "." and ".json" in x and "office" in x]
amazon_products, amazon_reviews = import_reviews_from_json(review_files )

with open(AMAZON_DATA.directory_output + "office_products.pkl", 'wb') as f:
    pickle.dump(amazon_products, f)


with open(AMAZON_DATA.directory_processing + "office_indvidual_reviews.pkl", 'wb') as f:
    pickle.dump(amazon_reviews, f)

""" 
with open(AMAZON_DATA.directory_processing + "products.pkl", 'rb') as f:
    x = pickle.load(f)
"""


### Transform individual reviews to a week format (i.e., average ratings, rating distribution)

with open(AMAZON_DATA.directory_processing + "indvidual_reviews.pkl", 'rb') as file:
    amazon_reviews = pickle.load(file)


def creating_weekly_data(amazon_reviews:list):
    """
    This function uses individual reviews stored as a list containing dictionaries, and creates a DataFrame that stores the weekly, accumulated rating averages as well as rating distributions.
    """

    print("Part 1")
    data = DataFrame(amazon_reviews)
    data = data[['asin', 'date', 'rating']]

    data['h_rating'] = data['rating'].astype(int)
    data['h_rating_1'] = np.where(data['h_rating']==1, 1, 0)
    data['h_rating_2'] = np.where(data['h_rating']==2, 1, 0)
    data['h_rating_3'] = np.where(data['h_rating']==3, 1, 0)
    data['h_rating_4'] = np.where(data['h_rating']==4, 1, 0)
    data['h_rating_5'] = np.where(data['h_rating']==5, 1, 0)

    data['date'] = data['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d', errors = 'coerce'))
    data['YYWW'] = data['date'].dt.isocalendar().year.astype(str) + "-" + data['date'].dt.isocalendar().week.astype(str).str.zfill(2)
    data['helper'] = data['asin'] + data['YYWW']
    data = data.sort_values(['asin', 'YYWW'], ascending=True).reset_index(drop=True)

    print("Part 2")
    data['rating_count'] = data.groupby('asin').cumcount() + 1
    data['rating'] = data.groupby('asin')['h_rating'].cumsum() / data['rating_count']
    data['rating_1'] = data.groupby('asin')['h_rating_1'].cumsum()
    data['rating_2'] = data.groupby('asin')['h_rating_2'].cumsum() 
    data['rating_3'] = data.groupby('asin')['h_rating_3'].cumsum() 
    data['rating_4'] = data.groupby('asin')['h_rating_4'].cumsum() 
    data['rating_5'] = data.groupby('asin')['h_rating_5'].cumsum()  
    data = data.groupby(['helper']).last().reset_index()

    result = []
    for asin in list(set(data['asin'].tolist())):
        timeCounter = 0 
        for i in range(1998, 2022):
            for j in range(1, 53):
                week = str(i) + "-" + str(str(j).zfill(2))
                result.append([asin, week])
                timeCounter += 1

    print("Part 3")
    sample = DataFrame(result, columns=['asin', 'YYWW'])
    sample['helper'] = sample['asin'] + sample['YYWW']
    sample['rating'] = sample['helper'].map(data.set_index('helper')['rating'])
    sample['rating_1'] = sample['helper'].map(data.set_index('helper')['rating_1'])
    sample['rating_2'] = sample['helper'].map(data.set_index('helper')['rating_2'])
    sample['rating_3'] = sample['helper'].map(data.set_index('helper')['rating_3'])
    sample['rating_4'] = sample['helper'].map(data.set_index('helper')['rating_4'])
    sample['rating_5'] = sample['helper'].map(data.set_index('helper')['rating_5'])
    sample['ratingCount'] = sample['helper'].map(data.set_index('helper')['rating_count'])


    sample['rating'] = sample.groupby('asin')['rating'].ffill()
    sample['rating_1'] = sample.groupby('asin')['rating_1'].ffill()
    sample['rating_2'] = sample.groupby('asin')['rating_2'].ffill()
    sample['rating_3'] = sample.groupby('asin')['rating_3'].ffill()
    sample['rating_4'] = sample.groupby('asin')['rating_4'].ffill()
    sample['rating_5'] = sample.groupby('asin')['rating_5'].ffill()
    sample['ratingCount'] = sample.groupby('asin')['ratingCount'].ffill()

    sample = sample[sample['YYWW'] >= "2017-01"]
    sample = sample[sample['YYWW'] <= "2021-52"]
    sample = sample.drop_duplicates()
    sample = sample.dropna()
    sample['Treatment'] = 1
    sample['Post'] = np.where(sample['YYWW'] >= "2020-01", 1, 0)
    sample  = sample.reset_index(drop= True)
    print(f"Done crating weekly data for {len(sample['asin'].drop_duplicates())} products.")
    return sample

amazon_weekly = creating_weekly_data(amazon_reviews=amazon_reviews.values.tolist())

with open(AMAZON_DATA.directory_output + "amazon_reviews_weekly.pkl", 'wb') as f:
    pickle.dump(amazon_weekly , f)





