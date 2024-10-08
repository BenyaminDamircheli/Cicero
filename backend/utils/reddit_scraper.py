import praw
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

def scrape_reddit(subreddit, limit = 1000):
    reddit = praw.Reddit(
        client_id = "9YcMFjtzVTx8rrSwogcrQA",
        client_secret = "Zq-HkQnwdBsO_ZB6nCPtZm2wjA-e_A",
        user_agent = "webscraper"
    )

    subreddit = reddit.subreddit(subreddit)
    posts = subreddit.new(limit = limit)

    data = []

    for post in posts:
        summary = summarize_text(post.selftext)
        data.append({
            "title": post.title,
            "score": post.score,
            "body": post.selftext,
            "created": post.created_utc,
            "id": post.id,
            "url": post.url,
            "summary": summary
        })

    return data

def summarize_text(text, sentences_count=3):
    nltk.download('punkt')
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")

    summary = summarizer(parser.document, sentences_count)
    return " ".join([str(sentence) for sentence in summary])


scraped_data = scrape_reddit("toRANTo", 300)

for post in scraped_data:
    print("----------------------------------------")
    print("post title: ", post["title"] + "\n")
    print("----------------------------------------")
    print("post body: ", post["body"] + "\n")
    print("----------------------------------------")
    print("post summary: ", post["summary"] + "\n")
    print("----------------------------------------")