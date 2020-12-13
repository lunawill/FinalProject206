import requests
import sqlite3
import math
from bs4 import BeautifulSoup

conn = sqlite3.connect('/Users/williamluna/Desktop/FinalProject206/MusicStats.db')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Hot100')
cur.execute('CREATE TABLE IF NOT EXISTS Hot100 (position INTEGER, song TEXT, artist TEXT, numWeeks INTEGER, yearRatio INTEGER)')

#connected db first then proceeded with beautifulsoup for website

source = requests.get("https://www.billboard.com/charts/hot-100")

soup = BeautifulSoup(source.content, 'html.parser')

rankList = []
songList = []
artistList = []
peakList = []
ratioList = []
weekYearVal = 52

container = soup.find_all('li', class_='chart-list__element display--flex')


for x in container:    #these are all in order from 1-100

    #1st make a list contains the position on the billboard
    spanRank = x.find('span', class_='chart-element__rank__number')
    rankList.append(spanRank.text.strip())

    #2nd make a list contains the song name      
    spanSong = x.find('span', class_='chart-element__information__song text--truncate color--primary')
    songList.append(spanSong.text.strip())

    #3rd make a list that contains the astists
    spanArtist = x.find('span', class_='chart-element__information__artist text--truncate color--secondary')
    artistList.append(spanArtist.text.strip())

    #4th make a list that contains the number of weeks on billvoard top 100
    spanPeakTime = x.find('span', class_='chart-element__meta text--center color--secondary text--week')     
    peakList.append(spanPeakTime.text.strip())

# We worked on getting a ratio of the number of weeks a song was on a billboard and put it in comparison
# with number of weeks in a year  some songs will have more tham 52 which will result in ratio > 1
for y in range(len(peakList)):
    variable = float(peakList[y])
    yRatio = (variable/weekYearVal)
    yRatio = format(yRatio, ".3f")   
    ratioList.append(yRatio)


for z in range(len(rankList)):

    cur.execute('INSERT INTO Hot100 (position, song, artist, numWeeks, yearRatio) VALUES (?,?,?,?,?)', (rankList[z], songList[z], artistList[z], peakList[z], ratioList[z]))
    conn.commit()


cur.close()
