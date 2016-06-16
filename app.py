#!/usr/bin/env python
# encoding: utf-8

import tweepy
import csv
import os
from time import sleep

#Twitter API credentials
consumer_key = os.environ["con_secret"]
consumer_secret = os.environ["con_secret_key"]
access_key = os.environ["token"]
access_secret = os.environ["token_key"]

handle_list_file = "handle_list_test.txt" #change for production list
keywords = ["transparencia"]


def build_counts(keywords, alltweets):
	output = {keyword:0 for keyword in keywords}
	for tweet in alltweets:
		for keyword in keywords:
			if keyword in tweet.text.lower():
				output[keyword] += 1
	return output


def get_tweet_counts(screen_name):
	print("Printing for " + screen_name)
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1

	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print("getting tweets before %s" % (oldest))
		#sleep(40) #to avoid twitter awfully low api limits.

		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

		#save most recent tweets
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

		print("...%s tweets downloaded so far" % (len(alltweets)))

	output = build_counts(keywords, alltweets)

	return output


def read_list_file(filepath):
	with open(filepath) as f:
		lines = f.read().splitlines()
	return lines


def print_first_row(keywords):
	first_row = "Handle"
	for keyword in keywords:
		first_row = first_row + "," + keyword
	first_row = first_row + "\n"
	return first_row


def print_counts(senator, keywords, counts):
	row = senator
	for keyword in keywords:
		row = row + ","+ str(counts[keyword])
	row = row + "\n"
	return row


if __name__ == '__main__':
	with open('output_counts.txt', 'a') as output_file:
		output_file.write(print_first_row(keywords))
		senators = read_list_file(handle_list_file)
		for senator in senators:
			counts = get_tweet_counts(senator)
			output_file.write(print_counts(senator, keywords, counts))
