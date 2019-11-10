"""
* Daniel Bitters
* 2018
*
* This script creates an internal ArcGIS Pro tool that reads in a netCDF file and outputs
* a single day's raster layer in ArcGIS Pro as a GRIDFLOAT (.flt).  The tool also 
* creates an organized file structure such that a year folder and data variable folder are created to store
* the new .flt file. 

"""

import os
import arcpy
from arcpy import mp
from arcpy import env
#env.workspace= 'c:/GISClass/home'
env.overwriteOutput=True


#get project workspace (home folder-not default geodatabase), date of data, .nc file name, and raster name the user wants
ws=arcpy.GetParameterAsText(0)
data_file=arcpy.GetParameterAsText(1)
date= arcpy.GetParameterAsText(2)
nrl = arcpy.GetParameterAsText(3)

data_file_split= data_file.split('_')

#get year out of the .nc file name and variable
year=data_file_split[3]
var=data_file_split[2]

#make the year and variable folder
yeardir= ws+ '\\' + year
if not os.path.exists(yeardir):
    os.mkdir(yeardir)
os.chdir(yeardir)

outdir= yeardir+ '\\' + var
if not os.path.exists(outdir):
    os.mkdir(outdir)
os.chdir(outdir)

#make the day file name
day=date.replace('/', '-')
file= var +'_'+ day+ '.flt'

float_raster_path=outdir + '\\' + file

#cdf raster layer-map view
cdf_raster= arcpy.md.MakeNetCDFRasterLayer(data_file,var,'x','y','cdf_raster')

#cdf raster showing a specific day
dimension_raster=arcpy.md.SelectByDimension(cdf_raster,[['time',date]], 'BY_VALUE')

#make a FLT for a specific day
float_raster=arcpy.conversion.RasterToFloat(dimension_raster, float_raster_path)   

p=arcpy.mp.ArcGISProject("CURRENT")
m=p.listMaps()[0]
#make a raster from the flt file
temp=arcpy.MakeRasterLayer_management(float_raster_path)
temp[0].name= nrl
#add the flt file with the name the user provided
m.addLayer(temp[0])




