#-------------------------------------------------------------------------------
# Name:        engine.py
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Created:     16/09/2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

from bases import *
from svg_load import *
from glued_items import *


SVG_FUNCTION_BLOCK = \
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
   width="591.4375"
   height="81.78125"
   id="svg5056"
   version="1.1"
   inkscape:version="0.48.2 r9819"
   sodipodi:docname="New document 5">
  <defs
     id="defs5058" />
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="0.35"
     inkscape:cx="206.42019"
     inkscape:cy="-344.81267"
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
     id="metadata5061">
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
     transform="translate(-118.57981,-105.76826)">
    <g
       transform="translate(25.04856,450.54951)"
       id="digital_write"
       inkscape:label="#g5037">
      <path
         sodipodi:nodetypes="ccccccccccccccccc"
         inkscape:connector-curvature="0"
         id="path3889"
         d="m 104.80344,-272.8773 c 3.53553,0 92.63099,-0.35355 92.63099,-0.35355 l 10.25305,9.72272 60.28086,-0.17678 10.42982,-10.25305 396.15657,0.53033 9.89949,-10.25305 1e-5,-50.0278 -10.25305,-10.42982 -395.80303,-0.17679 -10.07627,10.60661 -61.51829,-0.35355 -9.36916,-9.8995 -93.16132,0.17678 -10.253035,10.07626 0.176776,50.20459 z"
         style="fill:@FILL_COLOR@;fill-opacity:1;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
      <text
         sodipodi:linespacing="125%"
         id="text3852"
         y="-291.91696"
         x="108.94611"
         style="font-size:@FONT_SIZE@px;font-style:normal;font-weight:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:Sans"
         xml:space="preserve"><tspan
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;fill:#ffffff;font-family:@FONT_FAMILY@;-inkscape-font-specification:Palatino Linotype Bold"
           y="-291.91696"
           x="108.94611"
           id="tspan3854"
           sodipodi:role="line">@BLOCK_NAME@</tspan></text>
    </g>
  </g>
</svg>"""

SVG_INSERTION_MARKER = \
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
   width="385.50787"
   height="23.10881"
   id="svg5384"
   version="1.1"
   inkscape:version="0.48.2 r9819"
   sodipodi:docname="New document 6">
  <defs
     id="defs5386" />
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="0.75605469"
     inkscape:cx="457.31219"
     inkscape:cy="-206.48744"
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
     id="metadata5389">
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
     transform="translate(105.45866,-302.76593)">
    <path
       sodipodi:nodetypes="cccccccccccccc"
       inkscape:connector-curvature="0"
       id="path3889-40"
       d="m 7.7643425,315.78396 c 2.7171805,2.29138 10.0898205,10.09078 10.0898205,10.09078 l 70.97473,-0.0975 9.54307,-9.83333 181.628937,0.38554 c 10e-4,-7.27329 0.0181,-5.31522 0.0483,-13.55042 l -186.796067,-0.0131 -10.07627,10.60661 -61.19095,0.13746 -9.6965,-10.39051 -93.16132,0.17678 -24.398473,-0.0801 -0.18828,13.04827 z"
       style="fill:#333333;fill-opacity:0.96862745;stroke:none" />
  </g>
</svg>
"""

class GxSVGFunctionBlock(GxSVGItem, AbstractGlueableItem):
    """
    This class ilustrates how the multiple inheritance can be useful.
    Here,
    """
    def __init__(self, name='functionName', color='#0078b0', pos=(100,100),
        gb_scene=None):
        """
        svg_data: string. From GxSVGItem.
        gb_scene: GlueableScene().
        """
        self.name = name
        svg_data = SVG_FUNCTION_BLOCK

        self.font_family = 'Palatino Linotype'
        self.font_size = 40

        self.svg_config = {'@FONT_FAMILY@': self.font_family,
            '@FONT_SIZE@': str(self.font_size),
            '@BLOCK_NAME@': str(name), '@FILL_COLOR@': str(color)}

        for k, v in self.svg_config.items():
            svg_data = svg_data.replace(k, v)

        GxSVGItem.__init__(self, svg_data)
        AbstractGlueableItem.__init__(self, gb_scene)

        self.font = QFont(self.font_family, self.font_size-15)
        self.font_metrics = QFontMetrics(self.font)
        self.name_rect = self.font_metrics.boundingRect(self.name)

        edit = QLineEdit()
        edit.setFont(QFont('Consolas', 18))
        proxy_w = QGraphicsProxyWidget(self)
        proxy_w.setWidget(edit)
        proxy_w.setPos(self.name_rect.width() + 30, 20)

        self.setPos(QPointF(pos[0], pos[1]))
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)
    
    def paint(self, painter, option, widget=None):
        GxSVGItem.paint(self, painter, option, widget)
#        painter.setFont(self.font)
#        painter.drawText(self.boundingRect(), Qt.AlignLeft, self.name)


##TODO 1: resize the block based on the funcion name width

##TODO 2: widgets for argument values

##TODO 3: argument


def main():
    app = QApplication(sys.argv)

    gb_scene = GxGlueableScene(insertion_maker = GxSVGItem(
        SVG_INSERTION_MARKER))
    gb_scene.GLUED_ITEMS_PADD = -5

    block_digital_write = GxSVGFunctionBlock('digitalWrite', '#0078b0',
         (100, 100), gb_scene)

    block_delay = GxSVGFunctionBlock('delay', '#ff00b0',
         (150, 300), gb_scene)

    block_digital_read = GxSVGFunctionBlock('digitalRead', '#0078b0',
         (100, 400), gb_scene)

    block_analog_read = GxSVGFunctionBlock('analogRead', '#009900',
         (150, 450), gb_scene)

    block_analog_write = GxSVGFunctionBlock('analogWrite', '#009900',
         (150, 250), gb_scene)

    view = BaseView(gb_scene)
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

