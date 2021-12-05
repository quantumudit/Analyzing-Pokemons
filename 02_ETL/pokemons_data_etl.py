# -- Importing Libraries -- #

print('\n')
print('Importing libraries to perform ETL...')

import pandas as pd
import pyfiglet

print('Initiating ETL Process...')
print('\n')

# -- Starting ETL Process --#

etl_title = "POKEMON DATA ETL"
ascii_art_title = pyfiglet.figlet_format(etl_title, font='small')
print(ascii_art_title)
print('\n')

# -- Connecting to Dataset -- #

print('Connecting to raw dataset')

scraped_data = pd.read_csv("../01_WEBSCRAPING/pokemons_scraped_data.csv", index_col=False)

print(f'Shape of scraped dataset: {scraped_data.shape}')
print('\n')

# -- Adding Calculated Columns -- #

print('Adding "Attack" and "Defense" Numbers')

scraped_data['total_attack'] = scraped_data['attack'] + scraped_data['special_attack']
scraped_data['total_defense'] = scraped_data['defense'] + scraped_data['special_defense']

print(f'Shape of dataframe after the addition of 2 calculated columns: {scraped_data.shape}')
print('\n')

# -- Removing Unnecessary Columns --#

print('Removing unnecessary columns')

keep_columns = ['rank','pokemon_name','type','icon','details_link','total_attack','total_defense','hit_points','speed']
required_data = scraped_data[keep_columns]

print(f'Shape of dataframe after removal of unnecessary columns: {required_data.shape}')
print('\n')

# -- Renaming Existing Columns --#

print('Renaming existing columns')

new_column_names = ['Rank','Pokemon','Type', 'Icon', 'Details Link', 'Attack','Defense','HP','Speed']
required_data.columns = new_column_names

print(f'New column names in the dataframe: {list(required_data.columns)}')
print('\n')

# -- Transposing Metric Columns --#

print('Transposing metric columns')

id_cols = ['Rank','Pokemon', 'Type', 'Icon', 'Details Link']
transposed_data = required_data.melt(id_vars=id_cols, var_name="Metric", value_name="Values")

print(f'New column names after transpose: {list(transposed_data.columns)}')
print(f'Shape of the dataframe after transpose: {transposed_data.shape}')
print('\n')

# -- Split "Type" Column into Rows --#

print('Splitting "Type" column into rows')

all_other_columns = ['Rank', 'Pokemon', 'Icon', 'Details Link', 'Metric', 'Values']

flat_data = (transposed_data.set_index(all_other_columns).apply(lambda x: x.str.split(',').explode()).reset_index())

print(f'Shape of the dataframe after splitting the "Type" column into rows: {flat_data.shape}')
print('\n')

# -- Rearranging Columns -- #

print('Rearranging columns')
print(f'Existing column arrangement: {list(flat_data.columns)}')

rearranged_columns = ['Rank','Type', 'Pokemon', 'Icon', 'Details Link', 'Metric', 'Values']

pokedex_data = flat_data.reindex(columns=rearranged_columns)

print(f'New column arrangement: {list(pokedex_data.columns)}')
print('\n')

# -- Adding Custom Index Column -- #

print('Adding custom index column to the dataframe')

custom_index_col = pd.RangeIndex(start=1000, stop=1000+len(pokedex_data), step=1, name='PokeID')

pokedex_data.index = custom_index_col
pokedex_data.index = 'P' + pokedex_data.index.astype('string') + '-' + pokedex_data["Rank"].astype('string')

print(f'Is the index column unique: {pokedex_data.index.is_unique}')
print(f'Snippet of the transformed dataframe:')
print('\n')
print(pokedex_data.head())
print('\n')

# -- Exporting Data to CSV File --#

print('Exporting the dataframe to CSV file...')

pokedex_data.to_csv('../03_DATA/pokedex_data.csv', encoding='utf-8', index_label='PokeID')

print('Data exported to CSV...')
print('ETL Process completed !!!')