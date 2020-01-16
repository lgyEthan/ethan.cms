#!/bin/env python3
#From https://github.com/Mabinogiysk/VASP-script.git
#Thank you Mabinogiysk - modified by GYLee (2019.02.17)
#Coordinate Conversion (Cartesian to Direct, Direct to Cartesian)
#For terminal version. -> file input default is different.


import sys
import re
import argparse
import glob

pars = argparse.ArgumentParser()
pars.add_argument('-m', type = int, choices=[1,2], help='Output file. 1=Cartesian output, 2=Direct(fractional) output',default=1)
pars.add_argument('-f', type = str, help='''File name which you want to convert.
    |-------| Example 1) -f POSCAR
    |-------| Example 2) -f 1.vasp <- Convert one file
    |-------| Example 3) -f '1.vasp 2.vasp' <- Convert several selected files.
    |-------| Example 4) -f all    <- convert every files
    |-------| Example 5) -f all.vasp <- convert every files which have .vasp extension.
    |-------| Example 6) Don't use -f tags : convert every files. same as example 4
    ''', default="all")
args = pars.parse_args()
m, f = args.m, args.f


def dirkar(basis, coordinates):
    for i in range(0, len(coordinates)):
        v1 = coordinates[i][0] * basis[0][0] + coordinates[i][1] * basis[1][0] + coordinates[i][2] * basis[2][0]
        v2 = coordinates[i][0] * basis[0][1] + coordinates[i][1] * basis[1][1] + coordinates[i][2] * basis[2][1]
        v3 = coordinates[i][0] * basis[0][2] + coordinates[i][1] * basis[1][2] + coordinates[i][2] * basis[2][2]
        coordinates[i][0] = v1
        coordinates[i][1] = v2
        coordinates[i][2] = v3
    return coordinates



def kardir(basis, coordinates):
    inverse = [[basis[1][1]*basis[2][2]-basis[2][1]*basis[1][2], basis[2][1]*basis[0][2]-basis[0][1]*basis[2][2], basis[0][1]*basis[1][2]-basis[1][1]*basis[0][2]],
               [basis[2][0]*basis[1][2]-basis[1][0]*basis[2][2], basis[0][0]*basis[2][2]-basis[2][0]*basis[0][2], basis[1][0]*basis[0][2]-basis[0][0]*basis[1][2]],
               [basis[1][0]*basis[2][1]-basis[2][0]*basis[1][1], basis[2][0]*basis[0][1]-basis[0][0]*basis[2][1], basis[0][0]*basis[1][1]-basis[1][0]*basis[0][1]]]
    omega = basis[0][0]*basis[1][1]*basis[2][2] + basis[0][1]*basis[1][2]*basis[2][0] + basis[0][2]*basis[1][0]*basis[2][1] - \
            basis[0][2]*basis[1][1]*basis[2][0] + basis[1][2]*basis[2][1]*basis[0][0] + basis[2][2]*basis[0][1]*basis[1][0]

    inverse = [[inverse[0][0]/omega, inverse[0][1]/omega, inverse[0][2]/omega],
               [inverse[1][0]/omega, inverse[1][1]/omega, inverse[1][2]/omega],
               [inverse[2][0]/omega, inverse[2][1]/omega, inverse[2][2]/omega]]

    for i in range(0, len(coordinates)):
        v1 = coordinates[i][0] * inverse[0][0] + coordinates[i][1] * inverse[1][0] + coordinates[i][2] * inverse[2][0]
        v2 = coordinates[i][0] * inverse[0][1] + coordinates[i][1] * inverse[1][1] + coordinates[i][2] * inverse[2][1]
        v3 = coordinates[i][0] * inverse[0][2] + coordinates[i][1] * inverse[1][2] + coordinates[i][2] * inverse[2][2]

        # move atoms to primative cell
        coordinates[i][0] = v1 + 60 - int(v1 + 60)
        coordinates[i][1] = v2 + 60 - int(v2 + 60)
        coordinates[i][2] = v3 + 60 - int(v3 + 60)
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

# [GYLee]
# In original script, it always converts to Cartesian.
# To differentiate coordinate_type, One more parameter is needed(ori_coordinate_type).
    ori_coordinate_type=coordinate_type

    if re.search(r'^[Cc]', coordinate_type) is None:
        coordinate_type = 'Cartesian'
        coordinates = dirkar(basis, coordinates)

    return lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective, ori_coordinate_type


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




###################### Running
if m==1:
    Out_Coord_type, tag = "Cartesian", "C"
else:
    Out_Coord_type, tag = "Direct", "D"

print('\n--------------------- Converts to, "%s" ---------------------' %Out_Coord_type, end="\n\n")

if f=="all.vasp":
    files=glob.glob("*.vasp")
elif f=="all":
    files=glob.glob("*")
else:
    files=f.split()

for vasp_file in files:
    try:
        lattice, basis, elements, num_atoms, selectiveflag, coordinate_type, coordinates, selective, ori_coordinate_type = readVasp(vasp_file)        
        print('                      processing %s, [%s ---> %s]' % (vasp_file, ori_coordinate_type, Out_Coord_type))

        if vasp_file.endswith('.vasp'):
            vasp_file = '%s-' % vasp_file[:-5] +tag+'.vasp'
        else:
            vasp_file = '%s-' % vasp_file +tag+'.vasp'
        writeVasp(vasp_file, lattice, basis, elements, num_atoms, selectiveflag, Out_Coord_type, coordinates, selective)
    except:
        print("- - - - - - - - - - - Error in : %s" %(vasp_file))

print('')
print('                   ---------- Done ----------')
print('')
