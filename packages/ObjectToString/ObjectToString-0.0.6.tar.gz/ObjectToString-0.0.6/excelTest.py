#-*- coding: utf-8 -*-
import pdslib
import time

def ReadExcel():
    l=pdslib.pglibreadexcel("222222.xlsx")
    print(l)

def WriteExcel():
    pdslib.pgWriteExcel("222222.xlsx",("a","b"),[("1","2"),("1.111","2")],“hhhhh”)


if __name__ ==  '__main__':
    print(pdslib.register("c311e10c57fc0c9b8b3b394e53593112f723a62600c84b2a510e819f61ea72d744e0f80ea93456964a8f87cdc73fd01896ad616e5a7244ad2ae2a472862edfa3"))
    WriteExcel()
    ReadExcel()