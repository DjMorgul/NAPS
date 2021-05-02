# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gr�fica de usuario (GUI) con PyGame para el int�rprete PAW-like
# Copyright (C) 2010, 2018-2021 Jos� Manuel Ferrer Ortiz
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

from prn_func import *
from sys      import version_info

import math    # Para ceil
import string  # Para algunas constantes

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
escalada = None
modo     = 'normal'  # Modo de ventana: normal, scale[2-3]x (escalado), o fullscreen (a pantalla completa)
ventana  = None

fuente = pygame.image.load ('fuente.png')  # Fuente tipogr�fica
fuente.set_palette (((255, 255, 255), (0, 0, 0)))

guion_bajo = pygame.Surface ((6, 8))  # Car�cter de gui�n bajo con transparencia, para marcar posici�n de input
guion_bajo.blit (fuente, (0, 0), ((79 % 63) * 10, (79 // 63) * 10, 6, 8))  # '_' est� en la posici�n 79
guion_bajo.set_colorkey ((0, 0, 0))  # El color negro ser� ahora transparente

# Variables que ajusta el int�rprete
cambia_brillo    = None      # Car�cter que si se encuentra en una cadena, dar� o quitar� brillo al color de tinta de la letra
cambia_flash     = None      # Car�cter que si se encuentra en una cadena, pondr�a o quitar�a efecto flash a la letra
cambia_papel     = None      # Car�cter que si se encuentra en una cadena, cambiar� el color de papel/fondo de la letra
cambia_tinta     = None      # Car�cter que si se encuentra en una cadena, cambiar� el color de tinta de la letra
centrar_graficos = []        # Si se deben centrar los gr�ficos al dibujarlos
juego_alto       = None      # Car�cter que si se encuentra en una cadena, pasar� al juego de caracteres alto
juego_bajo       = None      # Car�cter que si se encuentra en una cadena, pasar� al juego de caracteres bajo
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con cambia_*
todo_mayusculas  = False     # Si la entrada del jugador ser� incondicionalmente en may�sculas
ruta_graficos    = ''

banderas_antes  = None  # Valor anterior de las banderas
banderas_viejas = None  # Banderas que antes cambiaron de valor
historial       = []    # Historial de �rdenes del jugador
historial_temp  = []    # Orden a medias, guardada al acceder al historial

# Todas las coordenadas son columna, fila
num_subvens = 8                # DAAD tiene 8 subventanas
elegida     = 1                # Subventana elegida (la predeterminada es la 1)
opcs_input  = 2                # Opciones para la entrada del usuario (TODO: revisar valor por defecto)
subv_input  = 0                # Subventana para entrada del usuario (0 indica la actual)
limite      = [53, 25]         # Ancho y alto m�ximos absolutos de cada subventana
cursores    = [[0, 0],] * 8    # Posici�n relativa del cursor de cada subventana
cursores_at = [(0, 0),] * 8    # Posici�n relativa del cursor guardado mediante SAVEAT de cada subventana
subventanas = [[0, 0],] * 8    # Posici�n absoluta de cada subventana (de su esquina superior izquierda)
topes       = [[53, 25],] * 8  # Topes relativos de cada subventana de impresi�n
topes_gfx   = [53, 25]         # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0
resolucion  = (320, 200)       # Resoluci�n gr�fica de salida, sin escalar


def abre_ventana (traza, modoPantalla, bbdd):
  """Abre la ventana gr�fica de la aplicaci�n"""
  global escalada, modo, resolucion, ventana
  pygame.display.set_caption ('NAPS - ' + bbdd)
  modo = 'normal'
  if traza:
    ventana = pygame.display.set_mode ((780, 200))  # Ventana juego + banderas
  # Ventana juego s�lo
  else:
    if limite[0] == 42:
      resolucion = (256, 192)
    if modoPantalla[:5] == 'scale' and modoPantalla[5].isdigit() and modoPantalla[-1] == 'x':
      factorEscala = int (modoPantalla[5])
      modo         = 'scale' + modoPantalla[5] + 'x'
      escalada     = pygame.display.set_mode ((resolucion[0] * factorEscala, resolucion[1] * factorEscala), pygame.RESIZABLE)
      ventana      = pygame.Surface (resolucion)
    else:
      ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
  return
  # FIXME: si no funciona el modo gr�fico, deja X Window mal permanentemente, a�n al cerrarse el int�rprete
  if modoPantalla == 'fullscreen':
    ventana = pygame.display.set_mode ((640, 400), ventana.get_flags() ^ pygame.FULLSCREEN)

def actualizaVentana ():
  if modo[:5] == 'scale':
    factorEscala = int (modo[5])
    pygame.transform.scale (ventana, (resolucion[0] * factorEscala, resolucion[1] * factorEscala), escalada)
  pygame.display.flip()

def redimensiona_ventana (evento = None):
  """Maneja eventos en relaci�n a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  global escalada, modo, ventana
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
  if evento.w < resolucion[0] or evento.h < resolucion[1]:
    modo       = 'normal'
    superficie = ventana.copy()
    ventana    = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    ventana.blit (superficie, (0, 0) + resolucion)
    actualizaVentana()
  else:
    if evento.w > (resolucion[0] * 2) or evento.h > (resolucion[1] * 2):
      factorEscala = 3
    elif evento.w > resolucion[0] or evento.h > resolucion[1]:
      factorEscala = 2
    modo       = 'scale' + str (factorEscala) + 'x'
    superficie = ventana.copy()
    escalada   = pygame.display.set_mode ((resolucion[0] * factorEscala, resolucion[1] * factorEscala), pygame.RESIZABLE)
    ventana    = superficie
    actualizaVentana()


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
  if frase_guardada and texto_nuevo:
    espera_tecla()  # Esperamos pulsaci�n de tecla si se hab�an entrado varias frases y se hab�a mostrado texto nuevo
    del texto_nuevo[:]
  if not desdeCursor:
    cursores[elegida] = [0, 0]
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if elegida == 0:
    tope = topes_gfx
  inicio_x = (subventana[0] + cursor[0]) * 6  # Esquina superior izquierda X
  inicio_y = (subventana[1] + cursor[1]) * 8  # Esquina superior izquierda Y
  ancho    = math.ceil (((tope[0] - cursor[0]) * 6) / 8.) * 8  # Anchura del rect�ngulo a borrar
  alto     = (tope[1] - cursor[1]) * 8  # Altura del rect�ngulo a borrar
  # Los gr�ficos pueden dibujar hasta dos p�xeles m�s all� de la �ltima columna de texto
  if subventana[0] + tope[0] == 53:
    ancho += 2
  ventana.fill ((0, 0, 0), (inicio_x, inicio_y, ancho, alto))
  if not desdeCursor and not noRedibujar:
    actualizaVentana()
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope, 'limpiada y cursor en', cursores[elegida])

def borra_todo ():
  """Limpia la pantalla completa"""
  ventana.fill ((0, 0, 0), (0, 0) + resolucion)
  actualizaVentana()

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

# FIXME: Hay que dibujar s�lo la regi�n que no sale de los topes
def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gr�fico en la posici�n del cursor

El par�metro descripcion indica si se llama al describir la localidad
El par�metro parcial indica si es posible dibujar parte de la imagen"""
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
  try:
    grafico = pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
  except Exception as e:
    if traza:
      prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
      prn (e)
    return  # No dibujamos nada
  if elegida == 0:
    topes_gfx[0] = min (grafico.get_width()  // 8, limite[0])
    topes_gfx[1] = min (grafico.get_height() // 8, limite[1])
  if (descripcion or elegida == 0) and not parcial:
    ancho = tope[0] * 6
    # TODO: se centran los gr�ficos en la Aventura Original, pero no en El Jabato. Averiguar si es por el valor de alguna bandera
    if centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
      destino      = ((ancho - grafico.get_width()) // 2, 0)
      topes_gfx[0] = min ((grafico.get_width() + (ancho - grafico.get_width()) // 2) // 8, limite[0])
    else:
      destino = (0, 0)
    ventana.blit (grafico, destino)
  else:
    # TODO: Asegurarse de si hay que tener en cuenta la posici�n del cursor
    ancho   = ((tope[0] - cursor[0]) * 6)  # Anchura del dibujo
    alto    = ((tope[1] - cursor[1]) * 8)  # Altura del dibujo
    destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
    if centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
      destino[0] += (ancho - grafico.get_width()) // 2
    # Los gr�ficos pueden dibujar hasta dos p�xeles m�s all� de la �ltima columna de texto
    if ancho < grafico.get_width() and subventana[0] + tope[0] == 53:
      ancho += max (2, grafico.get_width() - ancho)
    ventana.blit (grafico, destino, (0, 0, ancho, alto))
  actualizaVentana()
  # TODO: Ver si hay que actualizar la posici�n del cursor (puede que no)

def elige_subventana (numero):
  """Selecciona una de las subventanas"""
  global elegida
  elegida = numero
  if traza:
    prn ('Subventana', elegida, 'elegida, en', subventanas[elegida],
         'con topes', topes[elegida], 'y cursor en', cursores[elegida])

def espera_tecla (tiempo = 0):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  pygame.time.set_timer (pygame.USEREVENT, tiempo * 1000)  # Ponemos el timer
  while True:
    evento = pygame.event.wait()
    if evento.type == pygame.KEYDOWN:
      if ((evento.key < 256) and (chr (evento.key) in teclas_edicion)) or evento.key in teclas_kp or evento.key in teclas_mas_256:
          pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
          return evento.key
    elif evento.type == pygame.USEREVENT:  # Tiempo de espera superado
      pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
      return None
    redimensiona_ventana (evento)

def carga_cursor ():
  """Carga la posici�n del cursor guardada de la subventana elegida """
  mueve_cursor (*cursores_at[elegida])

def guarda_cursor ():
  """Guarda la posici�n del cursor de la subventana elegida """
  cursores_at[elegida] = tuple (cursores[elegida])

def hay_grafico (numero):
  """Devuelve si existe el gr�fico de n�mero dado"""
  try:
    pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
  except Exception as e:
    if traza:
      prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
      prn (e)
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
  elif espaciar and cursores[elegida][1] >= topes[elegida][1] - 2 and cursores[elegida][0]:
    prompt = '\n' + prompt  # Dejaremos una l�nea en blanco entre el �ltimo texto y el prompt
  # El prompt se imprimir� en la siguiente l�nea de la subventana de entrada
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
    borra_pantalla (True)
  if not subv_input or opcs_input & 2:  # Realimentaci�n permanente de la orden, junto al texto del juego
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
    banderas_antes  = [0,] * 256
    banderas_viejas = set (range (256))
    # Seleccionamos el color de impresi�n
    fuente.set_palette (((0, 192, 192), (0, 0, 0)))
    # Imprimimos los �ndices de cada bandera
    for num in range (256):
      columna = 320 + ((num // 25) * 42)
      fila    = (num % 25) * 8
      cadena = str (num).zfill (3).translate (iso8859_15_a_fuente)
      for pos in range (3):
        c = ord (cadena[pos])
        ventana.blit (fuente, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
  for num in range (256):
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

def imprime_cadena (cadena, scroll = True, redibujar = True):
  """Imprime una cadena en la posici�n del cursor (dentro de la subventana)

El cursor deber� quedar actualizado.

Si scroll es True, se desplazar� el texto del buffer hacia arriba (scrolling) cuando se vaya a sobrepasar la �ltima l�nea"""
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
    cadena = cambiada
  elif cambia_brillo:
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
    elif restante > 0:
      linea.append (chr (ordinal + juego))
      restante -= 1
    else:  # Hay que partir la l�nea, desde el �ltimo car�cter de espacio
      for i in range (len (linea) - 1, -1, -1):  # Desde el final al inicio
        if ord (linea[i]) == 16:  # Este car�cter es un espacio
          lineas.append (''.join (linea[:i]))
          linea = linea[i + 1:]
          iniLineas.append (iniLineas[-1] + i)
          break
      else:  # Ning�n car�cter de espacio en la l�nea
        if len (linea) == tope[0]:  # La l�nea nunca se podr� partir limpiamente
          # La partimos suciamente (en mitad de palabra)
          lineas.append   (''.join (linea))
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
  # TODO: Esperar si se escriben m�s l�neas que las que caben en la subventana
  #       i.e. paginar con pausa
  lineasAsubir = cursor[1] + len (lineas) - tope[1]
  if lineasAsubir > 0:  # Hay que desplazar el texto ese n�mero de l�neas
    scrollLineas (lineasAsubir, subventana, tope)
    cursor[1] -= lineasAsubir  # Actualizamos el cursor antes de imprimir
  # Imprimimos la cadena l�nea por l�nea
  for i in range (len (lineas)):
    if i > 0:  # Nueva l�nea antes de cada una, salvo la primera
      cursor = [0, cursor[1] + 1]
      cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
    if cambia_brillo:
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores, inicioLinea = iniLineas[i])
    else:
      imprime_linea (lineas[i], redibujar = redibujar)
  if lineas:  # Hab�a alguna l�nea
    if cadena[-1] == '\n':  # La cadena terminaba en nueva l�nea
      cursor = [0, cursor[1] + 1]
    else:
      cursor = [cursor[0] + len (lineas[-1]), cursor[1]]
    cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
  if traza:
    prn ('Fin de impresi�n, cursor en', cursor)

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
    ventana.blit (guion_bajo, (destinoX + (posInput * 6), destinoY), (0, 0, 6, 8))
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

def mueve_cursor (columna, fila = cursores[elegida][1]):
  """Cambia de posici�n el cursor de la subventana elegida"""
  cursores[elegida] = [columna, fila]
  subventana        = subventanas[elegida]
  tope              = topes[elegida]
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope,
         'y cursor movido a', cursores[elegida])

def prepara_topes (columnas, filas):
  """Inicializa los topes al n�mero de columnas y filas dado"""
  global topes, topes_gfx
  limite[0] = columnas                  # Ancho m�ximo absoluto de cada subventana
  limite[1] = filas                     # Alto m�ximo absoluto de cada subventana
  topes     = [[columnas, filas],] * 8  # Topes relativos de cada subventana de impresi�n
  topes_gfx = [columnas,  filas]        # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0

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
    cursores[i]    = [0, 0]
    subventanas[i] = [0, 0]
    topes[i]       = list (limite)
  topes_gfx = list (limite)
  if traza:
    prn ('Subventanas reiniciadas a [0, 0] con topes', limite,
         'y cursor en [0, 0]')


# Funciones auxiliares que s�lo se usan en este m�dulo

def parseaColores (cadena):
  """Procesa los c�digos de control de colores, devolviendo la cadena sin ellos, y un diccionario posici�n: colores a aplicar"""
  if not cambia_brillo:
    return cadena, {}
  brillo     = 0      # Sin brillo por defecto
  papel      = 0      # Color de papel/fondo por defecto (negro)
  tinta      = 7      # Color de tinta por defecto (blanco)
  sigBrillo  = False  # Si el siguiente car�cter indica si se pone o quita brillo al color de tinta
  sigFlash   = False  # Si el siguiente car�cter indica si se pone o quita efecto flash
  sigPapel   = False  # Si el siguiente car�cter indica el color de papel/fondo
  sigTinta   = False  # Si el siguiente car�cter indica el color de tinta
  sinColores = ''     # Cadena sin los c�digos de control de colores
  colores    = {0: (paleta[brillo][tinta], (0, 0, 0))}
  for i in range (len (cadena)):
    c = ord (cadena[i])
    if sigBrillo or sigFlash or sigPapel or sigTinta:
      if sigBrillo:
        brillo    = 1 if c else 0
        sigBrillo = False
      elif sigFlash:
        sigFlash = False
      elif sigPapel:
        papel    = c % len (paleta[brillo])
        sigPapel = False
      else:
        sigTinta = False
        tinta    = c % len (paleta[brillo])
      colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel])  # Color de tinta y papel a aplicar
    elif c in (cambia_brillo, cambia_flash, cambia_papel, cambia_tinta):
      if c == cambia_brillo:
        sigBrillo = True
      elif c == cambia_flash:
        sigFlash = True
      elif c == cambia_papel:
        sigPapel = True
      else:
        sigTinta = True
    elif cadena[i] in noEnFuente:
      sinColores += noEnFuente[cadena[i]]
    else:
      sinColores += cadena[i]
  if version_info[0] < 3:  # La versi�n de Python es 2.X
    sinColores = sinColores.encode ('iso-8859-15')
  return sinColores, colores

def scrollLineas (lineasAsubir, subventana, tope, redibujar = True):
  """Hace scroll gr�fico del n�mero dado de l�neas, en la subventana dada, con topes dados"""
  destino = (subventana[0] * 6, subventana[1] * 8)  # Posici�n de destino
  origenX = subventana[0] * 6  # Coordenada X del origen (a subir)
  origenY = (subventana[1] + lineasAsubir) * 8  # Coordenada Y del origen
  anchura = tope[0] * 6  # Anchura del �rea a subir
  altura  = (tope[1] - lineasAsubir) * 8  # Altura del �rea a subir
  # Copiamos las l�neas a subir
  ventana.blit (ventana, destino, (origenX, origenY, anchura, altura))
  # Borramos el hueco
  origenY = (subventana[1] + tope[1] - lineasAsubir) * 8
  altura  = lineasAsubir * 8
  ventana.fill ((0, 0, 0), (origenX, origenY, anchura, altura))
  if redibujar:
    actualizaVentana()
