#-------------------------------------------------------------------------------
# Name:        svg_load.py (SAMPLE)
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Purpose:     Show an alternative for loading SVG items in a QGraphicsScene().
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

from bases import *

SVG_STRING = \
"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="173.51591"
   height="159.04889"
   id="svg2"
   version="1.1"
   inkscape:version="0.48.2 r9819"
   sodipodi:docname="New document 1">
  <defs
     id="defs4" />
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="0.75605469"
     inkscape:cx="203.88545"
     inkscape:cy="62.356727"
     inkscape:document-units="px"
     inkscape:current-layer="layer1"
     showgrid="false"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0"
     inkscape:window-width="1287"
     inkscape:window-height="741"
     inkscape:window-x="70"
     inkscape:window-y="-9"
     inkscape:window-maximized="1" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-171.11455,-65.326444)">
    <path
       sodipodi:type="star"
       style="fill:#ffff00;fill-opacity:0.96862745;stroke:#000000;stroke-width:4;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
       id="path3755"
       sodipodi:sides="5"
       sodipodi:cx="220.88348"
       sodipodi:cy="278.60864"
       sodipodi:r1="108.37708"
       sodipodi:r2="54.188541"
       sodipodi:arg1="0.41450687"
       sodipodi:arg2="1.0428254"
       inkscape:flatsided="false"
       inkscape:rounded="0"
       inkscape:randomized="0"
       d="m 320.08266,322.25628 -71.89999,3.16211 -38.15632,61.02213 -25.22567,-67.4038 -69.82645,-17.43195 56.30967,-44.81995 -4.9988,-71.79567 60.02695,39.70355 66.73703,-26.94022 -19.21097,69.3581 z"
       inkscape:transform-center-x="2.7838802"
       inkscape:transform-center-y="5.5012238"
       transform="matrix(0.82976036,0,0,0.77414485,77.37296,-76.33266)" />
  </g>
</svg>
"""

class GxSVGItem(QGraphicsPixmapItem):
    """
    Provides a way of loading SVG items on a QGraphicsScene keeping
    the transparency right.

    It achieves that by loading the SVG into a pixmap, process in which
    the transparent area is maked properly. Then, the paint() method
    render the SVG on top of the pixmap - allowing it to be scalable.
    """
    def __init__(self, svg_data='', parent=None, scene=None):
        """
        Creates it's pixmap based on some SVG content. Such SVG is stored
        in the self.svg_renderer attribute.

        svg_data: string. It has two interpretations:
            (1) Initing with "<". The SVG is load from raw data, i.e., all
                the SVG content must be in this string.
            (2) Else, it treats as a filename, from which the SVG will be
                loaded.
            Currently the integrity of this values IS NOT cheked.

        parent: QGraphicsItem().
        scene: QGraphicsScene().
        """
        QGraphicsPixmapItem.__init__(self, parent, scene)

        if svg_data and len(svg_data) > 0 and svg_data[0] == '<':
            render_source = QByteArray().append(QString(svg_data))
        else:
            render_source = svg_data    # here, its a filename

        # creates the renderer based on some SVG string or filename
        self.svg_renderer = QSvgRenderer(render_source)

        pix = QPixmap(self.svg_renderer.defaultSize())
        pix.fill(Qt.transparent)

        self.svg_renderer.render(QPainter(pix),
                                 QRectF(self.svg_renderer.viewBox()))

        self.setPixmap(pix)

    def paint(self, painter, option, widget=None):
        """
        QGraphicsPixmapItem.paint()

        This complete overwrite QGraphicsPixmapItem.paint()!!!
        It uses the svg_renderer to draw the image using the painter.
        """
        self.svg_renderer.render(painter, QRectF(self.svg_renderer.viewBox()))

        if self.isSelected():
            self.drawSelectionRect(painter)

    def drawSelectionRect(self, painter):
        """
        Draws the selection rectangle mark. This was done by the original
        paint() method, but it was overwritten.

        RE-IMPLEMENT this if you want different shapes.

        painter: QPainter().
        """
        painter.setBrush(QBrush(Qt.transparent))
        painter.setPen(QPen(Qt.DashLine))
        painter.drawRect(self.boundingRect())


def main():
    app = QApplication([])

    scene = BaseScene()

    # default way on PyQt of loading SVG graphics in to a scene  ---------
    q_svg_item = QGraphicsSvgItem()
    q_svg_item.setSharedRenderer(QSvgRenderer(
        QByteArray().append(QString(SVG_STRING))))
    q_svg_item.setFlags(QGraphicsItem.ItemIsSelectable |
                       QGraphicsItem.ItemIsMovable)
    q_svg_item.setPos(100, 100)
    scene.addItem(q_svg_item)

    # loading the improved version ---------------------------------------
    svg_item = GxSVGItem(SVG_STRING)
    svg_item.setPos(200, 200)
    svg_item.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)
    scene.addItem(svg_item)

    view = BaseView(scene)
    view.setDragMode(QGraphicsView.RubberBandDrag)
    view.setGeometry(200, 200, 700, 500)
    view.show()

    app.exec_()


if __name__ == '__main__':
    main()