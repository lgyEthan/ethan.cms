#!/usr/bin/env python
# -*- coding=utf-8 -*-
# To find Vacuum level from "VLINE" file.

file="VLINE"
t=open(file,'r')
rd=t.readlines()
t.close()
rd=rd[1:]
dat_temp=[]
max_data_temp=[0,0]
i=0
for a in rd:
    i+=1
    tt=float(a.rstrip('\n').split(" ")[-1])
    dat_temp.append(tt)
    if max_data_temp[1]<tt:
        max_data_temp=[i,tt]
print("In ---- %s ---- \n Vacuum Level is %5.10s eV. Index : %s / %s"%(file, max_data_temp[1], max_data_temp[0], len(dat_temp)))
