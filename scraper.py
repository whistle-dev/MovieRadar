import requests
from bs4 import BeautifulSoup
import os
import json


def scrape():
    if os.path.exists("movies.json"):
        with open("movies.json", "r") as f:
            previous_movies = json.load(f)
    else:
        previous_movies = []

    response = requests.get("https://hdtoday.cc/home")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    trending_movies_container = soup.find("div", class_="film_list-wrap")
    movies = trending_movies_container.find_all("div", class_="flw-item")

    new_movies = []
    movie_list = []

    previous_movie_titles = {movie["title"]: movie["rank"] for movie in previous_movies}

    for i, movie in enumerate(movies):
        title = movie.find("h3").text.strip()
        info = movie.find("div", class_="fd-infor").text
        info_parts = info.split("\n")
        year = info_parts[1]
        length = info_parts[3]
        quality = movie.find("div", class_="pick film-poster-quality").text
        picture_url = movie.find("img", class_="film-poster-img")["data-src"]
        movie_url = movie.find("a", class_="film-poster-ahref")["href"]

        rank = i + 1  # Rank based on position in the current scraping

        movie_data = {
            "title": title,
            "year": year,
            "length": length,
            "quality": quality,
            "picture_url": picture_url,
            "movie_url": "https://hdtoday.cc/" + movie_url,
            "rank": rank,
        }

        if title not in previous_movie_titles:
            new_movies.append(movie_data)

        movie_list.append(movie_data)

    with open("movies.json", "w") as f:
        json.dump(movie_list, f)

    return new_movies
