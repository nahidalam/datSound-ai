# -*- coding: utf-8 -*-

import spotipy
import sys
import os
import json
import pprint
import songkick
import requests
import math
import time
from collections import OrderedDict

import spotipy.oauth2 as oauth2
import spotipy.util as util

CLIENT_ID = '7cc49bc4930c43f28ce2bc3740afb797'
CLIENT_SECRET = '9c1de0f1c11d41078d0778a9242769d9'
REDIRECT_URI='http://localhost/'

SONGKICK_API = 'hESMwz4CAtk50Bzd'
sk = songkick.Songkick(api_key='hESMwz4CAtk50Bzd')

'''
    Musica (query) -> Features / Analysis / Genre
    Artista (query) -> Top Tracks / Top Albuns / Related Artists
    User -> Top Tracks / Top Artists / Events near? / Followers?

    Authorization Code Flow -> private / longer
    Clients Credentials -> Appropriate for requests that do not require access to a user’s private data. 
'''

'''credentials = oauth2.SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)

token = credentials.get_access_token()'''

# Authorize app
scopes = 'user-top-read user-read-private user-read-recently-played'
username = 'user'
token = util.prompt_for_user_token(username, scopes, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
spotify = spotipy.Spotify(auth=token)

# Main definition - constants
menu_actions  = {}


def auth_new_user():
    global spotify
    username = 'user'
    scopes = 'user-top-read user-read-private user-read-recently-played'
    new_token = util.prompt_for_user_token(username, scopes, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    spotify = spotipy.Spotify(auth=new_token)


def main_menu():
    os.system('clear')
    print "RECOMMENDATIONS - MAIN MENU\n"

    print "1. Tracks"
    print "2. Events"
    print "3. New Releases\n"
    print "9. Reset User"
    print "0. Quit\n"

    choice = raw_input(">> ")
    exec_menu(choice, '1')
    return


def recommendations_menu():
    os.system('clear')
    print "TRACKS RECOMMENDATIONS MENU\n"

    print "1. Based on User's Top Tracks"
    print "2. Based on User's Top Artists"
    print "3. Based on User's Recently Played Tracks"
    print "4. Based on User's Top Tracks and Artists"
    print "5. Based on User's Top Tracks and Recently Played Tracks\n"
    print "9. Back"
    print "0. Quit\n"

    choice = raw_input(">> ")
    exec_menu(choice, '2')
    return


def events_menu():
    os.system('clear')
    print "EVENTS RECOMMENDATIONS MENU\n"

    print "1. Based on Top Artists"
    print "2. Based on Top Tracks' Artists"
    print "3. Based on Recently Played Tracks' Artists\n"
    print "9. Back"
    print "0. Quit\n"

    choice = raw_input(">> ")
    exec_menu(choice, '3')
    return


def releases_menu():
    os.system('clear')
    print "NEW RELEASES RECOMMENDATIONS MENU\n"

    print "1. Based on Top Tracks\n"
    print "9. Back"
    print "0. Quit\n"

    choice = raw_input(">> ")
    exec_menu(choice, '4')
    return


def print_loading():
    print "... Loading ..."


def get_artists_ids(artists_names):
    artists_ids = []

    for i in range(0, len(artists_names)):
        url = 'http://api.songkick.com/api/3.0/search/artists.json?apikey={a}&query={an}'.format(a=SONGKICK_API, an=artists_names[i].encode('utf-8').strip())
        response = requests.get(url).json()

        try:
            artists_ids.append(str(response['resultsPage']['results']['artist'][0]['id']))
        except:
            pass
        
    return artists_ids


def get_user_country():
    me = spotify.me()
    return str(me['country'])


def print_events_in_country(artists_ids, user_country, op):
    events_list = []
    for i in range(0, len(artists_ids)):
        url = 'http://api.songkick.com/api/3.0/artists/{a_id}/calendar.json?apikey={a}'.format(a=SONGKICK_API, a_id=artists_ids[i])
        events = requests.get(url).json()

        try:
            location = events['resultsPage']['results']['event'][0]["location"]['city']
            country = location.split(" ")[-1]

            if country == "Portugal" and user_country == "PT":
                # print type(events['resultsPage']['results']['event'][0]["displayName"])
                # print events['resultsPage']['results']['event'][0]["displayName"]
                events_list.append(str(events['resultsPage']['results']['event'][0]["displayName"]))
        except:
            pass

    os.system('clear')

    if op == 1:
        print "*** Events Recommendations based on your Top Artists ***"
    elif op == 2:
        print "*** Events Recommendations based on your Top Tracks' Artists ***"
    elif op == 3:
        print "*** Events Recommendations based on your Recently Played Tracks' Artists ***"

    if not events_list:
        print "No events near you."
    else:
        for e in events_list:
            print e


def get_artists_events(artists_names, op):
    artists_ids = get_artists_ids(artists_names)
    user_country = get_user_country()
    
    return print_events_in_country(artists_ids, user_country, op)


def add_new_top_tracks_artists(top_tracks_artists, newer_tracks):
    for i in range(0, len(newer_tracks['items'])):
        if newer_tracks['items'][i]['artists'][0]['name'] not in top_tracks_artists:
            top_tracks_artists.append(newer_tracks['items'][i]['artists'][0]['name'])


def get_tracks_artists(long_term_tracks, medium_term_tracks, short_term_tracks):
    top_tracks_artists = []

    for i in range (0, len(long_term_tracks['items'])):
        top_tracks_artists.append(long_term_tracks['items'][i]['artists'][0]['name'])

    add_new_top_tracks_artists(top_tracks_artists, medium_term_tracks)
    add_new_top_tracks_artists(top_tracks_artists, short_term_tracks)
    
    return top_tracks_artists


def add_new_top_artists(top_artists, newer_artists):
    for i in range (0, len(newer_artists['items'])):
        if newer_artists['items'][i]['name'] not in top_artists:
            top_artists.append(newer_artists['items'][i]['name'])


def get_all_artists(long_term_artists, medium_term_artists, short_term_artists):
    top_artists = []

    for i in range (0, len(long_term_artists['items'])):
        top_artists.append(long_term_artists['items'][i]['name'])

    add_new_top_artists(top_artists, medium_term_artists)
    add_new_top_artists(top_artists, short_term_artists)

    return top_artists


def events_top_artists():
    os.system('clear')
    print_loading()

    top_artists_limit = 50
    results_long = spotify.current_user_top_artists(limit=top_artists_limit, time_range='long_term')
    results_medium = spotify.current_user_top_artists(limit=top_artists_limit, time_range='medium_term')
    results_short = spotify.current_user_top_artists(limit=top_artists_limit, time_range='short_term')

    top_artists = get_all_artists(results_long, results_medium, results_short)

    get_artists_events(top_artists, 1)

    press_to_go_back(3)


# Events based on the artists of the top tracks
def events_top_tracks():
    os.system('clear')
    print_loading()

    top_tracks_limit = 50
    results_long = spotify.current_user_top_tracks(limit=top_tracks_limit, time_range='long_term')
    results_medium = spotify.current_user_top_tracks(limit=top_tracks_limit, time_range='medium_term')
    results_short = spotify.current_user_top_tracks(limit=top_tracks_limit, time_range='short_term')

    top_tracks_artists = get_tracks_artists(results_long, results_medium, results_short)

    get_artists_events(top_tracks_artists, 2)

    press_to_go_back(3)


def get_recent_tracks_artists(recent_tracks):
    recent_artists = []
    for i in range (0, len(recent_tracks['items'])):
        if(recent_tracks['items'][i]['track']['artists'][0]['name'] not in recent_artists):
            recent_artists.append(recent_tracks['items'][i]['track']['artists'][0]['name'])
    return recent_artists


def events_recent_tracks():
    os.system('clear')
    print_loading()

    recent_tracks_limit = 50
    results = spotify.current_user_recently_played(limit=recent_tracks_limit)

    recent_tracks_artists = get_recent_tracks_artists(results)

    get_artists_events(recent_tracks_artists, 3)

    press_to_go_back(3)


# doesn't return popularity
def track_features():
    os.system('clear')
    track = raw_input(" >> Track name: ")
    results = spotify.search(q=track, limit=1)
    track_id = results['tracks']['items'][0]['id']
    pprint.pprint(spotify.audio_features([track_id]))
    press_to_go_back(1)


# tuneable track attributes: all got in audio_features
def calc_avg_features(tracks):
    avgs = [['energy', 0.0], ['liveness', 0.0], ['tempo', 0.0],
        ['speechiness', 0.0], ['acousticness', 0.0], ['instrumentalness', 0.0],
        ['time_signature', 0], ['danceability', 0.0], ['key', 0],
        ['duration_ms', 0], ['loudness', 0.0], ['valence', 0.0],
        ['mode', 0]]
        #ints are duration, mode, key, time sig
    tracklist = []
    for t_id in tracks:
        results = spotify.audio_features([t_id])
        tracklist.append(results)
        for at in avgs:
            if type(at[1]) == float:
                at[1] += float(results[0][at[0]])
            else:
                at[1] += int(results[0][at[0]])
    for at in avgs:
        at[1] = at[1] / 5
    return avgs


def calc_std_deviation(avgs,tracks):
    tracklist = []
    for t_id in tracks:
        results = spotify.audio_features([t_id])
        tracklist.append(results)
    #CALCULATE DEVIATION: value - avg
    deviations = []
    for i in range(len(tracklist)):
        for at in avgs:
            if(type(at[1])) == float:
                res = float(tracklist[i][0][at[0]] - at[1])
            else:
                res = int(tracklist[i][0][at[0]]-at[1])
            deviations.append(res)
    #DEVIATIONS CALCULATED, NEED TO SQUARE and divide by number of samples
    for i in range(len(deviations)):
        deviations[i]*=deviations[i]

    final_devs = []

    for i in range(13):
        final_devs.append((deviations[i] + deviations[i+13] + deviations[i+13*2] + deviations[i+13*3] + deviations[i+13*4])/5)

    std_deviations = []
    for i in range(len(final_devs)):
        if (i == 6 or i == 8 or i == 9 or i == 12):
            std_deviations.append(int(math.sqrt(final_devs[i])))
        else:
            std_deviations.append(math.sqrt(final_devs[i]))

    return std_deviations


def generate_array(results, limit):
    arr = []
    for i in range (0, limit):
        arr.append(str(results['items'][i]['id']))
    return arr


def generate_array_recent(results, limit):
    arr = []
    for i in range (0, limit):
        arr.append(str(results['items'][i]['track']['id']))
    return arr


# returns user top tracks' ids
def user_top_tracks():
    limit = 5  # maximum = 50

    results = spotify.current_user_top_tracks(time_range='long_term')
    # pprint.pprint(results)

    return generate_array(results, limit)


# return user top artists' ids
def user_top_artists():
    limit = 5
    results = spotify.current_user_top_artists(time_range='long_term')
    # pprint.pprint(results)
    
    return generate_array(results, limit)


def user_recent_tracks():
    limit = 5
    results = spotify.current_user_recently_played()
    # pprint.pprint(results)
    
    return generate_array_recent(results, limit)


def recommend_top_tracks():
    os.system('clear')
    print_loading()

    top_tracks = user_top_tracks()

    tracks = spotify.tracks(top_tracks)
    limit = 33

    track_attributes = calc_avg_features(top_tracks)
    std_deviations = calc_std_deviation(track_attributes,top_tracks)

    targets = [at[1] for at in track_attributes]
    targets_max = [at[1] for at in track_attributes]
    targets_min = [at[1] for at in track_attributes]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]


    target_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = top_tracks, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])

    target_vector=[]
    min_vector=[]
    max_vector=[]


    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)

    top_15_id = []
    top_15_similarity = []

    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1
            song_id = song.get('id')
            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)

    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)

    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
        

    top_15_tracks = spotify.tracks(top_15_id)

    os.system('clear')

    print "*** Tracks Recommendations based on your Top Tracks ***"

    for i in range(0, len(top_15_id)):
        print str(i+1) + ". " + top_15_tracks['tracks'][i]['artists'][0]['name'] + " - " + top_15_tracks['tracks'][i]['name']

    press_to_go_back(2)


def recommend_recent_tracks():
    os.system('clear')
    print_loading()

    recent_tracks = user_recent_tracks()
    limit = 15

    track_attributes = calc_avg_features(recent_tracks)
    std_deviations = calc_std_deviation(track_attributes,recent_tracks)

    targets = [at[1] for at in track_attributes]
    targets_max = [at[1] for at in track_attributes]
    targets_min = [at[1] for at in track_attributes]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]

    target_results = spotify.recommendations(seed_tracks=recent_tracks, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=recent_tracks, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = recent_tracks, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])

    target_vector=[]
    min_vector=[]
    max_vector=[]

    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)


    top_15_id = []
    top_15_similarity = []


    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1
            song_id = song.get('id')
            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)

    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)

    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
        
    top_15_tracks = spotify.tracks(top_15_id)

    os.system('clear')

    print "*** Tracks Recommendations based on your Recently Played Tracks ***"

    for i in range(0, len(top_15_id)):
        print str(i+1) + ". " + top_15_tracks['tracks'][i]['artists'][0]['name'] + " - " + top_15_tracks['tracks'][i]['name']

    press_to_go_back(2)


def recommend_top_artists():
    os.system('clear')
    print_loading()

    top_artists = user_top_artists()
    limit = 15

    top_artists_tracks_1 = spotify.artist_top_tracks(top_artists[0])
    top_artists_tracks_2 = spotify.artist_top_tracks(top_artists[1])
    top_artists_tracks_3 = spotify.artist_top_tracks(top_artists[2])
    top_artists_tracks_4 = spotify.artist_top_tracks(top_artists[3])
    top_artists_tracks_5 = spotify.artist_top_tracks(top_artists[4])

    results_artists = spotify.recommendations(seed_artists=top_artists, limit=limit)

    track_ids = []
    for i in range(0, len(top_artists_tracks_1['tracks'])):
        track_ids.append(top_artists_tracks_1['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_2['tracks'])):
        track_ids.append(top_artists_tracks_2['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_3['tracks'])):
        track_ids.append(top_artists_tracks_3['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_4['tracks'])):
        track_ids.append(top_artists_tracks_4['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_5['tracks'])):
        track_ids.append(top_artists_tracks_5['tracks'][i]['id'])

    user_avgs = calc_avg_features(track_ids)
    std_deviations = calc_std_deviation(user_avgs, track_ids)

 
    targets = [at[1] for at in user_avgs]
    targets_max = [at[1] for at in user_avgs]
    targets_min = [at[1] for at in user_avgs]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]

    seed = [track_ids[0],track_ids[len(top_artists_tracks_1['tracks'])],track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])],
        track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])+len(top_artists_tracks_3['tracks'])],
        track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])+len(top_artists_tracks_3['tracks'])+len(top_artists_tracks_4['tracks'])]]

    target_results = spotify.recommendations(seed_tracks=seed, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=seed, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = seed, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])


    target_vector=[]
    min_vector=[]
    max_vector=[]
    artists_vector=[]


    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    for i in range(0, len(results_artists['tracks'])):
        artists_vector.append(results_artists['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)
    artist_features = spotify.audio_features(max_vector)
    

    top_15_id = []
    top_15_similarity = []

    for song in artist_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else:
                    break
            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)

    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else: 
                    break

            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)

    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1

            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)

    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else: 
                    break
            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)
                            
        
    top_15_tracks = spotify.tracks(top_15_id)

    os.system('clear')

    print "*** Tracks Recommendations based on your Top Artists ***"

    for i in range(0, len(top_15_id)):
        print str(i+1) + ". " + top_15_tracks['tracks'][i]['artists'][0]['name'] + " - " + top_15_tracks['tracks'][i]['name']

    press_to_go_back(2)


def recommend_top_tracks_top_artists():
    os.system('clear')
    print_loading()
    
    top_tracks = user_top_tracks()
    top_artists = user_top_artists()
    limit = min(len(top_tracks), len(top_artists))

    limit = 33

    track_attributes = calc_avg_features(top_tracks)
    std_deviations = calc_std_deviation(track_attributes,top_tracks)

    targets = [at[1] for at in track_attributes]
    targets_max = [at[1] for at in track_attributes]
    targets_min = [at[1] for at in track_attributes]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]

    target_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = top_tracks, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])

    target_vector=[]
    min_vector=[]
    max_vector=[]

    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)


    top_15_id = []
    top_15_similarity = []


    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1
            song_id = song.get('id')
            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
                    

    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
                    

    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
                        
        
    ################################################################# CALC NOW FOR TOP ARTISTS

    top_artists_tracks_1 = spotify.artist_top_tracks(top_artists[0])
    top_artists_tracks_2 = spotify.artist_top_tracks(top_artists[1])
    top_artists_tracks_3 = spotify.artist_top_tracks(top_artists[2])
    top_artists_tracks_4 = spotify.artist_top_tracks(top_artists[3])
    top_artists_tracks_5 = spotify.artist_top_tracks(top_artists[4])

    results_artists = spotify.recommendations(seed_artists=top_artists, limit=limit)
    

    track_ids = []
    for i in range(0, len(top_artists_tracks_1['tracks'])):
        track_ids.append(top_artists_tracks_1['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_2['tracks'])):
        track_ids.append(top_artists_tracks_2['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_3['tracks'])):
        track_ids.append(top_artists_tracks_3['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_4['tracks'])):
        track_ids.append(top_artists_tracks_4['tracks'][i]['id'])
    for i in range(0, len(top_artists_tracks_5['tracks'])):
        track_ids.append(top_artists_tracks_5['tracks'][i]['id'])

    user_avgs = calc_avg_features(track_ids)
    std_deviations = calc_std_deviation(user_avgs, track_ids)

 
    targets = [at[1] for at in user_avgs]
    targets_max = [at[1] for at in user_avgs]
    targets_min = [at[1] for at in user_avgs]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]

    seed = [track_ids[0],track_ids[len(top_artists_tracks_1['tracks'])],track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])],
        track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])+len(top_artists_tracks_3['tracks'])],
        track_ids[len(top_artists_tracks_1['tracks'])+len(top_artists_tracks_2['tracks'])+len(top_artists_tracks_3['tracks'])+len(top_artists_tracks_4['tracks'])]]

    target_results = spotify.recommendations(seed_tracks=seed, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=seed, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = seed, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])


    target_vector=[]
    min_vector=[]
    max_vector=[]
    artists_vector=[]


    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    for i in range(0, len(results_artists['tracks'])):
        artists_vector.append(results_artists['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)
    artist_features = spotify.audio_features(max_vector)

    #queremos as tracks que batam mais parecido com os targets

    for song in artist_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else:
                    break
            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)
                           

    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else: 
                    break

            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)
                           

    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1

            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)
                            

    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if (song!=None):
            for at,value in song.items():
                if at != None :
                    if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                        #somar atributos todos
                        at_sum += value * targets[j]
                        den_1 += value*value
                        den_2 += targets[j] * targets[j]
                        j+=1
                else: 
                    break
            song_id = song.get('id', None)
            if song_id != None:
                similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

                if (len(top_15_id)<15):
                    top_15_id.append(song_id)
                    top_15_similarity.append(similarity)
                else:
                    if similarity > min(top_15_similarity):
                        if(song_id not in top_15_id):
                            index = top_15_similarity.index(min(top_15_similarity))
                            top_15_similarity[index] = similarity
                            top_15_id[index] = (song_id)
    
    top_15_tracks = spotify.tracks(top_15_id)

    os.system('clear')

    print "*** Tracks Recommendations based on the Top Tracks of your Top Artists ***"

    for i in range(0, len(top_15_id)):
        print str(i+1) + ". " + top_15_tracks['tracks'][i]['artists'][0]['name'] + " - " + top_15_tracks['tracks'][i]['name']
    press_to_go_back(2)


def recommend_top_tracks_recent_tracks():
    print_loading()

    top_tracks = user_top_tracks()
   
    artists = []
    tracks = spotify.tracks(top_tracks)
    #----------------------------------
    limit = 33

    track_attributes = calc_avg_features(top_tracks)
    std_deviations = calc_std_deviation(track_attributes,top_tracks)

    targets = [at[1] for at in track_attributes]
    targets_max = [at[1] for at in track_attributes]
    targets_min = [at[1] for at in track_attributes]

    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]

    target_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=top_tracks, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = top_tracks, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])

    target_vector=[]
    min_vector=[]
    max_vector=[]
    
    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])


    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])
    

    
    target_features = spotify.audio_features(target_vector)
    
    min_features = spotify.audio_features(min_vector)
    
    max_features = spotify.audio_features(max_vector)
    
    top_15_id = []
    top_15_similarity = []

    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1
            song_id = song.get('id')
            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    
    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    recent_tracks = user_recent_tracks()
    limit = 15
    track_attributes = calc_avg_features(recent_tracks)
    std_deviations = calc_std_deviation(track_attributes,recent_tracks)

    targets = [at[1] for at in track_attributes]
    targets_max = [at[1] for at in track_attributes]
    targets_min = [at[1] for at in track_attributes]
    
    for i in range(len(targets_min)):
        targets_min[i] = targets[i] - std_deviations[i]
        targets_max[i] = targets[i] + std_deviations[i]
   
    target_results = spotify.recommendations(seed_tracks=recent_tracks, limit=limit,
    target_acousticness=targets[4], target_danceability=targets[7],
    target_energy=targets[0], target_instrumentalness=targets[5], target_key=targets[8],
    target_liveness=targets[1], target_loudness=targets[10], target_mode=targets[12],
    target_speechiness=targets[3], target_tempo=targets[2], target_time_signature=targets[6],
    target_valence=targets[11])

    min_results = spotify.recommendations(seed_tracks=recent_tracks, limit=limit, 
    min_acousticness=targets_min[4], min_danceability=targets_min[7],
    min_energy=targets_min[0], min_instrumentalness=targets_min[5], min_key=targets_min[8],
    min_liveness=targets_min[1], min_loudness=targets_min[10], min_mode=targets_min[12],
    min_speechiness=targets_min[3], min_tempo=targets_min[2], min_time_signature=targets_min[6],
    min_valence=targets_min[11])

    max_results = spotify.recommendations(seed_tracks = recent_tracks, limit=limit,
    max_acousticness=targets_max[4], max_danceability=targets_max[7],
    max_energy=targets_max[0], max_instrumentalness=targets_max[5], max_key=targets_max[8],
    max_liveness=targets_max[1], max_loudness=targets_max[10], max_mode=targets_max[12],
    max_speechiness=targets_max[3], max_tempo=targets_max[2], max_time_signature=targets_max[6],
    max_valence=targets_max[11])
   
    target_vector=[]
    min_vector=[]
    max_vector=[]

    for i in range(0, len(target_results['tracks'])):
        target_vector.append(target_results['tracks'][i]['id'])

    for i in range(0, len(min_results['tracks'])):
        min_vector.append(min_results['tracks'][i]['id'])

    for i in range(0, len(max_results['tracks'])):
        max_vector.append(max_results['tracks'][i]['id'])

    target_features = spotify.audio_features(target_vector)
    min_features = spotify.audio_features(min_vector)
    max_features = spotify.audio_features(max_vector)
    
    for song in target_features:
        j = 0
        similarity = 0
        at_sum = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1
            song_id = song.get('id')
            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    for song in min_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    for song in max_features:
        j = 0
        at_sum = 0
        similarity = 0
        den_1 = 0
        den_2 = 0
        if song != None:
            for at,value in song.items():
                if(at!='track_href' and at!='analysis_url' and at!='uri' and at!='type' and at!='id' and at!='mode'):
                    #somar atributos todos
                    at_sum += value * targets[j]
                    den_1 += value*value
                    den_2 += targets[j] * targets[j]
                    j+=1

            similarity = at_sum/(math.sqrt(den_1)*math.sqrt(den_2))

            song_id = song.get('id')

            if (len(top_15_id)<15):
                top_15_id.append(song_id)
                top_15_similarity.append(similarity)
            else:
                if similarity > min(top_15_similarity):
                    if(song_id not in top_15_id):
                        index = top_15_similarity.index(min(top_15_similarity))
                        top_15_similarity[index] = similarity
                        top_15_id[index] = (song_id)
    
    top_15_tracks = spotify.tracks(top_15_id)

    os.system('clear')

    print "*** Tracks Recommendations based on your Recently Played Tracks and your Top Tracks ***"

    for i in range(0, len(top_15_id)):
        print str(i+1) + ". " + top_15_tracks['tracks'][i]['artists'][0]['name'] + " - " + top_15_tracks['tracks'][i]['name']
    press_to_go_back(2)


def reset_user():
    os.system('clear')
    dir_name = os.path.dirname(os.path.realpath(__file__))
    file_list = os.listdir(dir_name)
    flag = 0

    for item in file_list:
        if item.startswith('.cache'):
            os.remove(os.path.join(dir_name, item))
            flag = 1
    
    if flag:
        print "User(s) removed with success!"
    
    time.sleep(2)
    auth_new_user()

    press_to_go_back(1)
    

def recommend_new_releases_top_tracks():
    print_loading()

    country = get_user_country()
    #new album releases:
    artists=[]
    new_releases = spotify.new_releases(country, limit=50)
    top_tracks = user_top_tracks()
    top_tracks2 = spotify.tracks(top_tracks)
   
    top_artists = user_top_artists()
    top_artists2 = spotify.artists(top_artists)

    for i in range(len(top_artists)):
        if(top_artists2['artists'][i]['name'] not in artists):
            artists.append(top_artists2['artists'][i]['name'])
        if(top_tracks2['tracks'][i]['artists'][0]['name'] not in artists):
            artists.append(top_tracks2['tracks'][i]['artists'][0]['name'])

    top_track_recommends = spotify.recommendations(seed_tracks=top_tracks, limit = 50)
    top_artists_recommends = spotify.recommendations(seed_artists=top_artists, limit = 50)

    for i in range(len(top_track_recommends['tracks'])):
        if(top_track_recommends['tracks'][i]['artists'][0]['name'] not in artists):
            artists.append(top_track_recommends['tracks'][i]['artists'][0]['name'])
        if(top_artists_recommends['tracks'][i]['artists'][0]['name'] not in artists):
            artists.append(top_artists_recommends['tracks'][i]['artists'][0]['name'])

    new_albums_artists = []
    new_albums_indexes = []

    for i in range(len(new_releases['albums'])):
        if new_releases['albums']['items'][i]['artists'][0]['name'] in artists:
            new_albums_artists.append(new_releases['albums']['items'][i]['artists'][0]['name'])
            new_albums_indexes.append(i)

    # print(artists)

    os.system('clear')
    print "*** New Releases Recommendations based on your Top Tracks ***"

    if not new_albums_artists:
            print "No new releases to recommend! :("
    else:
        for i in range(len(new_albums_artists)):
            print str(i+1) + ". " + new_releases['albums']['items'][new_albums_indexes[i]]['name'] + " - " + new_releases['albums']['items'][new_albums_indexes[i]]['artists'][0]['name']

    press_to_go_back(4)
    

def recommend_new_releases_top_artists():
    pass


def exec_menu(choice, menu_id):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions[menu_id]['menu']()
    else:
        if ch not in menu_actions[menu_id]:
            print 'Invalid selection, please try again.\n'
            menu_actions[menu_id]['menu']()
        else:
            menu_actions[menu_id][ch]()
    return


def press_to_go_back(menu_id):
    raw_input('>> Press to go back to menu')
    os.system('clear')
    menu_actions[str(menu_id)]['menu']()


# Back to main menu
def back():
    menu_actions['1']['menu']()

 
# Exit program
def exit():
    sys.exit()


# Menu definition
menu_actions = {
    '1' : {
        'menu': main_menu,
        '1': recommendations_menu,
        '2': events_menu,
        '3': releases_menu,
        '9': reset_user,
        '0': exit,
    },
    '2' : {
        'menu': recommendations_menu,
        '1': recommend_top_tracks,
        '2': recommend_top_artists,
        '3': recommend_recent_tracks,
        '4': recommend_top_tracks_top_artists,
        '5': recommend_top_tracks_recent_tracks,
        '9': back,
        '0': exit,
    },
    '3' : {
        'menu': events_menu,
        '1': events_top_artists,
        '2': events_top_tracks,
        '3': events_recent_tracks,
        '9': back,
        '0': exit,
    },
    '4': {
        'menu': releases_menu,
        '1': recommend_new_releases_top_tracks,
        '9': back,
        '0': exit,
    }
}


if __name__ == '__main__':
    main_menu()