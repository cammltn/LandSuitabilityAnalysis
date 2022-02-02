# Name: Camille Milton
# Date: 10 August 2018
# Assignment: Lab 9 Raster Analysis


# 3: Pre-processing

import arcpy

arcpy.env.overwriteOutput = True

arcpy.AddMessage("Running Script LandSuit...")


# 6: my exception classes

class WeightError(Exception):
    pass


class unitsError(Exception):
    pass


class LicenseError(Exception):
    pass


try:
    # 6: check if license is available - if not raise error
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise LicenseError

    arcpy.AddMessage("Setup Complete!")

    # 1: Input Parameters

    work = arcpy.GetParameterAsText(0)

    DEM = arcpy.GetParameterAsText(1)

    landuse = arcpy.GetParameterAsText(2)

    SlopeW1 = float(arcpy.GetParameterAsText(3))

    AspectW2 = float(arcpy.GetParameterAsText(4))

    units = arcpy.GetParameterAsText(5)

    suit_raster = arcpy.GetParameterAsText(6)

    path = arcpy.GetParameterAsText(7)

    # 6: check user input for both weights raise error if incorrect
    if (SlopeW1 > 1.00):
        raise WeightError
    elif (SlopeW1 < 0.00):
        raise WeightError
    elif (AspectW2 > 1.00):
        raise WeightError
    elif (AspectW2 < 0.00):
        raise WeightError
    elif (SlopeW1 + AspectW2 != 1):
        raise WeightError
    else:
        pass

    # 6: check if the user's input for units raise error if incorect
    units = units.lower()
    if ((units != 'acres') and (units != 'hectares')):
        raise unitsError
    else:
        pass

    arcpy.AddMessage("Setup Complete!")

    #  2: Run Suitability Model
    arcpy.AddMessage("Starting Suitability Model...")
    # Calculate Slope and Aspect of DEM

    outslope = arcpy.sa.Slope(DEM, "DEGREE")
    outslope.save("slope")
    arcpy.AddMessage("Slope Calculated from DEM Raster")

    outaspect = arcpy.sa.Aspect(DEM)
    outaspect.save("aspect")
    arcpy.AddMessage("Aspect Calculated from DEM Raster")

    # 2: Reclassify

    arcpy.AddMessage(
        "Begin Reclassification of Slope, Aspect, and Landuse Raster to Determine Land Suitability for Housing")
    slope_range = arcpy.sa.RemapRange([[0, 3, 5], [3, 6, 4], [6, 9, 3], [9, 15, 2], [15, 30, 1]])
    class_slope = arcpy.sa.Reclassify(outslope, "VALUE", slope_range)
    class_slope.save("class_slope")

    arcpy.AddMessage("Slope Raster Reclassified!")

    aspect_range = arcpy.sa.RemapRange(
        [[-1, 0, 5], [0, 45, 1], [45, 135, 3], [135, 225, 5], [225, 315, 3], [315, 360, 1]])
    class_aspect = arcpy.sa.Reclassify(outaspect, "VALUE", aspect_range)
    class_aspect.save("class_aspect")

    arcpy.AddMessage("Aspect Raster Reclassified!")

    land = ((landuse == 21) | (landuse == 31) | (landuse == 52) | (landuse == 71))
    class_land = arcpy.sa.Reclassify(landuse, "VALUE", land)
    class_land.save("class_land")
    arcpy.AddMessage("Landuse Raster Reclassified!")

    # Calculate Final Output Suitability Raster
    arcpy.AddMessage("Calculating Output Suitability Raster")
    suitability = (SlopeW1 * class_slope + AspectW2 * class_aspect) * class_land
    suitability.save(suit_raster)
    arcpy.AddMessage("Output Suitability Raster has been Created")

    # 4: Messaging

    rows = arcpy.da.SearchCursor(suit_raster, "Suitability Class", "Pixel Count")
    for row in rows:
        pixels = row.getValue("Pixel Count")
    desc = arcpy.Describe(suit_raster)

    descRast = arcpy.Describe(suit_rast)
    x_cell = descRast.meanCellWidth
    y_cell = descRast.meanCellHeight
    x_rast = descRast.width
    y_rast = descRast.height

    rasterHeight = y_cell * y_rast
    rasterWidth = x_cell * x_rast
    cellarea = (rasterHeight * rasterWidth)
    if (units == "acres"):
        area = cellarea * 0.000247105
    elif (units == "hectares"):
        area = (cellarea * 0.0001)
    round(area, 3)

    # 5: Output Text File

    arcpy.CreateTable_management(path, suit_raster)

except WeightError:
    arcpy.AddError(" ERROR: W1 and W2 must be between 0 and 1 and add up to 1!")
except unitsError:
    arcpy.AddError("ERROR: Units must be either 'acres' or 'hectares'!")
except LicenseError:
    arcpy.AddError("ERROR: License not available!")
except Exception as error:
    arcpy.AddError(error)

arcpy.CheckInExtension("Spatial")
arcpy.AddMessage("Suitability Model is Complete!")
