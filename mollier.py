import requests
import plotly.graph_objects as go
import numpy as np
import sys

def fetch_weather_data():
    api_key = sys.argv[1] # command line argument
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=51.387974063631475&lon=7.01352462559009&units=metric&appid={api_key}')
    data = response.json()

    print(data)

    if 'main' in data:
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        return temperature, humidity
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
        fig.add_trace(go.Scatter(
            x=temperature,
            y=ah,
            mode='lines',
            name=f'{int(rh)}%'
        ))
        fig.add_trace(go.Scatter(
            x=[20],
            y=[calculate_absolute_humidity(20, rh)],
            mode='text',
            text=[f'{int(rh)}%'],
            textposition='top center'
        ))
    fig.update_layout(
        title='Psychrometric Chart',
        xaxis_title='Temperature (°C)',
        yaxis_title='Absolute Humidity (g/m³)',
        xaxis=dict(range=[-10, 35], dtick=2.5, showgrid=True, gridwidth=1, gridcolor='LightGray'),
        yaxis=dict(range=[0, 20], dtick=2.5, showgrid=True, gridwidth=1, gridcolor='LightGray'),
        showlegend=False
    )

    return fig

def plot_actual_values(fig, temperature, humidity):
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
        line=dict(color='red', dash='dot'),
        name='Current Humidity'
    ))

    # Save the figure as an HTML file
    fig.write_html('mollier_diagram.html', full_html=False)

if __name__ == "__main__":
    temp, hum = fetch_weather_data()
    fig = plot_psychrometric_chart()
    print('** actual values', temp, hum)
    plot_actual_values(fig, temp, hum)