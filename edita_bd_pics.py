#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Editor de bases de datos gr�ficas de DAAD
# Copyright (C) 2022-2023 Jos� Manuel Ferrer Ortiz
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

import math
import os
import sys

try:
  from PyQt4.QtCore import *
  from PyQt4.QtGui  import *
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *

import graficos_bitmap


acc_exportar = None  # Acci�n de exportar base de datos gr�fica
dlg_abrir    = None  # Di�logo de abrir imagen
dlg_exportar = None  # Di�logo de exportar base de datos gr�fica
dlg_importar = None  # Di�logo de importar base de datos gr�fica
dlg_guardar  = None  # Di�logo de guardar imagen

filtro_img_def = 1  # �ndice en filtros_img del formato de imagen por defecto
filtros_img    = (('Im�genes BMP', ['bmp'])), ('Im�genes PNG', ['png'])  # Filtros de formatos de imagen soportados para abrir y guardar


class Recurso (QPushButton):
  """Bot�n para cada recurso"""
  def __init__ (self, numRecurso, imagen = None):
    if imagen:
      super (Recurso, self).__init__ (QIcon (QPixmap (imagen)), str (numRecurso))
      self.setIconSize (imagen.rect().size())
    else:
      super (Recurso, self).__init__ (str (numRecurso))
    self.imagen     = imagen
    self.numRecurso = numRecurso

  def contextMenuEvent (self, evento):
    contextual = QMenu (self)
    if self.imagen:
      accImgExportar  = QAction ('&Exportar imagen',  contextual)
      accImgSustituir = QAction ('&Sustituir imagen', contextual)
      accImgExportar.triggered.connect (self.exportarImagen)
      accImgSustituir.triggered.connect (self.importarImagen)
      contextual.addAction (accImgExportar)
      contextual.addAction (accImgSustituir)
    else:
      accImgAnyadir = QAction ('&A�adir imagen', contextual)
      accImgAnyadir.triggered.connect (self.importarImagen)
      contextual.addAction (accImgAnyadir)
    contextual.exec_ (evento.globalPos())

  def exportarImagen (self):
    global dlg_guardar
    filtro = []
    for descripcion, extensiones in filtros_img:
      filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    if not dlg_guardar:  # Di�logo no creado a�n
      dlg_guardar = QFileDialog (ventana, 'Exportar imagen', os.curdir, ';;'.join (filtro))
      dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
      dlg_guardar.setLabelText  (QFileDialog.LookIn,   'Lugares')
      dlg_guardar.setLabelText  (QFileDialog.FileName, '&Nombre:')
      dlg_guardar.setLabelText  (QFileDialog.FileType, 'Filtro:')
      dlg_guardar.setLabelText  (QFileDialog.Accept,   '&Guardar')
      dlg_guardar.setLabelText  (QFileDialog.Reject,   '&Cancelar')
      dlg_guardar.setOption     (QFileDialog.DontConfirmOverwrite)
      dlg_guardar.setOption     (QFileDialog.DontUseNativeDialog)
    dlg_guardar.selectNameFilter (filtro[filtro_img_def])  # Elegimos el formato por defecto
    if dlg_guardar.exec_():  # No se ha cancelado
      indiceFiltro  = list (dlg_guardar.nameFilters()).index (dlg_guardar.selectedNameFilter())
      nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_guardar.selectedFiles()[0])
      extension     = '.' + filtros_img[indiceFiltro][1][0]
      if nombreFichero[- len (extension):].lower() != extension:
        nombreFichero += extension
      if os.path.isfile (nombreFichero):
        dlgSiNo = QMessageBox (ventana)
        dlgSiNo.addButton ('&S�', QMessageBox.YesRole)
        dlgSiNo.addButton ('&No', QMessageBox.NoRole)
        dlgSiNo.setIcon (QMessageBox.Warning)
        dlgSiNo.setWindowTitle ('Sobreescritura')
        dlgSiNo.setText ('Ya existe un fichero con ruta y nombre:\n\n' + nombreFichero)
        dlgSiNo.setInformativeText ('\n�Quieres sobreescribirlo?')
        if dlgSiNo.exec_() != 0:  # No se ha pulsado el bot�n S�
          return
      ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
      self.imagen.save (nombreFichero)
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

  def importarImagen (self):
    global dlg_abrir
    extSoportadas = []  # Todas las extensiones de im�genes soportadas
    filtro        = []
    for descripcion, extensiones in filtros_img:
      filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
      extSoportadas.extend (extensiones)
    filtro.append ('Todas las im�genes soportadas (*.' + ' *.'.join (extSoportadas) + ')')
    if not dlg_abrir:  # Di�logo no creado a�n
      dlg_abrir = QFileDialog (ventana, 'Abrir imagen', os.curdir, ';;'.join (filtro))
      dlg_abrir.setFileMode  (QFileDialog.ExistingFile)
      dlg_abrir.setLabelText (QFileDialog.LookIn,   'Lugares')
      dlg_abrir.setLabelText (QFileDialog.FileName, '&Nombre:')
      dlg_abrir.setLabelText (QFileDialog.FileType, 'Filtro:')
      dlg_abrir.setLabelText (QFileDialog.Accept,   '&Abrir')
      dlg_abrir.setLabelText (QFileDialog.Reject,   '&Cancelar')
      dlg_abrir.setOption    (QFileDialog.DontUseNativeDialog)
    dlg_abrir.selectNameFilter (filtro[len (filtro) - 1])  # Elegimos el filtro de todas las im�genes soportadas
    if dlg_abrir.exec_():  # No se ha cancelado
      ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
      nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_abrir.selectedFiles()[0])
      imagen = QImage (nombreFichero)
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
      if imagen.isNull():
        muestraFallo ('No se puede abrir la imagen del fichero:\n' + nombreFichero)
        return
      if imagen.height() + imagen.width() < 1:
        muestraFallo ('Dimensiones inv�lidas', 'La imagen elegida (' + nombreFichero + u') tiene dimensiones inv�lidas, tanto su ancho como su alto deber�a ser mayor que cero')
        return
      if imagen.height() > graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][1]:
        muestraFallo ('Altura de imagen excesiva', 'La imagen elegida (' + nombreFichero + ') tiene ' + str (imagen.height()) + u' p�xeles de alto, mientras que el modo ' + graficos_bitmap.modo_gfx + u' de la base de datos gr�fica s�lo soporta hasta ' + str (graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][1]))
        return
      if imagen.width() > graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][0]:
        muestraFallo ('Anchura de imagen excesiva', 'La imagen elegida (' + nombreFichero + ') tiene ' + str (imagen.width()) + u' p�xeles de ancho, mientras que el modo ' + graficos_bitmap.modo_gfx + u' de la base de datos gr�fica s�lo soporta hasta ' + str (graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][0]))
        return
      if imagen.height() % 8:
        muestraFallo ('Altura de imagen incorrecta', 'La imagen elegida (' + nombreFichero + ') tiene ' + str (imagen.height()) + u' p�xeles de alto, cuando deber�a ser m�ltiplo de 8')
        return
      if imagen.width() % 8:
        muestraFallo ('Anchura de imagen incorrecta', 'La imagen elegida (' + nombreFichero + ') tiene ' + str (imagen.width()) + u' p�xeles de ancho, cuando deber�a ser m�ltiplo de 8')
        return
      if imagen.depth() > 8:  # No usa paleta indexada
        # Calculamos el n�mero de colores que tiene
        coloresUsados = set()
        ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
        for fila in range (imagen.height()):
          for columna in range (imagen.width()):
            coloresUsados.add (imagen.pixel (columna, fila))
        ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
        numColores    = len (coloresUsados)
        coloresUsados = list (coloresUsados)
      else:
        coloresUsados = imagen.colorTable()
        numColores    = imagen.colorCount()
      if numColores > graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]:
        muestraFallo ('Advertencia: n�mero de colores elevado', 'La imagen elegida (' + nombreFichero + ') utiliza ' + str (numColores) + ' colores diferentes, mientras que el modo ' + graficos_bitmap.modo_gfx + u' de la base de datos gr�fica s�lo soporta ' + str (graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]))
      if self.imagen and graficos_bitmap.recurso_es_unico (self.numRecurso):
        dlgSiNo = QMessageBox (ventana)
        dlgSiNo.addButton ('&S�', QMessageBox.YesRole)
        dlgSiNo.addButton ('&No', QMessageBox.NoRole)
        dlgSiNo.setIcon (QMessageBox.Warning)
        dlgSiNo.setWindowTitle ('Sustituir imagen')
        dlgSiNo.setText ('Esta imagen no es utilizada por ning�n otro recurso')
        dlgSiNo.setInformativeText ('\n�Seguro que quieres sustituirla por la imagen del fichero elegido?')
        if dlgSiNo.exec_() != 0:  # No se ha pulsado el bot�n S�
          return
      paletas = graficos_bitmap.da_paletas_del_formato()
      if len (paletas) > 1:
        muestraFallo ('No implementado', 'El formato de base de datos gr�fica soporta m�s de un modo gr�fico, y la selecci�n de colores para cada modo todav�a no est� implementada')
        return
      paletas = paletas[list (paletas.keys())[0]]

      # Buscamos los colores m�s cercanos de entre las paletas para los colores de la imagen
      masCercanos = []  # �ndice en paleta del color m�s cercano a los usados en la imagen, y su cercan�a, para ambas paletas
      for p in range (len (paletas)):
        masCercanos.append ([])
      for c in range (len (coloresUsados)):
        color = QColor (coloresUsados[c])
        for p in range (len (masCercanos)):
          masCercano = [-1, 999999]  # �ndice de color en paleta, y cercan�a del color m�s cercano en la paleta a �ste
          paleta     = paletas[p]
          for cp in range (len (paleta)):
            rojoPaleta, verdePaleta, azulPaleta = paleta[cp]
            if color.red() == rojoPaleta and color.green() == verdePaleta and color.blue() == azulPaleta:  # Coincidencia exacta
              masCercanos[p].append ((cp, 0))
              break
            else:
              if (color.red() + rojoPaleta) / 2 < 128:
                cercania = math.sqrt (1 * ((color.red() - rojoPaleta) ** 2) + 1 * ((color.green() - verdePaleta) ** 2) + 2 * ((color.blue() - azulPaleta) ** 2))
              else:
                cercania = math.sqrt (2 * ((color.red() - rojoPaleta) ** 2) + 1 * ((color.green() - verdePaleta) ** 2) + 1 * ((color.blue() - azulPaleta) ** 2))
              if cercania < masCercano[1]:
                masCercano = [cp, cercania]
          else:
            masCercanos[p].append (masCercano)

      # Buscamos la paleta m�s adecuada para los colores de la imagen
      if len (masCercanos) > 1:
        mejorCercania = 999999
        mejorPaleta   = None
        for p in range (len (masCercanos)):
          cercania = 0
          for masCercano in masCercanos[p]:
            cercania += masCercano[1]
          if cercania < mejorCercania:
            mejorCercania = cercania
            mejorPaleta   = p
      else:
        mejorPaleta = 0

      # Convertimos la imagen a los colores de la paleta m�s adecuada y la asignamos a este recurso
      ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
      paleta = []
      for rojo, verde, azul in paletas[mejorPaleta]:
        paleta.append (qRgb (rojo, verde, azul))
      imgConvertida = QImage (imagen.width(), imagen.height(), QImage.Format_Indexed8)
      imgConvertida.setColorTable (paleta)
      imgComoIndices = []  # Imagen como �ndices en la paleta
      for fila in range (imagen.height()):
        for columna in range (imagen.width()):
          indiceEnPaleta = masCercanos[mejorPaleta][coloresUsados.index (imagen.pixel (columna, fila))][0]
          imgConvertida.setPixel (columna, fila, indiceEnPaleta)
          imgComoIndices.append (indiceEnPaleta)
      self.imagen = imgConvertida
      self.setIcon (QIcon (QPixmap (imgConvertida)))
      self.setIconSize (imagen.rect().size())
      graficos_bitmap.cambia_imagen (self.numRecurso, imagen.width(), imagen.height(), imgComoIndices, paletas[mejorPaleta])
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

class Ventana (QMainWindow):
  """Ventana principal"""
  def __init__ (self):
    global acc_exportar
    super (Ventana, self).__init__()
    acc_exportar = QAction ('&Exportar', self)
    accImportar  = QAction ('&Importar', self)
    accSalir     = QAction ('&Salir',    self)
    acc_exportar.setEnabled (False)
    acc_exportar.triggered.connect (dialogoExportaBD)
    accImportar.triggered.connect (dialogoImportaBD)
    accSalir.setShortcut ('Ctrl+Q')
    menuArchivo = self.menuBar().addMenu ('&Archivo')
    menuArchivo.addAction (accImportar)
    menuArchivo.addAction (acc_exportar)
    menuArchivo.addSeparator()
    menuArchivo.addAction (accSalir)
    scroll = QScrollArea (self)
    self.rejilla = QWidget (scroll)
    self.rejilla.setLayout (QGridLayout (self.rejilla))
    scroll.setWidget (self.rejilla)
    accSalir.triggered.connect (self.close)
    self.setCentralWidget (scroll)
    self.setWindowTitle ('Editor de bases de datos gr�ficas')
    self.showMaximized()


def dialogoExportaBD ():
  """Exporta la base de datos gr�fica al fichero elegido por el usuario"""
  global dlg_exportar
  if graficos_bitmap.modo_gfx == 'CGA':
    extensiones   = ('.cga',)
    formatoFiltro = 'Bases de datos gr�ficas DAAD para CGA (*.cga)'
  elif graficos_bitmap.modo_gfx == 'EGA':
    extensiones   = ('.ega',)
    formatoFiltro = 'Bases de datos gr�ficas DAAD para EGA (*.ega)'
  elif graficos_bitmap.modo_gfx == 'PCW':
    extensiones   = ('.pcw', '.dat')
    formatoFiltro = 'Bases de datos gr�ficas DAAD para PCW (*.dat *.pcw)'
  elif graficos_bitmap.modo_gfx in ('ST', 'VGA'):
    extensiones   = ('.dat',)
    formatoFiltro = 'Bases de datos gr�ficas DAAD v3 para Amiga/PC (*.dat);;Bases de datos gr�ficas DAAD v3 para Atari ST/STE (*.dat)'
  if not dlg_exportar:  # Di�logo no creado a�n
    dlg_exportar = QFileDialog (ventana, 'Exportar base de datos gr�fica', os.curdir, formatoFiltro)
    dlg_exportar.setAcceptMode (QFileDialog.AcceptSave)
    dlg_exportar.setLabelText  (QFileDialog.LookIn,   'Lugares')
    dlg_exportar.setLabelText  (QFileDialog.FileName, '&Nombre:')
    dlg_exportar.setLabelText  (QFileDialog.FileType, 'Filtro:')
    dlg_exportar.setLabelText  (QFileDialog.Accept,   '&Guardar')
    dlg_exportar.setLabelText  (QFileDialog.Reject,   '&Cancelar')
    dlg_exportar.setOption     (QFileDialog.DontConfirmOverwrite)
    dlg_exportar.setOption     (QFileDialog.DontUseNativeDialog)
  if dlg_exportar.exec_():  # No se ha cancelado
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_exportar.selectedFiles()[0])
    for extension in extensiones:
      if nombreFichero[-4:].lower() == extension:
        break
    else:  # No ten�a extensi�n de las permitidas, se la a�adimos
      nombreFichero += extensiones[0]
    if os.path.isfile (nombreFichero):
      dlgSiNo = QMessageBox (ventana)
      dlgSiNo.addButton ('&S�', QMessageBox.YesRole)
      dlgSiNo.addButton ('&No', QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle ('Sobreescritura')
      dlgSiNo.setText ('Ya existe un fichero con ruta y nombre:\n\n' + nombreFichero)
      dlgSiNo.setInformativeText ('\n�Quieres sobreescribirlo?')
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el bot�n S�
        return
    ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    try:
      fichero = open (nombreFichero, 'wb')
    except IOError as excepcion:
      muestraFallo ('No se puede abrir el fichero:\n' + nombreFichero,
                    'Causa:\n' + excepcion.args[1])
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
      return
    graficos_bitmap.guarda_bd_pics (fichero, ordenAmiga = 'Amiga' in dlg_exportar.selectedNameFilter())
    fichero.close()
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos gr�fica, y lo intenta importar"""
  global dlg_importar
  if not dlg_importar:  # Di�logo no creado a�n
    dlg_importar = QFileDialog (ventana, 'Importar base de datos gr�fica', os.curdir, 'Bases de datos gr�ficas DAAD (*.cga *.dat *.ega *.pcw)')
    dlg_importar.setFileMode  (QFileDialog.ExistingFile)
    dlg_importar.setLabelText (QFileDialog.LookIn,   'Lugares')
    dlg_importar.setLabelText (QFileDialog.FileName, '&Nombre:')
    dlg_importar.setLabelText (QFileDialog.FileType, 'Filtro:')
    dlg_importar.setLabelText (QFileDialog.Accept,   '&Abrir')
    dlg_importar.setLabelText (QFileDialog.Reject,   '&Cancelar')
    dlg_importar.setOption    (QFileDialog.DontUseNativeDialog)
  if dlg_importar.exec_():  # No se ha cancelado
    ventana.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_importar.selectedFiles()[0])
    importaBD (nombreFichero)
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def importaBD (nombreFichero):
  """Importa una base de datos gr�fica desde el fichero de nombre dado"""
  error = graficos_bitmap.carga_bd_pics (nombreFichero)
  if error:
    muestraFallo ('No se puede abrir el fichero:\n' + nombreFichero, error)
    return

  global acc_exportar
  if (graficos_bitmap.modo_gfx in ('CGA', 'EGA', 'PCW')  # Modos gr�ficos de la versi�n 1 de DMG
      or graficos_bitmap.modo_gfx in ('ST', 'VGA') and graficos_bitmap.version > 1):  # Versi�n 3+ de DMG
    acc_exportar.setEnabled (True)
  else:
    acc_exportar.setEnabled (False)

  altoMax  = 0  # Alto  de imagen m�ximo
  anchoMax = 0  # Ancho de imagen m�ximo
  imagenes = []
  for numImg in range (256):
    recurso = graficos_bitmap.recursos[numImg]
    if not recurso:
      imagenes.append (None)
      continue
    paleta = []
    for rojo, verde, azul in recurso['paleta']:
      paleta.append (qRgb (rojo, verde, azul))
    ancho, alto = recurso['dimensiones']
    col    = 0  # Columna actual
    fila   = 0  # Fila actual
    imagen = QImage (ancho, alto, QImage.Format_Indexed8)
    imagen.setColorTable (paleta)
    for indicePaleta in recurso['imagen']:
      imagen.setPixel (col, fila, indicePaleta)
      col += 1
      if col == ancho:
        col   = 0
        fila += 1
    imagenes.append (imagen)
    if alto > altoMax:
      altoMax = alto
    if ancho > anchoMax:
      anchoMax = ancho

  # Borramos botones anteriores si los hab�a
  if ventana.rejilla.layout().count():
    for i in range (255, -1, -1):
      ventana.rejilla.layout().itemAt (i).widget().setParent (None)
    ventana.rejilla.setMinimumSize (0, 0)
    ventana.rejilla.resize (0, 0)

  dtWidget  = QDesktopWidget()  # Para obtener el ancho de la pantalla (dado que el de la ventana no se correspond�a con el real)
  geometria = dtWidget.availableGeometry (ventana)
  margen    = 8
  columnas  = geometria.width() // (anchoMax + margen)
  filas     = math.ceil (256. / columnas)
  ventana.rejilla.setMinimumSize (geometria.width() - 20, (filas * (altoMax + margen) + ((filas + 1) * 6)))

  col  = 0  # Columna actual
  fila = 0  # Fila actual
  for i in range (256):
    imagen = imagenes[i]
    widget = Recurso (i, imagen)
    widget.setMinimumSize (anchoMax + margen, altoMax + margen)
    ventana.rejilla.layout().addWidget (widget, fila, col)
    col += 1
    if col == columnas:
      col   = 0
      fila += 1

def muestraFallo (mensaje, detalle = '', parent = None):
  """Muestra un di�logo de fallo leve"""
  # TODO: sacar a m�dulo com�n con el IDE
  global dlg_fallo, ventana_principal
  try:
    dlg_fallo
  except:  # Di�logo no creado a�n
    if parent == None:
      parent = ventana_principal
    dlg_fallo = QMessageBox (parent)
    dlg_fallo.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_fallo.setIcon (QMessageBox.Warning)
    dlg_fallo.setWindowTitle ('Fallo')
  dlg_fallo.setText (mensaje)
  if detalle:
    dlg_fallo.setInformativeText ('Causa:\n' + detalle)
  else:
    dlg_fallo.setInformativeText ('')
  dlg_fallo.exec_()


aplicacion = QApplication (sys.argv)
ventana    = Ventana()
ventana_principal = ventana  # Para muestraFallo

if len (sys.argv) > 1:
  importaBD (sys.argv[1])

sys.exit (aplicacion.exec_())
