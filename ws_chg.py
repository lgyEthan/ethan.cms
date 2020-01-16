#!/usr/local/bin/python
import numpy as np
import argparse
import sys
from decimal import Decimal

def chgcar_read(chgfile):
    with open(chgfile, "r") as chg:
        celldata = []
        pos = []
        name = chg.readline().strip()
        scale = chg.readline().strip()
        for i in range(3):
            celldata.append(chg.readline().strip().split())
        celldata = np.array(celldata, dtype="d")
        elements = chg.readline().strip()
        numelem = chg.readline().strip()

        numatom = 0
        for x in numelem.split():
            numatom += int(x)

        coord_type = chg.readline().strip()

        for i in range(numatom):
            pos.append(chg.readline().strip().split())
        pos = np.array(pos, dtype="d")

        chg.readline()

        vol = np.dot(celldata[0], np.cross(celldata[1], celldata[2]))
        header = [name, scale, celldata, elements, numelem, coord_type, pos]

        ## Header finished, now chg data lines
        grid = chg.readline().strip().split()

        lines = chg.readlines()

        chglist = []
        for x in lines:
            if "a" in x:
                break
            else:
                tmp = x.split()
                for y in tmp:
                    chglist.append(y)

        chglist = np.reshape(np.array(chglist, dtype="d"), (int(grid[2]), int(grid[1]), int(grid[0])))
        return [chglist, grid, header, vol]

def planar_avg(chgdata, direction):
    avgdata = []
    x_avgdata = []
    if direction in "cCzZ3":
        for i in range(int(chgdata[1][2])):
            if i == 0:
                x_avgdata.append(0)
            else:
                x_avgdata.append(i / int(chgdata[1][2]))
        x_avgdata = np.array(x_avgdata)
        avgdata = np.mean(chgdata[0], axis=(1, 2))
        x_avgdata *= np.linalg.norm(chgdata[2][2][2] * float(chgdata[2][1]))

    elif direction in "bByY2":
        for i in range(int(chgdata[1][1])):
            if i == 0:
                x_avgdata.append(0)
            else:
                x_avgdata.append(i / int(chgdata[1][1]))
        x_avgdata = np.array(x_avgdata)
        avgdata = np.mean(chgdata[0], axis=(0, 2))
        x_avgdata *= np.linalg.norm(chgdata[2][2][1] * float(chgdata[2][1]))

    elif direction in "aAxX1":
        for i in range(int(chgdata[1][0])):
            if i == 0:
                x_avgdata.append(0)
            else:
                x_avgdata.append(i / int(chgdata[1][0]))
        x_avgdata = np.array(x_avgdata)
        avgdata = np.mean(chgdata[0], axis=(0, 1))
        x_avgdata *= np.linalg.norm(chgdata[2][2][0] * float(chgdata[2][1]))

    return [avgdata, x_avgdata]

def differences(chgdata1, chgdata2):
    if chgdata1[1] == chgdata2[1]:
        chgdata1[0] -= chgdata2[0]
    else:
        raise IOError("Grid not matching!")
    return chgdata1

def exportdata(chgdata, outfile):
    with open(outfile, "w") as out:
        for x in chgdata[2]:
            if type(x) is np.ndarray:
                for y in x:
                    out.write("%12.10f   %12.10f   %12.10f" %(y[0], y[1], y[2]))
                    out.write("\n")
            else:
                out.write(x)
                out.write("\n")
        out.write("\n")
        out.write("%4s  %4s  %4s" % (chgdata[1][0], chgdata[1][1], chgdata[1][2]))
        out.write("\n")
        chgdata[0] = chgdata[0].flatten()
        tmp = []
        for x in chgdata[0]:
            tmp.append("%14s" % ('{:>14.12E}'.format(Decimal(x))))
        out.write("   ".join(tmp))

def plotplanar(planardata, outfile, prefix):

    def graphpreset(outfile, leftmin, leftmax, botmin, botmax, width=340.157, height=340.157):
        # Writing the header part of .itx
        preset = ("X DefaultFont/U \"Times New Roman\"\n"
                  "X ModifyGraph marker=19\n"
                  "X ModifyGraph lSize=1.5\n"
                  "X ModifyGraph tick=2\n"
                  "X ModifyGraph mirror=1\n"
                  "X ModifyGraph fSize=28\n"
                  "X ModifyGraph lblMargin(left)=15,lblMargin(bottom)=10\n"
                  "X ModifyGraph standoff=0\n"
                  "X ModifyGraph axThick=1.5\n"
                  "X ModifyGraph axisOnTop=1\n"
                  "X Label left \"Planar averaged ρ (\\f02e\\f00/Å\S3\M)\"\n"
                  "X Label bottom \"Distance (Å)\"\n"
                  )

        outfile.write(preset)

        outfile.write("X ModifyGraph width=%f,height=%f\n" % (width, height))

        if leftmin is not None:
            leftaxis = ("X Setaxis left %4f, %4f\n" % (leftmin, leftmax))
            outfile.write(leftaxis)
        if botmin is not None:
            botaxis = ("X Setaxis bottom %4f, %4f\n" % (botmin, botmax))
            outfile.write(botaxis)

    with open(outfile, "w") as out:
        out.write("IGOR\n")
        out.write("WAVES/D planar_%s x_planar_%s\n" % (prefix, prefix))
        out.write("BEGIN\n")
        for i in range(len(planardata[0])):
            out.write("%12.10f  %12.10f \n" % (planardata[0][i], planardata[1][i]))
        out.write("END\n")

        out.write("X Display planar_%s vs x_planar_%s as \"planar_avg_%s\" \n" %(prefix, prefix, prefix))

        graphpreset(out, None, None, None, None)

def executefunc(args):
    datalist = []
    for x in args.infile:
        datalist.append(chgcar_read(x))

    if len(datalist) > 1:
        for i in range(len(datalist)):
            if i == 0:
                pass
            else:
                datalist[0] = differences(datalist[0], datalist[i])

    if args.planar is True:
        planar = planar_avg(datalist[0], args.direction)
        if args.novolumeavg is True:
            pass
        else:
            planar /= datalist[0][3]
        plotplanar(planar, args.outitx, args.prefix)

    else:
        exportdata(datalist[0], args.outfile)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument("-v", dest="verbose", action="store_true")
    parser.add_argument("-i", dest="infile", type=str, default="CHGCAR", nargs="*")
    parser.add_argument("-o", dest="outfile", type=str, default="DCD.vasp")
    parser.add_argument("-O", dest="outitx", type=str, default="planar.itx")
    parser.add_argument("-P", dest="prefix", type=str, default="")
    parser.add_argument("-d", dest="direction", type=str, default="z")
    parser.add_argument("-p", dest="planar", action="store_true")
    parser.add_argument("-v", dest="novolumeavg", action="store_true")
    parser.set_defaults(func=executefunc)
    args = parser.parse_args()

    try:
        getattr(args, "func")
    except AttributeError:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()


