import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime, time, requests
from time import sleep

#pip install basemap
from mpl_toolkits.basemap import Basema

import matplotlib.pyplot as plt
from IPython.display import Image
Image(filename='Covid-19.png', width='80%')


#Kaggle Dataset:https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset

covid_19_data = pd.read_csv('novel-corona-virus-2019-dataset/covid_19_data.csv')
covid_19_data['ObservationDate'] = pd.to_datetime(covid_19_data['ObservationDate'])
covid_19_data = covid_19_data.sort_values('ObservationDate', ascending=True)
print('Shape:', covid_19_data.shape)
print('Date min:', np.min(covid_19_data['ObservationDate']), 'Date max:', np.max(covid_19_data['ObservationDate']))
# replace NaN Provinces with string
covid_19_data['Province/State'] = covid_19_data['Province/State'].fillna('No_Province')
covid_19_data.tail()


# how many NaNs?
count_nan = len(covid_19_data) - covid_19_data.count()
count_nan

# how many countries do we have?
countries =list(set(covid_19_data['Country/Region']))
print('Unique Country/Regio found:', str(len(countries)))
countries


# how many province/states do we have?
zones =list((set(covid_19_data['Province/State'])))
print('Unique Province/State found:', str(len(zones)))



#Use openstreetmap Rest API to get lat/lon for each country
def get_lat_lon(zone, 
                output_as = 'center'):
    # thanks openstreetmap! 
    # create url
    url = '{0}{1}{2}'.format('http://nominatim.openstreetmap.org/search?q=',
                             zone,
                             '&format=json&polygon=0')
    # send out request
    response = requests.get(url).json()[0]

    # parse response to list
    if output_as == 'boundingbox':
        lst = response[output_as]
        output = [float(i) for i in lst]
    if output_as == 'center':
        lst = [response.get(key) for key in ['lon','lat']]
        output = [float(i) for i in lst]
        
    return output

geo_centers_lon = []
geo_centers_lat = []
total_ctry = len(countries)
counter_ = 0
for ctry in countries:
    if counter_ % 10 == 0: print(total_ctry - counter_)
    time.sleep(0.2)
    centroid = [None, None]
    try:
        centroid = get_lat_lon(ctry, output_as='center')

    except:
        print('Could not find:', ctry)
        
    geo_centers_lon.append(centroid[0])
    geo_centers_lat.append(centroid[1])
        
     
    counter_ += 1
    
# Add geos back to data frame
full_lats = []
full_lons = []
for i, r in covid_19_data.iterrows():
    country = r['Country/Region']
    index_list = countries.index(country)
    full_lats.append(geo_centers_lat[index_list])
    full_lons.append(geo_centers_lon[index_list])
     
# add to data frame
covid_19_data['Longitude'] = full_lons
covid_19_data['Latitude'] = full_lats
covid_19_data.head(10)
    
#Plot Infection Counts by Country using Basemap
def plot_world_map(virus_data, date, save_to_file_name = ''):
    # Set the dimension of the figure
    #plt.figure(figsize=(16, 8))
    # Set the dimension of the figure
    my_dpi=96
    plt.figure(figsize=(2600/my_dpi, 1800/my_dpi), dpi=my_dpi)

    # Make the background map
    m=Basemap(llcrnrlon=-180, llcrnrlat=-65,urcrnrlon=180,urcrnrlat=80)
    m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.3)
    m.drawcoastlines(linewidth=0.1, color="white")
    
    total_cases = np.sum(virus_data['Confirmed'])

    # Add a point per position
    m.scatter(virus_data['Longitude'], 
              virus_data['Latitude'], 
              s = virus_data['Confirmed'] * 8, # play around with the size or use np.log if you dont like the big circles
              alpha=0.4, 
              c=virus_data['labels_enc'], 
              cmap="Set1")

    plt.title(str(date) + ' Confirmed Covid-19 Cases: ' + str(int(total_cases)) + '\n(circles not to scale)', fontsize=50)
    
    if save_to_file_name != '':
        plt.savefig(save_to_file_name)
        
    plt.show()
    
# Create color map
# prepare a color for each point depending on the continent.
covid_19_data['labels_enc'] = pd.factorize(covid_19_data['Country/Region'])[0]
covid_19_data['labels_enc']  


date = '2020-07-01' 

virus_up_to_today = covid_19_data[covid_19_data['ObservationDate'] <= date]

# simplify data set
virus_up_to_today = virus_up_to_today[['Country/Region','Province/State', 'labels_enc', 'Confirmed',
                     'Deaths', 'Recovered',
                     'Longitude', 'Latitude']]


# get totals by province then by country as these are cumulative values by province first then by country and not all countries have provinces

# group by country and sum/mean values
virus_up_to_today=virus_up_to_today.groupby(['Country/Region', 'Province/State', 'labels_enc']).agg({'Confirmed':'last', 
                           'Deaths':'last',
                           'Recovered':'last',
                           'Longitude':'mean',
                          'Latitude':'mean'}).reset_index()



# group by country and sum/mean values
virus_up_to_today=virus_up_to_today.groupby(['Country/Region', 'labels_enc']).agg({'Confirmed':'sum', 
                           'Deaths':'sum',
                           'Recovered':'sum',
                           'Longitude':'mean',
                          'Latitude':'mean'}).reset_index()

# map out confirmed cases
plot_world_map(virus_up_to_today, str(date)[0:10])
    

image_file_name_counter = 0
for date in dates:
    virus_up_to_today = covid_19_data[covid_19_data['ObservationDate'] <= date]
    
    # simplify data set
    virus_up_to_today = virus_up_to_today[['Country/Region','Province/State', 'labels_enc', 'Confirmed',
                         'Deaths', 'Recovered',
                         'Longitude', 'Latitude']]


    # get totals by province then by country as these are cumulative values by province first then by country and not all countries have provinces

    # group by country and sum/mean values
    virus_up_to_today=virus_up_to_today.groupby(['Country/Region', 'Province/State', 'labels_enc']).agg({'Confirmed':'last', 
                               'Deaths':'last',
                               'Recovered':'last',
                               'Longitude':'mean',
                              'Latitude':'mean'}).reset_index()



    # group by country and sum/mean values
    virus_up_to_today=virus_up_to_today.groupby(['Country/Region', 'labels_enc']).agg({'Confirmed':'sum', 
                               'Deaths':'sum',
                               'Recovered':'sum',
                               'Longitude':'mean',
                              'Latitude':'mean'}).reset_index()
     
    # map out confirmed cases
    file_to_save_name = 'movie/anim_' + str(image_file_name_counter) + '.png'
    plot_world_map(virus_up_to_today, str(date)[0:10], file_to_save_name)
    
  
    image_file_name_counter += 1
    
    
    
    
    
