# coding=utf-8
##########################################################
# Authors: Gregory Giuliani, Anthony Lehmann, Denisa Rodila
# Affiliation: University of Geneva
# Version: 1.4.5
# Date: 13.01.2021
# Downscaling of Swiss LCLU data
##########################################################

# import libraries
import xlrd, numpy, math

##################################################################################################
# Step 1: create a land use grid at 100m resolution from Landuse100 statistics
# Step 2: remove from Landuse100 categories that correspond to linear features (river, road, train)
# Step 3: Rasterize the primary surfaces land cover vector base map at a 25m resolution (BaseMap25)
##################################################################################################

####################################################################################
# Step 4: Visit each BaseMap25 pixel
# Step 10: Loop from point 4 to 11 with next BaseMap25 pixel
# Input: BaseMap25 is the swisstopo layer for which we will visit each pixel
# Input: Expert table to get acceptable values and related weight
####################################################################################
from osgeo import gdal  # import GDAL

# Get the size (columns/rows) of the Base Map 25 raster
raster = gdal.Open('/Users/lehmanan/Dropbox/aISE/PROJETS/ValPar.CH/downscaling LU/Nathan/2018/PRI18_25GE.tif')  # open raster
cols = raster.RasterXSize  # get columns
rows = raster.RasterYSize  # get rows
band = raster.GetRasterBand(1)  # get band
data = band.ReadAsArray(0, 0, cols, rows)  # read raster at once
print('BaseMap25 - Image Size: Rows:'+str(rows)+' Columns:'+str(cols))

# Get the size (columns/rows) of the Landuse 100 raster
LUrast = gdal.Open('/Users/lehmanan/Dropbox/aISE/PROJETS/ValPar.CH/downscaling LU/Nathan/2018/AS18_72_25GE.tif')
cols2 = LUrast.RasterXSize
rows2 = LUrast.RasterYSize
band2 = LUrast.GetRasterBand(1)
data2 = band2.ReadAsArray(0, 0, cols2, rows2)
print('Landuse100 - Image Size: Rows:'+str(rows2)+' Columns:'+str(cols2))

###### create output raster file ######
ds_raster = '/Users/lehmanan/Dropbox/aISE/PROJETS/ValPar.CH/downscaling LU/Nathan/2018/results/LU2018v5ge.tif'  # filename
driver_tiff = gdal.GetDriverByName('GTiff')  # GeoTiff
ds = driver_tiff.Create(ds_raster, cols, rows, 1, gdal.GDT_Byte)  # create the output file
# ds = driver_tiff.Create(ds_raster, 1000, 1000, 1, gdal.GDT_Byte)  # create the output file
ds.SetGeoTransform(raster.GetGeoTransform())  # get the coordinate system
ds.SetProjection(raster.GetProjection())  # get the projection
ds.FlushCache()  # save file
ds = None  # close file

##### open expert table #####
loc = '/Users/lehmanan/Dropbox/aISE/PROJETS/ValPar.CH/downscaling LU/Nathan/2018/expert_table_72cat_v3.xls'  # path to the expert table
wb = xlrd.open_workbook(loc)  # open the workbook
sheet = wb.sheet_by_index(0)  # read the sheet
xls_cols = sheet.ncols  # get the number of columns of the Excel sheet
xls_rows = sheet.nrows  # get the number of rows of the Excel sheet
print("xls", xls_cols, xls_rows)

#iterate by lines and columns

for y in range(rows):
    print("row", y)
    for x in range(cols):
        value = data[y, x] #get pixel value (BaseMap25)
        if value > 0 and value < 255:  #only do something if the pixel value is greater than 0 (0=country mask) and smaller than 255 (no data)
            #print('BaseMap25 - Row:'+str(y), 'Column:'+str(x), 'Value:'+str(value)) #to locate current pixel and value
            ##############################################################################################################
            #Step 5: According to expert system table, select those categories that could be elected for the current pixel
            ##############################################################################################################
            BMvalue1 = []  # create an empty array to be filled by values 1 for BaspeMap25
            BMvalue2 = []  # create an empty array to be filled by values 2 for BaspeMap25
            BMvalue3 = []  # create an empty array to be filled by values 3 for BaspeMap25
            for i in range(xls_cols): #iterate in columns to find the BaseMap25 value
                if sheet.cell_value(2, i) == value: #once identified the corresponding value
                    j = 3 #start at the 3rd row to remove headers
                    while j < xls_rows: #read the identified column
                        if sheet.cell_value(j, i) == 1: #acceptable weight values for 1,  possible choices
                            BMvalue1.append(str(int(sheet.cell_value(j, 1)))+';'+str(sheet.cell_value(j, 2))+';'+str(int(sheet.cell_value(j, i)))) #insert [CODE, Landuse100, weight]
                        if sheet.cell_value(j, i) == 2: #acceptable weight values for 2, unique choice
                            BMvalue2.append(str(int(sheet.cell_value(j, 1)))+';'+str(sheet.cell_value(j, 2))+';'+str(int(sheet.cell_value(j, i)))) #insert [CODE, Landuse100, weight]
                        if sheet.cell_value(j, i) == 3: #acceptable weight values for 3, best replacement choice in case of lack of decision
                            BMvalue3.append(str(int(sheet.cell_value(j, 1)))+';'+str(sheet.cell_value(j, 2))+';'+str(int(sheet.cell_value(j, i)))) #insert [CODE, Landuse100, weight]
                        j = j+1 #iterate until last row of the expert table
                    #print('Number of acceptable values 1 in the expert table:'+str(len(BMvalue1)))
                    #print('Number of acceptable values 2 in the expert table:' + str(len(BMvalue2)))
                    #print('Number of acceptable values 3 in the expert table:' + str(len(BMvalue3)))

            ############################################################################################
            # Step 6: Select among the 36 nearest Landuse100 neigbours those with acceptable categories
            # Input: Landuse100 is from geostat and for which we will look for the 36 nearest neighboors
            ############################################################################################
            sizeWin = 20 #definition of the size of the window to identify nearest neighboors, should be 24 to match 600m
            value2 = data2[y, x]  # get pixel value (Landuse100)
            #print('Landuse100 - Row:'+str(y)+' Column:'+str(x)+' Value:'+str(value2))
            LUvalue = []  # create an empty array to be filled by values for Landuse100
            #iterate in the neighbours window starting from the UL corner
            yRow = round(y/4)*4 - 9
            for a in range(6):
                xCol = round(x/4)*4 - 10
                for b in range(6):
                    #print("yRow, xCol :", yRow, xCol)
                    if (yRow >= 0 and xCol >= 0 and yRow < rows and xCol < cols):
                        if data2[yRow, xCol] < 255:  # only pixel values inside Switzerland, nodata = 255
                            LUvalue.append(
                                str(yRow) + ';' + str(xCol) + ';' + str(data2[yRow, xCol]))  # insert [Row;Column;Value]
                    xCol = xCol + 4 #move from 4 pixels to correspond to a 100 pixel
                    #print("search x", xCol)
                yRow = yRow + 4 #move form 4 pixels to correspond to a 100 pixel
                #print("search y", yRow)

            # print('Number of acceptable values in Landuse100:' + str(len(LUvalue)))
            if (len(LUvalue)) == 0: #if not acceptable values, empty array
                #print('Landuse100 array is empty')
                uniqueValues = [0] #then the uniqueValues array is equal to 0 > pixelArrayValue will be empty
            ########################################################################
            # Step 7: Calculate the inverse distance to each neighbour
            # Step 8: Sum up the inverse distances for each category
            # Step 9: Assign the category with higher score to the BaseMap25 pixel
            # Input: LUvalue array; [optional] Alti 25 for Z values
            ########################################################################
            newArray = []
            pixelValueArray = []
            pixelValue = 0
            uniqueValues = []


            ###### Case 2 #####
            #print('BMValue1 length:' + str(len(BMvalue1)))
            #print('BMValue2 length:' + str(len(BMvalue2)))
            #print('BMValue3 length:' + str(len(BMvalue3)))
            if len(BMvalue2) > 0:  # unique value case; BM25 value = 2 then assign the only value possible in LU100
                pixelValue = BMvalue2[0].split(';')[0]  # directly assign the value
                #print('Assigned pixel value case 2: ' + str(pixelValue))

            ###### Case 3 #####
            if len(BMvalue1) > 0 and len(BMvalue3) > 0 and len(BMvalue2)==0: #case with possible value (1) and (3); (3) = default choice
                for d in range(len(LUvalue)):
                    newArray.append(LUvalue[d].split(';')[2])  # position 2 is the value
                    uniqueValues = numpy.unique(newArray)  # get unique values from the array
                for m in range(len(BMvalue1)): #iterate in all possible values for BM25 class = 1
                    for n in range(len(uniqueValues)): #iterate in all possible unique values of LU100
                        if uniqueValues[n] == BMvalue1[m].split(';')[0]: #compare values from BM25 and LU100
                            pixelValueArray.append(int(uniqueValues[n])) #insert in array only acceptable values
                for m in range(len(BMvalue3)): #iterate in all possible values for BM25 class = 3
                    for n in range(len(uniqueValues)): #iterate in all possible unique values of LU100
                        if uniqueValues[n] == BMvalue3[m].split(';')[0]: #compare values from BM25 and LU100
                            pixelValueArray.append(int(uniqueValues[n])) #insert in array only acceptable values
                if len(pixelValueArray) == 1:  # if only 1 value is stored in the array
                    pixelValue = int(pixelValueArray[0])  # assign the new pixel value to be written in the new raster file
                    # print('Assigned pixel value: ' + str(pixelValue))
                elif len(pixelValueArray) == 0: #in case the acceptable value array is empty, assign the default (3) value
                    pixelValue = BMvalue3[0].split(';')[0]  # assign the default (3) value
                    #print('Assigned default pixel value case 3 ' + str(pixelValue))
                else:
                    pxVal = []  # store class and sum of IDW
                    pxVal2 = []  # store only IDW values to identify the highest one
                    for l in range(
                            len(pixelValueArray)):  # iterate in LUvalue array to get position and calculate distances
                        px = []  # array for measuring distance
                        idwClass = 0  # used for summing IDW
                        for i in range(len(LUvalue)):
                            if pixelValueArray[l] == int(LUvalue[i].split(';')[2]):  # ensure that we iterate only with acceptable LU100 values
                                px.append(LUvalue[i])
                                # initial pixel position corresponds to BM25; y and x variables
                                dY = abs(y - int(LUvalue[i].split(';')[0]))  # distance following rows in pixel value
                                dX = abs(x - int(LUvalue[i].split(';')[1]))  # distance following columns in pixel value
                                distXYZ = math.sqrt((dX ** 2) + (dY ** 2))  # hypotenuse
                                rangeXY = 18.38  # sqrt (13^2+13^2) distance max 13 pixels
                                lissage = 0.1 # entre 0.01 et 1
                                IDW = 1 / (distXYZ/rangeXY + lissage)
                                #print("dx", dX, "dy", dY, "dist", distXYZ, "IDW", IDW)
                                idwClass = idwClass + IDW  # sum IDW by acceptable categories
                        #print('Number of pixels for class ' + str(pixelValueArray[l]) + ': ' + str(len(px)))
                        #print('IDW for class ' + str(pixelValueArray[l]) + ': ' + str(idwClass))
                        pxVal.append(str(pixelValueArray[l]) + ';' + str(idwClass))  # array with class and sum of IDW
                        pxVal2.append(str(idwClass))
                    # assign pixel value to the category with highest IDW
                    highIDW3 = max(pxVal2, key=lambda x: float(x))  # get the highest sum of IDW
                    for g in range(len(pxVal)):
                        if highIDW3 == pxVal[g].split(';')[1]:
                            pixelValue = pxVal[g].split(';')[0]
                #print('Assigned pixel value case 3: ' + str(value) + ":" + str(pixelValue))

            ###########################################################################################
            #Write output raster file
            # Input: ds_raster
            ###########################################################################################
            ras_out = gdal.Open(ds_raster, gdal.GA_Update)
            band1 = ras_out.GetRasterBand(1).ReadAsArray() #read the output file
            # print('Assigned pixel value: ' + str(x) + '  ' + str(y)+ '  '  + str(pixelValue))
            band1[0][x] = 255
            band1[y][x] = pixelValue

            ras_out.GetRasterBand(1).WriteArray(band1) #write value
            ras_out.FlushCache()  # save file
            ras_out = None #clear
##################################################################################################################
#Step 11: [optional] Replace categories wherever river, road or train linear segments are available from BaseMap25
##################################################################################################################