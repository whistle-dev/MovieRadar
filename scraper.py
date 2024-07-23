import requests
from bs4 import BeautifulSoup
import os
import json
import logging

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()],
)


def scrape():
    previous_movies = []
    if os.path.exists("movies.json"):
        with open("movies.json", "r") as f:
            previous_movies = json.load(f)

    response = requests.get("https://hdtoday.cc/home")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    trending_movies_container = soup.find("div", class_="film_list-wrap")
    if not trending_movies_container:
        logging.warning("No trending movies container found.")
        return []

    movies = trending_movies_container.find_all("div", class_="flw-item")
    if not movies:
        logging.warning("No movies found.")
        return []

    new_movies = []
    movie_list = []

    for i, movie in enumerate(movies):
        title = movie.find("h3").text.strip()
        info = movie.find("div", class_="fd-infor").text
        info_parts = info.split("\n")
        year = info_parts[1] if len(info_parts) > 1 else "Unknown"
        length = info_parts[3] if len(info_parts) > 3 else "Unknown"
        quality = movie.find("div", class_="pick film-poster-quality").text
        picture_url = movie.find("img", class_="film-poster-img")["data-src"]
        movie_url = movie.find("a", class_="film-poster-ahref")["href"]

        movie_data = {
            "title": title,
            "year": year,
            "length": length,
            "quality": quality,
            "picture_url": picture_url,
            "movie_url": "https://hdtoday.cc/" + movie_url,
            "rank": i + 1,
        }

        if movie_data not in previous_movies and "HD" in quality:
            new_movies.append(movie_data)
            logging.info(f"New movie found: {title}")

        movie_list.append(movie_data)

    if new_movies:
        logging.info(f"New movies added: {[movie['title'] for movie in new_movies]}")
    else:
        logging.info("No new movies found.")

    removed_movies = [
        movie["title"] for movie in previous_movies if movie not in movie_list
    ]
    if removed_movies:
        logging.info(f"Movies removed: {removed_movies}")

    with open("movies.json", "w") as f:
        json.dump(movie_list, f)

    return new_movies
