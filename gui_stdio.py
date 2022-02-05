# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gr�fica de usuario (GUI) con entrada y salida est�ndar para el int�rprete PAW-like
# Copyright (C) 2010, 2018-2022 Jos� Manuel Ferrer Ortiz
#
# *****************************************************************************
# *                                                                           *
# *  This program is free software; you can redistribute it and/or modify it  *
# *  under the terms of the GNU General Public License version 2, as          *
# *  published by the Free Software Foundation.                               *
# *                                                                           *
# *  This program is distributed in the hope that it will be useful, but      *
# *  WITHOUT ANY WARRANTY; without even the implied warranty of               *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU         *
# *  General Public License version 2 for more details.                       *
# *                                                                           *
# *  You should have received a copy of the GNU General Public License        *
# *  version 2 along with this program; if not, write to the Free Software    *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA  *
# *                                                                           *
# *****************************************************************************

import sys


from prn_func import *


traza = False  # Si queremos una traza del funcionamiento del m�dulo

# Variables que ajusta el int�rprete
cambia_brillo    = None      # Car�cter que si se encuentra en una cadena, dar�a o quitar�a brillo al color de tinta de la letra
cambia_flash     = None      # Car�cter que si se encuentra en una cadena, pondr�a o quitar�a efecto flash a la letra
cambia_papel     = None      # Car�cter que si se encuentra en una cadena, cambiar�a el color de papel/fondo de la letra
cambia_tinta     = None      # Car�cter que si se encuentra en una cadena, cambiar�a el color de tinta de la letra
centrar_graficos = []        # Si se deben centrar los gr�ficos al dibujarlos
historial        = []        # Historial de �rdenes del jugador
juego_alto       = None      # Car�cter que si se encuentra en una cadena, pasar�a al juego de caracteres alto
juego_bajo       = None      # Car�cter que si se encuentra en una cadena, pasar�a al juego de caracteres bajo
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con cambia_*
todo_mayusculas  = False     # Si la entrada del jugador ser� incondicionalmente en may�sculas
ruta_graficos    = ''

cursores    = [[0, 0]] * 2  # Posici�n relativa del cursor de cada subventana
limite      = [53, 25]      # Ancho y alto m�ximos absolutos de cada subventana
num_subvens = 8             # DAAD tiene 8 subventanas

# Variables propias de este m�dulo de entrada y salida est�ndar
elegida    = 1      # Subventana elegida (la predeterminada es la 1)
nuevaLinea = False  # Si el siguiente texto a imprimir deber�a ir en una nueva l�nea


# Funciones que no hacen nada al usar entrada y salida est�ndar de puro texto

def borra_orden ():
  """Borra la entrada realimentada en pantalla en la subventana de entrada si es subventana propia, y recupera la subventana anterior"""
  pass

def cambia_color_borde (color):
  """Cambia el color de fondo al borrar de la subventana actual por el de c�digo dado"""
  pass

def cambia_color_papel (color):
  """Cambia el color de papel/fondo al escribir la subventana actual por el dado"""
  pass

def cambia_color_tinta (color):
  """Cambia el color de tinta al escribir la subventana actual por el dado"""
  pass

def cambia_cursor (cadenaCursor):
  """Cambia el car�cter que marca la posici�n del cursor en la entrada del jugador"""
  pass

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, seg�n el condacto INPUT"""
  pass

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de impresi�n elegida"""
  pass

def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gr�fico en la posici�n del cursor"""
  pass

def espera_tecla (tiempo = 0):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  pass

def guarda_cursor ():
  """Guarda la posici�n del cursor de la subventana elegida """
  pass

def pos_subventana (columna, fila):
  """Cambia la posici�n de origen de la subventana de impresi�n elegida"""
  pass

def prepara_topes (columnas, filas):
  """Inicializa los topes al n�mero de columnas y filas dado"""
  pass

def redimensiona_ventana (evento = None):
  """Maneja eventos en relaci�n a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  pass

def reinicia_subventanas ():
  """Ajusta todas las subventanas de impresi�n a sus valores por defecto"""
  pass


# Funciones que implementan la entrada y salida por entrada y salida est�ndar de puro texto

def abre_ventana (traza, factorEscala, bbdd):
  """Abre la ventana gr�fica de la aplicaci�n"""
  global cambia_brillo, cambia_flash, cambia_papel, cambia_tinta, juego_alto, juego_bajo
  if juego_alto == 48:  # La @ de SWAN
    juego_alto = '@'
    juego_bajo = '@'
  elif juego_alto == 14:  # La � de las primeras versiones de DAAD
    juego_alto = '\x0e'
    juego_bajo = '\x0f'
  if cambia_brillo:
    cambia_brillo = chr (cambia_brillo)
    cambia_flash  = chr (cambia_flash)
    cambia_papel  = chr (cambia_papel)
    cambia_tinta  = chr (cambia_tinta)

def borra_pantalla (desdeCursor = False, noRedibujar = False):
  """Limpia la subventana de impresi�n"""
  marcaNuevaLinea()

def borra_todo ():
  """Limpia la pantalla completa"""
  marcaNuevaLinea()

def carga_cursor ():
  """Carga la posici�n del cursor guardada de la subventana elegida """
  marcaNuevaLinea()

def da_tecla_pulsada ():
  """Devuelve el par de c�digos ASCII de la tecla m�s recientemente pulsada si hay alguna tecla pulsada, o None si no hay ninguna pulsada"""
  return None

def elige_parte (partes, graficos):
  """Obtiene del jugador el modo gr�fico a usar y a qu� parte jugar, y devuelve el nombre de la base de datos elegida"""
  if len (partes) == 1:
    return partes.popitem()[1]
  numerosPartes = tuple (partes.keys())
  numParteMenor = min (numerosPartes)
  numParteMayor = max (numerosPartes)
  entrada = None
  while entrada not in numerosPartes:
    imprime_cadena ('�Qu� parte quieres cargar? (%d%s%d) ' % (numParteMenor, '/' if (numParteMayor - numParteMenor == 1) else '-', numParteMayor))
    try:
      entrada = int (raw_input())
    except (KeyboardInterrupt, ValueError) as e:
      if type (e).__name__ != 'ValueError':
        raise
      entrada = None
  return partes[entrada]

def elige_subventana (numero):
  """Selecciona una de las subventanas"""
  global elegida, nuevaLinea
  if numero != elegida:
    elegida    = numero
    nuevaLinea = True

def hay_grafico (numero):
  """Devuelve si existe el gr�fico de n�mero dado"""
  return False

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la salida de error est�ndar)"""
  global advertencia_banderas
  try:
    advertencia_banderas
  except:
    advertencia_banderas = True
    prn ('Impresi�n de banderas como texto (en stderr) no implementada', file = sys.stderr)

def imprime_cadena (cadena, scroll = True, redibujar = True):
  """Imprime una cadena en la posici�n del cursor (dentro de la subventana)"""
  global nuevaLinea
  if nuevaLinea:
    prn()
  prn (limpiaCadena (cadena), end = '')
  nuevaLinea = False

def lee_cadena (prompt, inicio, timeout, espaciar = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentaci�n al jugador

El par�metro prompt, es el mensaje de prompt
El par�metro inicio es la entrada a medias anterior
El par�metro timeout es una lista con el tiempo muerto, en segundos
El par�metro espaciar permite elegir si se debe dejar una l�nea en blanco tras el �ltimo texto"""
  entrada = None
  while not entrada:
    if prompt:
      imprime_cadena (prompt)
    entrada = raw_input()
  return entrada

def marcaNuevaLinea ():
  """La pr�xima vez que se escriba algo, hacerlo en l�nea nueva"""
  global nuevaLinea
  nuevaLinea = True

def mueve_cursor (columna, fila = None):
  """Cambia de posici�n el cursor de la subventana elegida"""
  marcaNuevaLinea()


# Funciones auxiliares que s�lo se usan en este m�dulo

def limpiaCadena (cadena):
  if not cambia_brillo and not cambia_flash and not cambia_papel and not cambia_tinta and not juego_alto and not juego_bajo:
    return cadena
  limpia = ''
  c = 0
  while c < len (cadena):
    if cadena[c] in (cambia_brillo, cambia_flash, cambia_papel, cambia_tinta, juego_alto, juego_bajo):
      if cadena[c] not in (juego_alto, juego_bajo):
        c += 1  # Descartamos tambi�n el siguiente byte, que indica el color o si se activa o no
    else:
      limpia += cadena[c]
    c += 1
  return limpia
