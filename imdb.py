#!/usr/bin/env python

# import the needed libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

headers = {
    'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

def movies_data():
    'This return a dataframe for the top movies on www.imdb.com'
    base_url = 'https://www.imdb.com'
    url = base_url + '/chart/top'
    response = requests.get(url,headers= headers)
    soup = BeautifulSoup(response.text,'lxml')

    # set the data
    df = pd.read_html(url,header=0)[0]
    # extarct the rank
    df['rank'] =  df['Rank & Title'].apply(lambda x: x.split(' ')[0].replace('.',''))
    # extract the title
    df['title'] = df['Rank & Title'].apply(lambda x: ' '.join(x.split(' ')[2:-2]))
    # extarct the year
    df['year'] = df['Rank & Title'].apply(lambda x: x.split(' ')[-1].replace('(','').replace(')',''))
    #rename the redundant columns
    df.rename(columns={'IMDb Rating':'imdb_rate'}, inplace=True)
    # drop the unnamed and other columns
    col_to_drop = ['Unnamed: 0','Your Rating','Unnamed: 4', 'Rank & Title' ]
    df.drop(columns=col_to_drop, axis=1 , inplace=True)
    # adjust the rate type to float
    df.imdb_rate = df.imdb_rate.astype('float')
    # re arrange the columns
    cols = df.columns.tolist()
    cols  = cols[1:]+cols[:1]
    df = df[cols]
    # extract the table
    tb = soup.find('table')
    l = [tag.get('href') for tag in tb.find_all('a')]
    # clean as l is dupliacted
    href = [base_url+k for i, k in enumerate(l) if i%2 == 0]
    # collect the href links
    df['href'] = href
    return df

def movie_parser(movie_url):
    r = requests.get(movie_url,headers=headers)
    soup = BeautifulSoup( r.text, 'lxml')
    # get cast
    cast = ','.join([i.find('a').find('img').get('alt') for i in soup.findAll('td',{'class':"primary_photo"})])
    # get the movie summary
    summary = soup.find('div',{'class':"summary_text"}).text.strip()
    record = {'summary': summary, 'cast': cast}
    return record

if __name__ == '__main__':
    df = movies_data()
    print('Start scraping...')
    movies = [movie_parser(l) for l in tqdm(df.href)]
    s,c  = [i['summary'] for i in movies],[i['cast'] for i in movies]
    df['summary'] , df['cast'] = s ,c
    df.to_csv('top_movies_imdb.csv', encoding ='utf-8-sig' , index= False)
    print('data is saved!')