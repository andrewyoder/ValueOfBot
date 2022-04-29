import praw
import os
import psycopg2
from psycopg2 import sql

# to add back in when getting updated banana prices via the web
'''
from bs4 import BeautifulSoup as BS
import urllib.request as urllib
'''


RESPONSE_TEMPLATE = "$%s is roughly %.1f bananas."
RESPONSE_FOOTER = "\n\n^(I am a bot currently in development. " \
                  "DM me with any suggestions.)"
CURRENCY = '$'
SUBREDDITS = "funny+AskReddit+facepalm+gaming+mildlyinfuriating" \
             "+mildlyinteresting+funnyanimals+meirl"


def main():
    """
    main() creates the reddit instance, accesses the subreddits we want
    to monitor, and passes submissions from those subreddits to 
    process_comments()

    the reddit instance is created from values stored in a hidden praw.ini file
    """

    # create reddit and subreddit instances
    print("Logging in...")
    reddit = login_heroku()
    print("Login successful.")
    print("Establishing subreddit instances...")
    mySub = reddit.subreddit(SUBREDDITS)
    print("Subreddit instances established.")

    # connect to db to store "seen" comments
    print("Connecting to database...")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    print("Database connection successful.")

    print("Going through submissions...")
    for submission in mySub.stream.submissions():
        submission.comment_sort = "best"
        submission.comments.replace_more(limit=None)
        commentForest = submission.comments.list()
        process_comments(commentForest, cur)
        conn.commit()

    # close db connection
    print("Closing database connections...")
    cur.close()
    conn.close()
    print("Database connections closed.")

    return 0
        

def process_comments(commentForest, cur):
    """
    process_comments() iterates through each comment in the CommentForest
    to see if a comment contains a currency value. if a currency symbol is
    found, the value is extracted and a response is formed.

    :param commentForest: the complete list of comments from a given submission
    :param cur: cursor in our database for adding "seen" comments
    """

    for comment in commentForest:
        if CURRENCY in comment.body:
            
            print((comment.subreddit).name + ': ' + 
                comment.submission.title + ' - ' + comment.id)

            # don't reply to myself
            if ((comment.author).name == 'ValueOfBot'):
                print("Skipping comment - I am the author.")
                continue

            # see if we've replied to this comment already
            try:
                query = sql.SQL("SELECT * FROM {table} WHERE {pkey} = %s".format(
                        table=sql.Identifier('replied_comments'),
                        pkey=sql.Identifier('comment_id')), 
                        comment.id)
                print(query).as_string()
                cur.execute(query)
                # cur.execute("SELECT comment_id FROM replied_comments " \
                #             "WHERE comment_id = comment.id")
                # found = cur.fetchone()
            except:
                print("Skipping comment - cur.execute() failed.")
                continue
            if (cur.fetchone()):
                print("Skipping comment - already responded.")
                continue

            print("New comment. Forming response.")

            # haven't responded yet, so let's respond
            value = extract_value(comment.body)
            if (value == None):
                print("Skipping comment - failed to extract value.")
                break
            intValue = float(value.replace(CURRENCY, ''))

            comment.reply(RESPONSE_TEMPLATE % (value, 
                    (intValue/get_banana_value())) + 
                    RESPONSE_FOOTER)

            print("Responded. Inserting comment ID %s into table.", comment.id)
            cur.execute(
                sql.SQL("INSERT INTO {} VALUES (%s, %s)")
                    .format(sql.Identifier('replied_comments')),
                    [comment.id, (comment.subreddit).name])
            # cur.execute("INSERT INTO replied_comments (comment_id, subreddit)"\
            #             "VALUES (${comment.id}, ${comment.subreddit.name})")

            # if I decide to check all currency values in a comment,
            # rather than just the first:
            '''
            values = extract_values(comment.body, currency)
            response = ''
            for value in values:
                response += RESPONSE_TEMPLATE
                      % (value, intValue/get_banana_value()) + '\n'
            print(response)
            comment.reply(response)
            '''
    return


def login_heroku():
    """
    login_heroku() fetches a reddit instance with our saved login config.
    
    :return: a reddit instance
    """

    return praw.Reddit(username = os.environ["reddit_username"],
            password = os.environ["reddit_password"],
            client_id = os.environ["client_id"],
            client_secret = os.environ["client_secret"],
            user_agent = os.environ["user_agent"],
            ratelimit_seconds=900,
            config_interpolation="basic")


# for local testing
def login_local():
    return praw.reddit("ValueOfBot", config_interpolation="basic")
    

def extract_value(comment):
    """
    extract_value() returns the first currency value in a comment.
    this will be replaced by extract_values(), which will return an array
    of ALL currency values found in a comment.

    :param comment: the comment body that contains a currency symbol
    :return: the word containing our currency value, as a string
    """
    comment = comment.split(' ')
    for word in comment:
        if CURRENCY in word:
            # remove the '$' character
            word = word.replace(CURRENCY, '')
            # check if decimal is actually period at end of sentence
            if word[-1] == '.':
                word = word[:-1]
            # some voodoo to make sure there's only one decimal present
            # (remove 1 decimal and call isdigit(), works with integers)
            if word.replace('.', '', 1).isdigit():
                return word

'''
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
'''

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