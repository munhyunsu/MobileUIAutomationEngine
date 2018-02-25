#!/usr/bin/env python3

import xml.etree.ElementTree as ET

tree = ET.parse('btemp.xml')
root = tree.getroot()
key_stack = list()

nodes = root.findall('node')
nodes.reverse()
for node in nodes:
    key_stack.append((node, 0))
while len(key_stack) > 0:
    (node, level) = key_stack.pop()
    if hasattr(node, 'attrib') == True:
        print('-'*level, node.attrib['class'], node.attrib['bounds'])
    nodes = node.findall('node')
    nodes.reverse()
    for cnode in nodes:
        key_stack.append((cnode, level+1))
 
#nodes = root.findall('node')
#nodes.reverse()
#key_stack.append((nodes, 0))
#while len(key_stack) > 0:
#    (nodes, level) = key_stack.pop()
#    for node in nodes:
#        print('-'*level, node.attrib['class'], node.attrib['bounds'])
#        cnodes = node.findall('node')
#        cnodes.reverse()
#        key_stack.append((cnodes, level+1))
#   
