# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones de apoyo de alto nivel
# Copyright (C) 2010, 2021, 2023-2024 Jos� Manuel Ferrer Ortiz
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

import os
import sys


validar = False  # Si queremos validar el funcionamiento correcto del c�digo

# C�digo de cada tipo de palabra por nombre en el c�digo fuente
tipos_pal_dict = {'verb': 0, 'adverb': 1, 'noun': 2, 'adjective': 3, 'preposition': 4, 'conjugation': 5, 'conjunction': 5, 'pronoun': 6}

# Identificadores (para hacer el c�digo m�s legible) predefinidos
IDS_LOCS = {'WORN': 253, 'CARRIED': 254, 'HERE': 255}


def carga_sce (fichero, longitud, LONGITUD_PAL, atributos, atributos_extra, condactos, condactos_nuevos, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, nueva_version, num_objetos, tablas_proceso, vocabulario):
  """Carga la base de datos desde el c�digo fuente SCE del fichero de entrada, con y sobre las variables pasadas como par�metro

  Para compatibilidad con el IDE:
  - Recibe como primer par�metro un fichero abierto
  - Recibe como segundo par�metro la longitud del fichero abierto
  - Devuelve False si ha ocurrido alg�n error"""
  global erExpresiones, erSimbolo, simbolos
  try:
    import lark
  except:
    prn ('Para poder importar c�digo fuente, se necesita la librer�a Lark', 'versi�n <1.0' if sys.version_info[0] < 3 else '', file = sys.stderr)
    return False
  try:
    import re
    codigoSCE    = fichero.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437')
    origenLineas = [[0, 0, codigoSCE.count ('\n') + 1, fichero.name, 0]]  # Inicio en c�digo, inicio en fichero, n� l�neas, ruta, nivel indentanci�n
    # Procesamos carga de ficheros externos con directivas de preprocesador /LNK e #include
    # TODO: extraer el c�digo com�n con abreFichXMessages, a funci�n en bajo_nivel
    encaje = True
    erLnk  = re.compile ('\n(/LNK|[ \t]*#include)[ \t]+([^ \n\t]+)', re.IGNORECASE)
    while encaje:
      encaje = erLnk.search (codigoSCE)
      if not encaje:
        break
      directiva  = encaje.group (1)
      nombreFich = encaje.group (2).lower().replace ('\\', os.sep)
      if '.' not in nombreFich:
        nombreFich += '.sce'
      # Buscamos el fichero con independencia de may�sculas y min�sculas
      rutaCarpeta = os.path.join (os.path.dirname (fichero.name), os.path.dirname (nombreFich))
      nombreFich  = os.path.basename (nombreFich)
      try:
        causa = 'No se encuentra la ruta "' + encaje.group (2)[:- len (nombreFich)] + '" requerida'
        for nombreFichero in os.listdir (rutaCarpeta):
          if os.path.basename (nombreFichero).lower() == nombreFich:
            nombreFich = nombreFichero
            break
        else:
          causa = 'No se encuentra el fichero "' + nombreFich + '" requerido'
          raise TabError
        causa      = 'No se puede abrir el fichero "' + nombreFich + '" requerido'
        ficheroLnk = open (os.path.join (rutaCarpeta, nombreFich), 'rb')
      except:
        prn (causa, 'por la directiva de preprocesador', directiva, encaje.group (2), file = sys.stderr)
        return False
      codigoIncluir = ficheroLnk.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437')
      lineaInicio   = codigoSCE[:encaje.start (0) + 1].count ('\n')  # L�nea donde estaba la directiva, contando desde 0
      lineasIncluir = codigoIncluir.count ('\n') + 1  # N�mero de l�neas del fichero a incluir
      restante      = ''  # C�digo restante detr�s de la directiva
      # Buscamos el bloque de origenLineas donde est� la l�nea de la directiva
      o = 0
      while o < len (origenLineas) and lineaInicio >= (origenLineas[o][0] + origenLineas[o][2]):
        o += 1
      nivelDirectiva = 0  # Nivel de indentaci�n/anidaci�n de esta directiva
      if len (directiva) == 4:  # Es una directiva /LNK
        if lineaInicio > origenLineas[o]:  # Quedar� alguna l�nea en el bloque o de origenLineas
          origenLineas = origenLineas[:o + 1]  # Eliminamos desde este bloque en adelante exclusive
          origenLineas[o][2] = lineaInicio - origenLineas[o][0]  # Reducimos longitud del bloque
        else:  # La directiva estaba en la primera l�nea del bloque
          origenLineas = origenLineas[:o]  # Eliminamos desde este bloque en adelante inclusive
      else:  # Es una directiva include
        nivelDirectiva = origenLineas[o][4]
        if o < len (origenLineas) - 1:  # Hay m�s bloques detr�s de �ste, as� que los extraemos
          finalOrigLineas = origenLineas[o + 1:]
          origenLineas    = origenLineas[:o + 1]
        else:  # Era el �ltimo bloque
          finalOrigLineas = []
        # Guardamos las l�neas restantes en el fichero de este bloque, omitiendo la l�nea del include
        lineasRestantes     = origenLineas[o][2] - (lineaInicio + 1 - origenLineas[o][0])
        origenLineas[o][2] -= lineasRestantes + 1  # Reducimos longitud del bloque, el resto ir� en otro
        # FIXME: caso cuando la directiva est� en la primera l�nea del bloque
        nlTrasDirectiva     = codigoSCE.find ('\n', encaje.end (0))
        if nlTrasDirectiva > -1:  # Hay m�s c�digo detr�s de la directiva
          restante = codigoSCE[nlTrasDirectiva + (1 if codigoIncluir[-1] == '\n' else 0):]
      # A�adimos bloque del fichero que se incluye
      if codigoIncluir[-1] == '\n':  # La �ltima l�nea del fichero a incluir es en blanco
        lineasIncluir -= 1
      nivelIncluir = nivelDirectiva + codigoSCE.find ('#', encaje.start (0) + 1) - (encaje.start (0) + 1)  # Nivel de indentaci�n del fichero a incluir
      origenLineas.append ([lineaInicio, 0, lineasIncluir, os.path.normpath (ficheroLnk.name), nivelIncluir])
      # A�adimos los bloques posteriores
      if len (directiva) > 4:  # Es una directiva include
        origenLineas.append ([lineaInicio + lineasIncluir, origenLineas[o][1] + origenLineas[o][2] + 1, lineasRestantes, origenLineas[o][3], nivelDirectiva])
        # Incrementamos la posici�n de los dem�s y los a�adimos al final
        for origenLinea in finalOrigLineas:
          origenLinea[0] = origenLineas[-1][0] + origenLineas[-1][2]
          origenLineas.append (origenLinea)
      # A�adimos si corresponde espacios antes de cada directiva del fichero a incluir
      erDirect = re.compile ('\n([ \t]*)#')  # Expresi�n regular para detectar directivas de preprocesador con #
      if nivelIncluir:
        codigoIncluir = erDirect.sub ('\n' + (' ' * nivelIncluir) + '\g<1>#', codigoIncluir)
      codigoSCE = codigoSCE[:encaje.start (0) + 1] + codigoIncluir + restante
      ficheroLnk.close()
      # Comprobamos que las l�neas de codigoSCE corresponden con las l�neas de los ficheros seg�n origenLineas
      if validar:
        lineasCodigo = codigoSCE.split ('\n')
        for inicioCod, inicioFich, numLineas, rutaFichero, nivelIndent in origenLineas:
          ficheroPrueba = open (rutaFichero, 'rb')
          lineasFichero = ficheroPrueba.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437').split ('\n')
          for n in range (numLineas):
            if inicioFich + n == len (lineasFichero):
              prn ('El fichero', rutaFichero, 'sale en origenLineas con m�s l�neas de las que tiene', file = sys.stderr)
              break
            lineaCodigo  = lineasCodigo[inicioCod + n]
            lineaFichero = lineasFichero[inicioFich + n]
            if erDirect.match ('\n' + lineasFichero[inicioFich + n]):
              lineaFichero = (' ' * nivelIndent) + lineaFichero
            if lineaCodigo != lineaFichero:
              prn (origenLineas, file = sys.stderr)
              prn ('La l�nea', inicioCod + n + 1, 'cargada no corresponde con la l�nea', inicioFich + n + 1, 'del fichero', rutaFichero, file = sys.stderr)
              contexto = 1  # L�neas de contexto que mostrar
              prn (lineasCodigo[inicioCod + n - contexto : inicioCod + n + contexto + 1], file = sys.stderr)
              prn ('versus', file = sys.stderr)
              prn (lineasFichero[inicioFich + n - contexto : inicioFich + n + contexto + 1], file = sys.stderr)
              sys.exit()
          ficheroPrueba.close()
    # Procesamos las dem�s directivas de preprocesador
    erExpresiones = re.compile ('([^ +-]+|[+-])')          # Expresi�n regular para partir expresiones de #define
    erPartirPals  = re.compile ('[ \t]+([^ \t]+)')         # Expresi�n regular para partir por palabras
    erSimbolo     = re.compile ('[A-Z_a-z][0-9A-Z_a-z]*')  # Expresi�n regular para detectar etiquetas de s�mbolos
    simbolos      = {'AMIGA': 0, 'C40': 0, 'C42': 0, 'C53': 1, 'CBM64': 0, 'CGA': 0, 'COLS': 53, 'CPC': 0, 'DEBUG': 0, 'DRAW': 0, 'EGA': 0, 'ENGLISH': 0, 'MSX': 0, 'PC': 1, 'PCW': 0, 'S48': 0, 'SP3': 0, 'SPANISH': 1, 'SPE': 0, 'ST': 0, 'VGA': 1}
    lineasCodigo  = codigoSCE.split ('\n')
    bloqueOrigen  = 0  # N�mero de bloque de la l�nea actual en origenLineas
    for numLinea in range (len (lineasCodigo)):
      if numLinea == origenLineas[bloqueOrigen][0] + origenLineas[bloqueOrigen][2]:
        bloqueOrigen += 1
      lineaCodigo = lineasCodigo[numLinea].lstrip()
      if not lineaCodigo or lineaCodigo[0] == ';' or lineaCodigo[0] != '#':
        continue  # Saltamos l�neas vac�as y sin directivas de preprocesador
      nivelDirect = len (lineasCodigo[numLinea]) - len (lineaCodigo)  # Nivel de indentaci�n/anidaci�n de la directiva
      if ';' in lineaCodigo:  # Quitamos comentarios
        lineaCodigo = lineaCodigo[: lineaCodigo.find (';')]
      if lineaCodigo[:7].lower() == '#define' or lineaCodigo[:4].lower() == '#var':
        encajesLinea = []
        for encaje in erPartirPals.finditer (lineaCodigo[4 if lineaCodigo[:4] == '#var' else 7:]):
          encajesLinea.append (encaje)
          if len (encajesLinea) > 1:
            break
        if not encajesLinea or encajesLinea[0].start():
          raise TabError ('espacio en blanco' + ('' if encajesLinea else ' y una etiqueta de s�mbolo'), (), (numLinea + 1, 8))
        simbolo = encajesLinea[0].group (1)
        if not erSimbolo.match (simbolo):
          raise TabError ('una etiqueta de s�mbolo v�lida', (), (numLinea + 1, 8 + encajesLinea[0].start (1)))
        if simbolo in simbolos and lineaCodigo[:4] != '#var':
          raise TabError ('El s�mbolo "%s" ya estaba definido', simbolo, (numLinea + 1, 8 + encajesLinea[0].start (1)))
        if len (encajesLinea) < 2:
          raise TabError ('expresi�n para definir el valor del s�mbolo', (), (numLinea + 1, len (lineaCodigo) + 1))
        valorExpr = daValorExpresion (lineaCodigo[7 + encajesLinea[1].start (1):], numLinea + 1, 8 + encajesLinea[1].start (1))
        # Asignamos el valor al s�mbolo, y comentamos la l�nea
        # TODO: cuando el IDE muestre l�neas con comentarios y directivas de preprocesador, marcar diferenciando entre l�neas deshabilitadas y procesadas
        simbolos[simbolo]      = valorExpr
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada esta l�nea
      elif lineaCodigo[:3].lower() == '#if':
        encajesLinea = []
        for encaje in erPartirPals.finditer (lineaCodigo[3:]):
          encajesLinea.append (encaje)
          if len (encajesLinea) > 1:
            break
        if not encajesLinea or encajesLinea[0].start():
          raise TabError ('espacio en blanco' + ('' if encajesLinea else ' y una etiqueta de s�mbolo'), (), (numLinea + 1, 4))
        simbolo = encajesLinea[0].group (1)
        if simbolo[0] == '!':
          negado  = True
          simbolo = simbolo[1:]
        else:
          negado = False
        if not erSimbolo.match (simbolo):
          raise TabError ('una etiqueta de s�mbolo v�lida', (), (numLinea + 1, 4 + encajesLinea[0].start (1) + (1 if negado else 0)))
        if simbolo in simbolos:
          satisfecho = simbolos[simbolo]
          if negado:
            satisfecho = not satisfecho
          for numLineaCond in range (numLinea + 1, len (lineasCodigo)):
            lineaCond = lineasCodigo[numLineaCond].lstrip()
            nivelCond = len (lineasCodigo[numLineaCond]) - len (lineaCond)  # Nivel de indentaci�n/anidaci�n de esta l�nea
            if nivelCond == nivelDirect:
              if lineaCond[:6].lower() == '#endif':
                lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Ya procesada esta l�nea
                break
              if lineaCond[:5].lower() == '#else':
                lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Ya procesada esta l�nea
                satisfecho = not satisfecho
                continue
            if satisfecho:  # Se cumple la condici�n de la directiva #if
              if lineaCond[:1] != '#' and lineasCodigo[numLineaCond][:1] == ' ':  # No es directiva y empieza por espacio
                # Quitamos un nivel de indentaci�n para que se pueda procesar correctamente la sintaxis de la l�nea
                lineasCodigo[numLineaCond] = lineasCodigo[numLineaCond][1:]
            else:  # No se cumple la condici�n de la directiva #if
              lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Deshabilitada esta l�nea
        else:
          raise TabError ('un s�mbolo ya definido', (), (numLinea + 1, 4 + encajesLinea[0].start (1)))
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada la l�nea de la directiva #if
      elif lineaCodigo[:5].lower() == '#echo':
        prn (lineaCodigo[6:])
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada esta l�nea
      else:
        raise TabError ('una directiva de preprocesador v�lida', (), (numLinea + 1, 1))
    parserSCE = lark.Lark.open ('gramatica_sce.lark', __file__, propagate_positions = True)
    arbolSCE  = parserSCE.parse ('\n'.join (lineasCodigo))
    # Cargamos cada tipo de textos
    for idSeccion, listaCadenas in (('stx', msgs_sys), ('mtx', msgs_usr), ('otx', desc_objs), ('ltx', desc_locs)):
      for seccion in arbolSCE.find_data (idSeccion):
        numEntrada = 0
        for entrada in seccion.find_data (idSeccion + 'textentry'):
          if type (entrada.children[0]) == lark.tree.Tree:
            numero = daValorExpresion (entrada.children[0].children)
          else:
            numero = int (entrada.children[0])
          if numero != numEntrada:
            raise TabError ('n�mero de entrada %d en lugar de %d', (numEntrada, numero), entrada.meta)
          lineas = []
          for lineaTexto in entrada.children[1:]:
            if lineaTexto.type == 'COMMENT':
              continue  # Omitimos comentarios reconocidos por la gram�tica
            linea = str (lineaTexto)
            if not lineas and linea[:2] == '\n;':
              continue  # Omitimos comentarios iniciales
            lineas.append (linea[1:])  # El primer car�cter siempre ser� \n
          # Evitamos tomar nueva l�nea antes de comentario final como l�nea de texto en blanco
          if lineas and not linea and codigoSCE[lineaTexto.start_pos + 1] == ';':
            del lineas[-1]
          for l in range (len (lineas) - 1, 0, -1):
            if lineas[l][:1] == ';':
              del lineas[l]  # Eliminamos comentarios finales
            else:
              break
          # Unimos las cadenas como corresponde
          cadena = ''
          for linea in lineas:
            if linea:
              cadena += ('' if cadena[-1:] in ('\n', '') else ' ') + linea
            else:
              cadena += '\n'
          listaCadenas.append (cadena)
          numEntrada += 1
    # Cargamos el vocabulario
    adjetivos     = {'_': 255}
    adverbios     = {}
    nombres       = {'_': 255}
    preposiciones = {}
    verbos        = {'_': 255}
    tipoParametro = {'j': (adjetivos, 'adjetivo'), 'n': (nombres, 'nombre'), 'r': (preposiciones, 'preposici�n'), 'v': (adverbios, 'adverbio'), 'V': (verbos, 'verbo')}
    for seccion in arbolSCE.find_data ('vocentry'):
      palabra = str (seccion.children[0])[:LONGITUD_PAL].lower()
      codigo  = int (seccion.children[1])
      tipo    = tipos_pal_dict[str (seccion.children[2].children[0]).lower()]
      vocabulario.append ((palabra, codigo, tipo))
      # Dejamos preparados diccionarios de c�digos de palabra para verbos, nombres y adjetivos
      if tipo == 0:
        verbos[palabra] = codigo
      elif tipo == 1:
        adverbios[palabra] = codigo
      elif tipo == 2:
        nombres[palabra] = codigo
        if codigo < 20:
          verbos[palabra] = codigo
      elif tipo == 3:
        adjetivos[palabra] = codigo
      elif tipo == 4:
        preposiciones[palabra] = codigo
    # Cargamos las conexiones entre localidades
    numEntrada = 0
    for seccion in arbolSCE.find_data ('conentry'):
      if seccion.children[0].type == 'UINT':
        numero = int (seccion.children[0])
      else:  # Es un s�mbolo
        simbolo = str (seccion.children[0])
        if simbolo in simbolos:
          numero = simbolos[simbolo]
        else:
          raise TabError ('un s�mbolo ya definido', (), seccion.children[0])
      if numero != numEntrada:
        raise TabError ('n�mero de localidad %d en lugar de %d', (numEntrada, numero), seccion.meta)
      salidas = []
      for conexion in seccion.find_data ('conitem'):
        verbo = str (conexion.children[0].children[0])[:LONGITUD_PAL].lower()
        if verbo not in verbos:
          raise TabError ('una palabra de vocabulario de tipo verbo', (), conexion.children[0])
        if conexion.children[1].type == 'UINT':
          destino = int (conexion.children[1])
        else:  # Es un s�mbolo
          simbolo = str (conexion.children[1])
          if simbolo in simbolos:
            destino = simbolos[simbolo]
          else:
            raise TabError ('un s�mbolo ya definido', (), conexion.children[1])
        if destino >= len (desc_locs):
          raise TabError ('n�mero de localidad entre 0 y %d', len (desc_locs) - 1, conexion.children[1])
        salidas.append ((verbos[verbo], destino))
      conexiones.append (salidas)
      numEntrada += 1
    if numEntrada != len (desc_locs):
      raise TabError ('el mismo n�mero de entradas de conexi�n (%d) que de descripciones de localidades (%d)', (numEntrada, len (desc_locs)))
    # Cargamos datos de los objetos
    numEntrada = 0
    for seccion in arbolSCE.find_data ('objentry'):
      if seccion.children[0].type == 'UINT':
        numero = int (seccion.children[0])
      else:  # Es un s�mbolo
        simbolo = str (seccion.children[0])
        if simbolo not in simbolos:
          raise TabError ('un s�mbolo ya definido', (), seccion.children[0])
        numero = simbolos[simbolo]
      if numero != numEntrada:
        raise TabError ('n�mero de objeto %d en lugar de %d', (numEntrada, numero), seccion.meta)
      # Cargamos la localidad inicial del objeto
      if seccion.children[1].children:
        localidad = seccion.children[1].children[0]
        if localidad.type == 'INT':
          locs_iniciales.append (int (localidad))
        elif localidad.type == 'SYMBOL':
          simbolo = str (localidad)
          if simbolo not in simbolos:
            raise TabError ('un s�mbolo ya definido', (), localidad)
          locs_iniciales.append (simbolos[simbolo])
        else:  # Valor no num�rico (p.ej. CARRIED)
          locs_iniciales.append (IDS_LOCS[str (localidad)])
      else:
        locs_iniciales.append (252)
      # Cargamos el peso del objeto
      entero = seccion.children[2]
      peso   = int (entero)
      if peso < 0 or peso > 63:
        raise TabError ('valor de peso del objeto %d entre 0 y 63', numEntrada, entero)
      # Cargamos los atributos del objeto
      valorAttrs = ''
      for atributo in seccion.find_data ('attr'):
        valorAttrs += '1' if atributo.children else '0'
      if len (valorAttrs) > 18:
        raise TabError ('N�mero de atributos para el objeto %d excesivo, NAPS s�lo soporta hasta 18', numEntrada, entero, 1)
      # Soportamos entre 2 y 18 atributos dejando a cero los que no se indiquen
      valorAttrs += '0' * (18 - len (valorAttrs))
      atributos.append (peso + ((valorAttrs[0] == '1') << 6) + ((valorAttrs[1] == '1') << 7))
      atributos_extra.append (int (valorAttrs[2:], 2))
      # Cargamos el vocabulario del objeto
      palabras = []
      for word in seccion.find_data ('word'):
        palabra = str (word.children[0])[:LONGITUD_PAL].lower() if word.children else '_'
        palabras.append (palabra)
        if len (palabras) == 1 and palabra not in nombres:
          break  # Para conservar la posici�n de la primera palabra inexistente
      if palabras[0] not in nombres or palabras[1] not in adjetivos:
        raise TabError ('una palabra de vocabulario de tipo %s', 'adjetivo' if len (palabras) > 1 else 'nombre', word.meta)
      nombres_objs.append ((nombres[palabras[0]], adjetivos[palabras[1]]))
      numEntrada += 1
    if numEntrada != len (desc_objs):
      raise TabError ('el mismo n�mero de objetos (%d) que de descripciones de objetos (%d)', (numEntrada, len (desc_objs)))
    num_objetos[0] = numEntrada
    # Preparamos c�digo y par�metros en cada versi�n, de los condactos, indexando por nombre
    datosCondactos = {}
    for listaCondactos in (condactos, condactos_nuevos):
      for codigo in listaCondactos:
        condacto = listaCondactos[codigo]
        if condacto[0] not in datosCondactos:
          datosCondactos[condacto[0]] = [None, None]
        datosCondacto = (codigo, condacto[1])
        if not condactos_nuevos:  # Para sistemas distintos a DAAD
          datosCondactos[condacto[0]][0] = datosCondacto
        elif condacto[4] == 3:  # El condacto es igual en ambas versiones
          datosCondactos[condacto[0]] = (datosCondacto, datosCondacto)
        else:
          datosCondactos[condacto[0]][condacto[4] - 1] = datosCondacto
    # Cargamos las tablas de proceso
    numProceso = 0
    version    = 0  # Versi�n de DAAD necesaria, 0 significa compatibilidad con ambas
    for seccion in arbolSCE.find_data ('pro'):
      entero = seccion.children[0]
      if type (entero) == lark.tree.Tree:
        numero = daValorExpresion (entero.children)
      else:
        numero = int (entero)
      if numero != numProceso:
        raise TabError ('n�mero de proceso %d en lugar de %d', (numProceso, numero), entero)
      # Guardamos las posiciones de las etiquetas de entrada
      etiquetas  = {}
      numEntrada = 0
      for procentry in seccion.find_data ('procentry'):
        for label in procentry.find_data ('label'):
          if label.children:
            etiquetas[label.children[0][1:]] = numEntrada
        numEntrada += 1
      # Cargamos cada entrada del proceso
      cabeceras = []
      entradas  = []
      for procentry in seccion.find_data ('procentry'):
        palabras = []
        for word in procentry.find_data ('word'):
          palabra = str (word.children[0])[:LONGITUD_PAL].lower() if word.children else '_'
          palabras.append (palabra)
          if len (palabras) == 1 and palabra not in verbos:
            break  # Para conservar la posici�n de la primera palabra inexistente
        if palabras[0] not in verbos or palabras[1] not in nombres:
          raise TabError ('una palabra de vocabulario de tipo %s', 'nombre' if len (palabras) > 1 else 'verbo', word.meta)
        cabeceras.append ((verbos[palabras[0]], nombres[palabras[1]]))
        entrada = []
        for condacto in procentry.find_data ('condact'):
          indireccion = 0  # Tomar� valor 128 cuando el condacto se use con indirecci�n
          nombre = str (condacto.children[0])
          if nombre not in datosCondactos:
            raise TabError ('Condacto de nombre %s inexistente', nombre, condacto.meta)
          parametros = []
          for param in condacto.find_data ('param'):
            if param.children:
              parametro = param.children[0]
              if type (parametro) == lark.tree.Tree:
                if str (parametro.data) == 'expression':  # Es una expresi�n
                  parametros.append (daValorExpresion (parametro.children))
                else:  # Es una regla de indirecci�n
                  if not condactos_nuevos:
                    raise TabError ('Este sistema no soporta indirecci�n de par�metros', (), parametro)
                  if parametros:
                    raise TabError ('S�lo se soporta indirecci�n en el primer par�metro', (), parametro)
                  indireccion = 128
                  valor = parametro.children[0]
                  if type (valor) == lark.tree.Tree:  # Es una expresi�n
                    parametros.append (daValorExpresion (valor.children))
                  else:  # Es un entero
                    parametros.append (int (valor))
              elif parametro.type == 'INT':
                parametros.append (int (parametro))
              elif parametro.type == 'VOCWORD':
                # TODO: tolerar esto en caso que la palabra del par�metro sea �nica en el vocabulario
                if version:
                  if not datosCondactos[nombre][version - 1]:
                    break  # Se comprueba esto de nuevo m�s adelante
                  tipoParam       = datosCondactos[nombre][version - 1][1][len (parametros) : len (parametros) + 1]
                  palabraAdmitida = tipoParam in tipoParametro
                else:
                  palabraAdmitida = False
                  for datoCondacto in datosCondactos[nombre]:
                    if datosCondacto and datoCondacto[1][len (parametros) : len (parametros) + 1] in tipoParametro:
                      palabraAdmitida = True
                      break
                if not palabraAdmitida:
                  # Podr�a ser una expresi�n en lugar de una palabra de vocabulario
                  simbolo = str (parametro)
                  if simbolo in simbolos:
                    parametros.append (simbolos[simbolo])
                  elif '+' in simbolo or '-' in simbolo:  # Parece ser una expresi�n
                    parametros.append (daValorExpresion (simbolo, parametro.line, parametro.column))
                  else:
                    raise TabError ('El condacto %s no admite una palabra de vocabulario como par�metro aqu�', nombre, parametro)
                if palabraAdmitida:
                  # Salvo SYNONYM, los condactos con este tipo de par�metro s�lo tienen uno de igual tipo en ambas versiones de DAAD
                  palabra      = str (parametro)[:LONGITUD_PAL].lower()
                  letraTipoPal = datosCondactos[nombre][1][1][len (parametros)]
                  listaVocab, tipoPalabra = tipoParametro[letraTipoPal]
                  if palabra not in listaVocab:
                    raise TabError ('una palabra de vocabulario de tipo %s', tipoPalabra, parametro)
                  parametros.append (listaVocab[palabra])
              elif parametro.type == 'LABEL':
                etiqueta = str (parametro[1:])
                if etiqueta not in etiquetas:
                  raise TabError ('una etiqueta existente en este proceso', (), parametro)
                salto = etiquetas[etiqueta] - len (entradas) - 1
                if salto < -127 or salto > 128:
                  raise TabError ('una etiqueta m�s cercana', (), parametro)
                if salto < 0:
                  salto += 256
                parametros.append (salto)
              else:  # Valores preestablecidos (p.ej. CARRIED)
                parametros.append (IDS_LOCS[str (parametro)])
            else:
              parametros.append (255)  # Es _
          # Detectamos incompatibilidades por requerirse versiones de DAAD diferentes
          versionAntes = version
          if version:
            if not datosCondactos[nombre][version - 1]:
              raise TabError ('Condacto de nombre %s inexistente en DAAD versi�n %d (asumida por condactos anteriores)', (nombre, version), condacto.meta)
            # La comprobaci�n del n�mero de par�metros se hace abajo
            entrada.append ((datosCondactos[nombre][version - 1][0] + indireccion, parametros))
          else:
            # Fijamos versi�n de DAAD si el condacto con ese nombre s�lo est� en una
            if not datosCondactos[nombre][0] or not datosCondactos[nombre][1]:
              version = 1 if datosCondactos[nombre][0] else 2
            elif len (parametros) != len (datosCondactos[nombre][0][1]) and len (parametros) != len (datosCondactos[nombre][1][1]):
              if len (datosCondactos[nombre][0][1]) == len (datosCondactos[nombre][1][1]):
                requerido = len (datosCondactos[nombre][0][1])
              else:
                requerido = ' o '.join (sorted ((len (datosCondactos[nombre][0][1]), len (datosCondactos[nombre][1][1]))))
              raise TabError ('El condacto %s requiere %d par�metro%s', (nombre, requerido, '' if requerido == 1 else 's'), condacto.meta)
            # Fijamos versi�n de DAAD si el condacto con ese n�mero de par�metros s�lo est� en una
            elif len (datosCondactos[nombre][0][1]) != len (datosCondactos[nombre][1][1]):
              version = 1 if len (parametros) == len (datosCondactos[nombre][0][1]) else 2
            entrada.append ((datosCondactos[nombre][0][0] + indireccion, parametros))
            # TODO: poner a condactos anteriores con c�digo diferente entre versiones, el de la versi�n 2
            if version == 2:
              pass
          # Comprobamos el n�mero de par�metros
          if version and len (parametros) != len (datosCondactos[nombre][version - 1][1]):
            requerido = len (datosCondactos[nombre][version - 1][1])
            raise TabError ('El condacto %s requiere %d par�metro%s en DAAD versi�n %d (asumida por %s)', (nombre, requerido, '' if requerido == 1 else 's', version, 'condactos anteriores' if version == versionAntes else ('este mismo condacto, que s�lo existe en la versi�n ' + str (version))), condacto.meta)
        entradas.append (entrada)
      tablas_proceso.append ((cabeceras, entradas))
      numProceso += 1
    if version == 2:
      condactos.update (condactos_nuevos)
      nueva_version.append (True)
    return
  except (TabError, lark.UnexpectedCharacters, lark.UnexpectedInput) as e:
    detalles      = ''
    numColumna    = None
    numLinea      = None
    textoPosicion = ''
    if type (e) == TabError:  # Es un error detectado por NAPS
      descripcion   = e.args[0]
      paramsFormato = e.args[1]
      if descripcion[0].islower():
        descripcion = 'Se esperaba ' + descripcion
      descripcion = descripcion % paramsFormato
      if len (e.args) > 2:
        posicion = e.args[2]
        numLinea = posicion[0] if type (posicion) == tuple else posicion.line
        if len (e.args) == 3:
          numColumna = posicion[1] if type (posicion) == tuple else posicion.column
    else:  # Es un error detectado por la librer�a Lark
      descripcion = str (e)
      posLineaCol = descripcion.find (', at line ')
      if posLineaCol > -1:  # El mensaje de error indica la l�nea del error
        inicioDetalles = descripcion.find ('\n', posLineaCol)
        if inicioDetalles > -1:  # El mensaje de error tiene m�s de una l�nea
          detalles    = descripcion[inicioDetalles:]
          descripcion = descripcion[:inicioDetalles]
        lineaColLark = descripcion[posLineaCol + 10:].split()
        descripcion  = descripcion[:posLineaCol]
        numLinea     = int (lineaColLark[0])
        if len (lineaColLark) > 2 and lineaColLark[1] == 'col':  # El mensaje de error indica la columna del error
          numColumna = lineaColLark[2]
    if numLinea != None:  # Disponemos del n�mero de l�nea del error
      # Buscamos el bloque de origenLineas donde est� la l�nea del error
      o = 0
      while o < len (origenLineas) and numLinea > (origenLineas[o][0] + origenLineas[o][2]):
        o += 1
      inicioCod, inicioFich, numLineas, rutaFichero, nivelIndent = origenLineas[o]
      textoPosicion  = ', en l�nea ' + str (inicioFich + numLinea - inicioCod)
      if numColumna != None:
        textoPosicion += ' columna ' + str (numColumna)
      textoPosicion += ' de ' + rutaFichero
    prn ('Formato del c�digo fuente inv�lido o no soportado:', descripcion + textoPosicion + detalles, file = sys.stderr, sep = '\n')
  except UnicodeDecodeError as e:
    prn ('Error de codificaci�n en el c�digo fuente, que debe usar codificaci�n cp437:', e, file = sys.stderr, sep = '\n')
  except:
    pass
  return False

def comprueba_nombre (modulo, nombre, tipo):
  """Devuelve True si un nombre est� en un m�dulo, y es del tipo correcto"""
  if (nombre in modulo.__dict__) and (type (modulo.__dict__[nombre]) == tipo):
    return True
  return False


# Funciones auxiliares que s�lo se usan en este m�dulo

def daValorExpresion (exprOpartesExpr, numLinea = None, colInicial = None):
  """Eval�a y devuelve el valor de una expresi�n compuesta por s�mbolos, operadores y/o n�meros"""
  operador   = None  # Operador pendiente de aplicar
  valorExpr  = None  # Valor hasta el momento de la expresi�n
  paramEsStr = type (exprOpartesExpr) in (str, str if sys.version_info[0] > 2 else unicode)
  partesExpresion = erExpresiones.finditer (exprOpartesExpr) if paramEsStr else exprOpartesExpr
  for parte in partesExpresion:
    parteExpr = parte.group (0) if paramEsStr else str (parte)
    if valorExpr == None or operador != None:  # No tenemos valor o bien ya tenemos valor y operador
      if parteExpr.isdigit():
        numero = int (parteExpr)
      elif erSimbolo.match (parteExpr):
        if parteExpr in simbolos:
          numero = simbolos[parteExpr]
        else:
          raise TabError ('un s�mbolo ya definido', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
      else:
        raise TabError ('n�mero o etiqueta de s�mbolo', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
      if valorExpr == None:  # No ten�amos valor
        valorExpr = numero
      elif operador == '+':  # Ya ten�amos valor y operador
        valorExpr += numero
      else:
        valorExpr -= numero
      operador = None
    else:  # Tenemos valor pero no hay operador
      if parteExpr in '+-':
        operador = parteExpr
      else:
        raise TabError ('operador de suma o resta', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
  return valorExpr
