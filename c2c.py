#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Made by Taehun Lee.
# Modified by Giyeok Lee, 2018/11/02
# I think choosing gridpoints is more effecient in job file. So keep argparse
import os, shutil, glob
import math 
import sys
import time
import argparse


# Mady by GYLee
s_t=time.time()
pars = argparse.ArgumentParser()
pars.add_argument('X', type = int, help='x grids')
pars.add_argument('Y', type = int, help='y grids')
pars.add_argument('Z', type = int, help='z grids')
args  = pars.parse_args()
nx = args.X
ny = args.Y
nz = args.Z
fft_total = int(nx) * int(ny) * int(nz) 
t_len=fft_total+int(nx)*int(ny)
f = open("CURSAVE", 'r')
resu=open("c2c_CAL_REPORT.txt",'w')
CUR=open("CURRENT_temp",'w')
xy=open('c2c_Real_xy_position.txt','w')
sall = f.readlines()
f.close()

# Delete first line of CURSAVE when there is "Backup file" or something.
try:
    [float(x) for x in sall[0].rstrip("\n").split(" ") if x!=""]
except:
    sall=sall[1:]


if len(sall)>=t_len and len(sall)<=t_len+2:
    print("[good] (%s,%s,%s) is valid grid point numbers."%(nx,ny,nz),file=resu)
    
    # converter
    for iz in range(0,nz+1):
        for iy in range(1,ny+1):
            for ix in range(1,nx+1):
                temp=((ix-1)*ny+(iy-1))*(nz+1)+iz
                a=sall[temp]

                if iz!=0:
                    print("%s"%a,file=CUR,end="")

                else:
                    xy_l=[float(x) for x in a.rstrip('\n').split(" ") if x!=""]
                    print("%f   %f"%(xy_l[0], xy_l[1]), file=xy)
        xy.close()
    CUR.close()

    ## rearrange CURRENT_temp to CURRENT <- from_TH
    ftr = open('./CURRENT_temp')
    ftr_split = [float(num) for num in ftr.read().split()];

    save = open("CURRENT", "w")


    if fft_total % 5 == 0:
        for i in range(0, fft_total, 5):
            print (str(ftr_split[i])+"   "+str(ftr_split[i+1])+"   "+str(ftr_split[i+2])+"   "+str(ftr_split[i+3])+"   "+str(ftr_split[i+4])+"   ",file=save)
    else:
        fft_max = int(fft_total / 5) * 5
        fft_remain = fft_total - fft_max
        for i in range(0, fft_max, 5):
            print( str(ftr_split[i])+"   "+str(ftr_split[i+1])+"   "+str(ftr_split[i+2])+"   "+str(ftr_split[i+3])+"   "+str(ftr_split[i+4])+"   ",file=save)
        print ('   '.join([str(ftr_split[j]) for j in range(fft_total-fft_remain, fft_total)]),file=save)
    save.close()    
    ftr.close()

else:
    print("[error] (%s,%s,%s) is wrong grid point numbers."%(nx,ny,nz), file=resu)
    CUR.close()
resu.close()


              
TiMe=open('c2c_Time.txt','w')
print("---%s seconds ---"%(time.time()-s_t),file=TiMe)
TiMe.close()

