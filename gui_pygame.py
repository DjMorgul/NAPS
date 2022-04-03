# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gr�fica de usuario (GUI) con PyGame para el int�rprete PAW-like
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

from os       import path
from prn_func import *
from sys      import version_info

import math    # Para ceil
import string  # Para algunas constantes

import graficos_daad
import pygame


traza = False  # Si queremos una traza del funcionamiento del m�dulo
if traza:
  from prn_func import prn

izquierda  = '���������������� !"�$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]�_`abcdefghijklmnopqrstuvwxyz{|}~\n'
noEnFuente = {'�': 'c', u'\u2192': '>', u'\u2190': '<'}  # Tabla de conversi�n de caracteres que no est�n en la fuente

der = []
for i in range (len (izquierda)):
  der.append (chr (i))
derecha = ''.join (der)

iso8859_15_a_fuente = maketrans (izquierda, derecha)

# Pares de c�digos ASCII para teclas pulsadas
teclas_ascii = {pygame.K_DOWN: (0, 80), pygame.K_LEFT: (0, 75), pygame.K_RIGHT: (0, 77), pygame.K_UP: (0, 72)}
# Teclas imprimibles y de edici�n, con c�digo < 256
teclas_edicion = string.printable + string.punctuation + '�纡\b\x1b'
# Teclas de edici�n con c�digo >= 256
# 314 es Alt Gr + ` (es decir, '[' en el teclado espa�ol)
teclas_mas_256 = (314, pygame.K_DELETE, pygame.K_DOWN, pygame.K_END, pygame.K_HOME, pygame.K_KP_ENTER, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
# Teclas imprimibles del teclado num�rico
teclas_kp = {pygame.K_KP0: '0', pygame.K_KP1: '1', pygame.K_KP2: '2', pygame.K_KP3: '3', pygame.K_KP4: '4', pygame.K_KP5: '5', pygame.K_KP6: '6', pygame.K_KP7: '7', pygame.K_KP8: '8', pygame.K_KP9: '9', pygame.K_KP_DIVIDE: '/', pygame.K_KP_MULTIPLY: '*', pygame.K_KP_MINUS: '-', pygame.K_KP_PLUS: '+', pygame.K_KP_PERIOD: '.'}
# Teclas que al pulsar Alt Gr son otra
teclas_alt_gr = {'�': '\\', '1': '|', '2': '@', '4': '~', '7': '{', '8': '[', '9': ']', '0': '}', '+': ']', '�': '~', '�': '}', 'z': '�', 'x': '�'}
# Teclas que al pulsar Shift son otra
teclas_shift = {'�': '�', '1': '!', '2': '"', '4': '$', '5': '%', '6': '&', '7': '/', '8': '(', '9': ')', '0': '=', "'": '?', '�': '�', '+': '*', '�': '�', '�': '�', '<': '>', ',': ';', '.': ':', '-': '_'}


pygame.init()  # Necesario para trabajar con la librer�a PyGame
pygame.event.set_blocked (pygame.MOUSEMOTION)  # No atenderemos los movimientos del rat�n
escalada     = None
factorEscala = 1  # Factor de escalado, de 1 a 3
ventana      = None

fuente = pygame.image.load (path.dirname (path.realpath (__file__)) + path.sep + 'fuente.png')  # Fuente tipogr�fica
fuente.set_palette (((255, 255, 255), (0, 0, 0)))

cad_cursor = '_'
chr_cursor = pygame.Surface ((6, 8))  # Car�cter con transparencia, para marcar posici�n de input

# Variables que ajusta el int�rprete
brillo           = 0         # Sin brillo por defecto
cambia_brillo    = None      # Car�cter que si se encuentra en una cadena, dar� o quitar� brillo al color de tinta de la letra
cambia_flash     = None      # Car�cter que si se encuentra en una cadena, pondr�a o quitar�a efecto flash a la letra
cambia_inversa   = None      # Car�cter que si se encuentra en una cadena, invertir� o no el papel/fondo de la letra
cambia_papel     = None      # Car�cter que si se encuentra en una cadena, cambiar� el color de papel/fondo de la letra
cambia_tinta     = None      # Car�cter que si se encuentra en una cadena, cambiar� el color de tinta de la letra
centrar_graficos = []        # Si se deben centrar los gr�ficos al dibujarlos
juego_alto       = None      # Car�cter que si se encuentra en una cadena, pasar� al juego de caracteres alto
juego_bajo       = None      # Car�cter que si se encuentra en una cadena, pasar� al juego de caracteres bajo
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con cambia_*
partir_espacio   = True      # Si se deben partir las l�neas en el �ltimo espacio
ruta_graficos    = ''        # Carpeta de donde cargar los gr�ficos a dibujar
tabulador        = None      # Car�cter que si se encuentra en una cadena, pondr� espacios hasta mitad o final de l�nea
todo_mayusculas  = False     # Si la entrada del jugador ser� incondicionalmente en may�sculas
txt_mas          = '(m�s)'   # Cadena a mostrar cuando no cabe m�s texto y se espera a que el jugador pulse una tecla

banderas_antes  = None   # Valor anterior de las banderas
banderas_viejas = None   # Banderas que antes cambiaron de valor
graficos        = {}     # Gr�ficos ya cargados
historial       = []     # Historial de �rdenes del jugador
historial_temp  = []     # Orden a medias, guardada al acceder al historial
teclas_pulsadas = []     # Lista de teclas actualmente pulsadas
tras_portada    = False  # Esperar pulsaci�n de tecla antes de borrar la portada

# Todas las coordenadas son columna, fila
num_subvens = 8                # DAAD tiene 8 subventanas
elegida     = 1                # Subventana elegida (la predeterminada es la 1)
opcs_input  = 2                # Opciones para la entrada del usuario (TODO: revisar valor por defecto)
subv_input  = 0                # Subventana para entrada del usuario (0 indica la actual)
limite      = [53, 25]         # Ancho y alto m�ximos absolutos de cada subventana
color_subv  = [[7, 0, 0]] * 8  # Color de tinta, papel y borde de cada subventana
cursores    = [[0, 0]] * 8     # Posici�n relativa del cursor de cada subventana
cursores_at = [(0, 0)] * 8     # Posici�n relativa del cursor guardado mediante SAVEAT de cada subventana
pos_gfx_sub = [[0, 0]] * 8     # Posici�n guardada de dibujo de gr�ficos flotantes en cada subventana
subventanas = [[0, 0]] * 8     # Posici�n absoluta de cada subventana (de su esquina superior izquierda)
topes       = [[53, 25]] * 8   # Topes relativos de cada subventana de impresi�n
topes_gfx   = [53, 25]         # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0
resolucion  = (320, 200)       # Resoluci�n gr�fica de salida, sin escalar


def abre_ventana (traza, escalar, bbdd):
  """Abre la ventana gr�fica de la aplicaci�n"""
  global escalada, factorEscala, resolucion, ventana
  copia = None
  if pygame.display.get_caption():  # Ya hab�a sido inicializada antes
    copia = ventana.copy()
  else:
    factorEscala = escalar
  pygame.display.set_caption ('NAPS - ' + bbdd)
  if traza and 'NUM_BANDERAS' in globals():
    if NUM_BANDERAS > 50:
      resolucion = (780, 200)  # Ventana juego + banderas
    else:
      resolucion = (400, 200)  # Ventana juego + banderas
  else:  # Ventana juego s�lo
    if limite[0] < 53:
      resolucion = (limite[0] * 6, limite[1] * 8)
  if factorEscala > 1:
    escalada = pygame.display.set_mode ((resolucion[0] * factorEscala, resolucion[1] * factorEscala), pygame.RESIZABLE)
    ventana  = pygame.Surface (resolucion)
  else:
    ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
  if copia:  # Recuperamos contenido anterior
    ventana.blit (copia, (0, 0) + resolucion)
    actualizaVentana()
  return
  # FIXME: si no funciona el modo gr�fico, deja X Window mal permanentemente, a�n al cerrarse el int�rprete
  if escalar == 0:  # Pantalla completa
    ventana = pygame.display.set_mode ((640, 400), ventana.get_flags() ^ pygame.FULLSCREEN)

def actualizaVentana ():
  if factorEscala > 1:
    pygame.transform.scale (ventana, (resolucion[0] * factorEscala, resolucion[1] * factorEscala), escalada)
  pygame.display.flip()

def redimensiona_ventana (evento = None, copiaVentana = None):
  """Maneja eventos en relaci�n a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  global escalada, factorEscala, ventana
  if not evento:
    if pygame.event.peek (pygame.VIDEORESIZE):  # Si ha ocurrido un evento de redimensi�n de ventana
      evento = pygame.event.get (pygame.VIDEORESIZE)[0]
    elif pygame.event.peek (pygame.QUIT):  # Si ha ocurrido un evento de cierre de ventana
      evento = pygame.event.get (pygame.QUIT)[0]
    else:
      return
  if evento.type == pygame.QUIT:
    import sys
    sys.exit()
  if evento.type != pygame.VIDEORESIZE:
    return
  if evento.w < resolucion[0] or evento.h < resolucion[1] or \
      (factorEscala == 2 and (evento.w < (resolucion[0] * 2) or evento.h < (resolucion[1] * 2))):
    factorEscala = 1
    superficie   = ventana.copy()
    ventana      = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    while ventana.get_size() != resolucion:
      ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    ventana.blit (superficie, (0, 0) + resolucion)
  else:
    if evento.w >= (resolucion[0] * 3) or evento.h >= (resolucion[1] * 3) or \
        (factorEscala == 2 and (evento.w > (resolucion[0] * 2) or evento.h > (resolucion[1] * 2))):
      factorEscala = 3
    elif evento.w > resolucion[0] or evento.h > resolucion[1] or \
        (factorEscala == 3 and (evento.w < (resolucion[0] * 3) or evento.h < (resolucion[1] * 3))):
      factorEscala = 2
    if copiaVentana:
      superficie = copiaVentana.copy()
    else:
      superficie = ventana.copy()
    ventana    = superficie
    resVentana = (resolucion[0] * factorEscala, resolucion[1] * factorEscala)
    escalada   = pygame.display.set_mode (resVentana, pygame.RESIZABLE)
    while escalada.get_size() != resVentana:
      escalada = pygame.display.set_mode (resVentana, pygame.RESIZABLE)
    pygame.transform.scale (ventana, resVentana, escalada)
  pygame.display.flip()


def borra_orden ():
  """Borra la entrada realimentada en pantalla en la subventana de entrada si es subventana propia, y recupera la subventana anterior"""
  if not subv_input:
    return
  global elegida
  # Guardamos la subventana que estaba elegida justo antes, y cambiamos a la de entrada
  subvAntes = elegida
  elegida   = subv_input
  borra_pantalla()
  elegida = subvAntes  # Recuperamos la subventana elegida

def borra_pantalla (desdeCursor = False, noRedibujar = False):
  """Limpia la subventana de impresi�n"""
  global tras_portada
  if tras_portada or (frase_guardada and texto_nuevo):
    espera_tecla()  # Esperamos pulsaci�n de tecla si se hab�an entrado varias frases y se hab�a mostrado texto nuevo
    tras_portada = False
    del texto_nuevo[:]
  if not desdeCursor:
    cursores[elegida] = [0, 0]
  colorBorde = daColorBorde()
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if elegida == 0:
    tope = topes_gfx
  inicioX = (subventana[0] + cursor[0]) * 6  # Esquina superior izquierda X
  inicioY = (subventana[1] + cursor[1]) * 8  # Esquina superior izquierda Y
  if desdeCursor:
    ancho = (tope[0] * 6) - inicioX  # Anchura del rect�ngulo a borrar
    alto  = 8                        # Altura del rect�ngulo a borrar, luego se borrar� el resto si es m�s de una l�nea
  else:
    ancho = int (math.ceil ((tope[0] * 6) / 8.)) * 8  # Anchura del rect�ngulo a borrar
    alto  = tope[1] * 8                               # Altura del rect�ngulo a borrar
  ventana.fill (colorBorde, (inicioX, inicioY, ancho, alto))
  if desdeCursor and tope[1] - cursor[1] > 0:  # Borrado de las siguientes l�neas
    inicioX = subventana[0] * 6                    # Esquina superior izquierda X
    inicioY = (subventana[1] + cursor[1] + 1) * 8  # Esquina superior izquierda Y
    ancho   = tope[0] * 6                          # Anchura del rect�ngulo a borrar
    alto    = (tope[1] - cursor[1] - 1) * 8        # Altura del rect�ngulo a borrar
    ventana.fill (colorBorde, (inicioX, inicioY, ancho, alto))
  if not desdeCursor and not noRedibujar:
    actualizaVentana()
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope, 'limpiada y cursor en', cursores[elegida])

def borra_todo ():
  """Limpia la pantalla completa"""
  colorBorde = daColorBorde()
  ventana.fill (colorBorde, (0, 0, 320, 200))
  actualizaVentana()

def cambia_color_borde (color):
  """Cambia el color de fondo al borrar de la subventana actual por el de c�digo dado"""
  if traza:
    prn ('Color de borde cambiado a', color)
  color_subv[elegida][2] = color % len (paleta[0])

def cambia_color_papel (color):
  """Cambia el color de papel/fondo al escribir la subventana actual por el dado"""
  if traza:
    prn ('Color de papel cambiado a', color)
  color_subv[elegida][1] = color % len (paleta[0])

def cambia_color_tinta (color):
  """Cambia el color de tinta al escribir la subventana actual por el dado"""
  if traza:
    prn ('Color de tinta cambiado a', color)
  color_subv[elegida][0] = color % len (paleta[0])

def cambia_cursor (cadenaCursor):
  """Cambia el car�cter que marca la posici�n del cursor en la entrada del jugador"""
  global cad_cursor
  cad_cursor = cadenaCursor

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, seg�n el condacto INPUT"""
  global subv_input, opcs_input
  subv_input = stream
  opcs_input = opciones

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de impresi�n elegida"""
  if not columna:
    columna = limite[0]
  if not fila:
    fila    = limite[1]
  topes[elegida] = [min (columna, limite[0] - subventanas[elegida][0]),
                    min (fila,    limite[1] - subventanas[elegida][1])]
  if traza:
    prn ('Subventana', elegida, 'en', subventanas[elegida],
         'con topes puestos a', topes[elegida], 'y cursor en',
         cursores[elegida])

def da_tecla_pulsada ():
  """Devuelve el par de c�digos ASCII de la tecla m�s recientemente pulsada si hay alguna tecla pulsada, o None si no hay ninguna pulsada"""
  if pygame.event.peek ((pygame.KEYDOWN, pygame.KEYUP)):
    for evento in pygame.event.get ((pygame.KEYDOWN, pygame.KEYUP)):
      if evento.type == pygame.KEYDOWN:
        if evento.key not in teclas_pulsadas:
          teclas_pulsadas.append (evento.key)
      else:  # evento.type == pygame.KEYUP
        if evento.key in teclas_pulsadas:
          teclas_pulsadas.remove (evento.key)
  redimensiona_ventana()
  if not teclas_pulsadas:
    return None
  if teclas_pulsadas[-1] in teclas_ascii:
    return teclas_ascii[teclas_pulsadas[-1]]
  return (teclas_pulsadas[-1], 0)

def carga_bd_pics (rutaBDGfx):
  """Carga la base de datos gr�fica de ruta dada, y prepara la paleta y lo relacionado con ella"""
  extension = rutaBDGfx[rutaBDGfx.rfind ('.') + 1:]
  graficos_daad.carga_bd_pics (rutaBDGfx)
  if graficos_daad.modo_gfx == 'CGA':
    cambiaPaleta (graficos_daad.paleta1b)  # Dejamos cargada la paleta CGA 1 con brillo
    tinta = 3
  else:
    tinta = 15
    cambiaPaleta (graficos_daad.paletaEGA, False)  # Dejamos cargada la paleta EGA
  for subventana in range (num_subvens):
    color_subv[subventana][0] = tinta  # Color de tinta
  if graficos_daad.recursos:
    precargaGraficos()

# FIXME: Hay que dibujar s�lo la regi�n que no sale de los topes
def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gr�fico en la posici�n del cursor

El par�metro descripcion indica si se llama al describir la localidad
El par�metro parcial indica si es posible dibujar parte de la imagen"""
  if ruta_graficos:
    try:
      grafico = pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
    except Exception as e:
      if traza:
        prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
        prn (e)
      return  # No dibujamos nada
  elif graficos_daad.recursos:
    if numero not in graficos:
      if not graficos_daad.recursos[numero] or 'imagen' not in graficos_daad.recursos[numero]:
        if traza:
          if not graficos_daad.recursos[numero]:
            razon = 'no est� en la base de datos gr�fica'
          else:
            razon = 'ese recurso de la base de datos gr�fica no es una imagen, o est� corrupta'
          prn ('Gr�fico', numero, 'inv�lido,', razon)
        return  # No dibujamos nada
      cargaGrafico (numero)
    recurso = graficos[numero]
    grafico = recurso['grafico']
    if 'flotante' not in recurso['banderas']:
      cambiaPaleta (recurso['paleta'])
    grafico.set_palette (paleta[0])
  else:
    return  # No dibujamos nada
  tope = topes[elegida]
  if descripcion:
    if traza:
      prn ('Dibujo', numero, 'desde la descripci�n de la localidad, en (0, 0)')
  else:
    cursor     = cursores[elegida]
    subventana = subventanas[elegida]
    if traza:
      prn ('Dibujo', numero, 'sobre subventana', elegida, 'en', subventana,
           'con topes', tope, 'y cursor en', cursor)
  if elegida == 0:
    topes_gfx[0] = min (grafico.get_width()  // 8, limite[0])
    topes_gfx[1] = min (grafico.get_height() // 8, limite[1])
  if (descripcion or elegida == 0) and not parcial:
    ancho = tope[0] * 6
    if numero in graficos and 'flotante' not in recurso['banderas']:
      destino = recurso['posicion']
    elif centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
      # Se centran los gr�ficos en la Aventura Original, pero no en El Jabato, as� est� en la base de datos gr�fica
      destino      = ((ancho - grafico.get_width()) // 2, 0)
      topes_gfx[0] = min ((grafico.get_width() + (ancho - grafico.get_width()) // 2) // 8, limite[0])
    else:
      destino = (0, 0)
    ventana.blit (grafico, destino)
  else:
    ancho = ((tope[0] - cursor[0]) * 6)  # Anchura del dibujo
    alto  = ((tope[1] - cursor[1]) * 8)  # Altura del dibujo
    if numero in graficos:
      if nueva_version and elegida > 0 and not espacial:
        if 'flotante' not in recurso['banderas']:
          pos_gfx_sub[elegida] = recurso['posicion']  # Otros graficos flotantes en esta subventana se dibujar�n aqu�
        destino = pos_gfx_sub[elegida]
      elif templos:
        # TODO: Probar esto m�s, ocurre as� con gr�ficos de localidad de Los Templos Sagrados, pero no en Chichen Itz�, ni sirve para Aventura Espacial
        ancho   = ((((tope[0] - cursor[0]) * 6) // 8) * 8)  # Anchura del dibujo
        destino = [(((subventana[0] + cursor[0]) * 6) // 8) * 8, (subventana[1] + cursor[1]) * 8]
      elif 'flotante' in recurso['banderas']:
        # TODO: Asegurarse de si hay que tener en cuenta la posici�n del cursor
        destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
      else:
        destino = recurso['posicion']
    else:
      # TODO: Asegurarse de si hay que tener en cuenta la posici�n del cursor
      destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
      if centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
        destino[0] += (ancho - grafico.get_width()) // 2
    # Los gr�ficos pueden dibujar hasta dos p�xeles m�s all� de la �ltima columna de texto
    if ancho < grafico.get_width() and subventana[0] + tope[0] == 53:
      ancho += max (2, grafico.get_width() - ancho)
    ventana.blit (grafico, destino, (0, 0, ancho, alto))
  actualizaVentana()
  # TODO: Ver si hay que actualizar la posici�n del cursor (puede que no)

def elige_parte (partes, graficos):
  """Obtiene del jugador el modo gr�fico a usar y a qu� parte jugar, y devuelve el nombre de la base de datos elegida"""
  global tras_portada
  if len (partes) == 1:
    return partes.popitem()[1]
  portada = None
  for modoPortada, tinta in (('dat', 15), ('ega', 15), ('cga', 3)):
    if modoPortada in graficos and 0 in graficos[modoPortada]:
      try:
        fichero = open (graficos[modoPortada][0], 'rb')
        imagen, palImg = graficos_daad.cargaPortada (fichero)
        strImg = b''
        for fila in imagen if modoPortada == 'cga' else [imagen]:
          if version_info[0] > 2:
            for pixel in fila:
              strImg += bytes ([pixel])
          else:
            for pixel in fila:
              strImg += chr (pixel)
        portada = pygame.image.frombuffer (strImg, (320, 200), 'P')
        portada.set_palette (palImg)
        paleta[0].extend (palImg)
        break
      except Exception:
        portada = None  # No dibujaremos nada
      if 'fichero' in locals():
        fichero.close()
  if not paleta[0]:
    paleta[0].extend (graficos_daad.paletaEGA)
    tinta = 15
  for subventana in range (num_subvens):
    color_subv[subventana][0] = tinta  # Color de tinta
  numerosPartes = tuple (partes.keys())
  numParteMenor = min (numerosPartes)
  numParteMayor = max (numerosPartes)
  entrada = None
  while entrada not in numerosPartes:
    borra_todo()
    if portada:
      ventana.blit (portada, (0, 0))
      ventana.fill (palImg[0], (11 * 8, 10 * 8, 19 * 8, 5 * 8))
    mueve_cursor (18, 11)
    imprime_cadena ('�Qu� parte quieres')
    mueve_cursor (21, 13)
    imprime_cadena ('cargar? (%d%s%d)' % (numParteMenor, '/' if (numParteMayor - numParteMenor == 1) else '-', numParteMayor))
    entrada = espera_tecla() - ord ('0')
  pygame.display.set_caption ('NAPS - ' + partes[entrada])
  if portada:
    ventana.blit (portada, (0, 0))
    actualizaVentana()
    tras_portada = True
    if entrada in graficos[modoPortada]:
      carga_bd_pics (graficos[modoPortada][entrada])
    elif 'dat' in graficos and entrada in graficos['dat']:
      carga_bd_pics (graficos['dat'][entrada])
  else:
    for modo in ('dat', 'ega', 'cga'):
      if modo in graficos and entrada in graficos[modo]:
        carga_bd_pics (graficos[modo][entrada])
        if graficos_daad.recursos:
          break
  return partes[entrada]

def elige_subventana (numero):
  """Selecciona la subventana dada y devuelve el n�mero de subventana anterior"""
  global elegida
  anterior = elegida
  elegida  = numero
  if traza:
    prn ('Subventana', elegida, 'elegida, en', subventanas[elegida],
         'con topes', topes[elegida], 'y cursor en', cursores[elegida])
  return anterior

def espera_tecla (tiempo = 0):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  global tras_portada
  tras_portada = False
  pygame.time.set_timer (pygame.USEREVENT, tiempo * 1000)  # Ponemos el timer
  copia = ventana.copy()  # Porque con PyGame 2 se pierde al menos al redimensionar
  while True:
    evento = pygame.event.wait (500) if pygame.vernum[0] > 1 else pygame.event.wait()
    if evento.type == pygame.KEYDOWN:
      if evento.key not in teclas_pulsadas:
        teclas_pulsadas.append (evento.key)
      if ((evento.key < 256) and (chr (evento.key) in teclas_edicion)) or evento.key in teclas_kp or evento.key in teclas_mas_256:
          pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
          return evento.key
    elif evento.type == pygame.KEYUP:
      if evento.key in teclas_pulsadas:
        teclas_pulsadas.remove (evento.key)
    elif evento.type == pygame.USEREVENT:  # Tiempo de espera superado
      pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
      return None
    elif evento.type in (pygame.QUIT, pygame.VIDEORESIZE):
      redimensiona_ventana (evento, copia)
    pygame.display.update()  # Para que recupere el contenido si se cubri� la ventana

def carga_cursor ():
  """Carga la posici�n del cursor guardada de la subventana elegida """
  mueve_cursor (*cursores_at[elegida])

def guarda_cursor ():
  """Guarda la posici�n del cursor de la subventana elegida """
  cursores_at[elegida] = tuple (cursores[elegida])

def hay_grafico (numero):
  """Devuelve si existe el gr�fico de n�mero dado"""
  if ruta_graficos:
    try:
      pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
    except Exception as e:
      if traza:
        prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
        prn (e)
      return False
  elif graficos_daad.recursos:
    if not graficos_daad.recursos[numero] or 'imagen' not in graficos_daad.recursos[numero]:
      if traza:
        if not graficos_daad.recursos[numero]:
          razon = 'no est� en la base de datos gr�fica'
        else:
          razon = 'ese recurso de la base de datos gr�fica no es una imagen, o est� corrupta'
        prn ('Gr�fico', numero, 'inv�lido,', razon)
      return False
  else:
    return False
  return True

def insertaHastaMax (listaChrs, posInput, caracter, longMax):
  """Inserta el car�cter dado a la posici�n de la lista de caracteres dada contenida en la lista posInput, si no superar�a con ello la longitud m�xima longMax. Incrementa la posici�n (valor entero) dentro de posInput si lo ha a�adido"""
  if len (listaChrs) < longMax:
    listaChrs.insert (posInput[0], caracter)
    posInput[0] += 1

def lee_cadena (prompt, inicio, timeout, espaciar = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentaci�n al jugador

El par�metro prompt, es el mensaje de prompt
El par�metro inicio es la entrada a medias anterior
El par�metro timeout es una lista con el tiempo muerto, en segundos
El par�metro espaciar permite elegir si se debe dejar una l�nea en blanco tras el �ltimo texto"""
  cursorMovido = None  # Posici�n de cursor que recuperar si se ha movido
  posHistorial = len (historial)
  textoAntes   = False  # Si hab�a texto en la subventana de entrada antes de la l�nea del prompt
  if subv_input:  # Guardamos la subventana que estaba elegida justo antes, y cambiamos a la de entrada
    global elegida
    if inicio:
      borra_orden()
    subvAntes = elegida
    elegida   = subv_input
    if cursores[elegida][0] > subventanas[elegida][0] and prompt[0] == '\n':  # Hay texto antes de la l�nea del prompt
      # Cambiamos la subventana de entrada para que omita el texto escrito antes, y as� no lo borre
      cursores[elegida][0]     = subventanas[elegida][0]
      cursores[elegida][1]    += 1
      subventanas[elegida][1] += 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
      prompt     = prompt[1:]
      textoAntes = True
  elif opcs_input & 8:  # Pedir la entrada debajo del todo
    cursorMovido = list (cursores[elegida])
  elif espaciar and cursores[elegida][1] >= topes[elegida][1] - 2 and cursores[elegida][0]:
    prompt = '\n' + prompt  # Dejaremos una l�nea en blanco entre el �ltimo texto y el prompt
  # El prompt se imprimir�
  if opcs_input & 8:  # Pedir la entrada debajo del todo
    lineas    = imprime_cadena (prompt, abajo = True)
    finPrompt = lineas[-1]  # �ltima l�nea del prompt
    if cursorMovido[1] + len (lineas) >= topes[elegida][1]:  # Hab�a hecho scroll
      cursorMovido[1] = topes[elegida][1] - len (lineas)
  else:  # Pedirla en la siguiente l�nea de la subventana de entrada
    imprime_cadena (prompt, False)
  entrada = []
  entrada.extend (list (inicio))  # Partimos la entrada anterior por caracteres
  longAntes = len (inicio) + 1  # Longitud de la entrada m�s el marcador (_) de entrada de car�cter (porque est� al final)
  longMax   = (topes[elegida][0] - cursores[elegida][0] - 1) + (topes[elegida][0] * (topes[elegida][1] - 1))  # Ancho m�ximo de la entrada
  posInput  = [len (inicio)]  # Posici�n del marcador (cursor) de entrada de car�cter, inicialmente al final
  while True:
    realimentacion = ''.join (entrada)
    if subv_input:
      borra_pantalla (noRedibujar = True)
      imprime_cadena (prompt, False, False)
    else:
      diferencia = longAntes - (len (entrada) + (1 if posInput[0] == len (entrada) else 0))  # Caracteres de m�s antes vs. ahora
      if diferencia > 0:
        realimentacion += ' ' * (diferencia + 1)  # Para borrar el resto de la orden anterior
      longAntes = len (entrada) + (1 if posInput[0] == len (entrada) else 0)
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente), posInput[0])
    tecla = espera_tecla (timeout[0])

    if tecla == None:  # Tiempo muerto vencido
      timeout[0] = True
      if subv_input:
        borra_pantalla()  # Borramos la entrada realimentada en pantalla
        if textoAntes:
          subventanas[elegida][1] -= 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
        elegida = subvAntes  # Recuperamos la subventana elegida justo antes
      else:  # Quitamos el gui�n bajo del final de la entrada
        realimentacion = ''.join (entrada) + ' '  # El espacio borrar� el gui�n bajo cuando estaba al final
        imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
      return ''.join (entrada)

    modificadores = pygame.key.get_mods()
    mayuscula     = (modificadores & pygame.KMOD_CAPS)  != 0  # Caps Lock activo
    altGr         = (modificadores & pygame.KMOD_MODE)  != 0
    control       = (modificadores & pygame.KMOD_CTRL)  != 0
    shift         = (modificadores & pygame.KMOD_SHIFT) != 0
    # Primero, tratamos los c�digos superiores a 255
    if tecla in (pygame.K_KP_ENTER, pygame.K_RETURN):
      if entrada:
        break
      # Seguimos leyendo entrada del jugador si se pulsa Enter sin haber escrito nada
    elif tecla == 314:  # Alt Gr + `
      insertaHastaMax (entrada, posInput, '[', longMax)
    elif tecla in teclas_kp:
      insertaHastaMax (entrada, posInput, teclas_kp[tecla], longMax)
    elif tecla == pygame.K_LEFT:
      if control:  # Salta al inicio de palabras
        if posInput[0]:  # S�lo si no est� al inicio del todo
          posInput[0] = ''.join (entrada).rfind (' ', 0, posInput[0] - 1) + 1
      else:
        posInput[0] = max (0, posInput[0] - 1)
    elif tecla == pygame.K_RIGHT:
      if control:  # Salta al final de palabras
        posInput[0] = ''.join (entrada).find (' ', posInput[0] + 2)
        if posInput[0] < 0:
          posInput[0] = len (entrada)
      else:
        posInput[0] = min (len (entrada), posInput[0] + 1)
    elif tecla == pygame.K_UP:
      if historial and posHistorial:
        if posHistorial == len (historial):
          historial_temp = list (entrada)  # Hace una copia para no modificarlo
        posHistorial = max (0, posHistorial - 1)
        entrada      = list (historial[posHistorial])  # Hace una copia para no modificarlo
        posInput[0]  = len (entrada)
    elif tecla == pygame.K_DOWN:
      if historial and posHistorial < len (historial):
        posHistorial = min (len (historial), posHistorial + 1)
        if posHistorial == len (historial):
          entrada = list (historial_temp)  # Hace una copia para no modificarlo
          del historial_temp[:]
        else:
          entrada = list (historial[posHistorial])  # Hace una copia para no modificarlo
        posInput[0] = len (entrada)
    elif tecla == pygame.K_HOME:
      posInput[0] = 0
    elif tecla == pygame.K_END:
      posInput[0] = len (entrada)
    elif tecla == pygame.K_DELETE:
      entrada = entrada[:posInput[0]] + entrada[posInput[0] + 1:]
    else:  # C�digo inferior a 256
      tecla = chr (tecla)
      if (tecla.isalpha() or tecla == ' ') and tecla != '�':  # Una tecla de letra
        # Vemos si tenemos que a�adirla en may�scula o min�scula
        if todo_mayusculas or mayuscula ^ shift:
          tecla = tecla.upper()
        insertaHastaMax (entrada, posInput, tecla, longMax)
      elif tecla == '\b':  # La tecla Backspace, arriba del Enter
        entrada     = entrada[:posInput[0] - 1] + entrada[posInput[0]:]
        posInput[0] = max (0, posInput[0] - 1)
      elif not shift:  # Shift sin pulsar
        if altGr:  # Alt Gr pulsado
          if tecla in teclas_alt_gr:
            insertaHastaMax (entrada, posInput, teclas_alt_gr[tecla], longMax)
        elif (tecla in string.digits) or (tecla in "�'���<,.-+"):
          insertaHastaMax (entrada, posInput, tecla, longMax)  # Es v�lida tal cual
      elif tecla in teclas_shift:  # Shift est� pulsado
        insertaHastaMax (entrada, posInput, teclas_shift[tecla], longMax)
  # Borramos la entrada realimentada en pantalla, s�lo si no es en subventana propia (usar borra_orden en el otro caso)
  if subv_input:
    borra_pantalla (noRedibujar = True)
    imprime_cadena (prompt, False, False)
    realimentacion = ''.join (entrada) + ' '  # El espacio borrar� el gui�n bajo
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
    if textoAntes:
      subventanas[elegida][1] -= 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
    elegida = subvAntes  # Recuperamos la subventana elegida
  else:
    if cursorMovido:
      cursores[elegida] = cursorMovido
    borra_pantalla (True)
  if not subv_input or opcs_input & 2:  # Realimentaci�n permanente de la orden, junto al texto del juego
    if prompt and opcs_input & 8:  # Se imprim�a abajo del todo y hab�a prompt
      imprime_linea (finPrompt)
      cursores[elegida][0] += len (finPrompt)
    imprime_cadena (''.join (entrada) + ' ')
    imprime_cadena ('\n')
  # Guardamos la entrada en el historial
  if not historial or historial[-1] != entrada:
    historial.append (entrada)
  # Devolvemos la cadena
  return ''.join (entrada)

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la extensi�n de la ventana)"""
  global banderas_antes, banderas_viejas
  if banderas_antes == None:
    banderas_antes  = [0,] * NUM_BANDERAS
    banderas_viejas = set (range (NUM_BANDERAS))
    # Seleccionamos el color de impresi�n
    fuente.set_palette (((0, 192, 192), (0, 0, 0)))
    # Imprimimos los �ndices de cada bandera
    for num in range (NUM_BANDERAS):
      columna = 320 + ((num // 25) * 42)
      fila    = (num % 25) * 8
      cadena = str (num).zfill (3).translate (iso8859_15_a_fuente)
      for pos in range (3):
        c = ord (cadena[pos])
        ventana.blit (fuente, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
  for num in range (NUM_BANDERAS):
    # S�lo imprimimos cada bandera la primera vez y cuando cambie de color
    if (banderas[num] == banderas_antes[num]) and (num not in banderas_viejas):
      continue
    columna = 339 + ((num // 25) * 42)
    fila    = (num % 25) * 8
    cadena  = str (banderas[num]).zfill (3).translate (iso8859_15_a_fuente)
    # Seleccionamos el color de impresi�n
    if banderas_antes[num] != banderas[num]:
      banderas_antes[num] = banderas[num]
      banderas_viejas.add (num)
      fuente.set_palette (((64, 255, 0), (0, 0, 0)))
    else:  # La bandera estaba en banderas_viejas
      banderas_viejas.remove (num)
      if banderas[num] == 0:
        fuente.set_palette (((96, 96, 96), (0, 0, 0)))
      else:
        fuente.set_palette (((255, 255, 255), (0, 0, 0)))
    # Imprimimos los valores de cada bandera
    for pos in range (3):
      c = ord (cadena[pos])
      ventana.blit (fuente, (columna + (pos * 6), fila),
                    ((c % 63) * 10, (c // 63) * 10, 6, 8))
  actualizaVentana()
  fuente.set_palette (((255, 255, 255), (0, 0, 0)))

def imprime_cadena (cadena, scroll = True, redibujar = True, abajo = False):
  """Imprime una cadena en la posici�n del cursor (dentro de la subventana), y devuelve la cadena partida en l�neas

El cursor deber� quedar actualizado.

Si scroll es True, se desplazar� el texto del buffer hacia arriba (scrolling) cuando se vaya a sobrepasar la �ltima l�nea

Si abajo es True, imprimir� abajo del todo de la subventana sin hacer scroll mientras no alcance el cursor"""
  # TODO: revisar por qu� hac�a falta el par�metro scroll, dado que se est� omitiendo
  if not cadena:
    return
  if not texto_nuevo:
    texto_nuevo.append (True)
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if cadena == '\n':  # TODO: sacar a funci�n nueva_linea
    if cursor[1] >= tope[1] - 1:
      scrollLineas (1, subventana, tope)
    cursores[elegida] = [0, min (tope[1] - 1, cursor[1] + 1)]
    if traza:
      prn ('Nueva l�nea, cursor en', cursores[elegida])
    return
  if traza:
    prn ('Impresi�n sobre subventana', elegida, 'en', subventana, 'con topes',
         tope, 'y cursor en', cursor)
  # Convertimos la cadena a posiciones sobre la tipograf�a
  if todo_mayusculas and juego_alto and izquierda[juego_alto] in cadena:  # Se trata de SWAN
    # En la fuente alta s�lo hay letras may�sculas, as� que las dem�s las ponemos como fuente baja
    juego    = False  # Si la parte actual de la cadena est� en juego alto o no
    bajado   = False  # Si la parte actual de la cadena est� pasada a juego bajo por letras no may�sculas
    cambiada = ''     # Cadena cambiada teniendo en cuenta que en la fuente alta s�lo hay letras may�sculas
    for c in cadena:
      if c == izquierda[juego_alto]:  # Es el mismo car�cter para alternar entre juego alto y bajo
        juego = not juego
        if not bajado:
          cambiada += c
        bajado = False
        continue
      if juego:
        if c.isupper():
          if bajado:
            bajado    = False
            cambiada += izquierda[juego_alto]
        elif not bajado:
          bajado    = True
          cambiada += izquierda[juego_alto]
      cambiada += c
    cadena  = cambiada
    colores = {}
  else:  # No es SWAN o no se cambia entre juego alto y bajo
    cadena, colores = parseaColores (cadena)
  convertida = cadena.translate (iso8859_15_a_fuente)
  # Dividimos la cadena en l�neas
  juego     = 0    # 128 si est� en el juego alto, 0 si no
  iniLineas = [0]  # Posici�n de inicio de cada l�nea, para colorear
  lineas    = []
  linea     = []
  restante  = tope[0] - cursor[0]  # Columnas restantes que quedan en la l�nea
  for c in convertida:
    ordinal = ord (c)
    if ((ordinal == len (izquierda) - 1) or  # Car�cter nueva l�nea (el �ltimo)
        ((restante == 0) and (ordinal == 16))):  # Termina la l�nea con espacio
      lineas.append (''.join (linea))
      iniLineas.append (iniLineas[-1] + len (linea) + (1 if (ordinal == len (izquierda) - 1) else 0))
      linea    = []
      restante = tope[0]
    elif ordinal == juego_alto and juego == 0:
      juego = 128
    elif ordinal == juego_bajo:
      juego = 0
    elif ordinal == 127:  # Es un tabulador
      posTabulador = iniLineas[-1] + len (linea)
      if restante > tope[0] // 2:
        numEspacios = (tope[0] // 2) - len (linea)  # Rellena con espacios hasta mitad de l�nea
      else:
        numEspacios = restante  # Rellena el resto de la l�nea con espacios
      linea.extend (chr (16) * numEspacios)
      restante -= numEspacios
      coloresNuevos = {}
      for inicio in tuple (colores.keys()):
        if inicio > posTabulador:
          coloresNuevos[inicio + numEspacios - 1] = colores[inicio]
        else:
          coloresNuevos[inicio] = colores[inicio]
      colores = coloresNuevos
    elif restante > 0:
      linea.append (chr (ordinal + juego))
      restante -= 1
    else:  # Hay que partir la l�nea, desde el �ltimo car�cter de espacio
      for i in range (len (linea) - 1, -1, -1):  # Desde el final al inicio
        if partir_espacio and ord (linea[i]) == 16:  # Este car�cter es un espacio
          lineas.append (''.join (linea[:i + 1]))
          linea = linea[i + 1:]
          iniLineas.append (iniLineas[-1] + i + 1)
          break
      else:  # Ning�n car�cter de espacio en la l�nea
        if len (linea) == tope[0]:  # La l�nea nunca se podr� partir limpiamente
          # La partimos suciamente (en mitad de palabra)
          lineas.append    (''.join (linea))
          iniLineas.append (iniLineas[-1] + len (linea))
          linea = []
        else:  # Lo que ya ten�amos ser� para una nueva l�nea
          lineas.append (' '.translate (iso8859_15_a_fuente) * len (linea))  # TODO: revisar qu� es esto y si es correcto
          iniLineas.append (iniLineas[-1] + len (linea))
      linea.append (chr (ordinal + juego))
      restante = tope[0] - len (linea)
  if linea:  # Queda algo en la �ltima l�nea
    lineas.append (''.join (linea))
  # Hacemos scrolling antes de nada, en caso de que vaya a ser necesario
  lineasAsubir = cursor[1] + len (lineas) - tope[1]
  if lineasAsubir > 0:  # Hay que desplazar el texto ese n�mero de l�neas
    scrollLineas (lineasAsubir, subventana, tope)
    cursor[1] -= min (cursor[1], lineasAsubir)  # Actualizamos el cursor antes de imprimir
  if abajo:
    cursor[0] = 0
    cursor[1] = max (0, tope[1] - len (lineas) - (1 if cadena[-1] == '\n' else 0))
  # Imprimimos la cadena l�nea por l�nea
  for i in range (len (lineas)):
    if i > 0:  # Nueva l�nea antes de cada una, salvo la primera
      cursor = [0, min (cursor[1] + 1, tope[1] - 1)]
      cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
      # Paginaci�n
      # FIXME: reimplementar para textos acumulados desde la �ltima orden
      if i % (tope[1] - 1) == 0 and (not subv_input or elegida != subv_input):
        imprime_linea (txt_mas.translate (iso8859_15_a_fuente))
        espera_tecla()
        imprime_linea (' '.translate (iso8859_15_a_fuente) * tope[0])
        # TODO: Hacer scroll de golpe, del n�mero de l�neas necesario
      elif i >= tope[1]:  # Tras sobrepasar el tope de l�neas, hay que hacer scroll con cada una
        scrollLineas (1, subventana, tope)
    elif 0 in colores and not lineas[i]:  # La primera l�nea es s�lo \n
      fuente.set_palette (colores[0])  # Cargamos el color inicial de la cadena
    if cambia_brillo:
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores, inicioLinea = iniLineas[i])
    else:
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores)
  if lineas:  # Hab�a alguna l�nea
    if cadena[-1] == '\n':  # La cadena terminaba en nueva l�nea
      if cursor[1] == tope[1] - 1:
        scrollLineas (1, subventana, tope, redibujar)
        cursor = [0, cursor[1]]
      else:
        cursor = [0, cursor[1] + 1]
    else:
      cursor = [cursor[0] + len (lineas[-1]), cursor[1]]
    cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
  if traza:
    prn ('Fin de impresi�n, cursor en', cursor)
  return lineas

def imprime_linea (linea, posInput = None, redibujar = True, colores = {}, inicioLinea = 0):
  """Imprime una l�nea de texto en la posici�n del cursor, sin cambiar el cursor

Los caracteres de linea deben estar convertidos a posiciones en la tipograf�a"""
  # Coordenadas de destino
  destinoX = (subventanas[elegida][0] + cursores[elegida][0]) * 6
  destinoY = (subventanas[elegida][1] + cursores[elegida][1]) * 8
  for i in range (len (linea)):
    c = ord (linea[i])
    if i + inicioLinea in colores:
      fuente.set_palette (colores[i + inicioLinea])
    # Curioso, aqu� fuente tiene dos significados correctos :)
    # (SPOILER: Como sin�nimo de origen y como sin�nimo de tipograf�a)
    ventana.blit (fuente, (destinoX + (i * 6), destinoY),
                  ((c % 63) * 10, (c // 63) * 10, 6, 8))
  if posInput != None:
    preparaCursor()
    ventana.blit (chr_cursor, (destinoX + (posInput * 6), destinoY), (0, 0, 6, 8))
  if redibujar:
    actualizaVentana()

def imprime_lineas (texto, posInput = None):
  """Imprime el texto en la posici�n del cursor, sin cambiar el cursor, partiendo por l�neas si texto alcanza el tope de la subventana

Los caracteres de linea deben estar convertidos a posiciones en la tipograf�a"""
  cursor     = list (cursores[elegida])  # Copia del cursor, para recuperarlo despu�s
  lineas     = []  # L�neas partidas como corresponde ("a lo bruto")
  maxPrimera = topes[elegida][0] - cursores[elegida][0]  # Anchura m�xima de la primera l�nea
  posInputEn = 0   # En qu� l�nea est� el gui�n bajo de feedback gr�fico de entrada
  if len (texto) < maxPrimera:
    lineas.append (texto)
  else:
    lineas.append (texto[:maxPrimera])
    inicio = maxPrimera
    fin    = maxPrimera + topes[elegida][0]
    if posInput >= inicio:
      posInputEn += 1
      posInput   -= maxPrimera
    while fin <= len (texto):
      lineas.append (texto[inicio:fin])
      inicio += topes[elegida][0]
      fin    += topes[elegida][0]
      if posInput >= inicio:
        posInputEn += 1
        posInput   -= topes[elegida][0]
    lineas.append (texto[inicio:fin])
  for l in range (len (lineas)):
    linea = lineas[l]
    if l:  # No es la primera l�nea
      cursores[elegida][0] = 0
      if posInput != None and subv_input:
      	scrollLineas (1, subventanas[elegida], topes[elegida], False)
      else:
      	cursores[elegida][1] += 1
    if posInputEn == l:
      imprime_linea (linea, posInput, False)
    else:
      imprime_linea (linea, redibujar = False)
  cursores[elegida] = cursor
  actualizaVentana()

def mueve_cursor (columna, fila = None):
  """Cambia de posici�n el cursor de la subventana elegida"""
  if fila == None:
    fila = cursores[elegida][1]
  cursores[elegida] = [columna, fila]
  if traza:
    prn ('Subventana', elegida, 'en', subventanas[elegida], 'con topes', topes[elegida],
         'y cursor movido a', cursores[elegida])

def prepara_topes (columnas, filas):
  """Inicializa los topes al n�mero de columnas y filas dado"""
  global topes, topes_gfx
  limite[0] = columnas           # Ancho m�ximo absoluto de cada subventana
  limite[1] = filas              # Alto m�ximo absoluto de cada subventana
  topes_gfx = [columnas, filas]  # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0
  for topesSubventana in topes:  # Topes relativos de cada subventana de impresi�n
    topesSubventana[0] = columnas
    topesSubventana[1] = filas

def pos_subventana (columna, fila):
  """Cambia la posici�n de origen de la subventana de impresi�n elegida"""
  subventanas[elegida] = [columna, fila]
  # Ajustamos los topes para que no revasen el m�ximo permitido
  # No s� si DAAD hace esto, en caso de no usar el condacto WINSIZE
  # FIXME: Comprobar qu� ocurre si no se usa WINSIZE, �se usan los topes
  #        anteriores, o se maximizan?
  topes[elegida] = [min (topes[elegida][0], limite[0] - columna),
                    min (topes[elegida][1], limite[1] - fila)]
  # Ponemos el cursor al origen de la subventana
  cursores[elegida] = [0, 0]
  if traza:
    prn ('Subventana', elegida, 'puesta en', subventanas[elegida], 'con topes',
         topes[elegida], 'y cursor en', cursores[elegida])

def reinicia_subventanas ():
  """Ajusta todas las subventanas de impresi�n a sus valores por defecto"""
  for i in range (num_subvens):
    color_subv[i]  = [len (paleta[0]) - 1, 0, 0]
    cursores[i]    = [0, 0]
    subventanas[i] = [0, 0]
    topes[i]       = list (limite)
  topes_gfx = list (limite)
  if traza:
    prn ('Subventanas reiniciadas a [0, 0] con topes', limite,
         'y cursor en [0, 0]')


# Funciones auxiliares que s�lo se usan en este m�dulo

def cambiaPaleta (nuevaPaleta, convertir = True):
  """Cambia la paleta de la ventana de juego por la dada, opcionalmente convirtiendo los colores dibujados por los nuevos"""
  if paleta[0]:
    if convertir and nuevaPaleta != paleta[0]:
      for x in range (320):
        for y in range (200):
          indicePaleta = paleta[0].index (ventana.get_at ((x, y))[:3])
          ventana.set_at ((x, y), nuevaPaleta[indicePaleta])
    del paleta[0][:]
  paleta[0].extend (nuevaPaleta)

def cargaGrafico (numero):
  """Carga un gr�fico del recurso de base de datos gr�fica de n�mero dado, dejando su informaci�n y la imagen PyGame preparada en graficos"""
  recurso   = graficos_daad.recursos[numero]
  bufferImg = bytes (bytearray (recurso['imagen']))
  graficos[numero] = {'grafico': pygame.image.frombuffer (bufferImg, recurso['dimensiones'], 'P')}
  for propiedad in ('banderas', 'paleta', 'posicion'):
    graficos[numero][propiedad] = recurso[propiedad]

def daColorBorde ():
  """Devuelve el color de borde o de fondo de la subventana elegida, seg�n corresponda a la plataforma"""
  if paleta[1]:  # Si hay dos paletas, debe ser Spectrum
    return paleta[0][color_subv[elegida][2]] if paleta[0] else (0, 0, 0)  # Color del borde
  return paleta[0][color_subv[elegida][1]] if paleta[0] else (0, 0, 0)  # Color del papel

def parseaColores (cadena):
  """Procesa los c�digos de control de colores, devolviendo la cadena sin ellos, y un diccionario posici�n: colores a aplicar"""
  global brillo
  inversa = False  # Si se invierten o no papel y fondo
  papel   = color_subv[elegida][1]  # Color de papel/fondo
  tinta   = color_subv[elegida][0]  # Color de tinta
  colores = {0: (paleta[brillo][tinta], paleta[brillo][papel])}
  if not cambia_brillo:
    return cadena, colores
  sigBrillo  = False  # Si el siguiente car�cter indica si se pone o quita brillo al color de tinta
  sigFlash   = False  # Si el siguiente car�cter indica si se pone o quita efecto flash
  sigInversa = False  # Si el siguiente car�cter indica si se invierten o no papel y fondo
  sigPapel   = False  # Si el siguiente car�cter indica el color de papel/fondo
  sigTinta   = False  # Si el siguiente car�cter indica el color de tinta
  sinColores = ''     # Cadena sin los c�digos de control de colores
  for i in range (len (cadena)):
    c = ord (cadena[i])
    if sigBrillo or sigFlash or sigInversa or sigPapel or sigTinta:
      if sigBrillo:
        brillo    = 1 if c else 0
        sigBrillo = False
      elif sigFlash:
        sigFlash = False
      elif sigInversa:
        if inversa and not c or not inversa and c:  # Si se ha activado o desactivado
          color = papel
          papel = tinta
          tinta = color
        inversa    = True if c else False
        sigInversa = False
      elif sigPapel:
        papel    = c % len (paleta[brillo])
        sigPapel = False
      else:
        sigTinta = False
        tinta    = c % len (paleta[brillo])
      colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel])  # Color de tinta y papel a aplicar
    elif c in (cambia_brillo, cambia_flash, cambia_inversa, cambia_papel, cambia_tinta):
      if c == cambia_brillo:
        sigBrillo = True
      elif c == cambia_flash:
        sigFlash = True
      elif c == cambia_inversa:
        sigInversa = True
      elif c == cambia_papel:
        sigPapel = True
      else:
        sigTinta = True
    elif c == tabulador:
      sinColores += chr (127)  # Necesario para que quede sin convertir
    elif cadena[i] in noEnFuente:
      sinColores += noEnFuente[cadena[i]]
    else:
      sinColores += cadena[i]
  if version_info[0] < 3:  # La versi�n de Python es 2.X
    sinColores = sinColores.encode ('iso-8859-15')
  return sinColores, colores

def precargaGraficos ():
  """Deja preparados los gr�ficos residentes en la base de datos gr�fica cargada"""
  for numero in range (len (graficos_daad.recursos)):
    recurso = graficos_daad.recursos[numero]
    if not recurso or 'imagen' not in recurso or 'residente' not in recurso['banderas']:
      continue
    cargaGrafico (numero)

def preparaCursor ():
  """Prepara el cursor con el car�cter y color adecuado"""
  cadenaCursor, colores = parseaColores (cad_cursor)
  if len (cadenaCursor) >= 1 and cadenaCursor[0] in izquierda:
    posEnFuente = izquierda.index (cadenaCursor[0])
    fuente.set_palette (colores[0])
    chr_cursor.blit (fuente, (0, 0), ((posEnFuente % 63) * 10, (posEnFuente // 63) * 10, 6, 8))
    chr_cursor.set_colorkey (colores[0][1])  # El color de papel/fondo ser� ahora transparente

def scrollLineas (lineasAsubir, subventana, tope, redibujar = True):
  """Hace scroll gr�fico del n�mero dado de l�neas, en la subventana dada, con topes dados"""
  destino = (subventana[0] * 6, subventana[1] * 8)  # Posici�n de destino
  origenX = destino[0]  # Coordenada X del origen (a subir)
  origenY = (subventana[1] + lineasAsubir) * 8  # Coordenada Y del origen
  anchura = tope[0] * 6  # Anchura del �rea a subir
  altura  = (tope[1] - lineasAsubir) * 8  # Altura del �rea a subir
  # Copiamos las l�neas a subir
  if altura > 0:
    ventana.blit (ventana, destino, (origenX, origenY, anchura, altura))
  # Borramos el hueco
  lineasAsubir = min (lineasAsubir, tope[1])
  colorBorde   = daColorBorde()
  origenY      = (subventana[1] + tope[1] - lineasAsubir) * 8
  altura       = lineasAsubir * 8
  ventana.fill (colorBorde, (origenX, origenY, anchura, altura))
  if redibujar:
    actualizaVentana()
