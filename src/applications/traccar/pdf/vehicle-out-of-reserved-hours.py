import os
import pandas as pd
import numpy as np

import plotly.express as px

# Example, how it must be df
# Vehicles  |   hours   |
# Renault C |   80      |
# Renault Z |   120     |
# Renault T |   50      |


# Vehicles
vehicles = np.array(['1234 Clio', '4312 Zoe', '2314 Zoe', '5413 Traffic', '5312 Scenic'])

# Hours
hours = np.array([30, 10, 15, 5, 20])

df_dict = {
    'vehicles': vehicles,
    'hours': hours
}

df = pd.DataFrame(df_dict)

month_title = ''
fig = px.histogram(
    df,
    title=f'Uso de Vehículos {month_title}',
    x='vehicles',
    y='hours',
    range_y=[0, 60],
    labels=dict(category='Leyenda')
)

fig.update_xaxes(title_text='Vehículos')
fig.update_yaxes(title_text='Horas')


fig.show()

if not os.path.exists('images'):
    os.mkdir('images')

fig.write_image('images/fig2.png')
