# -*- coding: utf-8 -*-
'''
Created on Apr 4, 2018

@author: jrenken
'''
from qgis.PyQt.QtCore import pyqtSlot
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.PyQt.Qt import Qt
from qgis.core import QgsGeometry, QgsDistanceArea, QgsProject, QgsPoint
from qgis.PyQt.QtWidgets import QToolTip
from math import pi
from qgis.PyQt.QtGui import QGuiApplication


class MeasureMapTool(QgsMapToolEmitPoint):
    '''
    MapTool for measuring distance and azimuth
    Display result as tooltip on the canvas
    '''

    def __init__(self, canvas):
        '''
        Constructor
        '''
        self.canvas = canvas
        super(MeasureMapTool, self).__init__(self.canvas)
        self.canvas.destinationCrsChanged.connect(self.onCrsChange)
        self.distArea = QgsDistanceArea()
        self.distArea.setEllipsoid(u'WGS84')
        self.onCrsChange()
        self.posText = ''

        self.rubberBand = QgsRubberBand(self.canvas)
        self.rubberBand.setZValue(1e6)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.rubberBand.reset()

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())

    def canvasReleaseEvent(self, e):
        self.startPoint = None
        if e.modifiers() == Qt.ControlModifier:
            QGuiApplication.clipboard().setText(self.posText)
        self.reset()

    def canvasMoveEvent(self, e):
        if not self.startPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.rubberBand.setToGeometry(
            QgsGeometry.fromPolyline([
                QgsPoint(self.startPoint),
                QgsPoint(self.endPoint)
            ]),
            None
            )
        if self.startPoint != self.endPoint:
            dist = self.distArea.measureLine(self.startPoint, self.endPoint)
            bearing = self.distArea.bearing(self.startPoint, self.endPoint) * 180 / pi
            if bearing < 0:
                bearing += 360.0
            text = u'{:.1f} m; {:.1f}\u00b0'.format(dist, bearing)
            QToolTip.showText(self.canvas.mapToGlobal(e.pos()), text, self.canvas)

    def activate(self):
        self.reset()
        super(MeasureMapTool, self).activate()

    def deactivate(self):
        self.reset()
        super(MeasureMapTool, self).deactivate()

    @pyqtSlot()
    def onCrsChange(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsDst = self.canvas.mapSettings().destinationCrs()
        self.distArea.setSourceCrs(crsDst, QgsProject.instance().transformContext())

    @pyqtSlot(str)
    def positionUpdate(self, pos):
        self.posText = pos
