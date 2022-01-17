# coding=utf-8
##########################################################
# Authors: Denisa Rodila
# Affiliation: University of Geneva
# Version: 1.4.5
# Date: 13.01.2022
# Merge of HPC execution tiles for Downscaling of Swiss LCLU data
##########################################################

# import libraries

import xarray as xr
from glob import glob
import numpy as np
import os
from osgeo import gdal
import re

#Nr. of tiles to merge
c = 30 #nr of columns 
r = 30 #nr of rows

raster = gdal.Open('PRI09_25.tiff')  # open one of the input files to get the size
cols = raster.RasterXSize  # get columns
rows = raster.RasterYSize  # get rows

def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]

###### merge the tiles output into a single raster #######

print("Merging ", r*c, " files ...")
myds = []
for j in range(c):

    fileList = glob('output/'+'*x'+str(j)+'.tif')
    fileList.sort(key=num_sort)

    line = []
    for f in fileList:
        file = gdal.Open(f)
        colsf = file.RasterXSize  # get columns
        rowsf = file.RasterYSize  # get rows
        bandf = file.GetRasterBand(1)  # get band
        dataf = bandf.ReadAsArray(0, 0, colsf, rowsf)  # read raster at once
        line.append(dataf)
    result_line = np.row_stack(line)
    myds.append(result_line)
 
result = np.column_stack(myds)

###### create output raster file ######

ds_raster = 'LU-CH.tif'  # filename

driver_tiff = gdal.GetDriverByName('GTiff')  # GeoTiff

ds = driver_tiff.Create(ds_raster, cols, rows, 1, gdal.GDT_Byte)  # create the output f$

ds.SetGeoTransform(raster.GetGeoTransform())  # get the coordinate system
ds.SetProjection(raster.GetProjection())  # get the projection

ds.GetRasterBand(1).WriteArray(result)
ds.GetRasterBand(1).SetNoDataValue(255)##if you want these values transparent
ds.FlushCache() ##saves to disk!!
ds = None
band=None

print("The raster ", ds_raster, " was succesfully created!")
