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


AVERAGE_RATING = 3.60428996442
ACTUAL_CUSTOMER_RATING = create_cache(
   "cache-actualCustomerRating.pickle")
AVERAGE_MOVIE_RATING_PER_YEAR = create_cache(
   "cache-movieAverageByYear.pickle")
YEAR_OF_RATING = create_cache("cache-yearCustomerRatedMovie.pickle")
CUSTOMER_AVERAGE_RATING_YEARLY = create_cache(
   "cache-customerAverageRatingByYear.pickle")


actual_scores_cache ={10040: {2417853: 1, 1207062: 2, 2487973: 3}}
movie_year_cache = {10040: 1990}
decade_avg_cache = {1990: 2.4}


# ----------------------
# get_user_average_rating
# ----------------------


def get_user_average_rating(user):

    rating = 0
    count = 0
    for n in range(1999,2006):
        try:
            rating += (CUSTOMER_AVERAGE_RATING_YEARLY[(user, n)])
            count += 1
        except KeyError: #the movie was not rated in that decade
            pass
    try:
        return (round((rating / count),2))
    except:
        return None

#print(get_user_average_rating(845841)) #check for function REMOVE

# ----------------------
# get_avg_movie_rating
# ----------------------

def get_avg_movie_rating(movie):
    assert type(movie) is int

    rating = 0.0
    count = 0
    for n in range(1999,2006): #iterate through the seven possible years of data
        try:
            rating += (AVERAGE_MOVIE_RATING_PER_YEAR[(movie, n)])
            count += 1
        except KeyError: #the movie was not rated in that decade
            pass

    try:
        return (round((rating / count),2)) #if count is zero then we do not have data for the movie, yield to user
    except:
        return None


#print(get_avg_movie_rating(3058)) #check for function REMOVE

# ------------
# make_prediction
# ------------

def make_prediction(movie,user,userWeight = 0.5):

    movie_pred = get_avg_movie_rating(movie) #average score for movie (how good/bad)

    user_pred = get_user_average_rating(user) #average score a user gives any movie (how nice/mean)

    complement = 1.0 - userWeight

    if user_pred is None: #The user has no rating data,but does exist. We predict the USER's average .
        return movie_pred
    if movie_pred is None: #The movie has no rating data, but does exist. We predict the MOVIE's average.
        return user_pred
    #else:                    # We have no data to predict either case. Assume the movie is average.
    #   return AVERAGE_RATING

    weighted_prediction = ((userWeight * movie_pred)
                         + (complement * user_pred))
    
    return round(weighted_prediction,2)


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
            #pred = movie_year_cache[int(current_movie)]
            #pred = (pred // 10) *10
            #prediction = decade_avg_cache[pred]
            writer.write(line)
            writer.write('\n')
        else:
		# It's a customer
            current_customer = int(line)
            prediction = make_prediction(movie_ID, int(current_customer))
            predictions.append(prediction)

            try:
                actual.append(ACTUAL_CUSTOMER_RATING[(int(current_customer), movie_ID)])
            except KeyError:
                actual.append(0)

            writer.write(str(prediction)) 
            writer.write('\n')
    # calculate rmse for predictions and actuals
    rmse = sqrt(mean(square(subtract(predictions, actual))))
    writer.write(str(rmse)[:4] + '\n')

#print(ACTUAL_CUSTOMER_RATING[(30878,1)])
#print(make_prediction(1,30878))



