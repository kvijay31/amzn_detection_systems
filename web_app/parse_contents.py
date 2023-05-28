from dash import html
import json
from predictions import get_prediction

def pre_process(review_text, classifier): 
    try: 
        if len(review_text)>0: 
            prediction = get_prediction(review_text, classifier)
            print(prediction)
            for key in prediction.keys(): 
                print(key)
                print(type(key))
                if key == 1: 
                    result = f'input string: \n {review_text}\n'
                    output= f'Ouput of Classification: It is {classifier} with probability {prediction[key]}'
                else:

                    result = f'Input String: \n {review_text}'
                    output = f'Ouput of Classification: It is not classified as {classifier} with probability {prediction[key]}'
                    

    except Exception as e: 
        return html.Div([
            'The input text is not of sufficient length. There is an error in processing the file.'
        ])
    return html.Div([
        html.Div(
        [html.Br(), html.Div(result, style ={'font-size':'20px', 'font-weight': 'bold', 'text-align': 'center'})
        ]
        ),
        html.Div(
         [html.Br(), html.Div(output, style ={'font-size':'20px', 'font-weight': 'bold', 'text-align': 'center'})
        ]
        ), 
        html.Hr()
        
    ])