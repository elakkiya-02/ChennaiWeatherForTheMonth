#!/usr/bin/env python
# coding: utf-8

#  # Chennai Weather for the Month - from Open Meteo

# ## Importing necessary libraries

# In[1]:


#Required Libraries
import pandas as pd
import requests
import plotly.express as px
from datetime import date, timedelta
import warnings
warnings.filterwarnings("ignore")


# ## Setting up the required parameters

# In[19]:


#Place - latitude, longitude
place='Chennai'
latitude = 13.0845
longitude = 80.2705
'''getting current date so that everytime we run the code, 
we stay with upto-date data
'''
today = date.today()
'''As this is a monthly weather report of our desired city, 
we set the start date as 1st of current month and 
the end date as the current date
'''
start_date = today.replace(day=1).isoformat()
'''date object is based on current date but day is set to 1. 
this preserves the month and year based on the current date
isformat() converts to a string rep YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.ffffff
'''

end_date = today.isoformat()
'''we are going to show the weather forecast for the next 7 days from current date
so days is set 7'''
forecast_end =(today+timedelta(days=7)).isoformat()

print(f"Fetching {place} weather data from {start_date} to {end_date}...")
print(f"And the forecast till {forecast_end}...")

'''
we have defined our location and the date range as per our requirements
'''


# ## Historical Data of the Month

# In[20]:


#Gettin the Weather History of the place
#link to archive api is available in https://open-meteo.com/en/docs/historical-weather-api

archive_url = "https://archive-api.open-meteo.com/v1/archive"
'''
The Params are defined based on their availablility in the respective API documentation
'''
archive_params = {"latitude":latitude,
                  "longitude":longitude,
                  "start_date":start_date,
                  "end_date":end_date,
                  "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_hours,wind_speed_10m_max",
                  "timezone":"auto"}
'''
Make sure the daily param is a comma seperated list without spaces.
The parameters we need are set and now historical data is to be fetched
as a request to the archive api url
'''
historical_data = requests.get(archive_url, params=archive_params).json()
print(historical_data)


# In[21]:


'''Base on the historical data from the api, we are about to create a dataframe to
work with the numbers'''
print(historical_data.get("daily",[]))
'''
daily comes with 'time' of type date
'''


# In[22]:


daily_data = historical_data.get("daily",{})#accessing "daily" key from the response
daily_data.keys()


# In[23]:


#we are dealing with weather_code param
'''
Based on weather variable documentation  / WMO Weather interpretation codes (WW)
https://open-meteo.com/en/docs
'''
weather_map = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


# In[24]:


'''Based on the daily data keys, 
we can name the dataframe columns accordingly'''
hist_df = pd.DataFrame({
    "Date" : daily_data.get("time", []),
    #"Weather" : daily_data.get("weather_code", []),#only to display code
    "Weather" : [weather_map.get(w_code, str(w_code)) for w_code in daily_data.get("weather_code", [])],
    "Max Temp" : daily_data.get("temperature_2m_max", []),
    "Min Temp" : daily_data.get("temperature_2m_min", []),
    "Rainfall" : daily_data.get("precipitation_sum", []),
    "Sum of Daily Rain" : daily_data.get("rain_sum", []),
    "Hours with Rain" : daily_data.get("precipitation_hours", []),
    "Wind Speed" :  daily_data.get("wind_speed_10m_max", []),
    "Type" : "Historical"
})
print(hist_df.shape)
print(hist_df.head())


# In[25]:


#checking whether all our weather codes were mapped accordingly
print(hist_df['Weather'].value_counts())


# ### Visualizing Historical data of the month

# In[26]:


'''
we can now visualize the Weather history of the current month
keeping the Date, Weather condition and Type as Historical/forecast 
as variables here
'''
hist_df_melt = hist_df.melt(
    id_vars = ["Date", "Weather", "Type"],
    var_name = "Metric",#Metric will be the name of our new col that stores maxtemp, mintemp etc.
    value_name = "Value")#this will have the value of the metrics
'''
creating an animated bar chart grouped along with each metric
on hovering we can see the weather on that particular date
bar for every date
'''
fig = px.bar(hist_df_melt, x="Metric", y="Value", color="Metric",
             animation_frame = "Date",
             animation_group = "Metric",
             hover_data = ["Weather"],
             range_y = [0, hist_df_melt["Value"].max()+10],
             #range_x is not needed here as our categories are fixed. but we can for the limits if needed
             title = place +" (Historical Weather of this month)"
            )
fig.update_layout(template = "plotly_dark",
                  height = 500,
                  width = 1050)
fig.show()


# In[37]:


#LINE PLOT - Additional View
hist_df_line_melt = hist_df.melt(id_vars = ["Date", "Weather"],
                                 var_name="Metric",
                                 value_name="Value")
figl = px.line(hist_df_line_melt, x="Date", y="Value", color="Metric",
              line_group = "Metric",
              hover_data = ["Weather"],
              title = place +" (Historical Weather of this month)"
             )
figl.show()


# ## Forecast Data of the Month

# In[27]:


#Gettin the Weather Forecase of the place
#link to forecast api is available in https://open-meteo.com/en/docs

forecast_url = "https://api.open-meteo.com/v1/forecast"
'''
The Params are defined based on their availablility in the respective API documentation
'''
forecast_params = {"latitude":latitude,
                   "longitude":longitude,
                   "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_hours,wind_speed_10m_max",
                   "forecast_days" : 7,
                  "timezone":"auto"}
'''
Make sure the daily param is a comma seperated list without spaces.
The parameters we need are set and now historical data is to be fetched
as a request to the archive api url
'''
forecast_data = requests.get(forecast_url, params = forecast_params).json()
forecast_data


# In[28]:


forecast_daily_data = forecast_data.get("daily", {})
forecast_daily_data.keys()


# In[29]:


'''Based on the forecasr daily data keys, 
we can name the dataframe columns accordingly'''
forecast_df = pd.DataFrame({
    "Date": forecast_daily_data.get("time", []),
    "Weather": [weather_map.get(fw_code, str(fw_code)) for fw_code in forecast_daily_data.get("weather_code", [])],
    "Max Temp" :forecast_daily_data.get("temperature_2m_max", []),
    "Min Temp" : forecast_daily_data.get("temperature_2m_min", []),
    "Rainfall" : forecast_daily_data.get("precipitation_sum", []),
    "Sum of Daily Rain": forecast_daily_data.get("rain_sum", []),
    "Hours with Rain" : forecast_daily_data.get("precipitation_hours", []),
    "Wind Speed" : forecast_daily_data.get("wind_speed_10m_max", []),
    "Type" : "Forecast"
})
print(forecast_df.shape)
print(forecast_df.head())


# In[30]:


#Together visualizing the historical and forecast data
this_month_weather = pd.concat([hist_df, forecast_df], ignore_index=True)
this_month_weather["Date"] = pd.to_datetime(this_month_weather["Date"])
print(this_month_weather.shape)


# In[32]:


#lets see this month weather date history+predicted of Chennai
print(this_month_weather[["Date", "Weather", "Type"]])


# ### Visualizing Both Historical and Forecast data of the month

# In[33]:


#Animated visualization
'''
Here we have dates under each type historical/forecast, so our vars will be these 2
'''
this_month_weather_melt = this_month_weather.melt(id_vars = ["Date","Weather","Type"],
                                                  var_name = "Metric",
                                                  value_name = "Value")
#ensuring all "Value" is numeric -
'''
We are having multiple colums for Value with different data types like temp - float, weather - string
on using pd.melt() - all comes under Value. If any non-numeric value is present then value will have mixed types.
so before plotting we need to make sure converting VALUE to NUMERIC .
this converts non-numeric to NaN that plotly skips

'''
try:
    fig1 = px.bar(this_month_weather_melt, x="Metric", y="Value", color="Metric",
                  animation_frame = "Date",
                  animation_group= "Metric",
                  facet_col = "Type",  #we are going to have side by side panel for 2 types
                  hover_data=["Weather"],
                  range_y = [0, this_month_weather_melt["Value"].max() + 10],
                  title = f"{place} Weather: {start_date} - {end_date}"
                 )
    
    fig1.update_layout(template = "plotly_dark", 
                      height = 600, 
                      width = 1050)
    fig1.show()
except Exception as e:
    print(f"Exceution failed due to : {e}")


# In[36]:


#Animated visualization trial2 
'''
Here we have dates under each type historical/forecast, so our vars will be these 2
'''
this_month_weather_melt = this_month_weather.melt(id_vars = ["Date","Weather","Type"],
                                                  var_name = "Metric",
                                                  value_name = "Value")
'''In the above viz date is complete in datetime format and it is difficult to follow the dates
so we here have converted that format by extracting only the day part from the Date column.
Now the visualization is clear that aligns with the animations.
'''
this_month_weather_melt["Day"] = pd.to_datetime(this_month_weather_melt["Date"]).dt.day.astype(str)
#ensuring all "Value" is numeric -
'''
We are having multiple colums for Value with different data types like temp - float, weather - string
on using pd.melt() - all comes under Value. If any non-numeric value is present then value will have mixed types.
so before plotting we need to make sure converting VALUE to NUMERIC .
this converts non-numeric to NaN that plotly skips

'''
try:
    fig1 = px.bar(this_month_weather_melt, x="Metric", y="Value", color="Type",
                  animation_frame = "Day",
                  animation_group= "Metric",
                  hover_data=["Weather"],
                  range_y = [0, this_month_weather_melt["Value"].max() + 10],
                  title = f"{place} Weather: {start_date} - {end_date}"
                 )
    
    fig1.update_layout(template = "plotly_dark", 
                      height = 600, 
                      width = 1050)
    
    fig1.show()
    #writing the html file. Animated Visualization to HTML
    '''CDN - content delivery network
    so to view this html internet connectivity is important.
    '''
    fig1.write_html("weather_animation.html", include_plotlyjs='cdn', auto_open=True)
except Exception as e:
    print(f"Exceution failed due to : {e}")

