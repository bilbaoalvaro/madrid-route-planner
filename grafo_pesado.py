"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPA13
Integrantes:
    - Javier Arraiza Arribas
    - Álvaro Bilbao Pardo
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq  # Priority queue for Dijkstra
from itertools import count

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G: Union[nx.Graph, nx.DiGraph],
             peso: Union[Callable[[nx.Graph, object, object], float],
                         Callable[[nx.DiGraph, object, object], float]],
             origen: object) -> Dict[object, object]:
    """Return the predecessor tree of shortest paths from ``origen``.

    ``peso`` must return a non-negative edge weight. A heap-based priority
    queue avoids repeatedly scanning a Python list for its minimum element.
    """
    if origen not in G:
        raise ValueError("El vértice de origen no pertenece al grafo.")

    distancias = {v: float("inf") for v in G.nodes()}
    padre = {v: None for v in G.nodes()}
    distancias[origen] = 0.0

    contador = count()  # Avoid comparing node labels when distances tie.
    cola = [(0.0, next(contador), origen)]

    while cola:
        distancia_v, _, v = heapq.heappop(cola)
        if distancia_v != distancias[v]:
            continue  # A better route to this vertex was queued later.

        for vecino in G.neighbors(v):
            peso_arista = float(peso(G, v, vecino))
            if peso_arista < 0:
                raise ValueError("Dijkstra requiere pesos de arista no negativos.")

            nueva_distancia = distancia_v + peso_arista
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                padre[vecino] = v
                heapq.heappush(cola, (nueva_distancia, next(contador), vecino))

    return padre
def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    # Ejecutamos Dijkstra para obtener el diccionario de padres
    padre = dijkstra(G, peso, origen)

    # Si el destino no es alcanzable
    if padre[destino] is None and destino != origen:
        return []

    # Reconstrucción del camino hacia atrás
    camino = [destino]
    actual = destino

    # Mientras no lleguemos al origen
    while actual != origen:
        actual = padre[actual]
        camino.append(actual)

    # Invertimos el camino
    camino.reverse()

    return camino


def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    padre = {}
    coste = {}
    seleccionado = {}

    # Inicialización
    for v in G.nodes():
        padre[v] = None
        coste[v] = float("inf")
        seleccionado[v] = False

    # Elegimos v0 SIN break: cogemos el PRIMER nodo recorriendo y usando un flag
    primer_nodo_asignado = False
    v0 = None

    for v in G.nodes():
        if not primer_nodo_asignado:
            v0 = v
            primer_nodo_asignado = True

    coste[v0] = 0

    # Bucle repetido |V| veces (como en el pseudocódigo)
    for _ in G.nodes():

        # Elegimos v_min SIN continue, usando un if
        v_min = None
        mejor_coste = float("inf")

        for v in G.nodes():
            if not seleccionado[v]:
                if coste[v] < mejor_coste:
                    mejor_coste = coste[v]
                    v_min = v

        # Marcamos v_min como seleccionado
        seleccionado[v_min] = True

        # Actualizamos vecinos
        for x in G.neighbors(v_min):
            if not seleccionado[x]:
                peso_vx = peso(G, v_min, x)
                if peso_vx < coste[x]:
                    coste[x] = peso_vx
                    padre[x] = v_min

    return padre


                

def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    # 1. Crear lista de aristas ordenada por peso
    aristas = []
    for u, v in G.edges():
        w = peso(G, u, v)
        aristas.append((w, u, v))

    # Ordenamos de menor a mayor peso
    # (sin lambda ni cosas raras: recorremos y ordenamos)
    for i in range(len(aristas)):
        for j in range(i + 1, len(aristas)):
            if aristas[j][0] < aristas[i][0]:
                aristas[i], aristas[j] = aristas[j], aristas[i]

    # 2. Inicializar componentes: cada nodo tiene su conjunto
    componente = {}
    for v in G.nodes():
        componente[v] = {v}

    # 3. Árbol abarcador mínimo
    T = []

    # Recorremos las aristas en orden creciente
    for w, u, v in aristas:

        # Si están en componentes diferentes, no forma ciclo
        if componente[u] != componente[v]:

            # Añadimos la arista
            T.append((u, v))

            # Unimos ambos conjuntos
            nuevo = componente[u].union(componente[v])

            # Actualizamos los componentes
            for x in nuevo:
                componente[x] = nuevo

    # Devolvemos la lista de aristas del árbol
    return T
