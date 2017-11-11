'''
Mostly direct port of awesome article by Joe Schwartz -
http://msdn.microsoft.com/en-us/library/bb259689.aspx
'''
from __future__ import division
import math


class TileUtils(object):
    earth_radius = 6378137
    min_lat = -85.05112878
    max_lat = 85.05112878
    min_lng = -180
    max_lng = 180

    def clipValue(self, value, minValue, maxValue):
        '''
        Makes sure that value is within a specific range.
        If not, then the lower or upper bounds is returned
        '''
        return min(max(value, minValue), maxValue)

    def getMapDimensionsByZoomLevel(self, zoomLevel):
        '''
        Returns the width/height in pixels of the entire map
        based on the zoom level.
        '''
        return 256 << zoomLevel

    def getGroundResolution(self, latitude, level):
        '''
        returns the ground resolution for based on latitude and zoom level.
        '''
        latitude = self.clipValue(latitude, self.min_lat, self.max_lat);
        mapSize = self.getMapDimensionsByZoomLevel(level)
        return math.cos(
            latitude * math.pi / 180) * 2 * math.pi * self.earth_radius / \
               mapSize

    def getMapScale(self, latitude, level, dpi=96):
        '''
        returns the map scale on the dpi of the screen
        '''
        dpm = dpi / 0.0254  # convert to dots per meter
        return self.getGroundResolution(latitude, level) * dpm

    def convertLatLngToPixelXY(self, lat, lng, level):
        '''
        returns the x and y values of the pixel corresponding to a latitude
        and longitude.
        '''
        mapSize = self.getMapDimensionsByZoomLevel(level)

        lat = self.clipValue(lat, self.min_lat, self.max_lat)
        lng = self.clipValue(lng, self.min_lng, self.max_lng)

        x = (lng + 180) / 360
        sinlat = math.sin(lat * math.pi / 180)
        y = 0.5 - math.log((1 + sinlat) / (1 - sinlat)) / (4 * math.pi)

        pixelX = int(self.clipValue(x * mapSize + 0.5, 0, mapSize - 1))
        pixelY = int(self.clipValue(y * mapSize + 0.5, 0, mapSize - 1))
        return (pixelX, pixelY)

    def convertPixelXYToLngLat(self, pixelX, pixelY, level):
        '''
        converts a pixel x, y to a latitude and longitude.
        '''
        mapSize = self.getMapDimensionsByZoomLevel(level)
        x = (self.clipValue(pixelX, 0, mapSize - 1) / mapSize) - 0.5
        y = 0.5 - (self.clipValue(pixelY, 0, mapSize - 1) / mapSize)

        lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
        lng = 360 * x

        return (lng, lat)

    def convertPixelXYToTileXY(self, pixelX, pixelY):
        '''
        Converts pixel XY coordinates into tile XY coordinates of the tile
        containing
        '''
        return (int(pixelX / 256), int(pixelY / 256))

    def convertTileXYToPixelXY(self, tileX, tileY):
        '''
        Converts tile XY coordinates into pixel XY coordinates of the
        upper-left pixel
        '''
        return (tileX * 256, tileY * 256)

    def tileXYZToQuadKey(self, x, y, z):
        '''
        Computes quadKey value based on tile x, y and z values.
        '''
        quadKey = ''
        for i in range(z, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (x & mask) != 0:
                digit += 1
            if (y & mask) != 0:
                digit += 2
            quadKey += str(digit)
        return quadKey

    def quadKeyToTileXYZ(self, quadKey):
        '''
        Computes tile x, y and z values based on quadKey.
        '''
        tileX = 0
        tileY = 0
        tileZ = len(quadKey)

        for i in range(tileZ, 0, -1):
            mask = 1 << (i - 1)
            value = quadKey[tileZ - i]

            if value == '0':
                continue

            elif value == '1':
                tileX |= mask

            elif value == '2':
                tileY |= mask

            elif value == '3':
                tileX |= mask
                tileY |= mask

            else:
                raise Exception('Invalid QuadKey')

        return (tileX, tileY, tileZ)

    def convertLngLatToTileXY(self, lng, lat, level):
        pixelX, pixelY = self.convertLatLngToPixelXY(lat, lng, level)
        return self.convertPixelXYToTileXY(pixelX, pixelY)

    def getTileOrigin(self, tileX, tileY, level):
        '''
        Returns the upper-left hand corner lat/lng for a tile
        '''
        pixelX, pixelY = self.convertTileXYToPixelXY(tileX, tileY)
        lng, lat = self.convertPixelXYToLngLat(pixelX, pixelY, level)
        return (lat, lng)


class TileFinder(object):
    def __init__(self, tileUtils, tileTemplate):
        '''
        Tile template is a template url which use {{x}}, {{y}}, {{z}} which
        will be replaced by
        their respective values.
        '''
        self.tileUtils = tileUtils
        self.tileTemplate = tileTemplate

    def getTileUrlsByLatLngExtent(self, xmin, ymin, xmax, ymax, level):
        '''
        Returns a list of tile urls by extent
        '''
        # Upper-Left Tile
        tileXMin, tileYMin = self.tileUtils.convertLngLatToTileXY(xmin, ymax,
                                                                  level)

        # Lower-Right Tile
        tileXMax, tileYMax = self.tileUtils.convertLngLatToTileXY(xmax, ymin,
                                                                  level)

        tileUrls = []

        for y in range(tileYMax, tileYMin - 1, -1):
            for x in range(tileXMin, tileXMax + 1, 1):
                tileUrls.append(self.createTileUrl(x, y, level))

        return tileUrls

    def createTileUrl(self, x, y, z):
        '''
        returns new tile url based on template
        '''
        return self.tileTemplate.replace('{{x}}', str(x)).replace('{{y}}', str(
            y)).replace('{{z}}', str(z))
