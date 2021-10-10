import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import datetime

ROOT_URL = 'https://pokemondb.net/'

HEADERS = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52",
    "accept-language": "en-US",
    "referer": "https://pokemondb.net/"
}

all_pokemons = []

def extract_content(URL: str):
    """
    This function takes the Pokedex URL and returns the content that has the required data for scraping
    Args:
        URL (str): The URL string
    Returns:
        The whole HTML table content for scraping
    """
    
    response = ses.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    full_table = soup.find('table', attrs = {'id':'pokedex'})
    return full_table.find('tbody').find_all('tr')

def scrape_content(content: str) -> None:
    """
    This function loops through each row of the content extracted from 'extract_content()' function, scrapes the required data and appends it to the 'all_pokemons' list
    Args:
        content (str): This is the HTML Table content extracted from 'extract_content()' function
    Returns:
        This function doesn't return anything but adds the data to the global list variable
    """
    
    for pokemon in content:
        icon = pokemon.find('td', class_ = 'cell-num cell-fixed').find('span', class_='infocard-cell-img').find('span')['data-src']
        rank = pokemon.find('td', class_ = 'cell-num cell-fixed').find('span', class_ = 'infocard-cell-data').text
        name = pokemon.find('td', class_= 'cell-name').find('a', class_ = 'ent-name').text
        
        try:
            meganame = pokemon.find('td', class_= 'cell-name').find('small', class_='text-muted').text
            name = name + "-" + meganame
        except:
            name = name
        
        pokemon_partial_url = pokemon.find('td', class_= 'cell-name').find('a', class_ = 'ent-name')['href']
        pokemon_details_link = urljoin(ROOT_URL, pokemon_partial_url)
        
        types = pokemon.find('td', class_='cell-icon').text.strip().replace(' ', ',')
        
        total_power = pokemon.find('td', class_='cell-total').text
        
        hp = pokemon.find_all('td', class_='cell-num')[1].text
        attack = pokemon.find_all('td', class_='cell-num')[2].text
        defense = pokemon.find_all('td', class_='cell-num')[3].text
        sp_attack = pokemon.find_all('td', class_='cell-num')[4].text
        sp_defense = pokemon.find_all('td', class_='cell-num')[5].text
        speed = pokemon.find_all('td', class_='cell-num')[6].text
        
        pokemon_dict = {
            'rank':rank,
            'pokemon_name': name,
            'type': types,
            'total_power': total_power,
            'hit_points': hp,
            'attack': attack,
            'defense': defense,
            'special_attack': sp_attack,
            'special_defense': sp_defense,
            'speed': speed,
            'icon': icon,
            'details_link': pokemon_details_link
        }
        
        all_pokemons.append(pokemon_dict)
    return

def load_data():
    """
    This function loads the scraped data into a CSV file
    """
    
    poke_df = pd.DataFrame(all_pokemons)
    poke_df.to_csv('pokemons_data.csv', index=False)

if __name__ == '__main__':
    
    URL = "https://pokemondb.net/pokedex/all"
    ses = requests.Session()
    
    start_time = datetime.datetime.now()
    
    print('\n\n')
    print('Catching Pokemons...')
    
    content = extract_content(URL)
    scrape_content(content)
    
    print(f'Total Pokemon Caught: {len(all_pokemons)}')
    
    end_time = datetime.datetime.now()
    scraping_time = end_time - start_time
    
    print('\n')
    print('Caught\'em all...')
    print(f'Time spent on scraping:{scraping_time}')
    print('\n')
    print('Loading data into CSV...')
    
    load_data()
    
    print('Data Exported to CSV...')
    print('Webscraping completed !!!')