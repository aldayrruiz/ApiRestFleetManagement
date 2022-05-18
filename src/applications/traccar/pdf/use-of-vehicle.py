import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Vehicles
vehicles = np.array(['1234 Clio', '4312 Zoe', '2314 Zoe', '5413 Traffic', '5312 Scenic'])

# Distance (km)
distance = np.array([1965, 2345, 1900, 2568, 3467])

# Max Speed (km/h)
max_speed = np.array([115, 112, 125, 145, 126])

# Average Speed (km/h)
average_speed = np.array([50, 45, 60, 75, 70])

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{'secondary_y': True}]])

distance_bar = go.Bar(x=vehicles,
                      y=distance,
                      name='Distancia (km)',
                      opacity=0.4,
                      text=distance,
                      textposition='auto')

max_speed_scatter = go.Scatter(x=vehicles,
                               y=average_speed,
                               name='Vel. Med (km/h)',
                               mode='lines+markers+text',
                               text=average_speed,
                               textposition='bottom center',
                               marker=dict(symbol='square', size=10, color='grey'))

average_speed_scatter = go.Scatter(x=vehicles,
                                   y=max_speed,
                                   name='Vel. Max (km/h)',
                                   mode='lines+markers+text',
                                   text=max_speed,
                                   textposition='bottom center',
                                   textfont=dict(color='red'),
                                   marker=dict(symbol='triangle-up', size=10, color='red'))

traces = [distance_bar, max_speed_scatter, average_speed_scatter]
secondary_ys = [False, True, True]

fig.add_traces(traces, secondary_ys=secondary_ys)

# Add figure title
fig.update_layout(title_text='Distancia y velocidad de vehículos')

# Set y-axes titles
fig.update_yaxes(title_text='Distancia', secondary_y=False)
fig.update_yaxes(title_text='Velocidad', secondary_y=True)

fig.show()

if not os.path.exists('images'):
    os.mkdir('images')

fig.write_image('images/fig3.png')
