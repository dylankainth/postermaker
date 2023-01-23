# connect to a mongodb and add housemasters to the each entry in the speakers field in the lectures collection

import pymongo
import json
import requests

# connect to mongodb with db 'test' and collection 'lectures'
# change the connection string to your own mongodb connection string
client = pymongo.MongoClient('mongodb+srv://dbuser:dbpass@cluster0.9ctff.mongodb.net/?retryWrites=true&w=majority')
db = client['test']

#get the lectures collection
lectures = db['lectures']

# loop through each lecture
for lecture in lectures.find():

        newspeakers = []
    
        # loop through each speaker
        for speaker in lecture['speakers']:
    
            # add a housemaster to the speaker 
            housemasters = {'B': 'DJE', 'D': 'BTM', 'E': 'AJC', 'G': 'CST', 'H': 'CTP','K': 'CO', 'L': 'NJM', 'M': 'SMS', 'N': 'EWH', 'P': 'BJDS', 'R': 'SNT', 'W': 'HAH'}

            # prompt the user to select a house
            print('Select a house for ' + speaker)
            
            # find the housemaster for the house and append it to the speaker in brakets
            speaker = speaker + ' (' + housemasters[input()] + ')'

            # add speaker to buffer array newspeakers
            newspeakers.append(speaker)
            
        # update the lecture in the database
        lectures.update_one({'_id': lecture['_id']}, {'$set': {'speakers': newspeakers}})