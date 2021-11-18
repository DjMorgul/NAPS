#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Int�rprete de sistemas PAW-like
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

from prn_func import prn

import argparse  # Para procesar argumentos de l�nea de comandos
import codecs    # Para codificar bien la salida est�ndar
import locale    # Para codificar bien la salida est�ndar
import os        # Para obtener la longitud del fichero de base de datos
import random    # Para choice y seed
import sys       # Para exit, salida est�ndar, y argumentos de l�nea de comandos


# Variables de estado del int�rprete

banderas     = []     # Banderas del sistema
conjunciones = []     # Palabras que son conjunciones
doall_activo = []     # Si hay bucle DOALL activo, guarda puntero al condacto DOALL activo
frases       = []     # Buffer de �rdenes parseadas por ejecutar, cuando el jugador tecle� m�s de una
locs_objs    = []     # Localidades de los objetos
orden        = ''     # Orden a medio obtener (para tiempo muerto)
orden_psi    = ''     # Parte de la orden entrecomillada
partida      = []     # Partida guardada mediante RAMSAVE
pila_procs   = []     # Pila con estado de los procesos en ejecuci�n
proceso_acc  = False  # Guarda si el proceso ejecut� alguna acci�n adecuada
proceso_ok   = None   # Guarda si el proceso ha terminado con DONE u OK (True), NOTDONE (False) o ninguno de estos (None)
pronombre    = ''     # Alguna palabra que sea pronombre

modulos = []     # M�dulos de condactos cargados
traza   = False  # Si queremos una traza de la ejecuci�n

frase_guardada = []     # Tendr� valor verdadero cuando se est� ejecutando la segunda frase introducida o posterior
hay_asterisco  = False  # Si est� la palabra '*', 1, 255 en el vocabulario, en sistema PAWS no compilado (con editor)
texto_nuevo    = []     # Tendr� valor verdadero cuando se haya escrito texto nuevo tras el �ltimo borrado de pantalla


# Funciones auxiliares para los m�dulos de condactos

def busca_condacto (firma):
  """Busca en los m�dulos de condactos la funci�n donde est� implementado el condacto con la firma dada"""
  for modulo in modulos:
    if firma in modulo.__dict__:
      return modulo.__dict__[firma]
  prn ('FIXME: Condacto con firma', firma, 'no implementado')
  sys.exit()

def cambia_articulo (texto, mayusculas = False):
  if not texto:
    return texto
  articulo = texto.split()[0].lower()
  if articulo in ('a', 'an', 'some'):  # Art�culos en ingl�s
    return texto[len (articulo) + 1:]  # Quita el art�culo
  elif articulo in ('um', 'uma', 'uns', 'umas'):  # Art�culos en portugu�s
    if articulo == 'uns':
      texto = 'os ' + texto[4:]
    elif articulo == 'um':
      texto = 'o ' + texto[3:]
    else:
      texto = texto[2:]
  elif articulo == 'un':
    texto = 'el ' + texto[3:]
  elif compatibilidad:
    if articulo[:2] == 'un':
      texto = 'l' + texto[2:]  # XXX: verificado que lo hace as� el int�rprete original
  else:
    if articulo == 'una':
      texto = 'la ' + texto[4:]
    elif articulo == 'unas':
      texto = 'las ' + texto[5:]
    elif articulo == 'unos':
      texto = 'los ' + texto[5:]
  if mayusculas:
    return texto[0].upper() + texto[1:]
  return texto

def da_peso (objeto, nivel = 0):
  """Devuelve el peso total del objeto dado, teniendo en cuenta que puede ser un contenedor"""
  peso = atributos[objeto] & 63  # Peso del objeto
  if peso and atributos[objeto] & 64 and nivel < 10:  # Es un contenedor con peso (si no tiene, no cuenta contenido)
    for i in range (len (locs_objs)):
      if locs_objs[i] == objeto:
        peso += da_peso (i, nivel + 1)
  return peso

def imprime_mensaje (texto):
  objetoReferido = ''
  if banderas[51] < len (desc_objs):
    objetoReferido = desc_objs[banderas[51]]
    if '.' in objetoReferido:
      objetoReferido = objetoReferido[:objetoReferido.index ('.')]
  if NOMBRE_SISTEMA == 'DAAD':
    iniParte = 0
    partes   = []
    for i in range (len (texto)):
      if texto[i] in ('\x0b', '\x0c'):  # Equivale a '\b', '\k'
        if i:
          partes.append (texto[iniParte:i])
        partes.append (texto[i])
        iniParte = i + 1
    if iniParte <= i:
      partes.append (texto[iniParte:])
  else:
    partes = [texto]
  for parte in partes:
    if parte == '\x0b':  # Equivale a \b
      busca_condacto ('a0_CLS') ()
    elif parte == '\x0c':  # Equivale a \k
      gui.espera_tecla()
    elif '_' in parte:
      gui.imprime_cadena (parte.replace ('_', cambia_articulo (objetoReferido)))
    elif '@' in parte and NOMBRE_SISTEMA == 'DAAD':
      gui.imprime_cadena (parte.replace ('@', cambia_articulo (objetoReferido, True)))
    else:
      gui.imprime_cadena (parte)

def obj_referido (objeto):
  """Asigna el objeto dado como nuevo objeto referido actual. Usar el valor 255 para limpiar las banderas de objeto referido"""
  if objeto == 255:
    banderas[51] = 255
    for numBandera in range (54, 60 if NOMBRE_SISTEMA == 'DAAD' and atributos_extra else 58):
      banderas[numBandera] = 0
    return
  banderas[51] = objeto
  banderas[54] = locs_objs[objeto]
  banderas[55] = da_peso (objeto)
  banderas[56] = 128 if atributos[objeto] &  64 else 0  # Si es contenedor
  banderas[57] = 128 if atributos[objeto] & 128 else 0  # Si es prenda
  # FIXME: �se pondr�a en la bandera 58 los atributos normales en versi�n de formato 1?
  if NOMBRE_SISTEMA == 'DAAD' and atributos_extra:
    banderas[58] = atributos_extra[objeto] // 256
    banderas[59] = atributos_extra[objeto]  % 256

def parsea_orden (psi):
  """Obtiene e interpreta la orden del jugador para rellenar la sentencia l�gica actual, o la del PSI entrecomillada. Devuelve verdadero en caso de fallo"""
  return prepara_orden (True, psi) == True

def restaura_objetos ():
  """Restaura las localidades iniciales de los objetos, y ajusta el n�mero de objetos llevados (bandera 1)"""
  banderas[1] = 0
  for i in range (num_objetos[0]):
    locs_objs[i] = locs_iniciales[i]
    # La bandera 1, que lleva el n�mero de objetos llevados, pero no puestos
    if locs_objs[i] == 254:  # De paso, contamos los objetos llevados
      banderas[1] += 1

# FIXME: cambiar el int�rprete para registrar si se registr� alguna acci�n o no
def tabla_hizo_algo ():
  """Devuelve si la �ltima tabla que termin�, lo hizo habiendo ejecutado alguna acci�n, o terminando con DONE, pero no con NOTDONE"""
  return proceso_acc


# Funciones que implementan el int�rprete tipo-PAWS

def bucle_daad_nuevo ():
  """Bucle principal del int�rprete, para �ltimas versiones de DAAD"""
  while True:
    inicializa()
    if traza:
      gui.imprime_banderas (banderas)
    tecla_o_fin()
    valor = True
    while valor:
      valor = ejecuta_proceso (0)
      if valor == 7:  # Terminar completamente la aventura
        return
    if valor == False:
      continue  # Se reinicia la aventura
    return

def bucle_paws ():
  """Bucle principal del int�rprete, para PAWS y primeras versiones de DAAD"""
  estado = 0  # Estado del int�rprete
  while True:
    if traza:
      gui.imprime_banderas (banderas)
      tecla_o_fin()

    if estado == 0:  # Inicializaci�n
      inicializa()
      estado = 1
    elif estado == 1:  # Descripci�n de localidad y Proceso 1
      describe_localidad()
      valor = ejecuta_proceso (1)
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == 7:  # Terminar completamente la aventura
        return
      # Si el proceso 1 termina con DESC, seguimos en este estado
      elif valor != True:
        estado = 2
    elif estado == 2:  # Proceso 2 y obtener orden
      valor = ejecuta_proceso (2)
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == 7:  # Terminar completamente la aventura
        return
      elif valor == True:  # Ha terminado con DESC
        estado = 1  # Saltamos a la descripci�n de la localidad
      else:
        if traza:
          gui.imprime_banderas (banderas)
        # Mientras no tengamos una orden v�lida, reiniciaremos este estado
        if obtener_orden() != True:
          estado = 3
    elif estado == 3:  # Incremento de turno y Tabla de respuestas
      incrementa_turno()
      valor = ejecuta_proceso (0)
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == True:  # Ha terminado con DESC
        estado = 1  # Saltamos a la descripci�n de la localidad
      elif valor == 7:  # Terminar completamente la aventura
        return
      elif proceso_ok:  # Ha terminado con DONE u OK
        estado = 2
      # TODO: �parece que en Jabato s� lo hace! Al menos tras un DOALL sin objetos que encajen, y tras un NOTDONE
      elif NOMBRE_SISTEMA == 'PAWS':  # DAAD no busca autom�ticamente en la tabla de conexiones, para eso la aventura debe usar MOVE 38 y dem�s
        estado = 4
      else:
        estado = 5
    elif estado == 4:  # Tabla de conexiones
      if busca_condacto ('c1_MOVE') (38):
        estado = 1
        if traza:
          gui.imprime_banderas (banderas)
      else:
        estado = 5
    elif estado == 5:  # Tablas de respuestas y de conexiones exhaustas, o se termin� con NOTDONE
      if not proceso_acc:  # No se ha ejecutado ninguna "acci�n"
        if banderas[33] >= 14:  # No es verbo de direcci�n
          gui.imprime_cadena (msgs_sys[8])  # No puedes hacer eso
        elif NOMBRE_SISTEMA == 'PAWS':  # DAAD no imprime este mensaje por s� mismo
          gui.imprime_cadena (msgs_sys[7])  # No puedes ir por ah�
      estado = 2

def inicializa ():
  """Hace lo que dice la gu�a t�cnica de PAWS, p�gina 7: 1.- LA INICIALIZACI�N DEL SISTEMA"""

  # Los colores de fondo y el juego de caracteres son seleccionados
  # FIXME

  # Las banderas son puestas a 0, las primeras 248 en el caso de las primeras versiones de DAAD, y todas en los dem�s
  for i in range (248 if NOMBRE_SISTEMA == 'DAAD' and not nueva_version else NUM_BANDERAS):
    banderas[i] = 0
  # excepto:

  # No lo dice la Gu�a T�cnica, pero las localidades de los objetos deben restaurarse a las localidades iniciales
  if NOMBRE_SISTEMA != 'DAAD' or not nueva_version:  # Pero en nuevas versiones de DAAD, s�lo RESET lo hace
    restaura_objetos()

  # La bandera 37, contiene el n�mero de objetos llevados, que se pondr� en 4
  banderas[37] = 4
  # La bandera 52, lleva el m�ximo peso permitido, que se pone a 10
  banderas[52] = 10
  # Las banderas 46 y 47, que llevan el pronombre actual, que se pondr�n en 255
  # (no hay pronombre)
  banderas[46] = 255
  banderas[47] = 255

  del gui.historial[:]

  if NOMBRE_SISTEMA == 'DAAD' or (NOMBRE_SISTEMA == 'PAWS' and extension == '.sna'):
    gui.reinicia_subventanas()  # Inicializamos las subventanas de impresi�n
    if NOMBRE_SISTEMA == 'DAAD':
      # La subventana predeterminada es la 1
      gui.elige_subventana (1)
      banderas[63] = 1

  # Permitimos que la librer�a inicialice banderas de modo distinto a la inicializaci�n PAWS est�ndar
  if 'inicializa_banderas' in libreria.__dict__:
    libreria.inicializa_banderas (banderas)

def describe_localidad ():
  """Hace lo que dice la gu�a t�cnica de PAWS, p�gina 7: 2.- DESCRIPCI�N DE LA LOCALIDAD ACTUAL"""
  # Si la bandera 2 no est� a cero, ser� decrementada en 1
  if banderas[2] > 0:
    banderas[2] -= 1

  # Si est� oscuro (que la bandera 0 no es cero) y la bandera 3 no es cero,
  # entonces la bandera 3 es decrementada
  if (banderas[0] > 0) and (banderas[3] > 0):
    banderas[3] -= 1

  # Si est� oscuro, la bandera 4 no est� a cero y el objeto 0 (la fuente de luz)
  # est� ausente, la bandera 4 es decrementada
  if (banderas[0] > 0) and (banderas[4] > 0) and busca_condacto ('c1_ABSENT') (0):
    banderas[4] -= 1

  # Se hace una limpieza de pantalla (clear) si el contenido del modo de
  # pantalla (el que se contiene en la bandera 40) es par
  # Seg�n http://graemeyeandle.atwebpages.com/advent/pawtech.html debe ser as�,
  # en lugar de si no est� a 1, como dec�a la gu�a t�cnica en papel
  if NOMBRE_SISTEMA == 'PAWS' and not banderas[40] & 1:
    if gui.elegida == 2:  # Se hab�a usado PROTECT
      gui.elige_subventana (1)
    gui.borra_pantalla()

  # Si est� oscuro y el objeto 0 est� ausente, entonces el Mensaje del Sistema 0
  # (el que se refiere al mensaje "est� muy oscuro para ver") se imprime
  if (banderas[0] > 0) and busca_condacto ('c1_ABSENT') (0):
    gui.borra_todo()  # TODO: ver si hay que borrar s�lo el gr�fico (subventana 0)
    if NOMBRE_SISTEMA == 'DAAD':
      busca_condacto ('a1_WINDOW') (1)
      gui.mueve_cursor (0, 0)
    gui.imprime_cadena (msgs_sys[0])
  # Si no, cualquier gr�fico presente para la localidad es dibujado, y la
  # descripci�n de la localidad en texto aparecer� sin hacer un NEWLINE
  else:
    if NOMBRE_SISTEMA == 'DAAD':
      if gui.hay_grafico (banderas[38]):
        busca_condacto ('a1_WINDOW') (0)
        gui.borra_pantalla()
        gui.dibuja_grafico (banderas[38], True)
      busca_condacto ('a1_WINDOW') (1)
      if not banderas[40] & 1:
        gui.borra_pantalla()
      else:
        gui.mueve_cursor (0, 0)
    else:
      gui.dibuja_grafico (banderas[38], True)
    if desc_locs[banderas[38]]:
      gui.imprime_cadena (desc_locs[banderas[38]])  # la bandera 38 contiene la localidad actual

def obtener_orden ():
  """Hace lo que dice la gu�a t�cnica de PAWS, p�ginas 8 y 9: 5.- COGER LA FRASE

Devuelve True si la frase no es v�lida o ha ocurrido tiempo muerto (para que vuelva a buscar en la tabla de proceso 2)"""
  # Si las banderas 5 a la 8 no est�n a cero, son decrementadas (la versi�n en espa�ol de la gu�a t�cnica dice de la 7 a la 8, pero es una errata)
  for i in range (5, 9):
    if banderas[i] > 0:
      banderas[i] -= 1

  # Si est� oscuro (la bandera 0 no est� a cero) y la bandera cero no est� a 9,
  # entonces se decrementa
  if (banderas[0] != 0) and (banderas[9] > 0):
    banderas[9] -= 1

  # Si est� oscuro y la bandera 10 no est� a cero, ser� decrementada si el
  # objeto 0 est� ausente
  if (banderas[0] > 0) and (banderas[10] > 0) and busca_condacto ('c1_ABSENT') (0):
    banderas[10] -= 1

  return prepara_orden() != None

def prepara_orden (espaciar = False, psi = False):
  """Prepara una orden de las pendientes de ejecutar u obtiene una nueva

Devuelve True si la frase no es v�lida, False si ha ocurrido tiempo muerto"""
  global frases, orden, orden_psi, traza
  # Borramos las banderas de SL actual
  for i in (tuple (range (33, 37)) + tuple (range (43, 46))):
    banderas[i] = 255
  # Si es orden de PSI o no hay �rdenes ya parseadas pendientes de ejecutar
  if psi or not frases:
    if not psi:
      if frase_guardada:
        del frase_guardada[:]  # Fin de ejecuci�n de frases pendientes de ejecutar
        gui.borra_orden()

      # Si el buffer de input est� vac�o
      if not orden:
        # se imprime el mensaje que contenga la bandera 42.
        if banderas[42] == 0:  # Si tiene un valor igual a 0,
          # los mensajes 2-5 ser�n seleccionados con una frecuencia de
          # 30:30:30:10, respectivamente
          peticion = random.choice ((2, 2, 2, 3, 3, 3, 4, 4, 4, 5))
        else:
          peticion = banderas[42]
        peticion = msgs_sys[peticion]
      else:
        peticion = ''
      # Quitamos la marca de tiempo muerto
      if banderas[49] & 128:
        banderas[49] ^= 128
      # Aunque no lo vea en la Gu�a T�cnica, se imprime el mensaje 33 justo antes de esperar la orden
      timeout = [banderas[48]]
      orden   = gui.lee_cadena (peticion + msgs_sys[33], orden, timeout, espaciar)

      # FIXME: esto es posible que no se haga autom�ticamente (�cuando es desde PARSE en nueva_version?)
      # Si ha vencido el tiempo muerto, el mensaje de sistema 35 aparece, y se
      # vuelve a la b�squeda en la tabla de proceso 2
      if timeout[0] == True:
        # TODO: comentado hasta que se pueda elegir modo de compatibilidad no estricto, porque no veo bien borrar la orden ya escrita
        # if compatibilidad and gui.centrar_graficos:  # En la Aventura Original, la orden se borra cuando hay timeout
        #   orden = ''
        if msgs_sys[35]:  # As� evitamos a�adir una l�nea en blanco sin necesidad
          gui.imprime_cadena (msgs_sys[35])
          gui.imprime_cadena ('\n')
        banderas[49] |= 128  # Indicador de tiempo muerto vencido
        return False

      # Activamos o desactivamos la depuraci�n paso a paso
      if orden.strip().lower() == '*debug*':
        orden = ''
        traza = not traza
        gui.borra_orden()
        return True

    # Una frase es sacada y convertida en una sentencia l�gica, por medio de la
    # conversi�n de cualquier palabra en ella presente, que est� en el
    # vocabulario, a su n�mero de palabra y poni�ndola luego en la bandera
    # requerida
    if psi:
      ordenes = separa_orden (orden_psi)[:1]  # Toma s�lo la primera
    else:
      ordenes = separa_orden (orden)
      if traza:
        prn ('Orden partida en estas frases:', ordenes)
    rango_vocabulario = range (len (vocabulario))
    for f in range (len (ordenes)):
      frase = {'Verbo': None, 'Nombre1': None, 'Nombre2': None, 'Adjetivo1': None, 'Adjetivo2': None, 'Adverbio': None, 'Preposici�n': None, 'Pronombre': None}
      for palabra in ordenes[f]:
        for i in rango_vocabulario:
          if vocabulario[i][0] == palabra:  # Hay encaje con esta palabra
            if vocabulario[i][2] > len (TIPOS_PAL):
              continue
            codigo = vocabulario[i][1]
            tipo   = TIPOS_PAL[vocabulario[i][2]]
            if tipo in ('Verbo', 'Adverbio', 'Preposici�n', 'Pronombre'):
              if not frase[tipo]:
                frase[tipo] = codigo
            elif tipo in ('Nombre', 'Adjetivo'):
              if frase['Pronombre']:
                if not frase['Nombre1'] and not frase['Adjetivo1']:  # Hubo Pronombre antes que Nombre o Adjetivo
                  frase[tipo + '2'] = codigo
              elif frase[tipo + '1']:
                frase[tipo + '2'] = codigo
              else:
                frase[tipo + '1'] = codigo
            else:
              import pdb
              pdb.set_trace()
              pass  # Tipo de palabra inesperado
            break  # No hay palabras de m�s de un tipo, pasamos a la siguiente palabra
      if not frase['Verbo']:
        if frase['Nombre1']:
          if frase['Nombre1'] < 20 and not frase['Preposici�n']:  # Sin verbo, pero con nombre que act�a como verbo
            frase['Verbo'] = frase['Nombre1']
          elif f and frases[-1]['Verbo']:  # Verbo heredado de la frase anterior
            frase['Verbo'] = frases[-1]['Verbo']
        elif NOMBRE_SISTEMA == 'SWAN' and frase['Preposici�n'] and frase['Preposici�n'] < 20:  # Con preposici�n que act�a como verbo
          # TODO: ver si esto ocurre tambi�n en PAWS y/o en DAAD
          frase['Verbo'] = frase['Preposici�n']
      frases.append (frase)
    if len (frases) > 1:
      del texto_nuevo[:]  # Hay m�s de una orden, por lo queremos saber cu�ndo se escribe texto nuevo
  else:  # Hab�a frases pendientes de ejecutar
    frase_guardada.append (True)
  if not frases:  # S�lo se escribi� espacio en blanco, conjunciones o ,.;:
    if not psi and (NOMBRE_SISTEMA != 'DAAD' or not nueva_version):
      gui.imprime_cadena (msgs_sys[6])  # No entend� nada
      gui.borra_orden()
    if psi:
      orden_psi = ''
    else:
      orden = ''
    return True

  frase  = frases.pop (0)
  valida = True
  if frase['Verbo']:
    # Cargamos pronombres
    if frase['Pronombre']:
      if frase['Nombre1']:
        if not frase['Nombre2']:
          frase['Nombre2']   = banderas[46]
          frase['Adjetivo2'] = banderas[47]
      else:
        frase['Nombre1']   = banderas[46]
        frase['Adjetivo1'] = banderas[47]
    # Guardamos las palabras de la frase en las banderas correspondientes
    for flagno, tipo in {33: 'Verbo', 34: 'Nombre1', 35: 'Adjetivo1', 36: 'Adverbio', 43: 'Preposici�n', 44: 'Nombre2', 45: 'Adjetivo2'}.items():
      banderas[flagno] = frase[tipo] if frase[tipo] else 255
    if frase['Nombre1'] and frase['Nombre1'] >= 50:  # Guardamos pronombres, s�lo para nombres considerados no propios (c�digo >= 50)
      banderas[46] = frase['Nombre1']
      banderas[47] = frase['Adjetivo1'] if frase['Adjetivo1'] else 255
    else:
      banderas[46] = 255
      banderas[47] = 255
    # TODO: ver cu�ndo se cambia o vac�a el �ltimo objeto referido
    # XXX: en el PARSE de nueva_version, lo vaciaba tras convertir nombre que actuaba como verbo
  else:
    # Si no se encuentra una frase v�lida, entonces se muestra el mensaje de sistema 6, y vuelve a buscar al proceso 2
    valida = False
    if frase['Nombre1']:
      if NOMBRE_SISTEMA == 'DAAD':
        for flagno, tipo in {34: 'Nombre1', 44: 'Nombre2'}.items():
          banderas[flagno] = frase[tipo] if frase[tipo] else 255
        valida = True
      else:
        gui.imprime_cadena (msgs_sys[8])  # No puedes hacer eso
    elif NOMBRE_SISTEMA != 'DAAD' or not nueva_version:
      gui.imprime_cadena (msgs_sys[6])  # No entend� nada

  if psi:
    orden_psi = ''  # Vaciamos ya la orden
  else:
    if not valida:
      del frases[:]  # Dejamos de procesar frases

    orden         = ''   # Vaciamos ya la orden
    banderas[49] &= 127  # Quitamos el indicador de tiempo muerto vencido
    if not frases:
      gui.borra_orden()

  if not valida:
    return True

def ejecuta_condacto (codigo, parametros):
  """Ejecuta el condacto con el c�digo y par�metros dados

Devuelve el modo en que el condacto altera el flujo de ejecuci�n:
  -X: pasa a ejecutar el subproceso X (como PROCESS)
   0: termina la ejecuci�n y reinicia la aventura (como END)
   1: termina la ejecuci�n y pasa a describir la localidad (como DESC)
   2: reinicia la ejecuci�n de la tabla actual (como REDO de DAAD)
   3: termina la ejecuci�n de la tabla actual con �xito (como DONE)
   4: termina la ejecuci�n de la tabla actual con fallo (como NOTDONE)
   5: termina la ejecuci�n de la tabla actual sin m�s detalle (como fallo GET)
   6: termina la entrada de tabla actual (como una condici�n que no se cumple)
   7: termina completamente la ejecuci�n de la aventura
None: pasa al siguiente condacto"""
  global proceso_acc
  if codigo > 127:  # TODO: S�lo v�lido si la librer�a soporta indirecci�n
    codigo    -= 128
    indirecto  = True
  else:
    indirecto = False
  condacto = libreria.condactos[codigo]
  firma    = ('a' if condacto[2] else 'c') + str (condacto[1]) + '_' + condacto[0]
  funcion  = busca_condacto (firma)
  if indirecto:
    parametros = [banderas[parametros[0]]] + parametros[1:]
  valor = funcion (*parametros)  # El * saca los par�metros de la lista
  if condacto[2] == False:  # El condacto es una condici�n
    if codigo in (20, 46, 106):  # QUIT, PLACE, MOVE
      proceso_acc = True
    if valor == False:  # No se cumple
      return 6
    if valor == True:  # Se cumple
      return None
    return valor  # Permite que condactos se comporten como acci�n y condici�n, como QUIT de PAWS
  if codigo == 103 or (codigo == 85 and valor == 4):  # NOTDONE, o DOALL que termina con NOTDONE
    proceso_acc = False
  elif codigo not in (75, 108, 116):  # PROCESS, REDO, SKIP
    proceso_acc = True
  return valor

def ejecuta_pasos (numPasos):
  """Ejecuta un n�mero dado de pasos de ejecuci�n

Un paso es la comparaci�n de una cabecera o la ejecuci�n de un condacto.

Devuelve True si ha ejecutado DESC o equivalente. False si se debe reiniciar la aventura"""
  global pila_procs, proceso_ok
  for paso in range (numPasos):
    if traza and numPasos > 1 and paso:
      imprime_condacto()
    # Obtenemos los �ndices de tabla, entrada y condacto actuales
    numTabla, numEntrada, numCondacto = pila_procs[-1]
    tabla = tablas_proceso[numTabla]
    cambioFlujo = 0
    if numCondacto == -1 and tabla[0]:  # Toca comprobar la cabecera
      cabecera = tabla[0][numEntrada]
      if (NOMBRE_SISTEMA == 'DAAD' or numTabla not in (1, 2)) and (
          (not hay_asterisco and ((cabecera[0] not in (255, banderas[33])) or (cabecera[1] not in (255, banderas[34])))) or
          (hay_asterisco and ((cabecera[0] not in (1, 255, banderas[33])) or (cabecera[1] not in (1, 255, banderas[34]))))):
         cambioFlujo = 6
      else:
        pila_procs[-1][2] = 0  # Apuntamos al primer condacto
        continue
    if tabla[0]:  # La tabla no est� vac�a
      # Toca ejecutar un condacto (o saltar la entrada si la cabecera no encaja)
      entrada = tabla[1][numEntrada]
      if cambioFlujo == 0:  # La cabecera encaj� (ahora o en su momento)
        cambioFlujo = ejecuta_condacto (entrada[numCondacto][0], entrada[numCondacto][1])
      if traza and (entrada[numCondacto][0] == 24 or (entrada[numCondacto][0] == 73) and nueva_version):
        paso = numPasos  # Dejaremos de ejecutar pasos tras ANYKEY, y tras PARSE en nueva_version
      if type (cambioFlujo) == int:
        if cambioFlujo < 0:  # Ejecutar subproceso
          prepara_tabla_proceso (-cambioFlujo)
          continue
        if cambioFlujo < 2:  # in (0, 1):  # Terminar todo
          del doall_activo[:]
          del pila_procs[:]
          if cambioFlujo == 0:  # Reiniciar aventura
            gui.borra_todo()  # TODO: se hace en DAAD, ver si tambi�n lo hace PAWS
            proceso_ok = None
            return False
          # cambioFlujo == 1:  # Saltar a describir la localidad
          proceso_ok = True  # TODO: comprobar si esto es as�
          return True
        if cambioFlujo == 2:  # Reiniciar tabla actual
          numEntrada  = 0
          numCondacto = -2
        elif cambioFlujo < 6:  # Terminar tabla
          if doall_activo and numTabla == doall_activo[0]:
            numEntrada  = doall_activo[1]
            numCondacto = doall_activo[2] - 1
          else:
            numEntrada  = len (tabla[0])
            numCondacto = -2
          if cambioFlujo == 3:  # Con �xito
            proceso_ok = True
          elif cambioFlujo == 4:  # Con fallo
            proceso_ok = False
          else:  # cambioFlujo == 5:  # Sin m�s detalle
            proceso_ok = None
        elif cambioFlujo == 6:  # Terminar entrada actual
          numCondacto = len (entrada)
        elif cambioFlujo == 7:  # Terminar completamente la aventura
          del pila_procs[:]
          return 7
      elif cambioFlujo != None:  # Saltar al inicio de una entrada contigua
        numEntrada  += cambioFlujo[0] + 1
        numCondacto  = -2
    else:
      entrada = []
    # Pasamos al siguiente condacto
    while True:
      numCondacto += 1
      if numCondacto >= len (entrada):  # Se ha terminado esta entrada
        numCondacto  = -1
        numEntrada  += 1
      if numEntrada >= len (tabla[0]):  # Se ha terminado esta tabla
        pila_procs.pop()
        if not pila_procs:  # No quedan m�s tablas en ejecuci�n
          break
        # Obtenemos los �ndices de tabla, entrada y condacto de la tabla antigua
        numTabla, numEntrada, numCondacto = pila_procs[-1]
        tabla   = tablas_proceso[numTabla]
        entrada = tabla[1][numEntrada]
        continue
      break
    if pila_procs:  # Queda alguna tabla en ejecuci�n
      pila_procs[-1][1] = numEntrada
      pila_procs[-1][2] = numCondacto
    else:
      return
    if paso == numPasos:
      return  # Dejamos de ejecutar el resto de pesos

def ejecuta_proceso (num_proceso):
  """Ejecuta una tabla de proceso hasta que esta termine

Devuelve True si termina con DESC o equivalente. False si hay que reiniciar la aventura"""
  prepara_tabla_proceso (num_proceso)
  while True:
    if traza:
      gui.imprime_banderas (banderas)
      imprime_condacto()
      pasos = tecla_o_fin()  # Ejecutaremos 1, 10, 100 � 1000 pasos a la vez, seg�n qu� se pulse
    else:
      pasos = 10000
    valor = ejecuta_pasos (pasos)
    if valor != None:
      return valor
    if not pila_procs:
      return  # Ha concluido la ejecuci�n de la tabla

def imprime_condacto ():
  """Imprime en la salida est�ndar el siguiente condacto que se ejecutar�"""
  # Obtenemos los �ndices de tabla, entrada y condacto actuales
  num_tabla, num_entrada, num_condacto = pila_procs[-1]
  tabla = tablas_proceso[num_tabla]
  if num_condacto == -1 and not num_entrada and not tabla[0]:  # Tabla vac�a
    prn ('[' + str (num_tabla) + ']')
    return
  prn (pila_procs[-1], ': ', sep = '', end = '')
  # Imprimimos la cabecera si corresponde hacerlo ahora
  if num_condacto == -1:
    cabecera = tabla[0][num_entrada]
    if cabecera[0] == 255:
      prn ('_', end = ' ')
    elif hay_asterisco and cabecera[0] == 1:
      prn ('*', end = ' ')
    else:
      if cabecera[0] < 20:  # Podr�a ser un nombre convertible en verbo
        id_tipos = (cabecera[0], 0), (cabecera[0], 2)
      else:
        id_tipos = ((cabecera[0], 0),)
      for palabra in vocabulario:
        if palabra[1:] in id_tipos:
          prn (palabra[0].rstrip().upper(), end = ' ')
          break
      else:  # Palabra no encontrada, as� que imprimimos el n�mero
        prn (cabecera[0], end = ' ')
    if cabecera[1] == 255:
      prn ('_')
    elif hay_asterisco and cabecera[1] == 1:
      prn ('*')
    else:
      for palabra in vocabulario:
        if palabra[1:] == (cabecera[1], 2):
          prn (palabra[0].rstrip().upper())
          break
      else:  # Palabra no encontrada, as� que imprimimos el n�mero
        prn (cabecera[1])
    return
  entrada = tabla[1][num_entrada]
  condacto, parametros = entrada[num_condacto]
  if condacto > 127:
    condacto -= 128
    indirecto = True
  else:
    indirecto = False
  condacto = libreria.condactos[condacto]
  prn (condacto[0].ljust (7), '@' if indirecto else ' ', end = '')
  for parametro in parametros:
    prn (str (parametro).rjust (3), end = ' ')
  prn()
  if condacto[0] == 'ANYKEY':  # Dejar� las banderas actualizadas al momento de esta pausa
    gui.imprime_banderas (banderas)

def incrementa_turno ():
  """Incrementa el n�mero de turnos jugados"""
  banderas[31] += 1  # LSB
  if banderas[31] > 255:
    banderas[31]  = 0  # LSB
    banderas[32] += 1  # MSB

def prepara_tabla_proceso (num_tabla):
  """Cambia el flujo de ejecuci�n para que se ejecute la tabla de proceso num_tabla"""
  global proceso_acc, proceso_ok
  proceso_acc = False
  if not pila_procs:  # Pila de procesos vac�a
    proceso_ok = None
  pila_procs.append ([num_tabla, 0, -1])  # �ndices de tabla, entrada y condacto
  if len (pila_procs) > 10:
    prn ('ERROR PAW: L�mite alcanzado: anidaci�n m�xima de subprocesos (10)')
    sys.exit()  # Salimos del programa

def separa_orden (orden):
  """Separa la orden por frases y palabras, recortadas a LONGITUD_PAL"""
  # TODO: modo de compatibilidad con c�mo hace DAAD con los pronombres, buscando sufijos -la -lo
  global orden_psi
  comillas = False
  frases   = []
  palabras = []
  palabra  = ''
  for caracter in orden:
    if caracter == '"':
      comillas = not comillas
      if comillas:  # Era apertura de comillas
        orden_psi = ''
    elif comillas:
      orden_psi += caracter
    elif caracter in ' ,.;:':
      if not palabra:
        continue
      if palabra in conjunciones:
        if palabras:
          frases.append (palabras)
          palabras = []
      # FIXME: buscar si la palabra sin el prefijo -la(s) -lo(s) est� en el vocabulario como verbo
      elif palabra[-4:] in ('alas', 'alos', 'elas', 'elos', 'rlas', 'rlos'):
        palabras.append ((palabra[:-3])[:LONGITUD_PAL])
        palabras.append (pronombre)
      elif palabra[-3:] in ('ala', 'alo', 'ela', 'elo', 'rla', 'rlo'):
        palabras.append ((palabra[:-2])[:LONGITUD_PAL])
        palabras.append (pronombre)
      else:
        palabras.append (palabra[:LONGITUD_PAL])
      palabra = ''
      if caracter != ' ' and palabras:
        frases.append (palabras)
        palabras = []
    else:
      palabra += caracter.lower()
  if palabra and palabra not in conjunciones:
    if palabra[-4:] in ('elas', 'elos', 'rlas', 'rlos'):
        palabras.append ((palabra[:-3])[:LONGITUD_PAL])
        palabras.append (pronombre)
    elif palabra[-3:] in ('ela', 'elo', 'rla', 'rlo'):
      palabras.append ((palabra[:-2])[:LONGITUD_PAL])
      palabras.append (pronombre)
    else:
      palabras.append (palabra[:LONGITUD_PAL])
  if palabras:
    frases.append (palabras)
  return frases

def tecla_o_fin ():
  """Espera que el usuario pulse una tecla

Si es Escape termina. Si es D entra en modo depuraci�n de Python.

Para depuraci�n paso a paso, devuelve el n�mero de pasos a ejecutar, que es: 10, 100, 1000 o 1; en funci�n de si la tecla pulsada era Espacio, Tabulador, Enter o cualquier otra; respectivamente"""
  sys.stdout.flush()  # Que se imprima todo lo que quede
  tecla = gui.espera_tecla()
  if tecla == None:
    return 1
  if tecla == gui.pygame.K_ESCAPE:
    sys.exit()  # Salimos del programa
  if tecla == gui.pygame.K_SPACE:
    return 10
  if tecla == gui.pygame.K_TAB:
    return 100
  if tecla in (gui.pygame.K_KP_ENTER, gui.pygame.K_RETURN):
    return 1000
  if tecla == gui.pygame.K_d:  # Depuramos desde Python
    import pdb
    pdb.set_trace()
  return 1


if __name__ == '__main__':
  if sys.version_info[0] < 3:
    reload (sys)  # Necesario para poder ejecutar sys.setdefaultencoding
    sys.stdout = codecs.getwriter (locale.getpreferredencoding()) (sys.stdout)  # Locale del sistema para la salida est�ndar
    sys.setdefaultencoding ('iso-8859-15')  # Nuestras cadenas est�n en esta codificaci�n, no en ASCII
  random.seed()  # Inicializamos el generador de n�meros aleatorios

  argsParser = argparse.ArgumentParser (sys.argv[0], description = 'Int�rprete de Quill/PAWS/SWAN/DAAD en Python')
  argsParser.add_argument ('-D', '--debug', action = 'store_true', help = 'ejecutar los condactos paso a paso')
  argsParser.add_argument ('-g', '--gui', choices = ('pygame', 'stdio'), help = 'interfaz gr�fica a utilizar')
  argsParser.add_argument ('bbdd', metavar = 'base_de_datos', help = 'base de datos de Quill/PAWS/SWAN/DAAD a ejecutar')
  argsParser.add_argument ('ruta_graficos', metavar = 'carpeta_gr�ficos', nargs = '?', help = 'carpeta que contiene las im�genes (con nombre pic###.png)')
  args  = argsParser.parse_args()
  traza = args.debug

  if not args.gui:
    if args.ruta_graficos:
      args.gui = 'pygame'
    else:
      try:
        import pygame
        args.gui = 'pygame'
      except:
        args.gui = 'stdio'
  gui = __import__ ('gui_' + args.gui)

  extension = args.bbdd[-4:].lower()
  if extension in ('.pdb', '.sna'):
    libreria = __import__ ('libreria_paws')
  elif extension == '.adb':
    libreria = __import__ ('libreria_swan')
  else:
    libreria = __import__ ('libreria_daad')

  constantes = ('EXT_SAVEGAME', 'LONGITUD_PAL', 'NOMBRE_SISTEMA', 'NUM_BANDERAS', 'TIPOS_PAL')
  funciones  = ('busca_condacto', 'cambia_articulo', 'da_peso', 'imprime_mensaje', 'obj_referido', 'parsea_orden', 'restaura_objetos', 'tabla_hizo_algo')
  variables  = ('atributos', 'atributos_extra', 'banderas', 'compatibilidad', 'conexiones', 'desc_locs', 'desc_objs', 'doall_activo', 'frases', 'locs_iniciales', 'locs_objs', 'msgs_usr', 'msgs_sys', 'nombres_objs', 'nueva_version', 'num_objetos', 'partida', 'pila_procs', 'tablas_proceso', 'vocabulario')

  # Hacemos lo equivalente a: from libreria import *, cargando s�lo lo exportable
  for lista in (constantes, variables):
    for variable in lista:
      if variable in libreria.__dict__:
        globals()[variable] = libreria.__dict__[variable]

  for modulo in libreria.mods_condactos:
    modulo = __import__ (modulo)
    # Propagamos las constantes y estructuras b�sicas del int�rprete y la librer�a entre los m�dulos de condactos
    modulo.gui = gui
    for lista in (constantes, variables):
      for variable in lista:
        if variable in globals():
          modulo.__dict__[variable] = globals()[variable]
    # Propagamos las funciones auxiliares para los m�dulos de condactos
    for funcion in funciones:
      modulo.__dict__[funcion] = globals()[funcion]
    modulos.append (modulo)

  # Cargamos la base de datos
  bbdd = open (args.bbdd, 'rb')
  if extension == '.sna':
    correcto = libreria.carga_bd_sna (bbdd, os.path.getsize (args.bbdd))
  else:
    correcto = libreria.carga_bd (bbdd, os.path.getsize (args.bbdd))
  if correcto == False:
    prn ('Error al tratar de cargar la base de datos', file = sys.stderr)
    sys.exit()
  bbdd.close()

  if extension == '.sna' or libreria.plataforma == 17:
    gui.prepara_topes (42, 24)
  else:
    gui.prepara_topes (53, 25)

  if args.ruta_graficos:
    gui.ruta_graficos = args.ruta_graficos
    if gui.ruta_graficos[-1] != '/':
      gui.ruta_graficos += '/'

  if NOMBRE_SISTEMA != 'DAAD':
    gui.todo_mayusculas = True
    if NOMBRE_SISTEMA == 'SWAN':
      gui.juego_alto = 48  # @
      gui.juego_bajo = 48
    elif NOMBRE_SISTEMA == 'PAWS' and libreria.num_abreviaturas < 128:  # PAWS de Spectrum
      gui.cambia_brillo = 19
      gui.cambia_flash  = 18
      gui.cambia_papel  = 17
      gui.cambia_tinta  = 16
      # Colores en este orden: negro, azul, rojo, magenta, verde, cyan, amarillo, blanco
      gui.paleta[0].extend (((0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215),  # Sin brillo
                             (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)))
      gui.paleta[1].extend (((0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),  # Con brillo
                             (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)))
      gui.cambia_cursor (msgs_sys[34])
  else:  # Es DAAD
    # Colores con brillo en este orden: negro, azul, rojo, magenta, verde, cyan, amarillo, blanco
    gui.paleta[0].extend (((0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
                           (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)))
    # XXX: apa�o para diferenciar la Aventura Original de aventuras posteriores
    if (len (msgs_usr) > 77 and msgs_usr[77] == '\x0eAVENTURA ORIGINAL I\x0f') or msgs_usr[0] == '\x0eAVENTURA ORIGINAL II\x0f':
      gui.centrar_graficos.append (True)
      gui.juego_alto = 14  # �
      gui.juego_bajo = 15  # �

  # Fallamos ahora si falta alg�n condacto
  if False:
    comprobados = set()
    for tabla in tablas_proceso:
      for entrada in tabla[1]:
        for codigo, parametros in entrada:
          if codigo > 127:
            codigo -= 128
          if codigo in comprobados:
            continue
          condacto = libreria.condactos[codigo]
          firma    = ('a' if condacto[2] else 'c') + str (condacto[1]) + '_' + condacto[0]
          funcion  = busca_condacto (firma)
          comprobados.add (codigo)

  gui.frase_guardada = frase_guardada
  gui.texto_nuevo    = texto_nuevo
  gui.abre_ventana (traza, 'scale2x', args.bbdd)

  # Preparamos las listas banderas, locs_objs y conjunciones
  banderas.extend  ([0,] * NUM_BANDERAS)    # Banderas del sistema
  locs_objs.extend ([0,] * num_objetos[0])  # Localidades de los objetos
  for palabraVoc in vocabulario:
    if palabraVoc[2] < len (TIPOS_PAL):
      tipo = TIPOS_PAL[palabraVoc[2]]
      if tipo == 'Conjunci�n':
        conjunciones.append (palabraVoc[0])
      elif tipo == 'Pronombre':
        pronombre = palabraVoc[0]
    elif NOMBRE_SISTEMA == 'PAWS' and palabraVoc[0] == '*' and palabraVoc[1] == 1 and palabraVoc[2] == 255:
      hay_asterisco = True

  if NOMBRE_SISTEMA == 'DAAD' and nueva_version:
    bucle_daad_nuevo()
  else:
    bucle_paws()

  tecla_o_fin()
