import operator
from typing import List,Dict
import itertools as itools
from model import Eleccion
def dhondt(votos:List[int], escanos:int):
    """
    Este método implementa el método D'Hondt para la asignación de escaños en la representación proporcional por lista de partido.

    Parámetros:
    votos (List[int]): Una lista de enteros que representan la cantidad de votos para cada partido.
    escanos (int): Un entero que representa el total de escaños a asignar.

    Retorna:
    List[int]: Una lista de enteros que representan la cantidad de escaños asignados a cada partido.
    """
    # Ordenamos los votos de mayor a menor
    _votos = votos.copy()

    #TODO: vi una optimizacion que deja afuera de entrada a los que obtuvieron 
    # menos de X cantidad de votos en relacion a la cantidad total de votos
    
    # Inicializamos la lista de escaños asignados a cada partido
    escanos_asignados = [0] * len(votos)

    # Asignamos los escaños
    while sum(escanos_asignados) < escanos:
        # Buscamos el partido con más votos
        indice = _votos.index(max(_votos))
        
        # Asignamos un escaño a ese partido
        escanos_asignados[indice] += 1
        
        # Actualizamos Votos/Indice
        _votos = [votos[i]/(1+escanos_asignados[i]) for i in range(len(_votos))]

    # Devolvemos la lista de escaños asignados a cada partido
    return escanos_asignados


def calcular_votos_por_lista(eleccion:Eleccion):
    
    total_votos = []
    votos = sorted(eleccion.votos, key=operator.attrgetter('lista'))
    groups = itools.groupby(votos, key=operator.attrgetter('lista'))
    for lista, group in groups:
        group = list(group)
        total_votos.append({'lista':lista,
                            'lista_id':lista.id,
                            'votos':sum(v.votos for v in group)})
    return total_votos

def calculo_escanos(lista_votos:List[Dict], escanos:int):

    lista_votos = sorted(lista_votos, key=operator.itemgetter('votos'), reverse=True)
    resultados = dhondt([v['votos'] for v in lista_votos], escanos)

    for idx, lv in enumerate(lista_votos):
        lv['escanos'] = resultados[idx]
    return lista_votos
