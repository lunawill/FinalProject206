import sys
import spotipy
import spotipy.util as util
import requests
import unittest
import sqlite3
import json
import os
import time
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
# from config.config import USERNAME, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
from bs4 import BeautifulSoup
spotify_client_id = "384531d1c01d4ea4b4fc9cbdb54740a5"
spotify_client_secret = "93c9145bd0b94192ae5edf5c2f9127b3"
spotify_user_id = "spotify:user:hairyorange"
spotify_playlist_id = "spotify:playlist:37i9dQZF1EM9XnLciEAGqD"


def get_playlist_info():
    
    token = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret).get_access_token()
    sp = spotipy.Spotify(token)
    playlist = sp.user_playlist_tracks(spotify_user_id, spotify_playlist_id)
    return playlist

def get_track_information():    
    playlist = get_playlist_info()
    track_names = []
    trackType = []
    trackPopularity = []
    trackDuration = []
    track_artists = []
    
    for i in range(len(playlist['items'])):
        track_names.append(playlist['items'][i]['track']['name'])
        trackType.append(playlist['items'][i]['track']['album']['album_type'])
        trackPopularity.append(playlist['items'][i]['track']['popularity'])
        trackDuration.append(playlist['items'][i]['track']['duration_ms'])
        track_artists.append(playlist['items'][i]['track']['artists'][0]['name'])

    print(len(track_names))
    print(len(trackType))
    print(len(trackPopularity))
    print(len(trackDuration))
    print(len(track_artists))

    return track_names, trackType, trackPopularity, trackDuration, track_artists
    
def get_track_artists():
    
    playlist = get_playlist_info()
    track_artists = []
    
    for song in range(len(playlist['items'])):
        track_artists.append(playlist['items'][song]['track']['artists'][0]['name'])
    return track_artists


def setUpArtistTable(track_artists):
    
    artistList = []

    for i in range(len(track_artists)):
        if track_artists[i] not in artistList:
            artistList.append(track_artists[i])
        
    conn = sqlite3.connect('/Users/williamluna/Desktop/FinalProject206/MusicStats.db')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS SpotifyAPI')
    cur.execute('CREATE TABLE IF NOT EXISTS SpotifyAPI (artist_id INTEGER PRIMARY KEY, artist TEXT)')

    for x in range(len(artistList)):
        cur.execute('INSERT INTO SpotifyAPI (artist_id, artist) VALUES (?,?)', (x+1, artistList[x]))
        conn.commit()

    cur.close()


def setUpInfoTable(track_names, trackType, trackPopularity, trackDuration, track_artists):

    conn = sqlite3.connect('/Users/williamluna/Desktop/FinalProject206/MusicStats.db')
    cur = conn.cursor()

    cur.execute("SELECT artist, artist_id FROM SpotifyAPI")
    dbTuple = cur.fetchall()
    dbTuple = dict(dbTuple)

    cur.execute('DROP TABLE IF EXISTS SpotifySongAPI')
    cur.execute('CREATE TABLE IF NOT EXISTS SpotifySongAPI (song TEXT, artist_id INTEGER, type TEXT, popularity INTEGER, duration INTEGER)')

    for x in range(len(track_names)):
        cur.execute('INSERT INTO SpotifySongAPI (song, artist_id, type, popularity, duration) VALUES (?,?,?,?,?)', (track_names[x], dbTuple[track_artists[x]], trackType[x], trackPopularity[x], trackDuration[x]))
        conn.commit()

    cur.close()



def main():
    track_names, trackType, trackPopularity, trackDuration, track_artists = get_track_information()
    track_artists=get_track_artists()
    setUpArtistTable(track_artists)
    setUpInfoTable(track_names, trackType, trackPopularity, trackDuration, track_artists)

if __name__ == '__main__':
    main()