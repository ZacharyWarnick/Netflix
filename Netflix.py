#!/usr/bin/env python3

# -------
# imports
# -------

from math import sqrt
import pickle
from requests import get
from os import path
from numpy import mean, square, subtract, sqrt

#print(sqrt(mean(square(subtract(3.7,4)))))
def create_cache(filename):
    """
    filename is the name of the cache file to load
    returns a dictionary after loading the file or pulling the file from the public_html page
    """
    cache = {}
    filePath = "/u/fares/public_html/netflix-caches/" + filename

    if path.isfile(filePath):
        with open(filePath, "rb") as f:
            cache = pickle.load(f)
    else:
        webAddress = "http://www.cs.utexas.edu/users/fares/netflix-caches/" + \
            filename
        bytes = get(webAddress).content
        cache = pickle.loads(bytes)

    return cache


AVERAGE_RATING = 3.6
ACTUAL_CUSTOMER_RATING = create_cache(
   "cache-actualCustomerRating.pickle")
AVERAGE_USER_RATING = create_cache("cache-averageCustomerRating.pickle")
AVERAGE_MOVIE_RATING = create_cache("cache-averageMovieRating.pickle")


# ----------------------
# get_user_average_rating
# ----------------------


def get_user_average_rating(user):
    try:
        return round(AVERAGE_USER_RATING[user],2)
    except KeyError:
        return AVERAGE_RATING

# ----------------------
# get_avg_movie_rating
# ----------------------

def get_avg_movie_rating(movie):

    try:
        return round(AVERAGE_MOVIE_RATING[movie],2)
    except KeyError:
        return AVERAGE_RATING
# ------------
# make_prediction
# ------------

def make_prediction(movie,user,userWeight = 0.5):

    movie_pred = get_avg_movie_rating(movie) #average score for movie (how good/bad)

    user_pred = get_user_average_rating(user) #average score a user gives any movie (how nice/mean)

    complement = 1.0 - userWeight

    weighted_prediction = round((userWeight * movie_pred)
                         + (complement * user_pred),1)
    
    return (weighted_prediction)


# ------------
# netflix_eval
# ------------

def netflix_eval(reader, writer) :
    predictions = []
    actual = []

    # iterate throught the file reader line by line
    for line in reader:
    # need to get rid of the '\n' by the end of the line
        line = line.strip()
        # check if the line ends with a ":", i.e., it's a movie title
        if line[-1] == ':':
		# It's a movie
            current_movie = line.rstrip(':')
            movie_ID = int(current_movie)
            writer.write(line)
            writer.write('\n')
        else:
		# It's a customer
            current_customer = int(line)
            prediction = (make_prediction(movie_ID,current_customer))
            predictions.append(prediction)


            actual.append(ACTUAL_CUSTOMER_RATING[(int(current_customer), movie_ID)])

            writer.write(str(prediction))
            writer.write('\n')

    # calculate rmse for predictions and actuals
    rmse = sqrt(mean(square(subtract(predictions, actual))))
    writer.write(str(rmse)[:4] + '\n')



