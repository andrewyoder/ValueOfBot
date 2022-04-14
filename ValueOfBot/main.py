import time
import re
import praw
from turtle import fd
import pprint

# to add back in when getting updated banana prices via the web
'''
from bs4 import BeautifulSoup as BS
import urllib.request as urllib
'''

RESPONSE_TEMPLATE = "$%s is roughly %.1f bananas."
RESPONSE_FOOTER = "\n\n^(I am a bot currently in development. DM me with any suggestions.)"
CURRENCY = '$'
SUBREDDITS = "funny+AskReddit+facepalm+gaming+mildlyinfuriating+mildlyinteresting+funnyanimals+meirl"


def main():
    """
    main() creates the reddit instance, accesses the subreddits we want
    to monitor, and passes submissions from those subreddits to 
    process_comments()

    the reddit instance is created from values stored in a hidden praw.ini file
    """

    # new reddit instance, configured from praw.ini
    reddit = praw.Reddit("ValueOfBot", config_interpolation="basic")

    mySub = reddit.subreddit(SUBREDDITS)

    # TODO replace with "mySub.stream.submissions()" to access 
    # only new submissions
    for submission in mySub.stream.submissions():
        print(submission.title)
        submission.comment_sort = "best"
        submission.comments.replace_more(limit=None)
        commentForest = submission.comments.list()
        process_comments(commentForest)

    return 0
        

def process_comments(commentForest):
    """
    process_comments() iterates through each comment in the CommentForest
    to see if a comment contains a currency value. if a currency symbol is
    found, the value is extracted and a response is formed.

    :param commentForest: the complete list of comments from a given submission
    """

    for comment in commentForest:
        if CURRENCY in comment.body:
            # TODO create an array of all currency values 
            # mentioned in the comment; currently just the first
            value = extract_value(comment.body)
            if (value == None):
                break
            intValue = float(value.replace(CURRENCY, ''))
            comment.reply(RESPONSE_TEMPLATE % (value, 
                    (intValue/get_banana_value())) + 
                    RESPONSE_FOOTER)
            # ratelimit should be handled by 15 minute PRAW setting,
            # but may need to add in a generic sleep()
            continue

            # NOTE: when multiple values are extracted, do not post a reply
            # until all currency symbols have been iterated through

            # values = extract_values(comment.body, currency)
            # response = ''
            # for value in values:
            #     response += RESPONSE_TEMPLATE
            #           % (value, intValue/get_banana_value()) + '\n'
            # print(response)
            # comment.reply(response)
    
    return


def extract_value(comment):
    """
    extract_value() returns the first currency value in a comment.
    this will be replaced by extract_values(), which will return an array
    of ALL currency values found in a comment.

    :param comment: the comment body that contains a currency symbol
    :return: the word containing our currency value, as a string
    """
    print(comment)
    comment = comment.split(' ')
    for word in comment:
        if CURRENCY in word:
            word = word.replace(CURRENCY, '')
            # print(word + ": " + str(word.replace(currency, '').isnumeric()))
            if word.replace('.', '', 1).isdigit():
                # TODO: check if period is just end of a sentence
                print(word)
                return word


def extract_values(comment, currency):
    """
    extract_values() returns an array of all currency values found in
    a comment for the given currency symbol passed

    :param comment: the comment body that contains a currency symbol
    :param currency: the currency symbol we're checking for
    :return: the word containing our currency value, as a string
    """
    values = []

    comment = comment.split(' ')
    for word in comment:
        if currency in word:
            if word.replace(currency, '').isdigit():
                values.push(word)

    return values


def get_banana_value():
    """
    get_banana_value() currently returns a hard-coded value, but will check
    the Trader Joe's website to get an updated value.

    :return: the current price of a banana
    """
    return 0.19

    # TODO get value from web, but for now, use $0.19/banana
    '''
    url ="https://www.traderjoes.com/home/products/pdp/bananas-048053"
    usock = urllib.urlopen(url)
    data = usock.read()
    usock.close()
    soup = BS(data, features='html.parser')
    # below <span class='ProductPrice_productPrice__price__3-50j'> returns None
    return soup.find('span', 
        {'class':'ProductPrice_productPrice__price__3-50j'}).text
    '''

'''
Value of a banana (in USD) found at 
https://www.traderjoes.com/home/products/pdp/bananas-048053, 
class = 'ProductPrice_productPrice__price__3-50j'
'''


if __name__ == "__main__":
    main()