"""User config parser."""

from dataclasses import dataclass, field
import os
import configparser
import re
import json
import logging
from typing import Dict, List
import pathvalidate
import pandas

from lapin.configs.others import (
    DELIM_CONNECTION,
    GEOREF_CP_CONNECTION,
    PROV_CONF,
    VIS_DELIM_CONNECTION,
)
from lapin.configs.tennery_creek import (
    LPR_CONNECTION,
    VEH_CONNECTION,
)
from lapin.configs.mtl_opendata import (
    ROADS_CONNECTION,
    ROADS_DB_CONNECTION,
)

logger = logging.getLogger(__name__)


def str2bool(string: str) -> bool:
    """Interpret a string to a boolean.

    Parameters
    ----------
    string : str
        Bool as as string.

    Returns
    -------
    bool
    """
    if string in ["True", "true", "1", "y", "Y"]:
        return True
    return False


def string2type(x: str, i_type: str = "int") -> float | bool | int | str:
    """Convert String to type i_type.

    Try to convert the string value into one of implemented type. Implemented
    type are float, bool, int, path, numeric. If the type passed as parameter
    is not implemented, the string is retunred.

    Parameters
    ----------
    x : str.
        Value to cast.
    i_type : str.
        Type to cast in, by default "int".

    Examples
    --------
    string2type("2", "int")
    >>> 2
    type(string2type("2", "int"))
    >>> int
    string2type("2.5", "float")
    >>> 2.5
    type(string2type("2.5", "numeric"))
    >>> float
    """

    if i_type == "float":
        return float(x)
    elif i_type == "bool":
        return str2bool(x)
    elif i_type == "int":
        return int(x)
    elif i_type == "path":
        return path_slashes(x)
    elif i_type == "numeric":
        try:
            return int(x)
        except ValueError:
            return float(x)
    else:
        return x


def raw(string: str) -> str:
    """Returns a raw string representation of text.

    Given a string return the raw value of the string (i.e. r prefixed string
    if the string contains escaped char.)

    Parameters
    ----------
    string : str.
        String to cast as raw.

    Returns
    -------
    str
    """
    escape_dict = {
        "\a": r"\a",
        "\b": r"\b",
        "\c": r"\c",
        "\f": r"\f",
        "\n": r"\n",
        "\r": r"\r",
        "\t": r"\t",
        "\v": r"\v",
        "'": r"\'",
        "\0": r"\0",
        "\1": r"\1",
        "\2": r"\2",
        "\3": r"\3",
        "\4": r"\4",
        "\5": r"\5",
        "\6": r"\6",
        "\7": r"\7",
        "\8": r"\8",
        "\9": r"\9",
    }
    new_string = ""
    for char in string:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


def path_slashes(string: str) -> str:
    """Convert windows' backslashes or unix slashes to OS's type .

    Parameters
    ----------
    string : str.
        String to cast as raw.

    Returns
    -------
    str
    """
    inter = raw(string).replace("\\", os.sep)
    return raw(inter).replace("/", os.sep)


def parse_dict_string(item: str) -> dict:
    """Safely evaluate a dictionary in a string.

    Parameters
    ----------
    item : str
        Dictionary as a string, by default str.

    Returns
    -------
    dict

    Examples
    --------
    parseDictString("{}")
    >>> {}
    """
    start = item.find("{")
    end = item.rfind("}")
    content = item[start + 1 : end]

    keys = []
    values = []
    part = ""
    open_b = 0  # accounting for internal dicts/lists/tuples
    skip_t = False  # accounting for strings
    for c in content:
        if c in "{[(":
            open_b += 1
        if c in ")]}":
            open_b -= 1
        if c in ['"', "'"] and not skip_t:
            skip_t = True
        if c not in ":," or open_b > 0 or skip_t:
            part += c
        else:
            if len(keys) == len(values):
                keys.append(part.strip())
            else:
                values.append(part.strip())
            part = ""
        if c in ['"', "'"] and skip_t:
            skip_t = False

    if part != "":
        values.append(part.strip())

    return keys, values


##################
#   Structures   #
##################
def list1d(item: str, i_type: str = "int", type: object = list) -> list | set | tuple:
    """Parse string format into 1 dimensional array (values).

    Will automatically generate range for int values
    (i.e. [1,3-5] -> [1,3,4,5]).

    Parameters
    ----------
    item : str
        String to parse as a list.
    i_type : str
        Type of object in the list, by default "int".
    type : object
        Exit type (list, set, etc.), by default list.
    Returns
    -------
    list

    Alternative
    -----------
    import ast
    x = '[0.90837,0.90837]'
    ast.literal_eval(x)
    """
    translator = str.maketrans({key: None for key in ["[", "]", " ", "\n"]})
    item = item.translate(translator).split(",")
    item = list(filter(None, item))
    if len(item) > 0:
        if i_type == "int":
            if len(list(set(item))) != len(item):
                allow_duplicates = True
            else:
                allow_duplicates = False
            for i in range(len(item)):
                if "-" in item[i]:
                    temp = item[i].split("-")
                    item += list(range(int(temp[0]), int(temp[-1]) + 1))
                    item[i] = None
            item = list(filter(None, item))
            if not allow_duplicates:
                item = list(set(item))
            return type(sorted([int(x) for x in item]))
        else:
            return type([string2type(x, i_type=i_type) for x in item])
    else:
        return type([])


def list2d(item: str, i_type: str = "int", type: object = list) -> list | set | tuple:
    """Parse string format into 2 dimensional array (values).

    Set type=list to gt a list back or type=tuple to get a tuple back.

    Parameters
    ----------
    item : str
        String to parse as a list.
    i_type : str
        Type of object in the list, by default "int".
    type : object
        Exit type (list, set, etc.), by default list
    Returns
    -------
    list

    Alternative
    -----------
    import ast
    x = '[0.90837,0.90837]'
    ast.literal_eval(x)

    See Also
    --------
    list1d
    """
    translator = str.maketrans({key: None for key in [" ", "\n"]})
    parsing = item.translate(translator)
    parsing = parsing.split("],[")
    parsing = list(filter(None, parsing))
    item = []
    if len(parsing) > 0:
        translator = str.maketrans({key: None for key in ["[", "]", "(", ")", ","]})
        for i in range(len(parsing)):
            parsingx = parsing[i].split(",")
            for j in range(len(parsingx)):
                parsingx[j] = parsingx[j].translate(translator)
            item.append(type([string2type(x, i_type=i_type) for x in parsingx]))
        return type(item)
    else:
        return type(type())


PAR = re.compile("\(([^)]+)\)", re.VERBOSE)
BRA = re.compile("\[([^)]+)\]", re.VERBOSE)

PAREXTRACT = re.compile("((?<=\()(?:[^()]+\([^)]+\)))", re.VERBOSE)


def mixed_list(item: str, i_type: str = "int") -> list[object]:
    """Parse string format into 1 dimensional array that can contain list-like
    elements.

    Parameters
    ----------
    item : str
        String that contains the list.
    i_type: str
        Type of elements, by default int.

    Return
    ------
    list[object]
        Evaluation of 'item'.

    Examples
    --------
    mixedList('[1,2,(2,3)]')
    >>> [1,2,(2,3)]
    """
    translator = str.maketrans({key: None for key in [" ", "\n"]})
    parsing = item.translate(translator)
    parsing = [x for x in BRA.split(parsing, maxsplit=1) if x != ""][0]

    item = []
    if len(parsing) > 0:
        flag = tuple
        brasearch = BRA.search(parsing)
        if brasearch:
            parsing = parsing.replace("[", "(")
            parsing = parsing.replace("]", ")")
            flag = list

        parsearch = PAR.search(parsing)
        if not parsearch:
            return list1d(parsing, i_type=i_type)

        beg = parsing.split(r"(")[0]
        end = parsing.split(r")")[-1]
        mid = parsing[len(beg) + 1 : -(len(end) + 1)]

        item += list1d(beg, i_type=i_type)
        item.append(flag(list1d(mid, i_type=i_type)))
        item += list1d(end, i_type=i_type)

        return item
    else:
        return [[]]


def nddict(item: str, i_type: str = "int", k_type: str = "str") -> dict:
    """Parse string format to extract a dictionnary that can contain
    subcontainers.

    Parse string format to extract a dictionnary that can contain
    subcontainers (list1d, tuple1d, list2d, tuple2d, mixedList, dictionnary)
    as long as the internalmost elements all follow i_type. Keys must all match
    the same k_type.

    Parameters
    ----------
    item : str.
        String to parse.
    i_type : str, optional.
        Type of values, by default 'str'.
    k_type : str, optional.
        Type of the dictionary keys, by default 'str'.

    Returns
    -------
    dict
        Evaluation of item.

    Examples
    --------
    i1 = 'trailing {10:[1], 4:2, 6:[1,2,(2,3)], 1000:{3:1, 99: 2}}'
    i2 = 'trailing {this:[1], 3:2, containing:[1,2,(2,3)], and:{a:1, with a: 2}}'
    dictND(i1, i_type='int', k_type='int')
    >>> {10: [1],
         4: 2,
         6: [1,2,(2,3)],
         1000: {3:1, 99: 2}
        }

    dictND(i2, i_type='int', k_type='str')
    >>> {'this': [1],
         '3': 2,
         'containing': [1,2,(2,3)]
         'and': {'a':1, 'with a': 2}
        }
    """
    keys, values = parse_dict_string(item)
    base = {string2type(keys[i], i_type=k_type): values[i] for i in range(len(keys))}

    for k, v in base.items():
        if "[[" in v and "]]" in v:
            base[k] = list2d(v, i_type=i_type, type=list)
        elif "((" in v and "))" in v:
            v = v.replace("((", "[[")
            v = v.replace("))", "]]")
            base[k] = list2d(v, i_type=i_type, type=tuple)
        elif "(" in v and "[" in v and "]" in v and ")" in v:
            base[k] = mixed_list(v, i_type=i_type)
        elif "[" in v and "]" in v:
            base[k] = list1d(v, i_type=i_type, type=list)
        elif "(" in v and ")" in v:
            v = v.replace("(", "[")
            v = v.replace(")", "]")
            base[k] = list1d(v, i_type=i_type, type=tuple)
        elif "{" in v and "}" in v:
            base[k] = nddict(v, i_type=i_type, k_type=k_type)
        else:
            base[k] = string2type(v, i_type=i_type)
    return base


##################
#   Write utils  #
##################
def split_list(
    items: list,
    max_item_per_line: int = 5,
    pad_newlines_with: str = " ",
    sep: str = ", ",
    end_bracket_on_newline: bool = True,
    c_type: str = "list",
) -> str:
    """Display a list by spliting it on several lines.

    Display list elements by spliting it on several lines of
    fixed length.

    Parameters
    ----------
    items : list
        List to display.
    max_item_per_line : int, optional.
        Max item to show on a single line, by default 5.
    pad_newlines_with : str, optional.
        Padding to use when starting a new line, by default " ".
    sep : str, optional.
        Separator to print between list items, by default "."
    end_bracket_on_newline : bool, optional.
        Put the closing bracket on a new line, by default True.
    c_type : str, optional.
        Type of item we iterate on, by default "list".

    Returns
    -------
    str
        String displayed.

    Examples
    --------
    split_list([1,2,3,4], 2, " ", "| ")
    >>> [1| 2|
     3| 4|
    ]

    """

    if max_item_per_line is None:
        max_item_per_line = len(items)
    string = "[" if c_type == "list" else "("
    is_additional_line = False
    while len(items) > 0:
        if is_additional_line:
            string += ",\n" + pad_newlines_with
        string += sep.join([f"{i}" for i in items[0:max_item_per_line]])
        items = items[max_item_per_line:]
        if len(items) > 0:
            is_additional_line = True

    if end_bracket_on_newline and is_additional_line:
        string += "\n" + pad_newlines_with
    string += "]" if c_type == "list" else ")"
    return string


def split_dict(
    dictio: dict,
    max_key_per_line: int = 1,
    pad_newlines_with: str = " ",
    sep: str = ", ",
    end_bracket_on_newline: bool = True,
    max_split_inside_list: int = 5,
) -> str:
    """Display a dictionary by printing it on a string.

    Parameters
    ----------
    dictio : dict
        Dictionary to store in a string.
    max_key_per_line : int, optional
        Maximum number of key to display on a single line, by default 5.
    pad_newlines_with : str, optional
        Padding for each new line, by default " ".
    sep : str, optional
        Separator to use between items, by default ", ".
    end_bracket_on_newline : bool, optional
        Put the closing bracket on a new line, by default True.
    max_split_inside_list : int, optional
        Maximum number of time a list is split, by default 5.

    Returns
    -------
    str
        Dictionnary displayed on a string.

    See Also
    --------
    split_list

    """
    if len(dictio) == 0:
        return "{}"

    items = list(dictio.keys())
    greatest_key = max([len(f"{k}") for k in items])
    pad_internal_with = (
        "".join([" " for i in range(greatest_key + 3)]) + pad_newlines_with
    )

    string = "{"
    is_additional_line = False
    while len(items) > 0:
        if is_additional_line:
            string += ",\n" + pad_newlines_with
        keys = items[0:max_key_per_line]

        stacks = []
        for key in keys:
            if isinstance(dictio[key], list):
                stringvalue = split_list(
                    dictio[key],
                    end_bracket_on_newline=False,
                    max_item_per_line=max_split_inside_list,
                    pad_newlines_with=pad_internal_with,
                    sep=sep,
                    c_type="list",
                )
            elif isinstance(dictio[key], tuple):
                stringvalue = split_list(
                    dictio[key],
                    end_bracket_on_newline=False,
                    max_item_per_line=max_split_inside_list,
                    pad_newlines_with=pad_internal_with,
                    sep=sep,
                    c_type="tuple",
                )
            elif isinstance(dictio[key], dict):
                stringvalue = split_dict(
                    dictio[key],
                    end_bracket_on_newline=False,
                    max_split_inside_list=max_split_inside_list,
                    pad_newlines_with=pad_internal_with,
                    sep=sep,
                    max_key_per_line=max_key_per_line,
                )
            else:
                stringvalue = f"{dictio[key]}"
            stacks.append(f"{key}: {stringvalue}")
        string += sep.join(stacks)
        items = items[max_key_per_line:]
        if len(items) > 0:
            is_additional_line = True

    if end_bracket_on_newline and is_additional_line:
        string += "\n" + pad_newlines_with
    string += "}"
    return string


#################
#    Helpers    #
#################
def build_cache(path: str):
    """Create cache dir.

    Parameters
    ----------
    path : str
        Cache path.

    """
    cache = os.path.join(path, "cache")
    os.makedirs(cache, exist_ok=True)


def build_results(path: str):
    """Create results dir.

    Parameters
    ----------
    path : str
        Results dir path.

    """
    cache = os.path.join(path, "resultat")
    os.makedirs(cache, exist_ok=True)


def build_dates(days_bounds: dict):
    """Set query dates values.

    Parameters
    ----------
    days_bounds : dict
        Query dates values

    """
    LPR_CONNECTION["dates"] = days_bounds
    VEH_CONNECTION["dates"] = days_bounds


def set_delimns(gis_bounds: str, gis_vis_bounds: str):
    """Set the geographic delims path.

    Parameters
    ----------
    gis_bounds : str
        Path of the geographic delimitation of the study.
    gis_vis_bounds : str
        Path of the sub-geographic delimitation. By default gis_vis_bound
        is the same as gis_bound.

    """
    DELIM_CONNECTION["filename"] = gis_bounds
    VIS_DELIM_CONNECTION["filename"] = gis_vis_bounds


def set_prov_origin(prov_origin_filename: str):
    """Set the origin path for OD computation.

    Parameters
    ----------
    prov_origin_filename : str
        Path to origins of car trips.

    """
    GEOREF_CP_CONNECTION["filename"] = prov_origin_filename


def set_prov_conf(conf):
    """Set all the configurations for provenance computation.

    Parameters
    ----------
    conf : LapinConfig
        Configuration of the project being analysed.

    """
    PROV_CONF["act_prov"] = conf.act_prov
    PROV_CONF["cp_base_filename"] = conf.plates_origin_file_name
    PROV_CONF["cp_folder_path"] = conf.plates_origin_path
    PROV_CONF["cp_regions_bounds"] = conf.plates_origin_bounds
    PROV_CONF["cp_regions_bounds_names"] = conf.plates_origin_bounds_name
    PROV_CONF["plates_periods"] = conf.plates_origin_periods
    PROV_CONF["cp_conf"] = GEOREF_CP_CONNECTION


def set_roads(roads_path: str, roads_dbl_path: str, projects_id: list[int]):
    """If there is a custom roads graph, set the path to those custom files.

    Parameters
    ----------
    roads_path : str
        File path to the road geometry
    roads_dbl_path : str
        File path to the road geometry used to represent the curbs.
    projects_id : list[int]
        Projects id for curbsnapp.

    """
    # OPTIONAL
    if roads_path != "Default.def":
        ROADS_CONNECTION["filename"] = roads_path
    if roads_dbl_path != "Default.def":
        ROADS_DB_CONNECTION["filename"] = roads_dbl_path

    ROADS_CONNECTION["config"]["projects_list"].extend(projects_id)
    ROADS_DB_CONNECTION["config"]["projects_list"].extend(projects_id)


##################
# Configuration  #
##################
@dataclass
class LapinConfig:
    # id
    num_proj: int = 0
    title_proj: str = ""
    client_proj: str = ""
    work_folder: str = ""
    curbsnapp_projects_id: List = field(default_factory=list)

    # options
    act_occup: bool = False
    act_rempla: bool = False
    act_prov: bool = False
    comp_sect_agg: bool = False
    handle_restriction: bool = False
    one_way_agg: bool = False
    act_report: bool = False

    # parameters
    days_bounds: List = field(default_factory=list)
    hour_bounds: Dict = field(default_factory=dict)
    analyse_freq: str = ""
    allow_veh_on_restrictions: List[str] = field(
        default_factory=lambda: ["Borne fontaine"]
    )
    restrictions_to_exclude: List[str] = field(default_factory=lambda: ["Défaut"])
    plates_origin_path: str = ""
    plates_origin_file_name: str = ""
    plates_origin_bounds: str = ""
    plates_origin_bounds_name: str = ""
    plates_origin_periods: Dict = field(default_factory=dict)
    plates_origin_gis: str = ""
    report_street_name: List[str] = field(default_factory=list)
    vehicule_conf: Dict = field(default_factory=dict)

    # optional
    ignore_agg_seg: List[int] = field(default_factory=list)
    vis_rotation: List[int] = field(default_factory=lambda: [-63])
    vis_buffer: List[int] = field(default_factory=lambda: [0])
    veh_size: float = 5.5
    compass_rose: bool = True
    anotation: bool = True
    capa_along_occ: bool = False
    build_leg: bool = False
    anotation_prov: bool = True
    regs_zoom_prov: List[int] = field(default_factory=list)
    plot_all_capa: bool = False
    roads_path: str = "Default.def"
    roads_dbl_path: str = "Default.def"


def json_covertible(json_file_path: str, encoding: str = "utf-8") -> dict | None:
    """Check if the file under json_file_path is json convertible. If it is,
    return the json dict. Otherwise return None.

    Parameters
    ----------
    json_file_path : str
        Path to the json file to check
    encoding : str, optional
        Encoding of the file.

    Returns
    -------
    dict | None
        Json file evaluated or None.

    """
    with open(json_file_path, "r", encoding=encoding) as f:
        try:
            json_conf = json.load(f)
            return json_conf
        except ValueError as error:  # includes JSONDecodeError
            logger.error(error)
            return None


@dataclass
class UserConfig(LapinConfig):
    """User config for Lapin analysis.

    Raises
    ------
    ValueError
        Error while parsing config formats
    """

    config: configparser.ConfigParser | None = field(init=False)
    handles: List | pandas.DataFrame = field(init=False)
    section: str = ""
    sections: List = field(init=False)

    @classmethod
    def from_file(cls, config_name: str, encoding: str = "latin-1"):

        # default value
        new_conf = cls()

        new_conf.config = configparser.ConfigParser(allow_no_value=True)

        # Handle json as input
        new_conf.config.read(config_name, encoding=encoding)

        new_conf.handles = []

        new_conf.section = "DESCRIPTION"
        new_conf.store("num_proj", "Numéro de projet [required]", "1", c_type="int")
        new_conf.store(
            "title_proj", "Titre de projet  [required]", "<Titre>", c_type="string"
        )
        new_conf.store("client_proj", "Client", "<Client>", c_type="string")
        new_conf.store(
            "work_folder",
            "Dossier de travail [required]",
            "Path\to\folder",
            c_type="path",
            p_type="folder",
        )
        new_conf.store(
            "curbsnapp_projects_id",
            "No de projet Curbsnapp [required]",
            "[]",
            c_type="string",
            c_struct="list1D",
        )

        new_conf.section = "OPTIONS"
        new_conf.store("act_occup", "Analyser les occupations", "True", c_type="bool")
        new_conf.store("act_rempla", "Analyser le remplacement", "False", c_type="bool")
        new_conf.store("act_prov", "Analyser les provenances", "False", c_type="bool")
        new_conf.store("comp_sect_agg", "Aggréger par secteurs", "True", c_type="bool")
        new_conf.store(
            "handle_restriction",
            "Calculer uniquement les points sur zone non restrainte",
            "True",
            c_type="bool",
        )
        new_conf.store(
            "one_way_agg", "Agréger les rues à sens unique", "False", c_type="bool"
        )
        new_conf.store(
            "act_report",
            "Modéliser le report des stationnements d'une rue sur les rues avoisinante",
            "False",
            c_type="bool",
        )

        new_conf.section = "PARAMÈTRES"
        new_conf.store(
            "gis_bounds",
            "Analyse - Fichier des limites",
            "Path\to\file.json",
            c_type="path",
            p_type="file",
        )
        new_conf.store(
            "gis_bounds_names",
            "Analyse - Header des noms de limites",
            "Nom",
            c_type="string",
        )
        new_conf.store(
            "gis_ana_vis_same_bounds",
            "Carto et Analyse - Même fichier GIS",
            "True",
            c_type="bool",
        )
        new_conf.store(
            "days_bounds",
            "Dates de collecte",
            '[{"from":"2000-01-01", "to":"2099-12-31"}]',
            c_struct="json",
        )
        new_conf.store(
            "hour_bounds",
            "Jours et heures d'analyse",
            '{"lun-dim":[{"from": "0h00", "to":"23h59"}]}',
            c_struct="json",
        )
        new_conf.store("analyse_freq", "Fréquence d'analyse", "1h", c_type="string")
        new_conf.store(
            "allow_veh_on_restrictions",
            "Liste des infractions où l'on autorise le stat.",
            '["Borne fontaine"]',
            c_struct="json",
        )
        new_conf.store(
            "restrictions_to_exclude",
            "Liste des réglementations à exclure",
            '["Défaut"]',
            c_struct="json",
        )
        new_conf.store(
            "plates_origin_path",
            "Provenance - Emplacement des fichiers de plaque",
            "Path\to\folder",
            c_type="path",
            p_type="folder",
        )
        new_conf.store(
            "plates_origin_file_name",
            "Provenance - Squelette nom des fichiers de plaque",
            "Plaques_zone_{}_periode_{}.XLS",
            c_type="string",
        )
        new_conf.store(
            "plates_origin_bounds",
            "Provenance - Fichier géographique des zones de plaque",
            "Path\to\file.json",
            c_type="path",
            p_type="file",
        )
        new_conf.store(
            "plates_origin_bounds_name",
            "Provenance - Header des noms de limites",
            "Nom",
            c_type="string",
        )
        new_conf.store(
            "plates_origin_periods",
            "Provenance - Périodes temporelle",
            "{}",
            c_type="string",
            c_struct="dictND",
        )
        new_conf.store(
            "plates_origin_gis",
            "Provenance - Fichier des limites des code postaux",
            "Path\to\file",
            c_type="path",
            p_type="folder",
        )
        new_conf.store(
            "report_street_name",
            "Report - Nom de la rue à reporter",
            "[]",
            c_type="string",
            c_struct="list1D",
        )
        new_conf.store(
            "vehicule_conf", "Configuration des caméras", "{}", c_struct="json"
        )

        new_conf.section = "OPTIONEL"
        new_conf.store(
            "roads_path",
            "Fichier de géobase personalisé",
            "Default.def",
            c_type="path",
            p_type="file",
        )
        new_conf.store(
            "roads_dbl_path",
            "Fichier de route double personalisé",
            "Default.def",
            c_type="path",
            p_type="file",
        )
        new_conf.store(
            "ignore_agg_seg",
            "Ignorer les segments dans l'aggrégation du coté de rue",
            "[]",
            c_type="int",
            c_struct="list1D",
        )
        new_conf.store(
            "gis_vis_bounds",
            "Carto - Fichier des limites",
            "Path\to\file.json",
            c_type="path",
            p_type="file",
        )
        new_conf.store(
            "gis_vis_bounds_names",
            "Carto - Header des noms de limites",
            "-",
            c_type="string",
        )
        new_conf.store(
            "vis_rotation",
            "Carto - Rotation du Nord (degrés)*",
            "[]",
            c_type="float",
            c_struct="list1D",
        )
        new_conf.store(
            "vis_buffer",
            "Carto - Distance au pourtour (m)*",
            "[]",
            c_type="float",
            c_struct="list1D",
        )
        new_conf.store(
            "veh_size", "Longueur moyenne d'un véhicule", "5.5", c_type="float"
        )
        new_conf.store(
            "compass_rose", "Affichage de la rose des vents", "True", c_type="bool"
        )
        new_conf.store("anotation", "Affichage des annotations", "True", c_type="bool")
        new_conf.store(
            "capa_along_occ",
            "Afficher la capacité avec l'occupation",
            "False",
            c_type="bool",
        )
        new_conf.store(
            "build_leg", "Affichage de la légende dans la carte", "False", c_type="bool"
        )
        new_conf.store(
            "anotation_prov",
            "Provenance - Affichage des annotations",
            "True",
            c_type="bool",
        )
        new_conf.store(
            "regs_zoom_prov",
            "Provenance - Zoom sur des arrondissements",
            "[]",
            c_type="string",
            c_struct="list1D",
        )
        new_conf.store(
            "plot_all_capa",
            "Affichage de toutes les capacitées désagrégées",
            "False",
            c_type="bool",
        )

        # finishing touches
        new_conf.__dict__.pop("section")
        new_conf.sections = new_conf.config.sections()
        new_conf.handles = pandas.DataFrame(new_conf.handles)
        new_conf._handle_potential_copies()
        new_conf.init_config()

        if not os.path.isfile(config_name):
            logger.info(
                "Notice: No default configuration found. Creating new %s",
                str(config_name),
            )
            new_conf.write(config_name)

        return new_conf

    @classmethod
    def from_dict(cls, d: dict):

        # init
        new_conf = cls()

        if d is not None:
            for key, value in d.items():
                setattr(new_conf, key, value)

        new_conf.config = None
        new_conf.handles = []
        new_conf.section = ""
        new_conf.sections = []

        new_conf.init_config()

        return new_conf

    def _handle_potential_copies(self):
        candidates = {
            "gis_ana_vis_same_bounds": {
                "gis_vis_bounds": "gis_bounds",
                "gis_vis_bounds_names": "gis_bounds_names",
            }
        }

        for cand, _ in candidates.items():
            if getattr(self, cand):
                for dependent, keyed_to in candidates[cand].items():
                    value = getattr(self, keyed_to)
                    setattr(self, dependent, value)
                    self._update_handle_df(dependent, value)

    def _update_handle_df(self, key, value):
        handlesdf = self.handles.copy().set_index("attr")
        handlesdf.at[key, "value"] = value
        self.handles = handlesdf.reset_index()

    def store(
        self,
        attr,
        key,
        default,
        c_type="int",
        c_struct="simple",
        k_type="str",
        p_type=None,
    ):
        """_summary_

        Parameters
        ----------
        attr : _type_
            _description_
        key : _type_
            _description_
        default : _type_
            _description_
        c_type : str, optional
            _description_, by default 'int'
        c_struct : str, optional
            _description_, by default 'simple'
        k_type : str, optional
            _description_, by default 'str'
        p_type : _type_, optional
            _description_, by default None

        Returns
        -------
        _type_
            _description_
        """
        value = self.parse(
            key, default, c_type=c_type, c_struct=c_struct, k_type=k_type, p_type=p_type
        )
        self.handles.append(
            {
                "section": self.section,
                "attr": attr,
                "text": key,
                "value": value,
                "c_type": c_type,
                "c_struct": c_struct,
            }
        )
        setattr(self, attr, value)

        return value

    def parse(
        self, key, default, c_type="int", c_struct="simple", k_type="str", p_type=None
    ):
        """Handle configuration file values."""
        if not self.config.has_section(self.section):
            self.config.add_section(self.section)
        if not self.config.has_option(self.section, key):
            self.config.set(self.section, key, default)

        if c_struct == "list1D":
            return list1d(self.config.get(self.section, key), i_type=c_type)
        elif c_struct == "list2D":
            return list2d(self.config.get(self.section, key), i_type=c_type)
        elif c_struct == "mixedList":
            return mixed_list(self.config.get(self.section, key), i_type=c_type)
        elif c_struct == "dictND":
            return nddict(
                self.config.get(self.section, key), i_type=c_type, k_type=k_type
            )
        elif c_struct == "json":
            return json.loads(self.config.get(self.section, key).replace("'", '"'))

        if c_type == "int":
            return self.config.getint(self.section, key)
        elif c_type == "float":
            return self.config.getfloat(self.section, key)
        elif c_type == "bool":
            return self.config.getboolean(self.section, key)
        elif c_type == "path":
            return self.verify_path(self.config.get(self.section, key), p_type)
        else:
            return self.config.get(self.section, key)

    def to_string(self, attr, **kwargs):
        value = getattr(self, attr)

        if self.handles.set_index("attr").at[attr, "c_struct"] == "json":
            return f"{value}"
        elif isinstance(value, (list, tuple)):
            return split_list(value, **kwargs)
        elif isinstance(value, dict):
            return split_dict(value, **kwargs)
        else:
            if self.handles.set_index("attr").at[attr, "c_type"] == "path":
                return f"{path_slashes(value)}"
            return f"{value}"

    def _get_min_indent(self):
        current_min = 0
        for section in self.sections:
            for key, default in self._get_defaults(section, indent=0):
                if len(key) > current_min:
                    current_min = len(key)
        return current_min

    def _get_defaults(self, section, indent=5):
        raw = self.handles[self.handles["section"] == section][
            ["text", "attr"]
        ].to_dict(orient="records")
        return [
            (i["text"], self.to_string(i["attr"], pad_newlines_with=" " * indent))
            for i in raw
        ]

    def write(self, config_name, indent="auto"):
        with open(config_name, "w") as new_file:
            new_file.write(
                "# Fichier de configuration pour la production de rapports d'analyse utilisant les \n"
                "# données d'une collecte LAPI.\n"
                "# \n"
                "# Instructions:\n"
                "#    - Les entêtes de sections doivent être respectées (ie: il n'est pas possible \n"
                "#      de déplacer un élément d'une section à l'autre) \n"
                "#    - Les éléments d'une section peuvent être omis, à l'exception de ceux avec la \n"
                "#      mention '[required]'. Les valeurs par défaut seront \n"
                "#      alors utilisées. \n"
                "#    - Une section entière peut également être omise si aucun de ses éléments n'est \n"
                "#      marqué de la mention '[required]'. \n"
                "# \n"
                "#    TYPES SPÉCIAUX \n"
                "#    - Les listes s'écrivent encadrées de braquettes: '[' et ']' \n"
                "#    - Les éléments ci-dessous constituent des listes: \n"
                "#           + Carto - Rotation du Nord (degré) \n"
                "#           + Carto - Distance au pourtour (m)* \n"
                "# \n"
                "#    - Les dictionnaires s'écrivent encadrés d'accolades: '{' et '}' \n"
                "#    - Les éléments ci-dessous constituent des dictionnaires: \n"
                "#           + AUCUN DICTIONNAIRE À CE JOUR \n"
                "# \n"
                "#    - Les éléments mixtes combinent les caractéristiques des listes et des \n"
                "#     dictionnaires.\n"
                "#    - Certains sont des dictionnaires contenant des listes: \n"
                "#           + Jours et heures d'analyse \n"
                "#    - D'autres sont des listes contenant des dictionnaires: \n"
                "#           + Dates de collecte \n"
                "# \n"
                "#    - Les dictionnaires et les listes peuvent être écrits sur plusieurs lignes pour \n"
                "#      augmenter la lisibilité du fichier, en autant que les lignes additionnelles \n"
                "#      comportent une indentation d'au moins quelques espaces et que les éléments \n"
                "#      de la liste soient séparés par une virgule (,), même lorsque le suivant se \n"
                "#      situe sur une autre ligne.\n"
                "# \n"
                "#    NOTA BENE \n"
                "#    - Les éléments notés par un astérisque (*) s'appliquent par secteurs. \n"
            )
            if indent == "auto":
                indent = self._get_min_indent()
            if not isinstance(indent, int):
                raise TypeError(
                    f"If not 'auto', the keyword 'indent' must be of type 'int', received {indent.__class__}"
                )

            for section in self.sections:
                new_file.write(f"[{section.upper()}]\n")
                for text, default in self._get_defaults(section, indent=indent):
                    new_file.write(f"{text.capitalize():<{indent}} = {default} \n")
                new_file.write("\n")

    def verify_path(self, raw, p_type):
        xform = path_slashes(raw)

        # verify that we have a valid scheme - works for both folder and file scheme
        # will raise an error is invalid
        pathvalidate.validate_filepath(xform, platform="auto")

        # pathvalidate does not differentiate between file and folder, let's
        # see if we got an extension
        if p_type == "folder" and not os.path.splitext(xform)[-1] == "":
            raise ValueError("Folder path should not contain an extension")
        if p_type == "file" and os.path.splitext(xform)[-1] == "":
            raise ValueError("File path should contain an extension")

        return xform

    def init_config(self):
        build_cache(self.work_folder)
        build_results(self.work_folder)
        build_dates(self.days_bounds)
        set_prov_origin(self.plates_origin_gis)
        set_roads(self.roads_path, self.roads_dbl_path, self.curbsnapp_projects_id)
        set_prov_conf(self)
