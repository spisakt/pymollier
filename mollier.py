import requests
import plotly.graph_objects as go
import numpy as np
import sys
import configparser
from datetime import datetime
def fetch_weather_data(latitude, longitude, api_key):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={api_key}')
    data = response.json()
    print(data)
    if 'main' in data:
        return data
    else:
        raise ValueError("Weather data not found in response. Check the API key and city name.")

def calculate_absolute_humidity(T, RH):
    return (6.112 * np.exp((17.67 * T) / (T + 243.5)) * RH * 2.1674) / (273.15 + T)

def plot_psychrometric_chart():
    temperature = np.linspace(-20, 40, 100)
    relative_humidity = np.linspace(0, 100, 11)

    T, RH = np.meshgrid(temperature, relative_humidity)
    AH = calculate_absolute_humidity(T, RH)

    fig = go.Figure()

    for rh in relative_humidity:
        ah = calculate_absolute_humidity(temperature, rh)
        # Calculate color from red (high rh) to blue (low rh)
        red_value = int(255 * (rh / 100))
        blue_value = int(255 * (1 - rh / 100))
        fig.add_trace(go.Scatter(
            x=temperature,
            y=ah,
            mode='lines',
            name=f'{int(rh)}%',
            line=dict(color=f'rgba({red_value}, 0, {blue_value}, 1)')
        ))
        fig.add_trace(go.Scatter(
            x=[20],
            y=[calculate_absolute_humidity(20, rh)],
            mode='text',
            text=[f'{int(rh)}%'],
            textposition='top center'
        ))
        
    fig.update_layout(
        #title='Psychrometric Chart',
        xaxis_title='Temperature (°C)',
        yaxis_title='Absolute Humidity (g/m³)',
        xaxis=dict(range=[-10, 35], dtick=2.5, showgrid=True, gridwidth=1, gridcolor='LightGray'),
        yaxis=dict(range=[0, 20], dtick=2.5, showgrid=True, gridwidth=1, gridcolor='LightGray'),
        showlegend=False
    )

    return fig

def calculate_dew_point(T, RH):
    """
    Calculate the dew point temperature given the temperature and relative humidity.
    
    Parameters:
    T (float): Temperature in degrees Celsius
    RH (float): Relative Humidity in percentage
    
    Returns:
    float: Dew point temperature in degrees Celsius
    """
    a = 17.27
    b = 237.7
    alpha = ((a * T) / (b + T)) + np.log(RH / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

def calculate_relative_humidity(T, AH):
    """
    Calculate the relative humidity given the temperature and absolute humidity.
    
    Parameters:
    T (float): Temperature in degrees Celsius
    AH (float): Absolute Humidity in g/m³
    
    Returns:
    float: Relative Humidity in percentage
    """
    # Constants for the calculation
    a = 17.27
    b = 237.7
    
    # Calculate the saturation vapor pressure
    saturation_vapor_pressure = 6.112 * np.exp((a * T) / (b + T))
    
    # Calculate the actual vapor pressure
    actual_vapor_pressure = AH / 2.1674
    
    # Calculate the relative humidity
    RH = (actual_vapor_pressure / saturation_vapor_pressure) * 100
    
    return RH

def plot_actual_values(fig, data, target_temperature, current_time):
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind_speed = data['wind']['speed']
    weather_description = data['weather'][0]['description']
    location = data['name']
    country = data['sys']['country']
    sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
    sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')



    print(f'** Date {current_time}, temperature: {temperature}°C, humidity: {humidity}%')

    absolute_humidity = calculate_absolute_humidity(temperature, humidity)
    fig.add_trace(go.Scatter(
        x=[temperature],
        y=[absolute_humidity],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Actual Value'
    ))

    # Draw a horizontal line at the current absolute humidity
    fig.add_trace(go.Scatter(
        x=[-10, 35],
        y=[absolute_humidity, absolute_humidity],
        mode='lines',
        line=dict(color='blue', dash='dot'),
        name='Current Humidity'
    ))

    #draw a longer line from the current temperature to the target temperature
    fig.add_trace(go.Scatter(
        x=[temperature, target_temperature],
        y=[absolute_humidity, absolute_humidity],
        mode='lines',
        line=dict(color='red'),
        name='Target Humidity'
    ))

    # Print the actual temperature and RH outside, target temperature and corresponding RH, and the dew point in the top left corner
    dew_point = calculate_dew_point(temperature, humidity)
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[19],
        mode='text',
        text=[f'Actual: {temperature}°C, {humidity}% RH'],
        textposition='top right',
        textfont=dict(size=16)
    ))
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[18],
        mode='text',
        text=[f'Target: {target_temperature}°C, {int(calculate_relative_humidity(target_temperature, absolute_humidity))}% RH'],
        textposition='top right',
        textfont=dict(size=16)
    ))
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[17],
        mode='text',
        text=[f'Dew Point: {np.round(dew_point, 1)}°C'],
        textposition='top right',
        textfont=dict(size=16)
    ))
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[16],
        mode='text',
        text=[f'Location: {location}, {country}'],
        textposition='top right',
        textfont=dict(size=12)
    ))  
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[15.2],
        mode='text',
        text=[f'Sunrise: {sunrise}'],
        textposition='top right',
        textfont=dict(size=12)
    ))
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[14.4],
        mode='text',
        text=[f'Sunset: {sunset}'],
        textposition='top right',
        textfont=dict(size=12)
    ))
    fig.add_trace(go.Scatter(
        x=[-9],
        y=[13.6],
        mode='text',
        text=[f'Last Updated: {current_time}'],
        textposition='top right',
        textfont=dict(size=12)
    ))

    # Save the figure as an HTML file
    fig.write_html('mollier_diagram.html', full_html=False)
    #fig.show() # for development only

if __name__ == "__main__":

    api_key = sys.argv[1] # command line argument

    config = configparser.ConfigParser()
    config.read('config.ini')

    print(config)

    latitude = float(config['DEFAULT']['latitude'])
    longitude = float(config['DEFAULT']['longitude'])
    target_temperature = float(config['DEFAULT']['target_temperature'])

    data = fetch_weather_data(latitude, longitude, api_key)

    fig = plot_psychrometric_chart()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    plot_actual_values(fig, data, target_temperature, current_time)
