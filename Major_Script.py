import os 
from qgis.core import *

#Remove map layers from current project
QgsProject.instance().removeAllMapLayers()

#Write import statements 
filePath = r"C:\Users\david\OneDrive\Documents\SEM2 2019\Geo Progrmming\Mari\PYTHON\PYTHON\\"


#set up local variables like filepaths.
planning_fileName  = "planningzones.shp"
area_fileName = "precinct5A.shp"

#Add your input layers 
planningLayer = iface.addVectorLayer(filePath + planning_fileName , planning_fileName[:-4], "ogr")
areaLayer = iface.addVectorLayer(filePath + area_fileName , area_fileName[:-4], "ogr")

#Clip planning scheme by area 
clipOutput = filePath + "clipOutput_57.shp"

clipdict = { "INPUT" : planningLayer, 
              "OVERLAY" : areaLayer  ,
              "OUTPUT" : clipOutput}

processing.run("native:clip", clipdict) 

iface.addVectorLayer(clipOutput, "", 'ogr')

#Add new field for area of clipped polygons

clippedLayer = iface.activeLayer()

clippedLayer.startEditing()

clippedLayer.dataProvider().addAttributes([QgsField("AREA" , QVariant.Double)])
clippedLayer.dataProvider().addAttributes([QgsField("CODE" , QVariant.String)])

clippedLayer.updateFields()

#ADD AREA INTO FIELD
features = clippedLayer.getFeatures()

idx = clippedLayer.fields().indexOf('ZONE_CODE')

area_index = f.fieldNameIndex('AREA')

atot = 0.0 
for f in features: 
    
    geom = f.geometry().area()
            
#    print('Area: ', geom)
    
    f.setAttribute(area_index , geom)
    
    clippedLayer.updateFeature(f)
    
#Fill in ZONE CODE field with code minus numbers 
    area_attr = f.attributes()[idx_a]
    
    atotal = atot + area_attr
    
    
    attbs = f.attributes()[idx]
    
    no_digits = []
    
    for i in attbs:
        if not i.isdigit():
            no_digits.append(i)
        
            result = ''.join(no_digits)
                    
    
    f.setAttribute(f.fieldNameIndex('CODE'), result)
    
    clippedLayer.updateFeature(f)

clippedLayer.commitChanges()
print (atotal)

#Sum area values of polygons with the same zone code

code_idx = clippedLayer.fields().indexOf('CODE')

zone_codes = clippedLayer.uniqueValues(code_idx)
#print (zone_codes)
    
idx_a = clippedLayer.fields().indexOf('AREA')



for uv in zone_codes :
         
# statement to select only features with same zone code 

    expression = ('"CODE" = ' + "'" + uv +"'")
#    print(expression)
    request = QgsFeatureRequest().setFilterExpression(expression)
#   print (request)
    
# get features with same zone code    
    featforuv = clippedLayer.getFeatures(request)
#    print (featforuv)
    total = 0.0
      
    for a in featforuv:
        attributes = a.attributes()[idx_a]
#        print (attributes)
        
        total = total + attributes
        
#        print('total:', total)
       
    print("ZONE:",uv, "Total area:", total/1000000)
    
