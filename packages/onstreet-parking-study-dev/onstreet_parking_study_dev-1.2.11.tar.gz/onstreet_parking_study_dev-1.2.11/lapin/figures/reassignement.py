import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def veh_reassignement_plot(df:pd.DataFrame, roads_id:list, path:str,
                           legend_name:dict={}, separe_plots=False):

    default_rename={
        'veh_rm'                : 'Occupées - rue principale',
        'cap_rm'                : 'Totales  - rue principale',
        'capacity'              : 'Totales  - rues secondaires',
        'rest'                  : 'Situation actuelle',
        'avg_free_parking_spot' : 'Report réaliste',
        'min_free_parking_spot' : 'Report complet',
    }
    if legend_name:
        default_rename = legend_name


    # compute columns
    df = df.reset_index().set_index('segment')
    roads_id = np.intersect1d(roads_id, df.index)
    df['rest'] = df['capacity'] - df['parking_occurences']
    df['veh_rm'] = 0.0
    df.loc[roads_id, 'veh_rm'] = -df.loc[roads_id, 'parking_occurences']
    df['cap_rm'] = 0.0
    df.loc[roads_id, 'cap_rm'] = -df.loc[roads_id, 'capacity']
    df.loc[roads_id, 'capacity'] = 0

    df = df[list(default_rename.keys())+['hour']].reset_index()
    df.rename(
        columns=default_rename,
        inplace=True
    )

    # sum whole region
    df = df.drop(columns='segment').groupby('hour').sum().reset_index()


    if separe_plots:
        data = -1*df[['Occupées - rue principale',
                      'Totales  - rue principale'
                      ]].copy()
        data = data.div(data['Totales  - rue principale'], axis=0)
        data *= 100
        data = data[['Occupées - rue principale']]
        data['hour'] = df['hour']

        data = data.melt(id_vars='hour', value_name='Pourcentage', var_name='Portion de place')

        f, ax = plt.subplots(figsize=(8, 6), dpi=150)
        sns.barplot(
            data=data,
            x='hour',
            y='Pourcentage',
            hue='Portion de place',
            palette='hls',
            ax=ax,
            legend=False
        )
        ax.set_xlabel('Heure');
        ax.set_ylabel('Pourcentage de places occupées');
        ax.set_title('Rue principale')
        ax.tick_params(axis='x', labelrotation=90)
        # sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        f.savefig(path+f'/Capacité_et_occupation_rue_principale.png', bbox_inches='tight')

        data = df[['Totales  - rues secondaires',
                   'Situation actuelle',
                   'Report réaliste',
                   'Report complet']].copy()
        data = data.div(data['Totales  - rues secondaires'], axis=0)
        data *= 100

        #data['totales  - rues secondaires'] -= data['Situation actuelle']
        #data['Situation actuelle'] -= data['Report réaliste']
        #data['Report réaliste'] -= data['Report complet']
        data = data[[
            'Report complet',
            'Report réaliste',
            'Situation actuelle',
            #'totales  - rues secondaires'
            ]].copy()

        data['hour'] = df['hour']
        data = data.melt(id_vars='hour', value_name='Portion de places', var_name='Portion de place libre')

        f, ax = plt.subplots(figsize=(8, 6), dpi=150)
        sns.barplot(
            data=data,
            x='hour',
            y='Portion de places',
            hue='Portion de place libre',
            palette=['#003366', '#0892d0', '#add8e6'],
            ax=ax
        )
        ax.set_ylim(top=100)
        ax.set_xlabel('Heure')
        ax.set_ylabel('Pourcentage de places disponibles restantes')
        ax.set_title('Rues secondaires')
        ax.tick_params(axis='x', labelrotation=90)
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

        #f, ax = plot_stacked_charge_graphs(
            #charges=data.T.values,
            #groupnames=data.columns,
            #x=None,
            #xlabel='Heures',
            #ylabel='Pourcentage de places',
            #ticklabels=df['hour'],
            #legend_kwargs={'loc':'upper left', 'bbox_to_anchor':(1,1)},
            #colormap=['#003366', '#0892d0', '#add8e6'],
            #return_fig=True
        #)

        f.savefig(path+f'/Capacité_et_occupation_rue_secondaire_apres_report.png', bbox_inches='tight')
    else:
        df = df.melt(id_vars='hour', value_name='Portion de places', var_name='Type')

        f, ax = plt.subplots(figsize=(8, 6), dpi=150)
        sns.barplot(
            data=df,
            x='hour',
            y='Portion de places',
            hue='Type',
            palette='hls'
        )
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(np.abs(ax.get_yticks()).astype(int))

        ax.set_xlabel('Heure');
        ax.set_ylabel('Nombre de places');
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

        f.savefig(path+f'/Capacité_résiduelle_horaire_secteur.png', bbox_inches='tight')
