#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET

def main(argv):
    tree = ET.parse(argv[1])
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
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
