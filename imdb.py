import requests
from bs4 import BeautifulSoup
from pprint import pprint
from time import sleep
import json

headers = {
    'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


# This will grab the links of movie from Top movies
def grab_list():
    links = []
    try:
        base_url = 'http://www.imdb.com'
        url = base_url + '/chart/top'
        r = requests.get(url, headers=headers)
        html = None
        if r.status_code != 200:
            return None
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        titles = soup.select('.titleColumn a')
        for title in titles:
            links.append(base_url + title['href'])
    except Exception as ex:
        print(str(ex))
    finally:
        return links


url = 'http://www.imdb.com/title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=2398042102&pf_rd_r=0C6F7VTS482XW3HJNXKQ&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1'


# Parse info of an individual movie page
def parse_movie(url):
    title = '-'
    summary = '-'
    cast = []
    record = {}

    try:
        sleep(3)
        url = url.rstrip('\n')
        print('Processing..' + url)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None

        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        title_section = soup.select('.title_wrapper > h1')
        summary_section = soup.select('.plot_summary .summary_text')
        cast_list = soup.select('.cast_list')

        if summary_section:
            summary = summary_section[0].text.strip()

        if title_section:
            title = title_section[0].text.strip()
        if cast_list:
            actors = cast_list[0].findAll('span', {'itemprop': 'name'})
            for actor in actors:
                cast.append(actor.text.strip())

            record = {'title': title, 'summary': summary, 'cast': cast}
    except Exception as ex:
        print(str(ex))
    finally:
        return record


if __name__ == '__main__':
    links = grab_list()

    movies = [parse_movie(l) for l in links]
    # Write in a file
    with open('top_movies.txt', 'a+') as f:
        f.write(json.dumps(movies))

    print('Movie Data Stored successfully')
