from bs4 import BeautifulSoup
import requests
from datetime import datetime


headers = {
    "USER-AGENT": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "ACCEPT-LANGUAGE": "en-US,en;q=0.5",
    "ACCEPT-ENCODING": "gzip, deflate, br"
}

url = "https://www.goodreads.com/book/show/41085104-classroom-of-the-elite-light-novel-vol-1"

response = requests.get(url, headers=headers)
soup =  BeautifulSoup(response.text, "lxml")
title = soup.find("h1").get_text().strip()

author_illustrator = soup.find_all("span", class_="ContributorLink__name")
author = author_illustrator[0].get_text()
illustrator = author_illustrator[1].get_text()

description = soup.find("div", class_="BookPageMetadataSection__description").get_text()

genre_tag_list = soup.find_all("span", class_="BookPageMetadataSection__genreButton")
genre_list = [genre_tag.get_text() for genre_tag in genre_tag_list]

featured_details_div = soup.find("div", class_="FeaturedDetails")
pages = int(featured_details_div.find_all("p")[0].get_text().split(" ")[0])

# format date in yyyy-mm-dd
published_date = " ".join(featured_details_div.find_all("p")[1].get_text().split(" ")[2:])
published_date = datetime.strptime(published_date, "%b %d, %Y")
published_date = datetime.strftime(published_date, "%Y-%m-%d")

# work_details_div = soup.select("div div span span")
series = soup.find("h3",
                    class_="Text Text__title3 Text__italic Text__regular Text__subdued"
                    )
series = series.get_text().split("#")[0].strip()

# recommended series on the same page
more_like_this = soup.find_all("div", class_="DynamicCarousel__item")
print(more_like_this)

print(f"{title = }")
print(f"{author = }")
print(f"{illustrator = }")
print(f"{description = }")
print(f"{genre_list = }")
print(f"{pages = }")
print(f"{published_date = }")
print(f"{series = }")