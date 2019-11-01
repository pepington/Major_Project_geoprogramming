import os 
from qgis.core import *

#Remove map layers from current project
QgsProject.instance().removeAllMapLayers()

#Write import statements 
filePath = r"C:\Users\david\OneDrive\Documents\SEM2 2019\Geo Progrmming\Major Projj\suburbs\\"

#set up local variables like filepaths.
planning_fileName  = "planningzones.shp"
area_fileName = "merged.gpkg"

#Add your input layers 
planningLayer = iface.addVectorLayer(filePath + planning_fileName , planning_fileName[:-4], "ogr")
areaLayer = iface.addVectorLayer(filePath + area_fileName , area_fileName[:-4], "ogr")

#Clip planning scheme by area
#Set variable for clip output 
clipOutput = filePath + "clipOutput_67.shp"

#Create dictionary for clip parameters 
clipdict = { "INPUT" : planningLayer, 
              "OVERLAY" : areaLayer  ,
              "OUTPUT" : clipOutput}
              
#Run clip, passing dictionary as parameters
processing.run("native:clip", clipdict) 

#Add clipped layer to QGIS
iface.addVectorLayer(clipOutput, "", 'ogr')

#Add new fields for area of clipped polygons and code
#Set clip output layer as active variable 
clippedLayer = iface.activeLayer()

#As we are changing the fields of the layer, start editing 
clippedLayer.startEditing()

#Add new layers, defining names and expected type of data 
clippedLayer.dataProvider().addAttributes([QgsField("AREA" , QVariant.Double)])
clippedLayer.dataProvider().addAttributes([QgsField("CODE" , QVariant.String)])

#Updte fields to expect added fields
clippedLayer.updateFields()

#ADD AREA INTO FIELD
#Collect features from clipped layer
features = clippedLayer.getFeatures()

#Set variable for index of zone codes 
idx = clippedLayer.fields().indexOf('ZONE_CODE')

#Set variable for index of newly created area field  
area_index = clippedLayer.fields().indexOf('AREA')


a_tot = 0.0
#Begin iterating throough features in clipped layer
for f in features: 
    
#Set variable for area of feature      
    geom = f.geometry().area()
            

# Set area of feature to the new AREA field 
    f.setAttribute(area_index , geom)
    
#Update feature to expect new attribute
    clippedLayer.updateFeature(f)
    
    
#Fill in new CODE field with ZONE_CODE minus numbers 
# set variable for feature ZONE_CODE attributes       
    attbs = f.attributes()[idx]
    
#Set variable to replace numbers with vacant space    
    no_digits = []
    
#begin iterating through string values in ZONE_CODE    
    for i in attbs:

#If string value is a digit, replace with vacant space
        if not i.isdigit():
#append string value with vacant space             
            no_digits.append(i)
#Given in some codes there is now a vacant space, join string pieces together        
            result = ''.join(no_digits)
                    
#Set new attributes of new CODE field to result of iteration
#Attributes in CODE field are now the same as ZONE_CODE field, without numbers
    f.setAttribute(f.fieldNameIndex('CODE'), result)

#FIND TOTAL AREA OF INVESTIGATION AREA
#set variable for index of AREA            
    a_attr = f.attributes()[area_index]

#To find total area of investigation area, a_tot set to zero above
#With each iteration of features, feature area will be added
#When iteration finished, will result in total area of all feaures
    a_tot = a_tot + a_attr
    
#Update features to exect new attributes 
    clippedLayer.updateFeature(f)
    
 
#Finish  editing clipped layer
clippedLayer.commitChanges()

#CREATE DICTIONARY OF ZONE CODES 
zone_dict = {"SUZ" : "Special Use Zone",
            "PUZ"  : "Public Use Zone",
            "MUZ"  : "Mixed Use Zone",
            "RDZ"  : "Road Zone",
            "UFZ"  : "Urban Floodway Zone",
            "RGZ"  : "Residential Growth Zone",
            "NRZ"  : "Neighbourhood Residential Zone",
            "ACZ"  : "Activity Centre Zone",
            "GRZ"  : "General Residential Zone",
            "CZ"   : "Commercial Zone",
            "INZ"  : "Industrial Zone",
            "PZ"   : "Port Zone",
            "PPRZ" : "Public Park and Recreation Zone",
            "CA"   : "Commonwealth Land Zone",
            "CDZ"  : "Comprehensive Development Zone"
            }


#SUM AREA VALUES OF POLYGONS WITH SAME VALUE IN CODE FIELD
#Set variable for index of code field
code_idx = clippedLayer.fields().indexOf('CODE')

#Set variable for unique vaues in CODE field
zone_codes = clippedLayer.uniqueValues(code_idx)

#Set variable for AREA field index    
idx_a = clippedLayer.fields().indexOf('AREA')


#Begin iterating through the unique values
for uv in zone_codes :

         
# statement to select only features with same zone code 
    expression = ('"CODE" = ' + "'" + uv +"'")
    
# Select features based on statement 
    request = QgsFeatureRequest().setFilterExpression(expression)
    
# Set variable for selected features    
    featforuv = clippedLayer.getFeatures(request)
    
#Set variable to zero 
    total = 0.0
    
#Begin iterating through groups of features with same CODE      
    for a in featforuv:
        
#Set variable for features index of AREA field 
        attributes = a.attributes()[idx_a]

#With each feature iterated through, area will be added 
#When last feature iterated, total area of common CODE features found
        total = total + attributes


#set variable for passing unique zone codes through zone code dictionary     
    Zone_exp =  zone_dict[uv]

#Area fields set to square meters, divide by 1000000 to return sqkm
#convert total area of investigation area to sqkm
    totalkm2 = total/1000000 
    
#Convert total area of grouped zone features to sqkm    
    a_totalkm2 = a_tot/1000000
    
#Divide grouped features by total investigation area, area to find percentage proportion
# each zone code makes contributes to total area
    perc = (totalkm2/a_totalkm2)*100

#PRINT ZONE CODE, ZONE MEANING , TOTAL AREA OF ZONE AND PERCENTAGE PROPORTION    
    print("ZONE:",uv, "(",Zone_exp,")" ,"\n", "Total area km2:", totalkm2 , "\n", "Percentage:", perc, "%")
    
