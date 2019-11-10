"""

* Daniel Bitters
* 2018
* 
* This script analyzes netCDF data by creating an ArcGIS Pro chart of the 
* frequencies of temperature differences from two previous rasters from the "Raster Creation" tool.

"""

import os
import arcpy
import numpy
from arcpy import env
from arcpy import mp
#env.workspace= 'c:/GISClass/home'
env.overwriteOutput=True


#ws must be geodatabase
ws=arcpy.GetParameterAsText(0)
#get first raster
fr= arcpy.GetParameterAsText(1)
#second raster
sr= arcpy.GetParameterAsText(2)

#get lower left corner of first raster layer for projection later on
desc = arcpy.Describe(fr)
x = desc.extent.XMin
y = desc.extent.YMin

#convert first and second raster to numpy array
fr_array= arcpy.RasterToNumPyArray(fr)
sr_array= arcpy.RasterToNumPyArray(sr)

#get difference between second raster and first raster
diff_array=sr_array-fr_array

#convert the difference raster to array
diff_raster=arcpy.NumPyArrayToRaster(diff_array,arcpy.Point(x,y),'','',-9999)

final_ws= ws + '\\'
diff_raster.save(final_ws + 'diff_raster')
 
#get spatial reference of original first raster
coor_system = arcpy.Describe(fr).spatialReference

#project the difference raster to match the original raster 
projected_raster=arcpy.management.ProjectRaster(diff_raster,final_ws+'projected_raster',coor_system,'','','','',coor_system)
#projected_raster.save(final_ws +'projected_raster')

#add differnece layer to map
p=arcpy.mp.ArcGISProject("CURRENT")
m=p.listMaps()[0]
#make a feature layer from feature class
temp=arcpy.management.MakeRasterLayer(final_ws+'projected_raster','temp')
temp[0].name= 'difference_raster'
#add to map
m.addLayer(temp[0])

#convert float raster to int raster in order to convert it to polygon later on
times_raster=arcpy.sa.Times(projected_raster,100)
int_times_raster=arcpy.sa.Int(times_raster)
#int_times_raster.save(final_ws+'int_times_raster')

#final polygon with raster features from difference raster
polygon_raster=arcpy.conversion.RasterToPolygon(int_times_raster, final_ws+'polygon_rasten')

#get back the float values
arcpy.AddField_management(polygon_raster,'double', 'DOUBLE')
arcpy.CalculateField_management(polygon_raster, 'double','!gridcode!/100')


#add polygon layer to map
p=arcpy.mp.ArcGISProject("CURRENT")
m=p.listMaps()[0]
#make a feature layer from feature class
temp=arcpy.MakeFeatureLayer_management(final_ws+'polygon_raster')
temp[0].name= 'polygon_raster'
#add to map
m.addLayer(temp[0])

#make the chart from the polygon
#aprx = arcpy.mp.ArcGISProject("current")
#layer = map.listLayers('polygon_raster')[0]
aprx = arcpy.mp.ArcGISProject("current")
map = aprx.listMaps()[0]
layer = map.listLayers('polygon_raster')[0]

c = arcpy.Chart('Difference of Temperatures between two days')

c.title='Difference of Temperatures between two days'
c.type = 'histogram'
c.xAxis.field='double'
c.xAxis.title='temperature values'

c.histogram.binCount=21
c.histogram.showMean=True
c.histogram.showMedian=True
c.histogram.showStandardDeviation=True

c.addToLayer(layer)



