#!/bin/env python3
#From https://github.com/Mabinogiysk/VASP-script.git
#Thank you Mabinogiysk - GYLee


import sys
import re


def dirkar(basis, coordinates):
    for i in range(0, len(coordinates)):
        v1 = coordinates[i][0] * basis[0][0] + coordinates[i][1] * basis[1][0] + coordinates[i][2] * basis[2][0]
        v2 = coordinates[i][0] * basis[0][1] + coordinates[i][1] * basis[1][1] + coordinates[i][2] * basis[2][1]
        v3 = coordinates[i][0] * basis[0][2] + coordinates[i][1] * basis[1][2] + coordinates[i][2] * basis[2][2]
        coordinates[i][0] = v1
        coordinates[i][1] = v2
        coordinates[i][2] = v3
    return coordinates


def readVasp(file_name):
    """
    :param file_name:
    :return: [lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective]
    lattice: scale, float
    basis: [x1, y1, z1], [x2, y2, z2], [x3, y3, z3]], float
    elements: [element1, element2, ...], str
    num_atoms: [number_of_element1, number_of_element2, ...], int
    selectiveflag: 'Selective dynamics' or '', str
    coordinate_type: 'Cartesian', str
    coordinates: [[x1, y1, z1], [x2, y2, z2], ...], float
    selective: [[T/F, T/F, T/F], [T/F, T/F, T/F], ...], str
    """
    space = re.compile(r'\s+')
    with open(file_name) as input_file:
        content = input_file.readlines()

    lattice = float(content[1].strip())

    basis = []
    for i in range(2, 5):
        line = space.split(content[i].strip())
        basis.append([float(line[0]), float(line[1]), float(line[2])])

    elements = space.split(content[5].strip())
    num_atoms = list(map(int, space.split(content[6].strip())))

    if re.search(r'^[Ss]', content[7]) is None:
        selectiveflag = ''
        index = 7
    else:
        selectiveflag = content[7].strip()
        index = 8

    if re.search(r'^[Dd]', content[index]) is None:
        coordinate_type = 'Cartesian'
    else:
        coordinate_type = 'Direct'

    coordinates = []
    selective = []
    start = index + 1
    end = start + sum(num_atoms)
    if selectiveflag == '':
        for i in range(start, end):
            line = space.split(content[i].strip())
            coordinates.append([float(line[0]), float(line[1]), float(line[2])])
    else:
        for i in range(start, end):
            line = space.split(content[i].strip())
            coordinates.append([float(line[0]), float(line[1]), float(line[2])])
            if len(line) == 6:
                selective.append([line[3], line[4], line[5]])
            else:
                selective.append(['', '', ''])

    if re.search(r'^[Cc]', coordinate_type) is None:
        coordinate_type = 'Cartesian'
        coordinates = dirkar(basis, coordinates)

    return lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective


def writeVasp(file_name, lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective):
    """
    :param file_name: str
    :param lattice: float
    :param basis: [x1, y1, z1], [x2, y2, z2], [x3, y3, z3]], float
    :param elements: element1, element2, element3], str
    :param num_atoms: [number_of_element1, number_of_element2, ...], int
    :param selectiveflag: 'Selective dynamics' or '', str
    :param coordinate_type: 'Cartesian' or 'Direct', str
    :param coordinates: [[x1, y1, z1], [x2, y2, z2], ...], float
    :param selective: [[T/F, T/F, T/F], [T/F, T/F, T/F], ...] or [], str
    :return:
    """
    with open(file_name, 'w') as output_file:
        description = ' '.join(elements)
        output_file.write('%s\n' % description)
        output_file.write("  %15.10f\n" % lattice)
        for i in range(0, 3):
            output_file.write("  %15.10f  %15.10f  %15.10f\n" % (basis[i][0], basis[i][1], basis[i][2]))
        output_file.write(description.rstrip() + '\n')

        num_atom = ' '.join(list(map(str, num_atoms)))
        output_file.write('%s\n' % num_atom)

        if selectiveflag != '':
            output_file.write('%s\n' % selectiveflag)
        output_file.write('%s\n' % coordinate_type)

        if re.search(r'^[Dd]', coordinate_type):
            coordinates = kardir(basis, coordinates)

        # keeping dimension the same
        if len(coordinates) - len(selective) > 0:
            for i in range(len(selective), len(coordinates)):
                selective.append(['', '', ''])

        for i in range(0, len(coordinates)):
            output_file.write("%16.10f  %16.10f  %16.10f %s %s %s\n" % (coordinates[i][0], coordinates[i][1], coordinates[i][2],
                                                                      selective[i][0], selective[i][1], selective[i][2]))


if len(sys.argv) == 1:
    print('')
    print('Usage: %s vasp_file1 vasp_file2 ...' % sys.argv[0].split('/')[-1])
    print('')
    exit(1)

print('')
print('############ This script converts direct to cartesian ############')
print('          ############ direct -> cartesian ############')
print('')
for vasp_file in sys.argv[1:]:
    print('                      processing %s' % vasp_file)
    lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective = readVasp(vasp_file)
    if vasp_file.endswith('.vasp'):
        vasp_file = '%s-C.vasp' % vasp_file[:-5]
    else:
        vasp_file = '%s-C.vasp' % vasp_file
    writeVasp(vasp_file, lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective)

print('')
print('                   ---------- Done ----------')
print('')
