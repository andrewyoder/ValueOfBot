# imports
```
import praw
import pprint
```

# creating the reddit instance (needed for API calls)
`reddit = praw.Reddit("ValueOfBot", config_interpolation="basic")`

- shows redditor name (mine)
`print(reddit.user.me())`

- shows the available actions for our reddit instance
`print(reddit.auth.scopes())`

# to access a specific subreddit:
mySub = reddit.subreddit('ValueOfBot')

- we can also monitor multiple subreddits with a `+`, or scan all and remove some with a `-`
```
mySub = reddit.subreddit("ValueOfBot+AskReddit+LearnPython")
mySub = reddit.subreddit("all-ValueOfBot")
```

- For front page listings:
```
for submission in reddit.front.hot():
    print(submission)
```

- submissions sorted by top, hot, new, rising, controversial, gilded
- limit is the number of submissions we want to show
```
for submission in subreddit.top(limit=1):
    # some actions we can take on "submission"
    submission.title, .score, .id, .url
```


# getting Redditor info
```
    redditor = submission.author
    redditor.name, .link_karma
``` 

# COMMENTS
- change the sort order like so, with values of `hot, controversial, top, best, new`
    `submission.comment_sort = "new"`

- get new comments using the below, must be called AFTER a sort
- Note: calling `replace_more()` is destructive. Calling it again on the same submission instance has no effect.
- limit is how many comments we want to load--default is 32, and "none" will load all comments in the CommentForest
    `submission.comments.replace_more(limit=None)`

- to create a list of all top-level comments
    `topLevelComments = list(submission.comments)`

- to create a list of ALL comments (sorted by first-level, second-level, etc)
- note we must call replace_more() BEFORE creating the list
    `allComments = submission.comments.list()`

- and then iterate with a simple
```
    for comment in allComments:
        print(comment)
```

- add `.body` to get only a comment's body--probably more what we want
        `print(comment.body)`


- to get only NEW comments (after bot has started running)
```
    for comment in subreddit.stream.comments(skip_existing=True):
        print(comment)
```

# Submission properties
- print the attributes of a submission object with `vars()` and `pprint`
- must call some other function first to make the object "non-lazy"
- `vars()` shows all available attributes and their values (when non-lazy)
```
    print(submission.title)
    pprint.pprint(vars(submission))
```

- we can also check the number of comments with
    `submission.num_comments`
though this may not match up with all the comments extracted by PRAW, since it includes deleted, removed, and spam comments

# Submission stream
- We probably want to use the submission stream to monitor only new comments, we can do this with
```
subreddit = reddit.subreddit("ValueOfBot")
for submission in subreddit.stream.submissions():
    do something...
```

# Replying to a comment
- we can reply to a comment with simply:
    `comment.reply("response")`