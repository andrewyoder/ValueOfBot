import praw
import pprint

RESPONSE_TEMPLATE = "%s is roughly %d bananas."

def main():
    reddit = praw.Reddit("ValueOfBot", config_interpolation="basic")

    # testing on my own, private sub
    mySub = reddit.subreddit("ValueOfBot")

    # iterate through submissions
    # may want to replace with "mySub.stream.submissions()" after testing to access new submissions
    for submission in mySub.top(limit=3):
        
        # sort by top comments
        submission.comment_sort = "top"

        # get a CommentForest, populate it with every comment
        submission.comments.replace_more(limit=None)
        allComments = submission.comments.list()

        # iterate through our comments
        for comment in allComments:
            if '$' in comment.body:
                comment.reply(extract_value(comment.body))
                break


def extract_value(comment):
    return comment


if __name__ == "__main__":
    main()