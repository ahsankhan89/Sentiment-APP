import pandas as pd
import numpy as np
import nltk
from transformers import BertTokenizer, TFBertForSequenceClassification
from scipy.special import softmax
import re
from nltk.corpus import stopwords
import traceback
import requests
from urllib.parse import urlencode

# nltk.download('stopwords')

MODEL = 'nlptown/bert-base-multilingual-uncased-sentiment'
tokenizer = BertTokenizer.from_pretrained(MODEL)
model = TFBertForSequenceClassification.from_pretrained(MODEL)
stop_words = stopwords.words('english')

def remove_stopwords(review):
    return " ".join([word for word in review.split() if word.lower() not in stop_words])

def get_sentiment_label(scores):
    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[np.argmax(scores)]
    return sentiment

def get_sentiment_scores(review):
    encoded_text = tokenizer(review, return_tensors='tf', padding=True, truncation=True, max_length=512)
    output = model(encoded_text)
    scores = output.logits.numpy()[0]
    scores = softmax(scores)
    return {
        'negative': scores[0] + scores[1],
        'neutral': scores[2],
        'positive': scores[3] + scores[4]
    }

## Creating Header for API Request
headers = {
            'User-Agent': 'My User Agent 1.0',
            'Content-Type': 'application/x-www-form-urlencoded',
}



def do_analysis(df):
    try:
        print(df.columns)
        df.columns = ['Review', 'Ratings', 'Reviewer', 'Date_Posted','product_title','tcin_number','upc_number','item_number','artautomationid','sentiment_date','recommendation']
        df = df.dropna()

        df['Review'] = df['Review'].apply(
            lambda x: re.sub(r'\[.?This review was collected as part of a promotion\..?\]', '', str(x)))
        df['Review'] = df['Review'].apply(lambda x: " ".join(re.sub(r'[^\w\s]', '', word.lower()) for word in x.split()))

        target_data = df.copy()
        target_data['Review'] = target_data['Review'].apply(remove_stopwords)

        df[['negative', 'neutral', 'positive']] = df['Review'].apply(lambda x: pd.Series(get_sentiment_scores(x)))
        df['emotion'] = df[['negative', 'neutral', 'positive']].apply(lambda x: get_sentiment_label(x.values), axis=1)

        ## Make Connection for Header and API Request
        print(df.head(10))

        headers = {
            'User-Agent': 'My User Agent 1.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        #
        url = "https://art.artisticmilliners.com:8081/ords/art/sentiment/sentiment_data"

        for index, row in df.iterrows():
            sentiment_data = {
                'REVIEW': row['Review'],
                'RATING': row['Ratings'],
                'PRODUCTNAME': row['product_title'],
                'TCIN': row['tcin_number'],
                 'UPC': row['upc_number'],
                'ITEMNUMBER': row['item_number'],
                'REVIEWDATE': row['Date_Posted'],
                'NEGATIVE_SCORE': row['negative'],
                'NEUTRAL_SCORE': row['neutral'],
                'POSITIVE_SCORE': row['positive'],
                'SENTIMENT': row['emotion'],
                'ARTAUTOMATIONID': row['artautomationid'],
                'SENTIMENTDATE': row['sentiment_date'],
                'RECOMMENDATION': row['recommendation']

            }
            form_data = urlencode(sentiment_data)
            res = requests.post(url, data=form_data, headers=headers,verify=False)

            print(f"Review: {row['Review']}")
        ########################################################
        csv_file_name = 'reviews_sentiment.csv'
        df.to_csv(csv_file_name, index=False)
        print('saving output')
        #
        # insert_into_database(df)
        # print('data inserted')
    except Exception as e:
        print(e)
        print(traceback.print_exc())
