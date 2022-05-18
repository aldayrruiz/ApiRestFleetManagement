import os
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Vehicles
vehicles = np.array(['1234 Clio', '4312 Zoe', '2314 Zoe', '5413 Traffic', '5312 Scenic'])

# Take (h)
take = np.array([1.4, 0.5, 2.3, 1.2, 2.2])

# Free (h)
free = np.array([2.5, 3.5, 3.3, 3.2, 1.7])

# Create figure with secondary y-axis
fig = make_subplots()

take_scatter = go.Scatter(x=vehicles,
                               y=take,
                               name='Recoger',
                               mode='lines+markers',
                               marker=dict(symbol='circle', size=10, color='blue'))

free_scatter = go.Scatter(x=vehicles,
                                   y=free,
                                   name='Liberar',
                                   mode='lines+markers',
                                   marker=dict(symbol='circle', size=10, color='orange'))

traces = [take_scatter, free_scatter]

fig.add_traces(traces)

# Add figure title
title_month = ''
fig.update_layout(title_text=f'Puntualidad por vehículo {title_month}')

# Set y-axes titles
fig.update_yaxes(title_text='Horas')

fig.show()

if not os.path.exists('images'):
    os.mkdir('images')

fig.write_image('images/fig4.png')
