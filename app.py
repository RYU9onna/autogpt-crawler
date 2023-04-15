from flask import Flask, render_template, request
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

def fetch_tweets(api, search_words, count):
    tweets = api.search_tweets(q=search_words, count=count)
    return [tweet.text for tweet in tweets]

def fetch_gpt_info(prompt1, prompt2, search_words, count):
    api = get_twitter_auth()
    tweets = fetch_tweets(api, search_words, count)

    openai.api_key = os.environ.get("OPENAI_API_KEY")

    translated_tweets = []
    for tweet in tweets:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"{prompt1}: {tweet}",
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        translated_tweet = response.choices[0].text.strip()
        translated_tweets.append(translated_tweet)

    # Extract the most interesting news
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{prompt2}",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    buzzworthy_tweet = response.choices[0].text.strip()
    return translated_tweets, buzzworthy_tweet

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt1 = request.form['prompt1']
        prompt2 = request.form['prompt2']
        search_words = request.form['search_words']
        count = int(request.form['count'])
        translated_info, buzzworthy_tweet = fetch_gpt_info(prompt1, prompt2, search_words, count)
        return render_template('index.html', translated_info=translated_info, buzzworthy_tweet=buzzworthy_tweet)

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
