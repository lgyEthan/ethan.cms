#!/usr/local/bin/python
import argparse
import glob
import numpy as np



def read_POSCAR(file_name="POSCAR"):
	'''Read structure files of VASP program.
    [input] : file's name. Default="POSCAR"
    [output] : system_name, lattice, cell_vec, species, natoms, coord_type, coord, Selective, selective_tags
	|-> system_name : name of system. @str
    |-> lattice : scale @float
    |-> cell_vec: [x1, y1, z1], [x2, y2, z2], [x3, y3, z3]] @np.array(dtype='d')
    |-> species: [atomt1, atom2, ...] @list(str)
    |-> natoms: [number_of_atom1, number_of_atom2, ...] @list(int)
	|-> coord_type: "DIRECT" / "CARTESIAN" @str
	|-> coord : coordination of each atoms @np.array(dtype='d')
    |-> Selective : True / False @bool
    |-> selective_tags : [[T/F, T/F, T/F], [T/F, T/F, T/F], ...] @np.array(dtype=str)
    '''
	ip=open(file_name, 'r')
	system_name=ip.readline().strip()
	lattice=float(ip.readline().strip())
	#cell vector
	cell_vec=[]
	for i in range(3):
	    cell_vec.append(ip.readline().split())
	cell_vec=np.array(cell_vec,dtype="d")

	# atomic information (species, number)
	species=ip.readline().split()
	nspecies=len(species)
	natoms=list(map(lambda x:int(x),ip.readline().split()))
	tot_natoms=sum(natoms)

	# Selective Dynamics & Coord_Type
	what1=ip.readline().strip()
	if what1.upper().startswith("S"):
		Selective=True
		what2=ip.readline().strip()
		if what2.upper().startswith("D"):
			Cartesian=False
		elif what2.upper().startswith("F"):
			Cartesian=False
		else:
			Cartesian=True
	else:
		Selective=False
		if what1.upper().startswith("D"):
			Cartesian=False
		elif what1.upper().startswith("F"):
			Cartesian=False
		else:
			Cartesian=True
	if Cartesian:
		coord_type="CARTESIAN"
	else:
		coord_type="DIRECT"

	# Coordination
	coord=[]
	selective_tags=[]
	if not(Selective):
		for i in range(tot_natoms):
			coord.append(ip.readline().split())
		coord=np.array(coord,dtype="d")
	else:
		for i in range(tot_natoms):
			line=ip.readline().split()
			coord.append(line[0:3])
			selective_tags.append(line[3:])
		coord=np.array(coord,dtype="d")	
		selective_tags=np.array(selective_tags,dtype=str)
	ip.close()
	return system_name, lattice, cell_vec, species, natoms, coord_type, coord, Selective, selective_tags

def write_POSCAR(output_file, system_name, lattice, cell_vec, species, natoms, coord_type, coord, Selective=False, selective_tags=[]):
	'''Write structure files of VASP program.
    [input] : output_file(name of output file), lattice, cell_vec, species, natoms, coord_type, coord, Selective, selective_tags
	|-> system_name : name of system. @str
    |-> lattice : scale @float
    |-> cell_vec: [x1, y1, z1], [x2, y2, z2], [x3, y3, z3]] @np.array(dtype='d')
    |-> species: [atomt1, atom2, ...] @list(str)
    |-> natoms: [number_of_atom1, number_of_atom2, ...] @list(int)
	|-> coord_type: "DIRECT" / "CARTESIAN" @str
	|-> coord : coordination of each atoms @np.array(dtype='d')
    |-> Selective : True / False @bool
    |-> selective_tags : [[T/F, T/F, T/F], [T/F, T/F, T/F], ...] @np.array(dtype=str)
    [output] : VASP format structure file.
    '''
	op=open(output_file,'w')
	print(system_name,file=op)
	print("   %16.14f"%(lattice),file=op)
	for i in range(3):
	    print("    %19.16f   %19.16f   %19.16f"%(cell_vec[i][0],cell_vec[i][1],cell_vec[i][2]),file=op)

	print("",end=" ",file=op)
	for i in range(len(species)):
	    print("%4s"%(species[i]),end="",file=op)
	print("",file=op)

	for i in range(len(natoms)):
	    print("%6d"%(natoms[i]),end="",file=op)
	print("",file=op)

	if Selective:
	    print("Selective dynamics",file=op)
	if coord_type=="CARTESIAN":
	    print("Cartesian",file=op)
	else:
	    print("Direct",file=op)

	if Selective:
	    for (x1,y1) in zip(coord,selective_tags):
	        for i in x1:
	            print("%20.16f"%(i),end="",file=op)
	        for p in y1:
	            print("%4s"%(p),end="",file=op)
	        print("",file=op)
	else:
	    for x1 in coord:
	        for i in x1:
	            print("%20.16f"%(i),end="",file=op)
	        print("",file=op)
	op.close()
	print("(+) Structure file [%s] was generated"%(output_file))

def dir2car(coord,cell_vec):
    '''Direct to Cartesian
    [input] : coord, cell_vec
    |-> coord : coordination. @np.array(dtype="d")
    |-> cell_vec : cell vector. @np.array(dtype='d')
    [output] : new coordination @np.array(dtype='d')
    '''
    return np.matmul(coord,cell_vec)

def car2dir(coord,cell_vec):
    '''Cartesian to Direct
    [input] : coord, cell_vec
    |-> coord : coordination. @np.array(dtype='d')
    |-> cell_vec : cell vector. @np.array(dtype='d')
    [output] : new coordination @np.array(dtype='d')
    '''
    inv_cell_vec=np.linalg.inv(cell_vec)
    return np.matmul(coord,inv_cell_vec)


##################### Input
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


###################### Running
if m==1:
    Out_Coord_type, tag = "CARTESIAN", "C"
else:
    Out_Coord_type, tag = "DIRECT", "D"

print('\n--------------------- Converts to, "%s" ---------------------' %Out_Coord_type, end="\n\n")

if f=="all.vasp":
    files=glob.glob("*.vasp")
elif f=="all":
    files=glob.glob("*")
else:
    files=f.split()

for vasp_file in files:
    try:
        system_name, lattice, cell_vec, species, natoms, coord_type, coord, Selective, selective_tags = read_POSCAR(vasp_file)        
        print('                      processing %s, [%s ---> %s]' % (vasp_file, coord_type, Out_Coord_type))
        if m==1:
        	if coord_type=="DIRECT":
        		coord=dir2car(coord,cell_vec)
        else:
        	if coord_type=="CARTESIAN":
        		coord=car2dir(coord,cell_vec)

        if vasp_file.endswith('.vasp'):
            vasp_file = '%s-' % vasp_file[:-5] +tag+'.vasp'
        else:
            vasp_file = '%s-' % vasp_file +tag+'.vasp'
        write_POSCAR(vasp_file, system_name, lattice, cell_vec, species, natoms, coord_type, coord, Selective, selective_tags)
    except:
        print("- - - - - - - - - - - Error in : %s" %(vasp_file))

print('')
print('                   ---------- Done ----------')
print('')
