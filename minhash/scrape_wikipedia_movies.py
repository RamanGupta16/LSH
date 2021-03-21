import requests
import urllib
import bs4 # BeautifulSoup
import re
import datetime
import json
from dateutil.parser import parse as dateutil_parse

'''
Read Highest-grossing films of each year
'''

CURRENT_YEAR = int(datetime.date.today().year)

# Parse expressions like "/wiki/2020_in_film", "/wiki/1990_in_film", "/wiki/1890_in_film", but not "wiki/2020s_in_film"
YEAR_MOVIE_HREF = re.compile('\/wiki\/(?P<year>[1,2][0,8,9][0-9][0-9])_in_film')

# Corpus Output File
CORPUS_WIKIPEDIA = 'corpus_wikipedia.txt'
corpus_wikipedia_file = None

# Unique Id for each movie in corpus
GLOBAL_ID_PREFIX = 'WIKI' 
GLOBAL_ID = 0

def get_global_id():
	global GLOBAL_ID
	GLOBAL_ID += 1
	return f"{GLOBAL_ID_PREFIX}{GLOBAL_ID}"
	
def parse_infobox_in_movie_link(movie_link):
	print(movie_link)

	# Initialize movie data JSON format
	movie_data = {'Type':'movie', 'Id':get_global_id(), 'Description':'', 'Duration':'', 'ReleaseYear':'', 'Cast':'', 'Director':'', 'Language':''}

	# Parse movie_link
	response = requests.get(movie_link)
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	infobox = soup.find('table', {'class': 'infobox'})
	for index, table_row in enumerate(infobox.find_all('tr')):
		name = None
		row_name = table_row.find_all('th')
		if row_name:
			name = row_name[0].text

		data = None
		row_data = table_row.find_all('td')
		if row_data:
			data = row_data[0].text
	
		if name:
			if index == 0:
				movie_data['Title'] = name
			else:
				if name == 'Directed by':
					movie_data['Director'] = ', '.join([x for x in data.split('\n') if len(x) > 0]) # Select only top 2 if > 2
				elif name == 'Starring':
					movie_data['Cast'] = ', '.join([x for x in data.split('\n') if len(x) > 0]) # Select only top 2 if > 2
				elif name == 'Release date':
					# extract year trying various formats
					release_year = ''
					release_date = ''

					if not release_date:
						try:
							release_date = row_data[0].find('span', {"class":"bday dtstart published updated"})
							if release_date:
								release_date = release_date.text
								release_year = datetime.datetime.fromisoformat(release_date).year
						except Exception as e:
							release_year = ''
							release_date = ''
							print(f"Exception {e}")
					
					if not release_date:
						try:
							release_date = dateutil_parse(row_data[0].contents[0].split('(')[0])
							release_year = release_date.year
						except Exception as e:
							release_year = ''
							release_date = ''
							print(f"Exception {e}")
					movie_data['ReleaseYear'] = str(release_year)
				elif name == 'Language':
					movie_data['Language'] = data.split()[0]
				elif name == 'Running time':
					movie_data['Duration'] = data.split()[0] # Extract the numeric value

	# Missing Title is a serious error
	if not movie_data.get('Title'):
		raise ValueError('Title not found')

	#print(movie_data)
	corpus_wikipedia_file.write(json.dumps(movie_data))
	corpus_wikipedia_file.write('\n')


# Return Scheme, Network Location(netloc) of the URL as per scheme: scheme://netloc/path;parameters?query#fragment
def url_netloc(url):
	parsed_url = urllib.parse.urlparse(url)
	return parsed_url.scheme, parsed_url.netloc


# Parse year in films like 'https://en.wikipedia.org/wiki/2020_in_film'
def parse_year_movie_link(year_movie_url, year):
	print(f"Highest-grossing films of {year}")
	scheme, netloc = url_netloc(year_movie_url)
	response = requests.get(year_movie_url)
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	movie_links = []
	for item in soup.find_all(attrs={"class": "wikitable sortable"}):
		contents_list = item.contents # A Tag’s children are available in a list called "contents"
		caption = contents_list[1].contents[0]
		if isinstance(caption, bs4.element.NavigableString) and caption.strip() == f'Highest-grossing films of {year}':
			movie_table = contents_list[3].contents # Read Highest-grossing films Table
			for movie_table_item in movie_table:
				if isinstance(movie_table_item, bs4.element.Tag):
					ahref_list = movie_table_item.find_all('a')
					if ahref_list: 
						movie_href = ahref_list[0]['href']
						movie_link = urllib.parse.urlunsplit((scheme, netloc, movie_href, "", ""))
						try:
							parse_infobox_in_movie_link(movie_link)
						except Exception as e:
							print(f"Exception: {e} in parsing {movie_link}")


# Get data of all films by Year from https://en.wikipedia.org/wiki/Lists_of_films
def scrape_wikipedia_Lists_of_films():
	global corpus_wikipedia_file
	corpus_wikipedia_file = open(CORPUS_WIKIPEDIA, 'w')
	wiki_url = "https://en.wikipedia.org/wiki/Lists_of_films"
	scheme, netloc = url_netloc(wiki_url)
	response = requests.get(wiki_url)
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	year_movie_links = []
	for item in soup.find_all(attrs={"class": "hlist"}):
		# Find HTML element which has only "hlist" class
		if item["class"] != ["hlist"]:
			continue
		# Get all the hrefs
		for href in item.find_all('a'):
			year_movie_href = href['href']
			re_match = YEAR_MOVIE_HREF.match(year_movie_href)
			if re_match:
				year = re_match.group('year')
				if int(year) <= CURRENT_YEAR:
					year_movie_link = urllib.parse.urlunsplit((scheme, netloc, year_movie_href, "", ""))
					year_movie_links.append((year_movie_link, year))
					parse_year_movie_link(year_movie_link, year)
	corpus_wikipedia_file.close()
	return year_movie_links 
			
	
if __name__ == "__main__":
	scrape_wikipedia_Lists_of_films()
