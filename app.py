from flask import Flask, render_template
import os
import tweepy
import openai

app = Flask(__name__)

def get_twitter_auth():
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def fetch_tweets(api):
    # ここでキーワードや検索条件を設定して、Tweetを検索します。
    search_words = "ChatGPT"
    tweets = api.search_tweets(q=search_words, count=10)
    return [tweet.text for tweet in tweets]

def fetch_gpt_info():
    api = get_twitter_auth()
    tweets = fetch_tweets(api)

    openai.api_key = os.environ.get("OPENAI_API_KEY")

    translated_tweets = []
    for tweet in tweets:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Translate and summarize the following information about ChatGPT from English to Japanese in an easy-to-understand manner: {tweet}",
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        translated_tweet = response.choices[0].text.strip()
        translated_tweets.append(translated_tweet)

    return translated_tweets

@app.route('/')
def index():
    translated_info = fetch_gpt_info()
    return render_template('index.html', translated_info=translated_info)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
