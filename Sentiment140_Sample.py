#!python3
# -*- utf-8 -*-

#import os
#import pymssql
#from requests import request
#from urllib import urllib.request


import sys
import json
import pyodbc
import urllib2
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


#pass security information to variables  <-- all the keys should be read from a file and should be removed from the code
consumer_key="7jbj51PhiMzlA50SpM0KTgARB"
consumer_secret="sTjKyEeUojCDG8ja7EY00uk6BwlUavCEzlocgrhoC6NsO8mKsL"
access_key = "155989537-TomVnKsSP49FIICZxIXc98DDqGLbsTCqf0Oh1lJt"
access_secret = "yBXY1XUZ2p1v1537oSboFl0byRXPaKAhUfKIPKdoLZOD4"

#Connection Parameter
cnxn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};Server=tcp:personaltwitter.database.windows.net;PORT=1433;Database=Personal_TwitterDB;Uid=personaltwitteradmin;Pwd=Personal_Password')
cursor = cnxn.cursor()

#cursor.execute("SELECT WORK_ORDER.TYPE,WORK_ORDER.STATUS, WORK_ORDER.BASE_ID, WORK_ORDER.LOT_ID FROM WORK_ORDER")
#for row in cursor.fetchall():
#    print row

#use variables to access twitter   
auth = OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_key, access_secret)

#create an class called 'customStreamListener'
class listener(StreamListener):
    def on_data(self, data):
        all_data = json.loads(data)

        tweet = all_data['text']
        tweet_id = all_data['id_str']
        tweet_url = all_data['entities']['urls']
        print tweet_id
        print tweet_url
        print tweet

        process_db(all_data)
        #username = all_data["user"]["screen_name"]
        #retweet_count=0
        #if (all_data['retweeted']):
        #    retweet_count = all_data["retweet_count"]

        #c.execute("INSERT INTO taula (time, username, tweet) VALUES (%s,%s,%s)",
        #          (time.time(), username, tweet))

        #conn.commit()
        #if retweet_count > 0:
        #    print(tweet)
        #    print (username)
         #   print(retweet_count)

        return False

    def on_error(self):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream

    
def process_db(all_data):
    '''
    Function: To post the data to database for historical analysis and fetching
    
    Param: all_data: the data which is to be posted in the database
     
    Return:  
    '''
    tweetid = all_data['id_str']
    retweet = all_data['retweeted']  #bool  <-- modify db column
    username = all_data['user']['screen_name']
    favorited = all_data['favorited']   #bool <-- modify db column
    user_followers = all_data['user']['followers_count']
    user_friends = all_data['user']['friends_count']
    retweet_count  = all_data['retweet_count']
    cursor.execute('insert into personal_twitter_schema.tweets_data_test (tweetid, retweet, username, favorited, user_followers, user_friends, retweet_count) values (?,?,?,?,?,?,?)',
                  tweetid, retweet, username, favorited, user_followers, user_friends, retweet_count)
    cnxn.commit()
    print username

def sentiment_analysis(text):
    '''
    Function: Analyzes the sentiment of the text sent using sentiment140 api.
    
    Param text: Pass the pre parsed text to the function without any url or hashtags
      
    Return: Returns the Sentiment_score of the text passed
    
    :dependencies: urllib2 and json for 
    '''
    response = urllib2.urlopen('http://www.sentiment140.com/api/bulkClassifyJson', text)  # request to server
    page = response.read()  # get the response
    print page  # print the result

    sentiment_out_raw = json.loads(page)  # parse the result. The result is in JSON format
    sentiment_score = sentiment_out_raw['data']['polarity']
    return sentiment_score

def post(url, data):
    '''
    Function: to post data to powerbi streaming dataset.
    
    Param: Powerbi url along with data which is to be transmitted
    
    Return: Returns the HTTP response code
    
    Dependencies: urllib2 and time packages
    '''
    try:
    # make HTTP POST request to Power BI REST API
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        print("POST request to Power BI with data:{0}".format(data))
        print("Response: HTTP {0} {1}\n".format(response.getcode(), response.read()))
        return [response.getcode(), response.read()]
        time.sleep(1)

    except urllib2.HTTPError as e:
        return [e.reason, e.code]

    except urllib2.URLError as e:
        return [e.reason, e.code]

    except Exception as e:
        return [e.reason, e.code]

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["#android"],languages=['en'])


{"data": [{"text": "{0}","query": "{1}"}.format(tweet,filter_words)]
