import pandas as pd
import geopandas as gpd
import numpy as np
import branca.colormap as cmp
import folium
import copy

def coloring_data_from_value(df, cols,
                             colors=['red','yellow', 'green', 'blue',
                                     'purple', 'orange', 'pink']):
    
    df = df.copy()
    df = df.assign(id_col = df[cols].replace({df[cols].unique()[i]:i
                                           for i in range(df[cols].unique().shape[0])}))
    color_dict = df.copy().set_index(cols)['id_col'].drop_duplicates()
    
    cmap = cmp.LinearColormap(
        colors,
        vmin=np.min(df.id_col), vmax=np.max(df.id_col),
        caption=cols.__str__() #Caption for Color scale or Legend
    )
    
    return df, color_dict, cmap

def plot_mult(dfs=[], dfs_col=dict(), dfs_colors=dict(), dfs_popup=dict(), zoom_start=14, zoom_df=0, mmap=None):
    
    # Folium map creation
    if not mmap:
        pos = ()
        if isinstance(dfs[zoom_df], gpd.GeoDataFrame):
            pos = dfs[zoom_df].to_crs('epsg:4326').geometry.centroid.iloc[0]
            pos = (pos.y, pos.x)
        elif isinstance(dfs[zoom_df], pd.DataFrame):
            pos = dfs[zoom_df][['lat', 'lng']].values[0]

        mmap = folium.Map(location=pos, zoom_start=zoom_start)

    #### GeoDataFrame
    for id_df, df in enumerate(dfs):
        df = df.copy()
        if isinstance(df, gpd.GeoDataFrame):
            if id_df not in dfs_col.keys():
                folium.GeoJson(df).add_to(mmap)
            else:
                col = dfs_col[id_df]
                if id_df not in dfs_colors.keys():
                    df, color_dict_geo, linear_geo = coloring_data_from_value(df, col)
                
                else:
                    df, color_dict_geo, linear_geo = coloring_data_from_value(df, col, dfs_colors[id_df])
            
                pop =  dfs_popup[id_df] if id_df in dfs_popup.keys() else col
                pop = [pop] if isinstance(pop, str) else pop

                folium.GeoJson(
                    df, 
                    tooltip=folium.features.GeoJsonTooltip(
                        fields=pop,
                        labels=True,
                        sticky=False
                    ),
                    style_function=lambda feature: {
                        'fillColor': linear_geo(color_dict_geo[feature['properties'][col]]),
                        'color': linear_geo(color_dict_geo[feature['properties'][col]]),     #border color for the color fills
                        'weight': 2          #how thick the border has to be
                #         'dashArray': '5, 3'  #dashed lines length,space between them
                    }
                ).add_to(mmap)
        #### DataFrame
        elif isinstance(df, pd.DataFrame):
            if id_df not in dfs_col.keys():
                for i, x in df.iterrows():
                    folium.Circle(location=(x.lat, x.lng), alpha=0.5, radius=1).add_to(mmap)
            else:
                col2 = dfs_col[id_df]
                pop2 = dfs_popup[id_df] if id_df in dfs_popup.keys() else col2
                if id_df not in dfs_colors.keys():
                    df, color_dict, linear = coloring_data_from_value(df, col2)
                
                else:
                    df, color_dict, linear = coloring_data_from_value(df, col2, dfs_colors[id_df])
            
                for i, x in df.iterrows():
                    pop_str = x[pop2].__str__() if isinstance(pop2, str) else "\n".join(x[pop2].__str__().split("\n")[:-1])
                    folium.Circle(location=(x.lat, x.lng), color=linear(color_dict[x[col2]]), alpha=0.5, radius=1, popup=pop_str).add_to(mmap)
    


    return mmap
