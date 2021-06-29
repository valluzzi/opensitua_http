# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2019 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        mapfile.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/09/2019
# -------------------------------------------------------------------------------
from osgeo import gdal, gdalconst
from osgeo import osr, ogr
import numpy as np
from .strings import *
from .filesystem import *
from .stime import *
import operator
import opensitua_core as pkg
from opensitua_core import template
from .http import Params,JSONResponse

# TYPE [chart|circle|line|point|polygon|raster|query]
GEOMETRY_TYPE = {
    ogr.wkb25DBit: "wkb25DBit",
    ogr.wkb25Bit: "wkb25Bit",
    ogr.wkbUnknown: "LINE",  # unknown
    ogr.wkbPoint: "POINT",
    ogr.wkbLineString: "LINE",
    ogr.wkbPolygon: "POLYGON",
    ogr.wkbMultiPoint: "POINT",
    ogr.wkbMultiLineString: "LINE",
    ogr.wkbMultiPolygon: "POLYGON",
    ogr.wkbGeometryCollection: "POLYGON",
    ogr.wkbNone: "NONE",
    ogr.wkbLinearRing: "POLYGON",
    ogr.wkbPoint25D: "POINT",
    ogr.wkbLineString25D: "LINE",
    ogr.wkbPolygon25D: "POLYGON",
    ogr.wkbMultiPoint25D: "POINT",
    ogr.wkbMultiLineString25D: "LINE",
    ogr.wkbMultiPolygon25D: "POLYGON",
    ogr.wkbGeometryCollection25D: "POLYGON"
}

def PixelOf(value,unit,style="solid"):

    if isstring(value):
        value = value.replace(",",".")
    if float(value)<=0.1 and style=="solid" :
        return 0.5
    elif unit=="Pixel":
        return round(float(value),2)
    elif unit =="MM":
        return round(float(value)*3.779,2)
    return -1

def safename(filename, additional_chars=r''):
    """
    safename - give a safe name for the filesystem
    """
    notallowed = r'~"#%&*:<>?{|}'
    chars = notallowed + additional_chars
    for j in range(len(chars)):
        c = chars[j]
        filename = filename.replace(c,'_')
    return filename

def randcolor(alpha=255):
    """
    randcolor
    """
    return (randint(255), randint(255), randint(255), alpha)

def classify(minValue, maxValue, k):
    w = (maxValue - minValue)
    w = w if w > 0 else 1.0
    step = w / float(k - 1)
    values = [minValue + step * j for j in range(k)]
    # colormap = plt.get_cmap('Spectral_r')
    # colors = [matplotlib.colors.to_hex(colormap(item/w)) for item in values]
    colors = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"]
    items = [{"alpha": 255, "value": values[j], "label": "%.2g" % values[j], "color": colors[j]} for j in
             range(len(values))]
    return items


def singlebandgray(minValue, maxValue):
    return {
        "brightnesscontrast": {"brightness": 0, "contrast": 0},
        "huesaturation": {"colorizeBlue": 128, "colorizeGreen": 128,
                          "colorizeOn": 0, "colorizeRed": 255, "colorizeStrength": 255, "grayscaleMode": 0,
                          "saturation": 0},
        "rasterrenderer": {
            "alphaBand": -1,
            "contrastEnhancement": {
                "algorithm": "StretchToMinimumMaximum",
                "maxValue": maxValue,
                "minValue": minValue
            },
            "gradient": "BlackToWhite",
            "grayBand": 1,
            "opacity": 1,
            "rasterTransparency": {},
            "type": "singlebandgray"
        },
        "rasterresampler": {"maxOversampling": 2}
    }


def singlebandpseudocolor(minValue, maxValue, k=5):
    minValue = minValue if not np.isnan(minValue) else 0.0
    maxValue = maxValue if not np.isnan(maxValue) else 0.0

    # [{'color': '#abdda4', 'alpha': 255, 'value': 0.296875, 'label': '0.3'},...]
    classes = classify(minValue, maxValue, k)

    return {
        "brightnesscontrast": {"brightness": 0, "contrast": 0},
        "huesaturation": {"colorizeBlue": 128, "colorizeGreen": 128,
                          "colorizeOn": 0, "colorizeRed": 255, "colorizeStrength": 255, "grayscaleMode": 0,
                          "saturation": 0},
        "rasterrenderer": {
            "alphaBand": 0,
            "rastershader": {
                "colorrampshader": {"colorRampType": "INTERPOLATED", "clip": 0,
                                    "item": classes
                                    },
            },

            "opacity": 1,
            "classificationMin": minValue,
            "classificationMax": maxValue,
            "classificationMinMaxOrigin": "MinMaxFullExtentExact",
            "band": 1,
            "rasterTransparency": {},
            "type": "singlebandpseudocolor"
        },
        "rasterresampler": {"maxOversampling": 2}
    }


def singlebandcustomcolor(classes, colorRampType="INTERPOLATED"):
    if len(classes):
        minValue = classes[0]["value"]
        maxValue = classes[-1]["value"]
    else:
        minValue, maxValue = 0, 0

    return {
        "brightnesscontrast": {"brightness": 0, "contrast": 0},
        "huesaturation": {"colorizeBlue": 128, "colorizeGreen": 128,
                          "colorizeOn": 0, "colorizeRed": 255, "colorizeStrength": 255, "grayscaleMode": 0,
                          "saturation": 0},
        "rasterrenderer": {
            "alphaBand": 0,
            "rastershader": {
                "colorrampshader": {"colorRampType": colorRampType, "clip": 0,
                                    "item": classes
                                    },
            },

            "opacity": 1,
            "classificationMin": minValue,
            "classificationMax": maxValue,
            "classificationMinMaxOrigin": "MinMaxFullExtentExact",
            "band": 1,
            "rasterTransparency": {},
            "type": "singlebandpseudocolor"
        },
        "rasterresampler": {"maxOversampling": 2}
    }


def multibandcolor():
    return {
        "brightnesscontrast": {"brightness": 0, "contrast": 0},
        "huesaturation": {"colorizeBlue": 128, "colorizeGreen": 128,
                          "colorizeOn": 0, "colorizeRed": 255, "colorizeStrength": 100, "grayscaleMode": 0,
                          "saturation": 0},
        "rasterrenderer": {"opacity": 1, "alphaBand": -1, "blueBand": 3, "greenBand": 2, "type": "multibandcolor",
                           "redBand": 1},

        "rasterresampler": {"maxOversampling": 2}
    }

def SimpleFill( name, color="#ff0000ff"):
    return {
            "type":"fill",
            "name":"%s"%(name),
            "force_rhr":0,
            "alpha":1,
            "clip_to_extent":1,
            "layer":{
                "class":"SimpleFill",
                "locked":0,
                "pass":0,
                "enabled":1,
                "prop": [
                    {"k":"border_width_map_unit_scale", "v":"3x:0,0,0,0,0,0"},
                    {"k":"color", "v":color},
                    {"k":"joinstyle", "v":"bevel"},
                    {"k":"offset", "v":"0,0"},
                    {"k":"offset_map_unit_scale", "v":"3x:0,0,0,0,0,0"},
                    {"k":"offset_unit", "v":"MM"},
                    {"k":"outline_color", "v":"#000000ff"},
                    {"k":"outline_style", "v":"solid"},
                    {"k":"outline_width", "v":"0.26"},
                    {"k":"outline_width_unit", "v":"MM"},
                    {"k":"style", "v":"solid"}
                ]
            }#end layer
        }

def SimpleLine( options ):

    line_color = options["line_color"] if "line_color" in options else randcolor()
    line_style = options["line_style"] if "line_style" in options else "solid"
    line_width = options["line_width"] if "line_width" in options else 0.26
    line_width_unit = options["line_width_unit"] if "line_width_unit" in options else "MM"
    joinstyle = options["joinstyle"] if "joinstyle" in options else "bevel"
    capstyle = options["capstyle"] if "capstyle" in options else "square"

    return {
        "type": "line",
        "name": "0",
        "force_rhr": 0,
        "alpha": 1,
        "clip_to_extent": 1,
        "layer": {
            "class": "SimpleLine",
            "locked": 0,
            "pass": 0,
            "enabled": 1,
            "prop": [
                {"k": "capstyle", "v": capstyle},
                {"k": "customdash", "v": "5;2"},
                {"k": "customdash_map_unit_scale", "v": "3x:0,0,0,0,0,0"},
                {"k": "customdash_unit", "v": "MM"},
                {"k": "draw_inside_polygon", "v": "0"},
                {"k": "joinstyle", "v": joinstyle},
                {"k": "line_color", "v": line_color},
                {"k": "line_style", "v": line_style},
                {"k": "line_width", "v": line_width},
                {"k": "line_width_unit", "v": line_width_unit},
                {"k": "offset", "v": "0"},
                {"k": "offset_map_unit_scale", "v": "3x:0,0,0,0,0,0"},
                {"k": "offset_unit", "v": "0"},
                {"k": "ring_filter", "v": "0"},
                {"k": "use_custom_dash", "v": "0"},
                {"k": "width_map_unit_scale", "v": "3x:0,0,0,0,0,0"}
            ]
        }#end layer
    }

def singleSymbol( options ):

    return {
        "type": "singleSymbol",
        "forceraster": 0,
        "symbollevels": 0,
        "enableorderby": 0,
        "symbols": {"symbol": SimpleLine(options)},
        "rotation": "",
        "sizescale": ""
    }

def categorizedSymbol( options ):

    symbols =[]
    categories =[]
    for category in options["categories"]:
        category["render"] = "true"
        symbol = SimpleFill( category["symbol"], category["color"]  )
        symbols.append(symbol)
        categories.append(category)

    return {
        "type": "categorizedSymbol",
        "attr": options["attr"],
        "forceraster":0, "symbollevels":0, "enableorderby":0,
        "categories": {"category":categories},
        "symbols": {"symbol":symbols},
        "rotation": "",
        "sizescale":""
    }

def graduatedSymbol( options ):

    symbols =[]
    categories =[]
    for category in options["ranges"]:
        category["render"] = "true"
        symbol = SimpleFill( category["symbol"], category["color"]  )
        symbols.append(symbol)
        categories.append(category)

    return {
        "type": "graduatedSymbol",
        "attr": options["attr"],
        "forceraster":0, "symbollevels":0, "enableorderby":0,
        "ranges": {"range":categories},
        "symbols": {"symbol":symbols},
        "rotation": "",
        "sizescale":""
    }


def renderer_v2(geomtype="POINT", options=None):
    geomtype = upper(geomtype)
    if geomtype == "POINT":
        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "marker",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleMarker",
                        "locked": 0,
                        "prop": [
                            {"k": "angle", "v": 0},
                            {"k": "color", "v": randcolor() },
                            {"k": "horizontal_anchor_point", "v": 1},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "name", "v": "circle"},
                            {"k": "offset", "v": [0, 0]},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "outline_color", "v": [0, 0, 0, 255]},
                            {"k": "outline_style", "v": "solid"},
                            {"k": "outline_width", "v": 0.26},
                            {"k": "outline_width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "outline_width_unit", "v": "MM"},
                            {"k": "scale_method", "v": "diameter"},
                            {"k": "size", "v": 2},
                            {"k": "size_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "size_unit", "v": "MM"},
                            {"k": "vertical_anchor_point", "v": 1}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    elif geomtype == "LINE":

        if options and "type" in options and options["type"]=="singleSymbol":
            return singleSymbol( options )
        if options and "type" in options and options["type"]=="categorizedSymbol":
            return categorizedSymbol( options )
        if options and "type" in options and options["type"]=="graduatedSymbol":
            return graduatedSymbol( options )

        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "line",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleLine",
                        "locked": 0,
                        "prop": [
                            {"k": "capstyle", "v": "square"},
                            {"k": "customdash", "v": "5;2"},
                            {"k": "customdash_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "customdash_unit", "v": "MM"},
                            {"k": "draw_inside_polygon", "v": 0},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "line_color", "v": randcolor() },
                            {"k": "line_style", "v": "solid"},
                            {"k": "line_width", "v": 0.26},
                            {"k": "line_width_unit", "v": "MM"},
                            {"k": "offset", "v": 0},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "use_custom_dash", "v": 0},
                            {"k": "width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    elif geomtype == "POLYGON":

        if options and "type" in options and options["type"]=="categorizedSymbol":
            return categorizedSymbol( options )
        if options and "type" in options and options["type"]=="graduatedSymbol":
            return graduatedSymbol( options )

        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "fill",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleFill",
                        "locked": 0,
                        "prop": [
                            {"k": "border_width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "color", "v": randcolor(75)},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "offset", "v": 0},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "outline_color", "v": [0, 0, 0, 255]},
                            {"k": "outline_style", "v": "solid"},
                            {"k": "outline_width", "v": 0.26},
                            {"k": "outline_width_unit", "v": "MM"},
                            {"k": "style", "v": "solid"}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    return {}


def GDAL_MAPLAYER(filename, layername=None, options=None):
    """
    GDAL_MAPLAYER
    """
    maplayer = {}

    if "|" in filename:
        filename, layerid = filename.split("|", 1)
        layerid = leftpart(layerid, "|")  # if any other |
        _, layerid = layerid.split("=", 1)
        layerid = int(layerid)
    else:
        layerid = 0

    ext = justext(filename).lower()
    filename = normpath(filename)
    layername = str(layername) if layername else str(juststem(filename))

    if ext in ("tif", "jpg", "jpeg"):
        filetfw = forceext(filename, "tfw")
        filejwg = forceext(filename, "jwg")
        filejgw = forceext(filename, "jgw")
        filejpgw = forceext(filename, "jpgw")
        filewld = forceext(filename, "wld")

        if os.path.isfile(filetfw):
            rename(filetfw, filewld)

        if os.path.isfile(filejwg):
            arr = filetoarray(filejwg)
            (px, rotA, rotB, py, x0, y0) = [item.strip("\r\n") for item in arr][:6]
            p1 = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (x0, y0))
            srs4326 = osr.SpatialReference()
            srs4326.ImportFromEPSG(4326)
            srs3857 = osr.SpatialReference()
            srs3857.ImportFromEPSG(3857)
            transform = osr.CoordinateTransformation(srs4326, srs3857)
            p1.Transform(transform)
            x0, y0 = p1.GetX(), p1.GetY()
            text = sformat("""{px}\n{rotA}\n{rotB}\n{py}\n{minx}\n{miny}""",
                           {"px": px, "py": -abs(float(py)), "minx": x0, "miny": y0, "rotA": rotA, "rotB": rotB})
            strtofile(text, filewld)
            #remove(filejwg)

        if os.path.isfile(filejgw):
            arr = filetoarray(filejgw)
            (px, rotA, rotB, py, x0, y0) = [item.strip("\r\n") for item in arr][:6]
            p1 = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (x0, y0))
            srs4326 = osr.SpatialReference()
            srs4326.ImportFromEPSG(4326)
            srs3857 = osr.SpatialReference()
            srs3857.ImportFromEPSG(3857)
            transform = osr.CoordinateTransformation(srs4326, srs3857)
            p1.Transform(transform)
            x0, y0 = p1.GetX(), p1.GetY()
            text = sformat("""{px}\n{rotA}\n{rotB}\n{py}\n{minx}\n{miny}""",
                           {"px": px, "py": -abs(float(py)), "minx": x0, "miny": y0, "rotA": rotA, "rotB": rotB})
            strtofile(text, filewld)
            #remove(filejgw)

        if os.path.isfile(filejpgw):
            rename(filejpgw, filewld)

        data = gdal.Open(filename, gdalconst.GA_ReadOnly)
        if data:

            b = data.RasterCount  #number of bands
            band = data.GetRasterBand(1)
            m, n = data.RasterYSize, data.RasterXSize
            gt, prj = data.GetGeoTransform(), data.GetProjection()

            srs = osr.SpatialReference()
            if len(prj):
                srs.ImportFromWkt(prj)
            else:
                srs.ImportFromEPSG(3857)

            epsg = srs.ExportToProj4()


            proj4 = epsg if epsg.startswith("+proj") else "init=%s" % epsg
            proj = re.findall(r'\+proj=(\w+\d*)', proj4)
            proj = proj[0] if proj else ""
            ellps = re.findall(r'\+ellps=(\w+\d*)', proj4)
            ellps = ellps[0] if ellps else ""
            geomtype = "raster"
            nodata = band.GetNoDataValue()
            rdata = band.ReadAsArray(0, 0, 1, 1)
            datatype = str(rdata.dtype)

            # Warning!!

            stats = band.GetStatistics(True, True)
            if stats:
                minValue, maxValue = stats[0], stats[1]
            else:
                # Warning!!
                rdata = band.ReadAsArray(0, 0, n, m)
                if rdata.dtype in (np.float32,np.float64):
                    rdata[rdata==nodata] = np.nan
                    minValue, maxValue = np.asscalar(np.nanmin(rdata)), np.asscalar(np.nanmax(rdata))
                else:
                    rdata = rdata.astype(np.float32)
                    rdata[rdata == nodata] = np.nan
                    minValue, maxValue = np.asscalar(np.nanmin(rdata)), np.asscalar(np.nanmax(rdata))


            del data
            (x0, px, rotA, y0, rotB, py) = gt
            minx = x0
            miny = y0 + m * py
            maxx = x0 + n * px
            maxy = y0
            extent = (minx, min(miny, maxy), maxx, max(miny, maxy))
            other = (px, py, nodata, datatype)
            descr = srs.GetName() #srs.GetAttrValue('projcs')
            pipe = {}

            if ext in ("jpg", "jpeg") and not (
                    os.path.isfile(filetfw) or os.path.isfile(filejwg) or os.path.isfile(filejgw) or os.path.isfile(filejpgw) or os.path.isfile(filewld)):
                text = sformat("""{px}\n{rotA}\n{rotB}\n{py}\n{minx}\n{miny}""",
                               {"px": px, "py": -abs(py), "minx": minx, "miny": miny, "rotA": rotA, "rotB": rotB})
                strtofile(text, filewld)

            if b == 1 and options and "pipe" in options:

                if options["pipe"] == "singlebandgray":
                    pipe = singlebandgray(minValue, maxValue)

                elif options["pipe"] == "singlebandpseudocolor" and "classes" in options:

                    colorRampType = options["colorRampType"] if "colorRampType" in options else "INTERPOLATED"
                    pipe = singlebandcustomcolor(options["classes"], colorRampType)

                elif options["pipe"] == "singlebandpseudocolor":

                    k = options["k-classes"] if "k-classes" in options else 5
                    pipe = singlebandpseudocolor(minValue, maxValue, k)

                elif options["pipe"] == "multibandcolor":
                    pipe = multibandcolor()

                else:
                    pipe = singlebandgray(minValue, maxValue)
            elif b == 3:
                pipe = multibandcolor()
            else:
                pipe = singlebandgray(minValue, maxValue)


            maplayer = {

                "minimumScale": 0,
                "maximumScale": 1e+08,
                "type": geomtype,
                "extent": {"xmin": minx, "ymin": miny, "xmax": maxx, "ymax": maxy},
                "id": safename(layername, ' ') + strftime("%Y%m%d%H%M%S", None),
                "datasource": filename,
                "keywordList": {"value": {}},
                "layername": layername,
                "geometry": "raster",
                "srs": {
                    "spatialrefsys": {
                        "authid": "",
                        "description": descr,
                        "ellipsoidacronym": ellps,
                        "geographicflag": (srs.IsGeographic() > 0),
                        "proj4": proj4,
                        "projectionacronym": srs.GetName(),
                        "srid": "",
                        "srsid": ""
                    }
                },
                "customproperties": {
                    "width": n,
                    "height": m,
                    "dtype": datatype,
                    "units": "degrees" if srs.IsGeographic() else "meters",
                    "px": px,
                    "py": py,
                    "bands": b,
                },
                "provider": "gdal",
                "noData": {"noDataList": {
                    "bandNo": 1,
                    "useSrcNoData": 0
                }},
                "map-layer-style-manager": {},
                "pipe": pipe,
                "blendMode": 0
            }
    elif ext in ("shp", "dbf", "sqlite", "dxf"):
        data = ogr.OpenShared(filename)
        if data and data.GetLayer(layerid):
            layer = data.GetLayer(layerid)
            layername = layer.GetName()
            minx, maxx, miny, maxy = layer.GetExtent()
            geomtype = GEOMETRY_TYPE[layer.GetGeomType()]
            nfeatures = layer.GetFeatureCount(True)
            srs = layer.GetSpatialRef()
            if not srs:
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(3857)
            if srs:
                descr = srs.GetAttrValue('projcs')
                proj4 = srs.ExportToProj4() if srs else "init=epsg:3857"
                proj = re.findall(r'\+proj=(\w+\d*)', proj4)
                proj = proj[0] if proj else ""
                ellps = re.findall(r'\+ellps=(\w+\d*)', proj4)
                ellps = ellps[0] if ellps else ""
            extent = (minx, miny, maxx, maxy)
            ##fieldnames
            definition = layer.GetLayerDefn()
            n = definition.GetFieldCount()
            fieldnames = [definition.GetFieldDefn(j).GetName() for j in range(n)]

            aliases, defaults, edittypes = [], [], []
            for j in range(len(fieldnames)):
                fieldname = fieldnames[j]
                aliases.append({"field": fieldname, "index": j, "name": ""})
                defaults.append({"field": fieldname, "expression": ""})
                edittypes.append({"widgetv2type": "TextEdit", "name": fieldname, "widgetv2config": {
                    "IsMultiline": 0, "fieldEditable": 1, "constraint": "", "UseHtml": 0, "labelOnTop": 0,
                    "constraintDescription": "", "notNull": 0
                }})

            maplayer = {
                "simplifyAlgorithm": 0,
                "minScale": 0,
                "maxScale": 1e+08,
                "simplifyDrawingHints": 1,
                "minLabelScale": 0,
                "maxLabelScale": 1e+08,
                "simplifyDrawingTol": 1,
                "readOnly": 0,
                "geometry": geomtype,
                "simplifyMaxScale": 1,
                "type": "vector",
                "hasScaleBasedVisibilityFlag": 0,
                "simplifyLocal": 1,
                "scaleBasedLabelVisibilityFlag": 1,
                "extent": {"xmin": minx, "ymin": miny, "xmax": maxx, "ymax": maxy},
                "id": safename(layername, ' ') + strftime("%Y%m%d%H%M%S", None),  # + "190001010000", #
                "datasource": filename,
                "nfeatures": nfeatures,
                "keywordList": {"value": {}},
                "layername": layername,
                "srs": {
                    "spatialrefsys": {
                        "authid": "",
                        "description": descr,
                        "ellipsoidacronym": ellps,
                        "geographicflag": (srs.IsGeographic() > 0),
                        "proj4": proj4,
                        "projectionacronym": proj,
                        "srid": "",
                        "srsid": ""
                    }
                },
                "provider": {"encoding": "System", "content": "ogr"},
                "map-layer-style-manager": {
                    "current": ""
                },
                "edittypes": {"edittype": edittypes},
                "renderer-v2": options["renderer-v2"] if "renderer-v2" in options else renderer_v2(geomtype , options),
                "labeling": options["labeling"] if "labeling" in options else {},
                "labelsEnabled": 1 if "labeling" in options else 0,
                "customproperties": {},
                "blendMode": 0,
                "featureBlendMode": 0,
                "layerTransparency": 0,
                "displayfield": "VALUE",
                "label": 0,
                "labelattributes": {
                    "label": {"fieldname": "", "text": "Etichetta"},
                    "family": {"fieldname": "", "name": "MS Shell Dlg 2"},
                    "size": {"fieldname": "", "units": "pt", "value": 12},
                    "bold": {"fieldname": "", "on": 0},
                    "italic": {"fieldname": "", "on": 0},
                    "underline": {"fieldname": "", "on": 0},
                    "strikeout": {"fieldname": "", "on": 0},
                    "color": {"fieldname": "", "red": 0, "blue": 0, "green": 0},
                    "x": {"fieldname": ""},
                    "y": {"fieldname": ""},
                    "offset": {"fieldname": "", "x": 0, "y": 0, "units": "pt", "yfieldname": "", "xfieldname": ""},
                    "angle": {"fieldname": "", "value": 0, "auto": 0},
                    "alignment": {"fieldname": "", "value": "center"},
                    "buffercolor": {"fieldname": "", "red": 255, "blue": 255, "green": 255},
                    "buffersize": {"fieldname": "", "units": "pt", "value": 1},
                    "bufferenabled": {"fieldname": "", "on": ""},
                    "multilineenabled": {"fieldname": "", "on": ""},
                    "selectedonly": {"on": ""}
                },
                "aliases": {"alias": aliases},
                "attributetableconfig": {
                    "actionWidgetStyle": "dropDown",
                    "sortExpression": "",
                    "sortOrder": 0,
                    "columns": {}
                },
                "defaults": {"default": defaults}
            }

    return maplayer

def MaplayerResponse(environ, options, start_response):
    """
    MaplayerResponse
    """
    params = Params(environ)
    filename = params.getvalue("filename","no!")
    APPNAME = params.getvalue("__APPNAME__")
    DOCUMENT_ROOT = params.getvalue("DOCUMENT_ROOT")
    DOCUMENT_WWW = params.getvalue("DOCUMENT_WWW")
    PROJECT_DIR = params.getvalue("__PROJECTDIR__")
    WHERE = params.getvalue("WHERE", "")

    if os.path.isfile(filename) and DOCUMENT_ROOT and DOCUMENT_WWW:
        filemap   = forceext(filename, "map")
        options = options if options else {"pipe": "singlebandgray"}
        # maplayer = GDAL_MAPLAYER(filename, options={"pipe": "singlebandgray"})

        # maplayer = GDAL_MAPLAYER(filename, layername,
        #     options={"pipe": "singlebandpseudocolor", "colorRampType": "INTERPOLATED", "classes": __CLASSES__})

        maplayer = GDAL_MAPLAYER(filename, options=options)
        # render filemap
        variables = {
            "os": os,
            "re": re,
            "operator": operator,
            "opensitua_core": pkg,
            "DOCUMENT_ROOT": DOCUMENT_ROOT,
            "DOCUMENT_WWW": DOCUMENT_WWW,
            "PROJECT_DIR": PROJECT_DIR,
            "qgis": {"projectname": APPNAME},
            "maplayers": [maplayer],
            "WHERE": WHERE
        }
        # jinja2 template
        tplmap ="{DOCUMENT_WWW}/lib/template/file.map".format(**variables)
        template(tplmap, filemap, variables)
        # none.html
        filenone = justpath(filemap) + "/none.html"
        if not os.path.isfile(filenone):
            strtofile("""// mapserver template\n{ "x":[x], "y":[y], "value_0": [value_0] }""", filenone)
        return JSONResponse(maplayer, start_response)
    return JSONResponse({"exception":"some params missing"}, start_response)


if __name__ == "__main__":
    # filename = r"D:\Users\vlr20\Projects\BitBucket\OpenGeco\projects\Valerio\Test01\test_geo.tif"
    # filename = r"D:\Users\vlr20\Projects\BitBucket\OpenGeco\projects\Valerio\Test03\611-GB-B-62001-1_A-3_MR-Model-000_1.jpg"
    maplayer = GDAL_MAPLAYER(filename, options={"pipe": "singlebandpseudocolor"})
    print(maplayer)
