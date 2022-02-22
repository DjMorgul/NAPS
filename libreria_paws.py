# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a de PAWS (parte com�n a editor, compilador e int�rprete)
# Copyright (C) 2020-2022 Jos� Manuel Ferrer Ortiz
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

from bajo_nivel import *


# Variables que se exportan (fuera del paquete)

# Ponemos los m�dulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y n�mero de par�metros) de los sistemas m�s nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_paws', 'condactos_quill')

atributos      = []   # Atributos de los objetos
conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Nombre y adjetivo de los objetos
num_objetos    = [0]  # N�mero de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso
vocabulario    = []   # Vocabulario

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (
  ('carga_bd',     ('pdb',), 'Bases de datos PAWS'),
  ('carga_bd_sna', ('sna',), 'Imagen de memoria de ZX 48K con PAWS'),
)
# Funci�n que crea una nueva base de datos (vac�a)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

EXT_SAVEGAME     = 'pgp'   # Extensi�n para las partidas guardadas
INDIRECCION      = False   # El parser no soporta indirecci�n (para el IDE)
LONGITUD_PAL     = 5       # Longitud m�xima para las palabras de vocabulario
NOMBRE_SISTEMA   = 'PAWS'  # Nombre de este sistema
NUM_ATRIBUTOS    = [8]     # N�mero de atributos de objeto
NUM_BANDERAS     = 256     # N�mero de banderas del parser
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposici�n', 'Conjunci�n', 'Pronombre')


alinear          = False       # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad   = True        # Modo de compatibilidad con los int�rpretes originales
conversion       = {}          # Tabla de conversi�n de caracteres
despl_ini        = 0           # Desplazamiento inicial para cargar desde memoria
fin_cadena       = ord ('\n')  # Car�cter de fin de cadena
nueva_linea      = ord ('\r')  # Car�cter de nueva l�nea
num_abreviaturas = 128         # N�mero de abreviaturas cuando se comprime el texto

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que �ste no es 0
despl_ini_plat = {
}
plats_LE = (2, )  # Plataformas que son Little Endian (PC)


# Diccionario de condactos

condactos = {
  # El formato es el siguiente:
  # c�digo : (nombre, n�mero_par�metros, es_acci�n)
    0 : ('AT',      1, False),
    1 : ('NOTAT',   1, False),
    2 : ('ATGT',    1, False),
    3 : ('ATLT',    1, False),
    4 : ('PRESENT', 1, False),
    5 : ('ABSENT',  1, False),
    6 : ('WORN',    1, False),
    7 : ('NOTWORN', 1, False),
    8 : ('CARRIED', 1, False),
    9 : ('NOTCARR', 1, False),
   10 : ('CHANCE',  1, False),
   11 : ('ZERO',    1, False),
   12 : ('NOTZERO', 1, False),
   13 : ('EQ',      2, False),
   14 : ('GT',      2, False),
   15 : ('LT',      2, False),
   16 : ('ADJECT1', 1, False),
   17 : ('ADVERB',  1, False),
   18 : ('INVEN',   0, True),
   19 : ('DESC',    0, True),
   20 : ('QUIT',    0, False),  # Se comporta como condici�n, no satisfecha si no termina
   21 : ('END',     0, True),
   22 : ('DONE',    0, True),
   23 : ('OK',      0, True),
   24 : ('ANYKEY',  0, True),
   25 : ('SAVE',    0, True),
   26 : ('LOAD',    0, True),
   27 : ('TURNS',   0, True),
   28 : ('SCORE',   0, True),
   29 : ('CLS',     0, True),
   30 : ('DROPALL', 0, True),
   31 : ('AUTOG',   0, True),
   32 : ('AUTOD',   0, True),
   33 : ('AUTOW',   0, True),
   34 : ('AUTOR',   0, True),
   35 : ('PAUSE',   1, True),
   36 : ('TIMEOUT', 0, False),
   37 : ('GOTO',    1, True),
   38 : ('MESSAGE', 1, True),
   39 : ('REMOVE',  1, True),
   40 : ('GET',     1, True),
   41 : ('DROP',    1, True),
   42 : ('WEAR',    1, True),
   43 : ('DESTROY', 1, True),
   44 : ('CREATE',  1, True),
   45 : ('SWAP',    2, True),
   46 : ('PLACE',   2, False),  # Se comporta como condici�n, no satisfecha al intentar poner un objeto en 255
   47 : ('SET',     1, True),
   48 : ('CLEAR',   1, True),
   49 : ('PLUS',    2, True),
   50 : ('MINUS',   2, True),
   51 : ('LET',     2, True),
   52 : ('NEWLINE', 0, True),
   53 : ('PRINT',   1, True),
   54 : ('SYSMESS', 1, True),
   55 : ('ISAT',    2, False),
   56 : ('COPYOF',  2, True),
   57 : ('COPYOO',  2, True),
   58 : ('COPYFO',  2, True),
   59 : ('COPYFF',  2, True),
   60 : ('LISTOBJ', 0, True),
   61 : ('EXTERN',  1, True),
   62 : ('RAMSAVE', 0, True),
   63 : ('RAMLOAD', 1, True),
   64 : ('BELL',    0, True),   # O BEEP, seg�n la plataforma que sea
   65 : ('PAPER',   0, True),
   66 : ('INK',     0, True),
   67 : ('BORDER',  0, True),
   68 : ('PREP',    1, False),
   69 : ('NOUN2',   1, False),
   70 : ('ADJECT2', 1, False),
   71 : ('ADD',     2, True),
   72 : ('SUB',     2, True),
   73 : ('PARSE',   0, False),  # Se comporta como condici�n, satisfecha con frase inv�lida
   74 : ('LISTAT',  1, True),
   75 : ('PROCESS', 1, True),
   76 : ('SAME',    2, False),
   77 : ('MES',     1, True),
   78 : ('CHARSET', 0, True),
   79 : ('NOTEQ',   2, False),
   80 : ('NOTSAME', 2, False),
   81 : ('MODE',    1, True),
   82 : ('LINE',    1, True),
   83 : ('TIME',    2, True),
   84 : ('PICTURE', 1, True),
   85 : ('DOALL',   1, True),
   86 : ('PROMPT',  1, True),
   87 : ('GRAPHIC', 1, True),
   88 : ('ISNOTAT', 2, False),
   89 : ('WEIGH',   2, True),
   90 : ('PUTIN',   2, True),
   91 : ('TAKEOUT', 2, True),
   92 : ('NEWTEXT', 0, True),
   93 : ('ABILITY', 2, True),
   94 : ('WEIGHT',  1, True),
   95 : ('RANDOM',  1, True),
   96 : ('INPUT',   1, True),
   97 : ('SAVEAT',  0, True),
   98 : ('BACKAT',  0, True),
   99 : ('PRINTAT', 2, True),
  100 : ('WHATO',   0, True),
  101 : ('RESET',   1, True),
  102 : ('PUTO',    1, True),
  103 : ('NOTDONE', 0, True),
  104 : ('AUTOP',   1, True),
  105 : ('AUTOT',   1, True),
  106 : ('MOVE',    1, False),  # Se comporta como condici�n
  107 : ('PROTECT', 0, True),
}


# Funciones que utiliza el IDE o el int�rprete directamente

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
def carga_bd (fichero, longitud):
  preparaPosCabecera ('pdb')
  return cargaBD (fichero, longitud)

# Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
def carga_bd_sna (fichero, longitud):
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum 48K
  # Detectamos la posici�n de la cabecera de la base de datos
  posicion = 0
  fichero.seek (posicion)
  encajeSec = []
  secuencia = (16, None, 17, None, 18, None, 19, None, 20, None, 21)
  c = fichero.read (1)
  while c:
    if secuencia[len (encajeSec)] == None or ord (c) == secuencia[len (encajeSec)]:
      encajeSec.append (c)
      if len (encajeSec) == len (secuencia):
        break
    elif encajeSec:
      del encajeSec[:]
      continue  # Empezamos de nuevo desde este caracter
    c = fichero.read (1)
    posicion += 1
  else:
    return False  # Cabecera de la base de datos no encontrada
  preparaPosCabecera ('sna48k', posicion)
  return cargaBD (fichero, longitud)

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representaci�n imprimible"""
  # TODO: el resto de las secuencias de control
  return cadena.replace ('\n', '\\n')


# Funciones de apoyo de alto nivel

# Carga las abreviaturas
def carga_abreviaturas ():
  global abreviaturas
  abreviaturas = []
  # Vamos a la posici�n de las abreviaturas
  posicion = carga_desplazamiento (CAB_POS_ABREVS)
  if posicion == 0:  # Sin abreviaturas
    return
  fich_ent.seek (posicion)
  for i in range (num_abreviaturas):
    abreviatura = []
    seguir      = True
    while seguir:
      caracter = carga_int1()
      if caracter > 127:
        caracter -= 128
        seguir    = False
      if chr (caracter) in conversion:
        abreviatura.append (conversion[chr (caracter)])
      else:
        abreviatura.append (chr (caracter))
    abreviaturas.append (''.join (abreviatura))
    #prn (i, ' |', abreviaturas[-1], '|', sep = '')

# Carga los atributos de los objetos
def carga_atributos ():
  # Cargamos el n�mero de objetos (no lo tenemos todav�a)
  fich_ent.seek (CAB_NUM_OBJS)
  num_objetos[0] = carga_int1()
  # Vamos a la posici�n de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos.append (carga_int1())

# Carga un conjunto gen�rico de cadenas
# pos_num_cads es la posici�n de donde obtener el n�mero de cadenas
# pos_lista_pos posici�n de donde obtener la lista de posiciones de las cadenas
# cadenas es la lista donde almacenar las cadenas que se carguen
def carga_cadenas (pos_num_cads, pos_lista_pos, cadenas):
  # Cargamos el n�mero de cadenas
  fich_ent.seek (pos_num_cads)
  num_cads = carga_int1()
  # Vamos a la posici�n de la lista de posiciones de cadenas
  fich_ent.seek (carga_desplazamiento (pos_lista_pos))
  # Cargamos las posiciones de las cadenas
  posiciones = []
  for i in range (num_cads):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada cadena
  inicioAbrevs   = 255 - num_abreviaturas  # Primer c�digo de car�cter que es abreviatura
  saltaSiguiente = False                   # Si salta el siguiente car�cter, como ocurre tras algunos c�digos de control
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if (caracter >= inicioAbrevs) and abreviaturas:
        try:
          cadena.append (abreviaturas[caracter - inicioAbrevs])
        except:
          prn (caracter)
          raise
      elif saltaSiguiente or (version == 21 and caracter in (range (16, 21))):  # C�digos de control
        cadena.append (chr (caracter))
        saltaSiguiente = not saltaSiguiente
      elif caracter == nueva_linea:
        cadena.append ('\n')
      elif chr (caracter) in conversion:
        cadena.append (conversion[chr (caracter)])
      else:
        cadena.append (chr (caracter))
    cadenas.append (''.join (cadena))

# Carga las conexiones
def carga_conexiones ():
  # Cargamos el n�mero de localidades
  fich_ent.seek (CAB_NUM_LOCS)
  num_locs = carga_int1()
  # Vamos a la posici�n de la lista de posiciones de las conexiones
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_CNXS))
  # Cargamos las posiciones de las conexiones de cada localidad
  posiciones = []
  for i in range (num_locs):
    posiciones.append (carga_desplazamiento())
  # Cargamos las conexiones de cada localidad
  for posicion in posiciones:
    fich_ent.seek (posicion)
    salidas = []
    while True:
      verbo = carga_int1()  # Verbo de direcci�n
      if verbo == 255:  # Fin de las conexiones de esta localidad
        break
      destino = carga_int1()  # Localidad de destino
      salidas.append ((verbo, destino))
    conexiones.append (salidas)

def carga_localidades_objetos ():
  """Carga las localidades iniciales de los objetos (d�nde est� cada uno)"""
  # Vamos a la posici�n de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def carga_nombres_objetos ():
  """Carga los nombres y adjetivos de los objetos"""
  # Vamos a la posici�n de los nombres de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_NOMS_OBJS))
  # Cargamos el nombre y adjetivo de cada objeto
  for i in range (num_objetos[0]):
    nombres_objs.append ((carga_int1(), carga_int1()))

# Carga las tablas de procesos
# El proceso 0 es la tabla de respuestas
# En los procesos 1 y 2, las cabeceras de las entradas se ignoran
def carga_tablas_procesos ():
  # Cargamos el n�mero de procesos
  fich_ent.seek (CAB_NUM_PROCS)
  num_procs = carga_int1()
  # prn (num_procs, 'procesos')
  # Vamos a la posici�n de la lista de posiciones de los procesos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_PROCS))
  # Cargamos las posiciones de los procesos
  posiciones = []
  for i in range (num_procs):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada tabla de procesos
  for num_proceso in range (num_procs):
    posicion = posiciones[num_proceso]
    fich_ent.seek (posicion)
    cabeceras    = []
    pos_entradas = []
    while True:
      verbo = carga_int1()
      if verbo == 0:  # Fin de este proceso
        break
      cabeceras.append ((verbo, carga_int1()))
      pos_entradas.append (carga_desplazamiento())
    entradas = []
    for num_entrada in range (len (pos_entradas)):
      pos_entrada = pos_entradas[num_entrada]
      fich_ent.seek (pos_entrada)
      entrada = []
      while True:
        condacto = carga_int1()
        if condacto == 255:  # Fin de esta entrada
          break
        if condacto > 127:  # Condacto con indirecci�n
          num_condacto = condacto - 128
        else:
          num_condacto = condacto
        parametros = []
        if num_condacto not in condactos:
          try:
            muestraFallo ('FIXME: Condacto desconocido', 'C�digo de condacto: ' + str (num_condacto) + '\nProceso: ' + str (num_proceso) + '\n�ndice de entrada: ' + str (num_entrada))
          except:
            prn ('FIXME: N�mero de condacto', num_condacto, 'desconocido, en entrada', num_entrada, 'del proceso', num_proceso)
          return
        for i in range (condactos[num_condacto][1]):
          parametros.append (carga_int1())
        entrada.append ((condacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: N�mero distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

# Carga el vocabulario
def carga_vocabulario ():
  # Vamos a la posici�n del vocabulario
  fich_ent.seek (carga_desplazamiento (CAB_POS_VOCAB))
  # Cargamos cada palabra de vocabulario
  while True:
    caracter = carga_int1()
    if caracter == 0:  # Fin del vocabulario
      return
    caracter ^= 255
    palabra   = [chr (caracter)]
    for i in range (4):
      caracter = carga_int1() ^ 255
      palabra.append (chr (caracter))
    # PAWS guarda las palabras de menos de cinco letras con espacios al final
    # PAWS guarda las palabras en may�sculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), carga_int1()))

# Prepara la configuraci�n sobre la plataforma
def prepara_plataforma ():
  global carga_int2, conversion, despl_ini, fin_cadena, guarda_int2, nueva_linea, num_abreviaturas, plataforma, version
  # Cargamos la versi�n del formato de base de datos y el identificador de plataforma
  fich_ent.seek (CAB_VERSION)
  version = carga_int1()
  # fich_ent.seek (CAB_PLATAFORMA)  # Son consecutivos
  plataforma = carga_int1()
  # Detectamos "endianismo"
  if plataforma in plats_LE or version == 21:  # Si el byte de versi�n vale 21, es formato sna
    carga_int2 = carga_int2_le
    bajo_nivel_cambia_endian (le = True)
  else:
    carga_int2 = carga_int2_be
    bajo_nivel_cambia_endian (le = False)
  # Preparamos el desplazamiento inicial para carga desde memoria
  if plataforma == 0 and version == 21:  # Formato sna de Spectrum 48K
    conversion       = {'#': '�', '$': '�', '%': '�', '&': '�', '@': '�', '[': '�', ']': '�', '^': '�', '`': '�', '|': '�', '\x7f': '�', '\x80': ' ', '\x92': u'\u2192', '\x93': u'\u2190', '\x97': '%'}
    despl_ini        = 16357
    fin_cadena       = 31
    nueva_linea      = 7
    num_abreviaturas = 91
    condactos[81]    = ('MODE', 2, True)
  elif plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
  bajo_nivel_cambia_despl (despl_ini)


# Funciones auxiliares que s�lo se usan en este m�dulo

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
def cargaBD (fichero, longitud):
  global fich_ent, long_fich_ent  # Fichero de entrada y su longitud
  fich_ent      = fichero
  long_fich_ent = longitud
  bajo_nivel_cambia_ent (fichero)
  try:
    prepara_plataforma()
    carga_abreviaturas()
    carga_cadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    carga_cadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    carga_cadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    carga_cadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    carga_atributos()
    carga_conexiones()
    carga_localidades_objetos()
    carga_vocabulario()
    carga_nombres_objetos()
    carga_tablas_procesos()
  except:
    return False

# Asigna las "constantes" de desplazamientos (offsets/posiciones) en la cabecera
def preparaPosCabecera (formato, inicio = 0):
  global CAB_VERSION, CAB_PLATAFORMA, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_NUM_PROCS, CAB_POS_ABREVS, CAB_POS_LST_POS_PROCS, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS, CAB_POS_ATRIBS_OBJS, CAB_LONG_FICH
  CAB_VERSION      = inicio + 0  # Versi�n del formato de base de datos
  CAB_PLATAFORMA   = inicio + 1  # Identificador de plataforma e idioma
  CAB_NUM_OBJS     = inicio + 3  # N�mero de objetos
  CAB_NUM_LOCS     = inicio + 4  # N�mero de localidades
  CAB_NUM_MSGS_USR = inicio + 5  # N�mero de mensajes de usuario
  CAB_NUM_MSGS_SYS = inicio + 6  # N�mero de mensajes de sistema
  CAB_NUM_PROCS    = inicio + 7  # N�mero de procesos
  if formato == 'pdb':
    CAB_POS_ABREVS           =  8  # Posici�n de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 10  # Posici�n lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 12  # Posici�n lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 14  # Posici�n lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 16  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 18  # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 20  # Posici�n lista de posiciones de conexiones
    CAB_POS_VOCAB            = 22  # Posici�n del vocabulario
    CAB_POS_LOCS_OBJS        = 24  # Posici�n de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 26  # Posici�n de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 28  # Posici�n de los atributos de los objetos
    CAB_LONG_FICH            = 30  # Longitud de la base de datos
  elif formato == 'sna48k':
    CAB_POS_ABREVS           = inicio + 11  # Posici�n de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 49140        # Posici�n lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 49142        # Posici�n lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 49144        # Posici�n lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 49146        # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 49148        # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 49150        # Posici�n lista de posiciones de conexiones
    CAB_POS_VOCAB            = 49152        # Posici�n del vocabulario
    CAB_POS_LOCS_OBJS        = 49154        # Posici�n de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 49156        # Posici�n de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 49158        # Posici�n de los atributos de los objetos
    CAB_LONG_FICH            = 49160        # Posici�n del siguiente byte tras la base de datos
