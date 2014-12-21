#! /usr/bin/env python


# dia2anim - Create animation from schematic diagram
# Copyright (C) 2007, Steve Pothier <b4ape@users.sourceforge.net>
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



'''\
Generate GIF movie from a dia graph'''

import string
import os
import sys
import imp
import tempfile

import Image
import ImageDraw
import networkx as NX

def offset_points(offset,points):
    return map(lambda point: (offset[0]+point[0],offset[1]+point[1]), points)

def scale_points(scale,points):
    return map(lambda point: (scale*point[0],scale*point[1]), points)

def add_points(p1,p2):
    return (p1[0]+p2[0],p1[1]+p2[1])

def subtract_points(p1,p2):
    return (p1[0]-p2[0],p1[1]-p2[1])

def add_polys(poly1,poly2):
    return map(lambda p1,p2: add_points(p1,p2),poly1,poly2)

def subtract_polys(poly1,poly2):
    return map(lambda p1,p2: subtract_points(p1,p2),poly1,poly2) 


##############################################################################
def draw_nonmovers(draw,nonmovers):
    for node in nonmovers:
        if node.props['type'] == 'Standard - Polygon':
            draw.polygon(offset_points(node.props['pos'],
                                       node.props['poly_points']),
                         fill=255)
        elif node.props['type'] == 'Standard - Box':
            # approximately right (better to add 1/2 dims)
            pos = node.props['pos']
            draw.rectangle([pos,(pos[0]+node.props['elem_width'],pos[1]+node.props['elem_height'])],
                           fill=node.props.get('inner_color','#ffffff'),
                           outline=node.props.get('border_color','#ffffff'))
        elif node.props['type'] == 'Standard - Line':
            #! draw.line(node.props['conn_endpoints'], width=node.props['line_width'])
            draw.line(node.props['conn_endpoints'], width=3,
                      fill=node.props.get('line_color', '#ff0000'))


def draw_explicit_frame(idx, nodes, nonmovers, filebase="_obsv"):
    '''\
Create a new GIF file with name derived from FILEBASE and IDX.
The GIF will contain a rendering of all the NODES (each is a seperate object).
RETURN: filename created'''
    im = Image.new("L",(600,600)) # grayscale
    draw = ImageDraw.Draw(im)

    draw_nonmovers(draw,nonmovers)
        
    for node in nodes:
        if node == None:
            continue
        elif node.props['type'] == 'Assorted - Sun': 
            continue
        elif node.props['type'] == 'Standard - Polygon':
            draw.polygon(offset_points(node.props['pos'],
                                       node.props['poly_points']),
                         fill=255)
        elif node.props['type'] == 'Standard - Box':
            # approximately right (better to add 1/2 dims)
            pos = node.props['pos']
            draw.rectangle([pos,(pos[0]+node.props['elem_width'],pos[1]+node.props['elem_height'])],
                           fill=255)
        
    filename = "%s_%04d.gif" % (filebase,idx)
    #! print "Writing: %s" % filename
    im.save(filename, "GIF")
    return filename

def draw_implicit_frames(idx, count, nodes0, nodes1, nonmovers, filebase="_obsv"):
    '''\
Create set of COUNT new GIF files that morph and interpolate between objects
in NODES0 and corresponding objects in NODES1.
RETURN: space seperate filenames created'''
    filenames = ""


    
    # each implict frame
    for i in range(count):
        im = Image.new("L",(600,600)) # grayscale
        draw = ImageDraw.Draw(im)
        draw_nonmovers(draw,nonmovers)
        
        # each object
        for n0, n1 in zip(nodes0,nodes1):
            # n0, n1 are "observations" of same obj connected in original graph
            if ((n1 == None) or
                (n0.props['type'] == 'Assorted - Sun') or
                (n1.props['type'] == 'Assorted - Sun')):
                continue
            dx = (n1.props['pos'][0] - n0.props['pos'][0])/float(count+1)
            dy = (n1.props['pos'][1] - n0.props['pos'][1])/float(count+1)
            
            loc = add_points(n0.props['pos'], (dx*i, dy*i))
            if n0.props['type'] == 'Standard - Polygon':
                pts = add_polys(n0.props['poly_points'],scale_points(i/float(count+1),subtract_polys(n1.props['poly_points'], n0.props['poly_points'])))
                draw.polygon(offset_points(loc,pts), fill=255)
            elif n0.props['type'] == 'Standard - Box':
                # approximately right (better to add 1/2 dims)
                draw.rectangle([loc,(loc[0]+n0.props['elem_width'],loc[1]+n0.props['elem_height'])],
                               fill=255)
        filename = "%s_%03d.gif" % (filebase,i+idx)
        filenames = filenames + " " + filename
        im.save(filename, "GIF")        
    return filenames

##############################################################################


# for n in walk_frames(n1):
#    do_stuff(n)
def walk_frames(graph, first_node):
    n = first_node
    while n:
        yield n
        try:
            n = graph.out_neighbors(n)[0]
        except IndexError:
            n = None
    raise StopIteration

def anim_movers_from_graph(allgraph,outdir,num_frames=None, delay=0):
    '''\
Create gif animations in "OUTDIR/layer.gif" from content of ALLGRAPH.  Each will
contain about NUM_FRAMES frames with DELAY * 1/100 secs between frames.

Nodes containing objtype=pad are used to prepad tracks with
non-observations. Short tracks will be padded at the end with
non-observations.

'''
    filebase = "_obsv"
    outfiles = ""

    # process nodes by layer
    background_graph = allgraph.subgraph([v for v in allgraph.nodes() if v.props['layer'] == 'Background'])

    # Process "active" layers
    # The 'Background" layer will be used for ALL animations
    all_layers = set([v.props['layer'] for v in allgraph.nodes()])
    if 1 == len(all_layers):
        layers = set(['Background'])
    else:
        layers = all_layers - set(['Background'])

    print "Processing layers: %s from %s" % (layers,all_layers)
    for layer in layers:
        infiles = ""
        if layer == 'Background':
            graph = allgraph.subgraph([v for v in allgraph.nodes() if v.props['layer'] == layer])
            print "%s: %d" % (layer, len(graph))
        else:
            graph = NX.union(background_graph,
                             allgraph.subgraph([v for v in allgraph.nodes() if v.props['layer'] == layer])
                             )
            print "%s: %d" % (layer, len(graph)-len(background_graph))

        nonmovers = [v for v in graph.nodes() if v.props['ntype'] == 'static']
        starters = [v for v in graph.nodes() if v.props['ntype'] == 'mover' and 0 == len(graph.in_neighbors(v))]
        tracks = map(lambda s: [n for n in walk_frames(graph,s)], starters)    
        # Shorter tracks will get value of "None" to pad out frame list at end
        frames = map(None,*(tracks+[[]]))
        i = fidx = 0
        n = len(frames)
        m = int((num_frames-n+2)/(n-1))
        # Do explicit frame plus implicit frames up to next explicit
        for i in range(n-1):
            movers = frames[i]
            explicit = draw_explicit_frame(fidx,movers,nonmovers)
            fidx = fidx + 1
            implicit = draw_implicit_frames(fidx, m, frames[i],frames[i+1], nonmovers)
            fidx = fidx + m
            infiles = infiles + " " + explicit + implicit 
            
        # draw last observation
        infiles = infiles + " " + draw_explicit_frame(fidx,frames[n-1],nonmovers)
        outfile = outdir + "/" + layer + ".gif"
        #! outfile = outdir + "/" + layer + ".mpg"
        cmd = "convert -loop 0 -delay %d %s %s" % (delay, infiles, outfile)
        os.system(cmd)
        os.system("rm %s" % infiles)
        outfiles += outfile + " "
    print "TRY: animate -loop 0 " + outfiles
    #! print "TRY: mplayer -loop 0 " + outfiles
    return(outfiles.split())

def xslt(xsl,inxml,outxml):
    #! print "This file: %s" % __file__
    swl = os.path.dirname(os.path.dirname(__file__))
    xslfile = swl + '/xsl/' + xsl + '.xsl'
    cmd = "xsltproc %s %s > %s" % (xslfile,inxml,outxml)
    print "EXECUTING: %s" % cmd
    os.system(cmd)
    return None

def read_mover_graph(diafile,zoom=20):
    # xsltproc dia2grasp.xsl three-node.dia > three-node-grasp.xml
    #   In all IDs change oh to zero
    graphnx = tempfile.NamedTemporaryFile()
    xslt('dia2networkx', diafile, graphnx.name)
    graph = imp.load_source('nxgraph',graphnx.name).create_graph()
    #! nxg = imp.load_source('nxgraph',graphnx.name)
    #! print "nxg=%s" % nxg
    #! graph = ngx.create_graph()
    for node in graph.nodes():
        if node.props['type'] == "Assorted - Sun":
            continue
        elif node.props['type'] == "Standard - Polygon":
            pts = node.props['poly_points']
            orig = node.props['pos']
            node.props['poly_points'] = scale_points(zoom,offset_points((-orig[0],-orig[1]),pts))
        elif node.props['type'] == "Standard - Box":
            node.props['elem_width'] *= zoom
            node.props['elem_height'] *= zoom
        elif node.props['type'] == 'Standard - Line':
            node.props['conn_endpoints'] = scale_points(zoom,node.props['conn_endpoints'])
        node.props['pos'] = scale_points(zoom,[node.props['pos']])[0]


    #! movers = [v for v in graph.nodes() if 0 != len(graph.neighbors(v))]
    #! starters = [v for v in movers if 0 == len(graph.in_neighbors(v))]
    #! tracks = map(lambda s: [n for n in walk_frames(graph,s)], starters)    
    #! print "Number of tracks=%d, lengths=%s" % (len(starters),map(lambda t: len(t), tracks))

    # mark non-movers (no edges), movers
    for v in graph.nodes():
        if 0 == (len(graph.in_neighbors(v)) + len(graph.out_neighbors(v))) : 
            v.props['ntype'] = 'static'
        else:
            v.props['ntype'] = 'mover'
            
    return graph

# Return list of filenames produced
def animate_from_dia(diafile, layergif, num_frames=50, delay=1):
    graph = read_mover_graph(diafile)
    return(anim_movers_from_graph(graph, layergif, num_frames, delay=1))


def usage(argv):
    #! print "This file: %s" % __file__
    print '''\
USAGE:
   dia2anim in_dia outdir
   
GOT:
  %s %s
  '''  % (argv[0], string.join(argv[1:]))
    sys.exit()

if __name__ == '__main__':
    acount = len(sys.argv)-1
    if not(2 <= acount <= 2): usage(sys.argv)

    dia = sys.argv[1]
    outdir = sys.argv[2]
    #! gif = tempfile.NamedTemporaryFile()
    #! gifname = gif.name
    
    #! animate_from_dia(dia,gifname)
    #! os.system('animate '+ gifname)
    if (not os.path.isdir(outdir)):
        os.makedirs(outdir)
    filenames = animate_from_dia(dia,outdir)
    print "filenames=%s" % filenames
  


