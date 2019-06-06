from bs4 import BeautifulSoup
import csv
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests

main_url = "https://www.lyrics.com"


# Given an artist's name, this attempts to scrape all the songs of the artist
# and returns a tuple with a dictionary of songs and the given artist
def get_songs(artist):
    # Requests the html of the given artist's page
    url = main_url + "/artist/" + artist
    artist_page = requests.get(url)
    artist_html = BeautifulSoup(artist_page.content, "html.parser")
    data = artist_html.find("div", {"class": "tdata-ext"})
    song_dictionary = {}
    if data is None:
        print("No songs found for given artist get_songs retrieved 0 songs")
        return {}, artist
    else:
        # finds every album table in the page
        for album_data in data.find_all("div", {"class": "clearfix"}):
            album = album_data.find("h3").text

            # finds the songs in the album
            for song_data in album_data.find_all("strong"):
                song_url = song_data.find("a")["href"]
                song_dictionary[song_data.text] = {
                    "album": album,
                    "url": song_url
                }
        return song_dictionary, artist


# Given a tuple with a dictionary of scraped songs and the artist, this collects all the lyrics of the songs
# and adds lyrics, word count, and most common word to the given dictionary
def get_all_lyrics(tuple):
    songs = tuple[0]
    if songs_exist(songs):
        for song in songs:
            # scrapes the lyrics from the song page
            song_url = main_url + songs[song]["url"]
            song_page = requests.get(song_url)
            song_html = BeautifulSoup(song_page.content, "html.parser")
            lyrics = song_html.find("pre").text
            songs[song]["lyrics"] = lyrics

            # creates a list of words without punctuation
            tokens = lyrics.split()
            songs[song]["word count"] = len(tokens)

            # filters the list of words removing all the stop words
            stop_words = stopwords.words("english")
            tokens = [token.lower() for token in tokens]
            filtered_tokens = [w for w in tokens if not w in stop_words]

            # frequency distribution to count non stop words and get the most common
            fdist = nltk.FreqDist(filtered_tokens)
            most_common_word = fdist.most_common(1)[0][0]
            songs[song]["most common word"] = most_common_word
    else:
        print("No songs found get_all_lyrics found 0 lyrics")


# Given a tuple of a dictionary of songs and an artist, this saves all the data to a csv file
# using the artist's name
def save_lyrics(tuple):
    songs = tuple[0]
    if songs_exist(songs):
        artist = tuple[1]
        with open(artist + ".csv", mode="w") as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for song in songs:
                album = songs[song]["album"]
                song_title = song
                url = main_url + songs[song]["url"]
                lyrics = songs[song]["lyrics"]
                word_count = songs[song]["word count"]
                most_common_word = songs[song]["most common word"]

                # writes a song to a row
                writer.writerow([artist, album, song_title, url, lyrics, word_count, most_common_word])
    else:
        print("No songs found save_lyrics did not save a csv file")


# Given a dictionary of songs this checks if the dictionary is empty
def songs_exist(songs):
    return len(songs) > 0
