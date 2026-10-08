"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPA13
Integrantes:
    - Javier Arraiza Arribas
    - Álvaro Bilbao Pardo

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
from pathlib import Path
from typing import Tuple

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
STREET_FILE_NAME = DATA_DIR / "direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME = DATA_DIR / "madrid.graphml"

MAX_SPEEDS = {
    'living_street': '20',
    'residential': '30',
    'primary_link': '40',
    'unclassified': '40',
    'secondary_link': '40',
    'trunk_link': '40',
    'secondary': '50',
    'tertiary': '50',
    'primary': '50',
    'trunk': '50',
    'tertiary_link': '50',
    'busway': '50',
    'motorway_link': '70',
    'motorway': '100'
}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AddressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

def grados_a_float(cadena: str) -> float:
    cadena = cadena.strip()

    ind_grado = cadena.find("°")
    ind_minuto = cadena.find("'")
    ind_segundo = cadena.find("''")

    grados = float(cadena[:ind_grado])
    minutos = float(cadena[ind_grado+1:ind_minuto]) / 60
    segundos = float(cadena[ind_minuto+1:ind_segundo]) / (60*60)

    numero = grados + minutos + segundos

    if cadena[-1] == "S" or cadena[-1] == "W":
        return -numero

    return numero


def carga_callejero() -> pd.DataFrame:
    """
    Carga el callejero de Madrid, lo procesa y devuelve un DataFrame con los datos procesados.
    """

    df = pd.read_csv(STREET_FILE_NAME, delimiter=";",encoding="Windows-1252")[["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]]

    df["LATITUD"] = df["LATITUD"].str.replace("ï¿½", "°", regex=False)
    df["LONGITUD"] = df["LONGITUD"].str.replace("ï¿½", "°", regex=False)

    df["LATITUD"] = df["LATITUD"].apply(grados_a_float)
    df["LONGITUD"] = df["LONGITUD"].apply(grados_a_float)

    return df



def busca_direccion(direccion: str, callejero: pd.DataFrame) -> Tuple[float, float]:
    direccion = direccion.split(", ")
    numero = direccion[1].strip()
    direccion = direccion[0].split(" ")

    opciones = set(callejero["VIA_PAR"].unique())
    parte1 = str(direccion[0])

    if len(direccion) > 2 and (direccion[1] + " " + direccion[2]).upper().strip() in opciones:
        parte2 = str(direccion[1] + " " + direccion[2]).upper().strip()
        parte3 = ""
        for palabra in direccion[3:]:
            parte3 += str(palabra) + " "

    elif direccion[1].upper().strip() not in opciones:
        parte2 = ""
        parte3 = ""
        for palabra in direccion[1:]:
            parte3 += str(palabra) + " "

        df_busqueda = callejero[callejero["VIA_CLASE"] == str(parte1.upper().strip())]
        df_busqueda = df_busqueda[df_busqueda["VIA_NOMBRE"] == str(parte3.upper().strip())]
        df_busqueda = df_busqueda[df_busqueda["NUMERO"] == int(numero.strip())]

        if df_busqueda.empty:
            raise AddressNotFoundError("Dirección no existente")

        return df_busqueda["LATITUD"].iloc[0], df_busqueda["LONGITUD"].iloc[0]

    else:
        parte2 = str(direccion[1]).upper().strip()
        parte3 = ""
        for palabra in direccion[2:]:
            parte3 += str(palabra) + " "

    df_busqueda = callejero[callejero["VIA_CLASE"] == str(parte1.upper().strip())]
    df_busqueda = df_busqueda[df_busqueda["VIA_PAR"] == parte2]
    df_busqueda = df_busqueda[df_busqueda["VIA_NOMBRE"] == str(parte3.upper().strip())]
    df_busqueda = df_busqueda[df_busqueda["NUMERO"] == int(numero.strip())]

    if df_busqueda.empty:
        raise AddressNotFoundError("Dirección no existente")

    return df_busqueda["LATITUD"].iloc[0], df_busqueda["LONGITUD"].iloc[0]


############## Parte 4 ##############

def carga_grafo() -> nx.MultiDiGraph:
    if MAP_FILE_NAME.exists():
        try:
            dibujo = ox.load_graphml(filepath=MAP_FILE_NAME)
            return dibujo
        except Exception:
            raise ServiceNotAvailableError("No se pudo cargar el archivo local.")

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        dibujo = ox.graph_from_place(PLACE_NAME, network_type="drive")
        ox.save_graphml(dibujo, filepath=MAP_FILE_NAME)
        return dibujo
    except Exception:
        raise ServiceNotAvailableError("No se pudo descargar el grafo desde OSM.")


def procesa_grafo(multidigrafo: nx.MultiDiGraph) -> nx.DiGraph:
    grafo_simple = ox.convert.to_digraph(multidigrafo)
    grafo_simple.remove_edges_from(nx.selfloop_edges(grafo_simple))
    return grafo_simple
