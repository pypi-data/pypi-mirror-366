""" Analyses's constants
"""
# ANALYSER
HOUR_BOUNDS = 'hour_interval'
SECTEUR_NAME = 'NomSecteur'

REMPL_CAT_NO_PARK = 'Capacité résiduelle'

# Trips
TRIPS_COLS = ['rtaudl', 'nb_plaque', 'region', 'period', 'week_day',
              'dest_lat', 'dest_lng', 'ori_lat', 'ori_lng']
TRIPS_WEEK = 'week_day'

# variable informations
SIDE_OF_STREET_INFO = """
    La variable side_of_street dépend du sens de numérisation de la géobase
    double qui lui-même suis le sens d'incrémentation des adresses.

       +-------------+----------------------+----------------+--------+-------+
       | ORIENTATION |     LOCALISATION     | SIDE_OF_STREET |  CÔTÉ  | RIVE  |
       +=============+======================+================+========+=======+
       | EST-OUEST   | Est de St-Laurent    |     -1         | GAUCHE | NORD  |
       +-------------+----------------------+----------------+--------+-------+
       | EST-OUEST   | Est de St-Laurent    |      1         | DROITE | SUD   |
       +-------------+----------------------+----------------+--------+-------+
       | EST-OUEST   | Ouest de St-Laurent  |     -1         | GAUCHE | SUD   |
       +-------------+----------------------+----------------+--------+-------+
       | EST-OUEST   | Ouest de St-Laurent  |      1         | DROITE | NORD  |
       +-------------+----------------------+----------------+--------+-------+
       | NORD-SUD    | Toutes               |     -1         | GAUCHE | OUEST |
       +-------------+----------------------+----------------+--------+-------+
       | NORD-SUD    | Toutes               |      1         | DROITE | EST   |
       +-------------+----------------------+----------------+--------+-------+
    """

OCCUPATION_INFO = """
    La valeur de l'occupation peut prendre les valeurs non-numériques
    suivantes:

    1.	La catégorie « non parcourue » désigne des tronçons de rue qui n'étaient
        pas incluses dans le plan de collecte de l'étude.
    2.	La catégorie « sans données » (NaN, blanc), quant à elle, peut à la fois
        désigner des tronçons qui étaient prévus mais n'ont pas pu être
        parcourue en raison des conditions terrains (travaux, manque de temps,
        etc.) ou des tronçons où aucun véhicule n'était présent. En effet, il
        pas possible dans l'état présent de la technologie utilisée de
        distinguer ces deux états car ils se traduisent de la même façon
        dans la base de données.
    3.	La catégorie « aucune place » désigne des tronçons où les obstacles et
        les interdictions de stationnement font en sorte qu'il est toujours
        interdit de s'y immobiliser.
    4.	La catégorie « travaux » désigne des tronçons qui étaient soit
        impossibles à parcourir ou des tronçons dont les places de
        stationnement étaient retirées en raison de chantiers de construction
        au moment de la collecte.

    """
