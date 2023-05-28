import pandas as pd 
import os 
import json 
import tensorflow as tf
import warnings 
warnings.filterwarnings("ignore")
from transformers import RobertaTokenizer


def prepare_data(input_text, tokenizer):
    with tf.device('/device:GPU:0'):
        
        token = tokenizer.encode_plus(
            input_text,
            max_length=256, 
            truncation=True, 
            padding='max_length', 
            add_special_tokens=True,
            return_tensors='tf'
        )
        return {
            'input_ids': tf.cast(token.input_ids, tf.float64),
            'attention_mask': tf.cast(token.attention_mask, tf.float64)
        }

def make_predictions(model, input_text,threshold=0.5, label_list=None ): 
    with tf.device('/device:GPU:0'):
        tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        processed_data = prepare_data(input_text, tokenizer)
        probs = model.predict(processed_data)
        if probs[0]> threshold: 
            return {label_list[0]:float(probs[0])}
        else: 
            return {label_list[1]: float(1-probs[0])}
        
def get_prediction(review, classifier): 
    label_list= [1, 0]
    if classifier == 'Rating Management Explicit': 
        model = tf.keras.models.load_model('/Users/kartikvijay/Documents/MADS/Thesis pt.2/web_app/models/rating_managment_explicit_v1')
    elif classifier == 'Disagreement With Rating': 
       model = tf.keras.models.load_model('/Users/kartikvijay/Documents/MADS/Thesis pt.2/web_app/models/disagreement_with_ratings_v1')
    elif classifier== 'Zero Star': 
        model = tf.keras.models.load_model('/Users/kartikvijay/Documents/MADS/Thesis pt.2/web_app/models/zero_star_v1')
    elif classifier == 'Wrong Buying': 
        model = tf.keras.models.load_model('/Users/kartikvijay/Documents/MADS/Thesis pt.2/web_app/models/wrong_buying_v1')
    else:
        model = tf.keras.models.load_model('/Users/kartikvijay/Documents/MADS/Thesis pt.2/web_app/models/read_reviews_v1')
    return make_predictions(model, review,0.5, label_list)


