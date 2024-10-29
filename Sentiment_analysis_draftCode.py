import pandas as pd
import numpy as np
import nltk
from transformers import BertTokenizer, TFBertForSequenceClassification
from scipy.special import softmax
import re
from nltk.corpus import stopwords
#import cx_Oracle
import traceback
#import Database_config

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



def do_analysis(df):
    try:
        print(df.columns)
        df.columns = ['Review', 'Ratings', 'Reviewer', 'Date_Posted','product_title','tcin_number','upc_number','item_number']
        df = df.dropna()

        df['Review'] = df['Review'].apply(
            lambda x: re.sub(r'\[.?This review was collected as part of a promotion\..?\]', '', str(x)))
        df['Review'] = df['Review'].apply(lambda x: " ".join(re.sub(r'[^\w\s]', '', word.lower()) for word in x.split()))

        target_data = df.copy()
        target_data['Review'] = target_data['Review'].apply(remove_stopwords)

        df[['negative', 'neutral', 'positive']] = df['Review'].apply(lambda x: pd.Series(get_sentiment_scores(x)))
        df['emotion'] = df[['negative', 'neutral', 'positive']].apply(lambda x: get_sentiment_label(x.values), axis=1)
        csv_file_name = 'reviews_sentiment.csv'
        df.to_csv(csv_file_name, index=False)
        print('saving output')
        #
        # insert_into_database(df)
        # print('data inserted')
    except Exception as e:
        print(e)
        print(traceback.print_exc())
