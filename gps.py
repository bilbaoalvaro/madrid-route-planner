import networkx as nx
import osmnx as ox
import folium
import webbrowser
from pathlib import Path

from callejero import (
    carga_callejero,
    busca_direccion,
    carga_grafo,
    procesa_grafo,
    MAX_SPEEDS,
    ServiceNotAvailableError,
)
from grafo_pesado import camino_minimo


def obtener_velocidad(grafo, nodo_actual, nodo_vecino):
    datos_arista = grafo[nodo_actual][nodo_vecino]

    if "maxspeed" in datos_arista:
        try:
            return float(datos_arista["maxspeed"])
        except:
            nada = 0

    if "highway" in datos_arista:
        tipo_via = datos_arista["highway"]
        if isinstance(tipo_via, list):
            tipo_via = tipo_via[0]
        if tipo_via in MAX_SPEEDS:
            return float(MAX_SPEEDS[tipo_via])

    return 50.0


def peso_distancia(grafo, nodo_actual, nodo_vecino):
    return grafo[nodo_actual][nodo_vecino]["length"]


def peso_tiempo(grafo, nodo_actual, nodo_vecino):
    datos_arista = grafo[nodo_actual][nodo_vecino]
    distancia = datos_arista["length"]
    velocidad_kmh = obtener_velocidad(grafo, nodo_actual, nodo_vecino)
    velocidad_ms = velocidad_kmh * 1000.0 / 3600.0
    return distancia / velocidad_ms


def peso_tiempo_penalizado(grafo, nodo_actual, nodo_vecino):
    # Heuristic: add a fixed 24-second penalty per graph edge. This is not
    # based on live traffic or on a verified inventory of traffic lights.
    return peso_tiempo(grafo, nodo_actual, nodo_vecino) + 24.0


def elegir_modo_ruta():
    modo = "0"
    while modo not in ["1", "2", "3"]:
        print("\nElige modo de ruta:")
        print("1 - Ruta más corta (distancia)")
        print("2 - Ruta más rápida (tiempo)")
        print("3 - Ruta rápida con penalización fija por tramo (heurística)")
        modo = input("Opción (1/2/3): ").strip()
    return modo


def generar_instrucciones(grafo, camino):
    instrucciones = []
    if len(camino) < 2:
        return instrucciones

    nodo_anterior = camino[0]
    nodo_actual = camino[1]
    datos = grafo[nodo_anterior][nodo_actual]
    nombre_calle = datos.get("name", "vía sin nombre")
    if isinstance(nombre_calle, list):
        nombre_calle = nombre_calle[0]
    distancia_acum = datos["length"]

    indice = 1
    while indice < len(camino) - 1:
        nodo_anterior = camino[indice]
        nodo_actual = camino[indice + 1]

        datos_tramo = grafo[nodo_anterior][nodo_actual]
        nombre_sig = datos_tramo.get("name", "vía sin nombre")
        if isinstance(nombre_sig, list):
            nombre_sig = nombre_sig[0]

        if nombre_sig == nombre_calle:
            distancia_acum = distancia_acum + datos_tramo["length"]
        else:
            instrucciones.append("Sigue por " + nombre_calle + " durante " + str(int(distancia_acum)) + " metros.")
            nombre_calle = nombre_sig
            distancia_acum = datos_tramo["length"]

        indice = indice + 1

    instrucciones.append("Sigue por " + nombre_calle + " durante " + str(int(distancia_acum)) + " metros.")
    return instrucciones


def dibujar_ruta_folium(grafo, camino, nombre_archivo="results/route.html"):
    puntos = []
    indice = 0
    while indice < len(camino):
        nodo = camino[indice]
        puntos.append((grafo.nodes[nodo]["y"], grafo.nodes[nodo]["x"]))
        indice = indice + 1

    latitud0, longitud0 = puntos[0]
    mapa = folium.Map(location=[latitud0, longitud0], zoom_start=14, tiles="CartoDB Positron")

    folium.PolyLine(puntos, color="red", weight=6, opacity=0.8).add_to(mapa)

    folium.Marker(puntos[0], tooltip="Origen", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(puntos[-1], tooltip="Destino", icon=folium.Icon(color="blue")).add_to(mapa)

    salida = Path(nombre_archivo)
    if not salida.is_absolute():
        salida = Path(__file__).resolve().parent / salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(salida))

    ruta_abs = salida.resolve()
    print("\nMapa generado en:", ruta_abs)
    print("Abriendo el mapa en el navegador…")
    webbrowser.open(ruta_abs.as_uri())


if __name__ == "__main__":

    try:
        callejero = carga_callejero()
    except FileNotFoundError:
        print("No se encuentra data/direcciones.csv. Ejecuta primero: python download_addresses.py")
        raise SystemExit(1)

    try:
        multidigrafo = carga_grafo()
        grafo = procesa_grafo(multidigrafo)
    except ServiceNotAvailableError as exc:
        print(f"No se pudo cargar el grafo de calles: {exc}")
        print("Comprueba la conexión a internet y vuelve a intentarlo.")
        raise SystemExit(1)

    origen_texto = "inicio"
    destino_texto = "inicio"

    while origen_texto != "" and destino_texto != "":
        print("\n<<<<<< NUEVA BÚSQUEDA >>>>>>")

        origen_texto = input("Introduce el origen (enter para salir): ").strip()

        if origen_texto != "":
            destino_texto = input("Introduce el destino (enter para salir): ").strip()

        if origen_texto != "" and destino_texto != "":
            try:
                latitud_origen, longitud_origen = busca_direccion(origen_texto, callejero)
                latitud_destino, longitud_destino = busca_direccion(destino_texto, callejero)
            except Exception:
                print("Dirección no encontrada. Intenta otra vez.")
                origen_texto = "inicio"
                destino_texto = "inicio"
            else:
                nodo_origen = ox.distance.nearest_nodes(grafo, longitud_origen, latitud_origen)
                nodo_destino = ox.distance.nearest_nodes(grafo, longitud_destino, latitud_destino)

                print("Nodo origen:", nodo_origen)
                print("Nodo destino:", nodo_destino)

                modo = elegir_modo_ruta()

                if modo == "1":
                    f_peso = peso_distancia
                elif modo == "2":
                    f_peso = peso_tiempo
                else:
                    f_peso = peso_tiempo_penalizado

                camino = camino_minimo(grafo, f_peso, nodo_origen, nodo_destino)

                if len(camino) == 0:
                    print("No existe un camino disponible para esta ruta.")
                else:
                    print("\nCamino encontrado:")
                    print(camino)

                    instrucciones = generar_instrucciones(grafo, camino)
                    print("\n <<<<< INSTRUCCIONES >>>>>")
                    indice = 0
                    while indice < len(instrucciones):
                        print(instrucciones[indice])
                        indice = indice + 1

                    print("\nA continuación se mostrará la ruta:")
                    dibujar_ruta_folium(grafo, camino, "results/route.html")

    print("\nEl programa ha acabado.")
