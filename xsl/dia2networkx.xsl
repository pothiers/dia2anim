
<!--
# dia2anim - Compact dia file into something easier to process
# Copyright (C) 2007, Steve Pothier (b4ape@users.sourceforge.net)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
-->

<!--
EXAMPLES:
  xsltproc dia2networkx.xsl traffic-layer.dia > traffic-layer.networkx.py
-->


<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  xmlns:dia="http://www.lysator.liu.se/~alla/dia/"
  >

  <xsl:param name="tab" select="'   '" />
  <xsl:param name="nl"  select="'&#010;'" />

<xsl:output
    method="text"
    indent="no"
    encoding="UTF-8" 
    />

<xsl:strip-space elements="*"/> 


<xsl:template match="/">
import networkx as NX

class Bag(object):
    def __init__(self, **props):
        self.props = props

def create_graph():  
  g = NX.XDiGraph()
  <xsl:apply-templates select="//dia:object[count(dia:connections/dia:connection) != 2]"/>
  <xsl:apply-templates select="//dia:object[count(dia:connections/dia:connection) = 2]"/>
  return g
</xsl:template>

<xsl:template match="dia:object[count(dia:connections/dia:connection) != 2]">
  <xsl:value-of select="$nl" />  N<xsl:value-of select="translate(@id,'O','0')"/> = Bag(
  id='<xsl:value-of select="translate(@id,'O','0')"/>',
  layer='<xsl:value-of select="ancestor::dia:layer/@name"/>',
  visible='<xsl:value-of select="ancestor::dia:layer/@visible"/>',
  type='<xsl:value-of select="@type"/>',
  pos=(<xsl:value-of select="dia:attribute[@name='obj_pos']/dia:point/@val"/>),
  <!-- TYPE specific attributes below here -->
  <xsl:if test="dia:attribute[@name='elem_width']">
    <xsl:text>elem_width=</xsl:text><xsl:value-of select="dia:attribute[@name='elem_width']/dia:real/@val"/>,
    <xsl:text>elem_height=</xsl:text><xsl:value-of select="dia:attribute[@name='elem_height']/dia:real/@val"/>,
  </xsl:if>
  
  <!-- Line properties -->
  <xsl:if test="dia:attribute[@name='line_color']">
    <xsl:text>line_color='</xsl:text><xsl:value-of select="dia:attribute[@name='line_color']/*/@val"/>',
  </xsl:if>
  <xsl:if test="dia:attribute[@name='line_width']">
    <xsl:text>line_width=</xsl:text><xsl:value-of select="dia:attribute[@name='line_width']/*/@val"/>,
  </xsl:if>
  <xsl:if test="dia:attribute[@name='line_style']">
    <xsl:text>line_style=</xsl:text><xsl:value-of select="dia:attribute[@name='line_style']/*/@val"/>,
  </xsl:if>

  <!-- ? NUMber of Connection Points ??? -->
  <xsl:if test="dia:attribute[@name='numcp']">
    <xsl:text>numcp=</xsl:text><xsl:value-of select="dia:attribute[@name='numcp']/*/@val"/>,
  </xsl:if>
  
  <!-- Rectangle properties  (aka *Box) -->
  <xsl:if test="dia:attribute[@name='border_width']">
    <xsl:text>border_width=</xsl:text><xsl:value-of select="dia:attribute[@name='border_width']/*/@val"/>,
  </xsl:if>
  <xsl:if test="dia:attribute[@name='border_color']">
    <xsl:text>border_color='</xsl:text><xsl:value-of select="dia:attribute[@name='border_color']/*/@val"/>',
  </xsl:if>
  <xsl:if test="dia:attribute[@name='inner_color']">
    <xsl:text>inner_color='</xsl:text><xsl:value-of select="dia:attribute[@name='inner_color']/*/@val"/>',
  </xsl:if>
  <xsl:if test="dia:attribute[@name='show_background']">
    <xsl:text>show_background='</xsl:text>
    <xsl:value-of select="dia:attribute[@name='show_background']/*/@val"/>',
  </xsl:if>    
  
  <xsl:if test="dia:attribute[@name='poly_points']">
    <xsl:text>poly_points=</xsl:text><xsl:text>[</xsl:text>
    <xsl:for-each select="dia:attribute[@name='poly_points']/dia:point">
      <xsl:text>(</xsl:text>
      <xsl:value-of select="@val"/>
      <xsl:text>),</xsl:text>
    </xsl:for-each>
    <xsl:text>],</xsl:text>
  </xsl:if>

  <xsl:if test="dia:attribute[@name='conn_endpoints']">
    <xsl:text>conn_endpoints=</xsl:text>
    <xsl:text>((</xsl:text>
    <xsl:value-of select="dia:attribute[@name='conn_endpoints']/dia:point[1]/@val"/>
    <xsl:text>),(</xsl:text>
    <xsl:value-of select="dia:attribute[@name='conn_endpoints']/dia:point[2]/@val"/>
    <xsl:text>))</xsl:text>
  </xsl:if>
  )
  g.add_node(N<xsl:value-of select="translate(@id,'O','0')"/>)
  <xsl:value-of select="$nl" />
</xsl:template>

<xsl:template match="dia:object[count(dia:connections/dia:connection) = 2]">
  g.add_edge(<xsl:text>N</xsl:text><xsl:value-of select="translate(dia:connections/dia:connection[1]/@to,'O','0')"/>
  <xsl:text>,</xsl:text>
  <xsl:text>N</xsl:text><xsl:value-of select="translate(dia:connections/dia:connection[2]/@to,'O','0')"/>
  <xsl:text>)</xsl:text>
  <xsl:value-of select="$nl" />
</xsl:template>

<xsl:template match="dia:attribute">
</xsl:template>

</xsl:stylesheet>
