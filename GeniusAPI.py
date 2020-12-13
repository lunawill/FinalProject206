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
genius_key = "JjLFTFPs7gI8UBuXpLM74Q3RiAugdlIj37CsQBr8D9EeEw6fDzkLXihz2_SxoWTw"

        
def get_playlist_info():
    
    token = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret).get_access_token()
    sp = spotipy.Spotify(token)
    playlist = sp.user_playlist_tracks(spotify_user_id, spotify_playlist_id)
    return playlist
    
def get_track_names():    
    playlist = get_playlist_info()
    track_names = []
    
    for song in range(len(playlist['items'])):
        track_names.append(playlist['items'][song]['track']['name'])
    return track_names
    
def get_track_artists():
    
    playlist = get_playlist_info()
    track_artists = []
    
    for song in range(len(playlist['items'])):
        track_artists.append(playlist['items'][song]['track']['artists'][0]['name'])
    return track_artists

    
def scrape_lyrics(url):
    song_url = url
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics1 = html.find("div", class_="lyrics")
    lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")
    if lyrics1:
        lyrics = lyrics1.get_text()
    elif lyrics2:
        lyrics = lyrics2.get_text()
    elif lyrics1 == lyrics2 == None:
        lyrics = None
    return lyrics

def get_lyrics():
    
    # playlist = get_playlist_info()
    track_names = get_track_names()
    track_artists = get_track_artists()
    song_lyrics = []

    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_key}
    search_url = base_url + '/search'
    count = 0
    for i in range(len(track_names)):
        print("\n")
        print(f"Working on track {i+1}.")
        
        data = {'q': track_names[i] + ' ' + track_artists[i]}
        response = requests.get(search_url, data=data, headers=headers)
        json = response.json()
        
        remote_song_info = None
        for hit in json['response']['hits']:
            if track_artists[i].lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break
        
        if remote_song_info == None:
            lyrics = None
            print(f"Track {i+1} is not in the Genius database.")
            song_lyrics.append('N/A')
        else:
            url = remote_song_info['result']['url']
            lyrics = scrape_lyrics(url)
            if lyrics == None:
                print(f"Track {i+1} is not in the Genius database.")
            else:
                print(f"Retrieved track {i+1} lyrics!")
            song_lyrics.append(lyrics)
        count+=1
        if count % 25 == 0 and count < len(track_artists):
            print("Pausing for a bit...")
            time.sleep(5)
        elif count % 25 != 0 and count < len(track_artists):
            print('*********')
        else:
            print('All songs retrieved!')
    return song_lyrics


def word_count(song_lyrics):
    word_counts_list = []
    for song in song_lyrics:
        song = song.split()
        count = len(song)
        word_counts_list.append(count)
    return word_counts_list


def setupSongTable(track_names, track_artists, song_lyrics, word_counts_list):
        
    conn = sqlite3.connect('/Users/williamluna/Desktop/FinalProject206/MusicStats.db')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS SpotifyAPI')
    cur.execute('CREATE TABLE IF NOT EXISTS GeniusAPI (artist_id INTEGER PRIMARY KEY, song TEXT, artist TEXT, lyrics TEXT, word_count INTEGER)')

    for i in range(len(track_artists)):
        cur.execute('INSERT INTO GeniusAPI (artist_id, song, artist, lyrics, word_count) VALUES (?,?,?,?,?)', (i+1, track_names[i], track_artists[i], song_lyrics[i], word_counts_list[i]))
        conn.commit()

    cur.close()



def main():
    track_names=get_track_names()
    track_artists=get_track_artists()
    song_lyrics = get_lyrics()
    word_counts_list = word_count(song_lyrics)
    setupSongTable(track_names, track_artists, song_lyrics, word_counts_list)
    

# Standard call for main() function
if __name__ == '__main__':
    main()
