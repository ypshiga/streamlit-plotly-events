import streamlit as st
from streamlit_plotly_events import plotly_events
import json
#Import plotly express and plotly graph_objects
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import *
import pandas as pd 
import numpy as np
import os
import numpy as np
import pandas as pd
import matplotlib 

appended_df_base = pd.read_csv('Charge_data_2.csv')
appended_df_base.drop("Unnamed: 0", axis=1, inplace=True) # drop index
df_agg = appended_df_base.groupby(['Item Name','2020 CPT Code'], as_index=False)['Average Charge'].agg(['mean',"std", 'count'])
agg_2 = df_agg.nlargest(20,'count')
list_20 = [val[0] for val in agg_2.index.values]
appended_df=appended_df_base[appended_df_base['Item Name'].isin(list_20)] # subset to top 20 most common

st.set_page_config(page_title='Hospital Cost Finder', page_icon="https://img.icons8.com/color/48/000000/hospital.png")
st.title('')
st.header('Find and compare hospital costs in California')


# In[ ]:

lat_init = 37.75
lon_init = -122.3
token = 'pk.eyJ1IjoieXNoaWdhIiwiYSI6ImNrcWg4emxyaDAwZzkyb285dXpqb2ZoNWgifQ.AoifeJJZ-EN-zEbrEsJj9Q'

#token = os.environ['TOKEN']

item_select = st.selectbox('Pick an item/procedure:',list(appended_df['Item Name'].unique()))
cpt_pick = appended_df["2020 CPT Code"][appended_df['Item Name']==item_select].unique()
#st.subheader('Displaying costs for: ' + str(item_select) + '.')
#df_temp = appended_df[appended_df["2020 CPT Code"]==cpt_index].copy()
#@st.cache
def df_map(item):
    df_temp = appended_df[appended_df["Item Name"]==item].copy()
    return df_temp
    
df_temp = df_map(item_select)
val_99 = np.nanpercentile(df_temp["Average Charge"],99)
val_1 = np.nanpercentile(df_temp["Average Charge"],1)
val_mean = int(np.mean(df_temp["Average Charge"]))
val_min = int(np.min(df_temp["Average Charge"]))
val_max = int(np.max(df_temp["Average Charge"]))

st.subheader('State-wide stats: Average = $' + str(val_mean) + '. Min = $' + str(val_min) + '. Max = $' + str(val_max) + '.')

#df_temp.loc[df_temp["Average Charge"]>val_99, "Average Charge"] = val_99
fig = px.scatter_mapbox(df_temp, lat="lat", lon="lon", color="Average Charge",size="Average Charge",
    color_continuous_scale='ylorrd',hover_data ={'lat':False,'lon':False,'Average Charge': True},
    range_color=[val_1,val_99],hover_name = "Hospital Name",size_max = 30)

fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token,
    title_x=0.5,
    margin=dict(l=0, r=0, t=25, b=10),
    coloraxis_colorbar=dict(
    xpad=3,title='Cost',
    tickprefix='$'),
    hovermode='closest',
    mapbox=dict(
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=lat_init,
            lon=lon_init
        ),
        pitch=15,
        zoom=9
    ))
selected_points = plotly_events(fig, click_event=False, select_event=True)

#st.plotly_chart(fig,use_container_width=True)
st.write('CPT code: ' + str(int(cpt_pick)))

st.write('Based on 2020 data from: [data.chhs.ca.gov](https://data.chhs.ca.gov/dataset/chargemasters/resource/95e415ee-5c11-40b9-b693-ff9af7985a94)')

# Select other Plotly events by specifying kwargs
if selected_points:
    res = json.loads(selected_points)
    inds = [x["pointNumber"] for x  in res]
    df = pd.DataFrame(df_temp[['Hospital Name','Average Charge']].iloc[inds])   
    df.style.background_gradient(cmap='Spectral_r')    
    st.table(df.assign(hack='').set_index('hack'))