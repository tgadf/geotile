class geotile():    
    class gps():
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude
            
            if latitude < -90.0 or latitude > 90.0:
                raise ValueError("Latitude must be between -90 and 90")
            if longitude < -180.0 or longitude > 180.0:
                raise ValueError("Longitude must be between -180 and 180")
            
        def get(self, trunc=True):
            if trunc is not True:
                return tuple([self.latitude, self.longitude])
            else:
                return tuple([round(self.latitude,6), round(self.longitude,6)])
                
        
    class element():
        
        def __init__(self, row, col, level):
            self.row   = row
            self.col   = col
            self.level = level
            
            MAX_ROW_SIZE = int(536870912)
            MAX_LEVEL_SIZE = int(30)
            MAX_COLUMN_SIZE = int(1073741824)
            
            if level < 0 or level >= MAX_LEVEL_SIZE:
                raise ValueError("Level {0} must be between 0 and {1}".format(level, MAX_LEVEL_SIZE))     
            if row < 0 or row >= MAX_ROW_SIZE:
                raise ValueError("Row {0} must be between 0 and {1}".format(row, MAX_ROW_SIZE))
            if col < 0 or row >= MAX_COLUMN_SIZE:
                raise ValueError("Col {0} must be between 0 and {1}".format(col, MAX_COLUMN_SIZE))       
            
        
        def get(self):
            return [self.row, self.col, self.level]
        
    class rectangle():
        def __init__(self, origin, opposite):
            self.origin   = origin
            self.opposite = opposite

        
    def __init__(self):
        __author__ = 'elinder'


        self.ROW_BIT_COUNT = int(29)
        self.LEVEL_BIT_COUNT = int(5)
        self.PARTITION_ID_BIT_COUNT = int(64)
        self.COLUMN_BIT_COUNT = int(30)

        #LEVEL_BIT_MASK       = 0b 1111100000 0000000000 0000000000 0000000000 0000000000 0000000000 0000
        #COLUMN_BIT_MASK      = 0b 0000011111 1111111111 1111111111 1111111111 1111111111 1111111111 1111
        #ROW_BIT_MASK         = 0b 1111111111 1111111111 1111111111 1111000000 0000000000 0000000000 0000

        #LEVEL_BIT_MASK       = 0b1111100000000000000000000000000000000000000000000000000000000000
        self.LEVEL_BIT_MASK = 17870283321406128128
        #COLUMN_BIT_MASK      = 0b0000000000000000000000000000000000111111111111111111111111111111
        self.COLUMN_BIT_MASK = 1073741823
        #ROW_BIT_MASK         = 0b0000011111111111111111111111111111000000000000000000000000000000
        self.ROW_BIT_MASK = 576460751229681664


        self.DISTANCE_BETWEEN_PARTITIONS = 1.0E-13        

        self.direction = {
            'north': 0,
            'northeast': 1,
            'east': 2,
            'southeast': 3,
            'south': 4,
            'southwest': 5,
            'west': 6,
            'northwest': 7
        }

        
        
        

    def getPartitionRectangle(self, partitionID, debug=False):
        if debug:
            print("Computing Partition Rectangle for ID: {0}".foramt(partitionID))
            
        originTile = self.decodeToTile(partitionID, debug)
        originGPS  = self.decodeFromTile(originTile)
        cornerTile = self.element(originTile.row+1, originTile.col+1, originTile.level)
        cornerGPS  = self.decodeFromTile(cornerTile)

        cornerLat  = cornerGPS.latitude
        cornerLng  = cornerGPS.longitude
    
        ## This seems like a floating point offset of some kind...
        oppositeLat = cornerLat # - self.DISTANCE_BETWEEN_PARTITIONS
        oppositeLng = cornerLng # - self.DISTANCE_BETWEEN_PARTITIONS
        oppositeGPS = self.gps(latitude=oppositeLat, longitude=oppositeLng)
        
        rect = self.rectangle(origin=originGPS, opposite=oppositeGPS)
        return rect
    
    
    def getCornersFromBBox(self, partitionID, debug=False):
        originTile = self.decodeToTile(partitionID, debug)
        nwTile = self.element(originTile.row + 1, originTile.col, originTile.level)
        neTile = self.element(originTile.row + 1, originTile.col + 1, originTile.level)
        seTile = self.element(originTile.row, originTile.col + 1, originTile.level)
        swTile = originTile
        box = {'nw': self.decodeFromTile(nwTile).get(), 'ne': self.decodeFromTile(neTile).get(),
               'sw': self.decodeFromTile(swTile).get(), 'se': self.decodeFromTile(seTile).get()}
        return box
        
        
    def getBBox(self, partitionID, returnPoints=False, returnCorners=False, debug=False):
        if debug:
            print("Getting Bounding Box for ID {0}".format(partitionID))
        
        if returnPoints is True or returnCorners is True:
            corners = self.getCornersFromBBox(partitionID)
            if returnPoints is True:
                points = [corners['sw'], corners['nw'], corners['ne'], corners['se'], corners['sw']]
                return points
            else:
                return corners
        else:
            rect = self.getPartitionRectangle(partitionID, debug)
            extremes = [rect.origin.get(), rect.opposite.get()]
            return extremes
            
        
        
    def switchOnDirections(self, orientation, step, tile, debug=False):
        row   = tile.row
        col   = tile.col
        level = tile.level
        
        newVal  = {'north': [row + step, col],
                   'northeast': [row + step, col - step],
                   'east': [row, col + step],
                   'southeast': [row - step, col - step],
                   'south': [row - step, col],
                   'southwest': [row - step, col + step],
                   'west': [row, col - step],
                   'northwest': [row + step, col + step]}.get(orientation)
        
        if newVal is None:
            raise ValueError("Could not get new row/col with moving {0}".format(orientation))
        
        
        if debug:
            print("Started at {0} and Moved to {1} with Orientation/Step {2}/{3}".format(currVal, newVal, orientation, step))
            
            
        ## Create new tile with new row,col, and old level
        newtile = self.element(newVal[0], newVal[1], level)
            
        return newtile

        

    def navigate(self, partitionId, orientation, step, debug=False):
        if orientation not in self.direction.keys():
            print("Orientation {0} is not in list of keys: {1}".format(orientation, self.direction.keys()))
            
        if debug:
            print("Navigating {0} From ID {1} With Step {2}".format(orientation, partitionId, step))
            
        tile    = self.decodeToTile(partitionId)
        newtile = self.switchOnDirections(orientation, step, tile)
        row     = newtile.row
        col     = newtile.col
        level   = newtile.level

        #Columns wrap - the safeguard below should never be called
        mxCol = self.maxColumn(level)
        if col>mxCol:
            col = col - mxCol
        elif col < 0:
            col = mxCol + col

        vr = self.isValidRow(row, level)
        if not vr:
            mxRow = self.maxRow(level)
            raise Exception("Encountered a row ID of "+str(row)+" while rows are expected to be in the range of 0 to "+str(mxRow-1)+" at level "+str(level))

        
        #columns wrap.  This is a safeguard that was left in. This should never happen.
        vc = self.isValidColumn(col, level)
        if not vc:
            raise Exception("Encountered a row ID of "+str(row)+" while rows are expected to be in the range of 0 to "+str(mxCol-1)+" at level "+str(level))

        newID = self.encodeFromTile(newtile)
        
        if debug:
            print("Moved From {0} to {1}".format(partitionId, newID))

        return newID



    def getRowFromPartition(self, partitionID):
        row    = (partitionID & self.ROW_BIT_MASK) >> self.COLUMN_BIT_COUNT
        return row


    def getColFromPartition(self, partitionID):
        column = (partitionID & self.COLUMN_BIT_MASK)
        return column
    

    def getLevelFromPartition(self, partitionID):
        level  = (partitionID & self.LEVEL_BIT_MASK) >> 64 - self.LEVEL_BIT_COUNT
        return level
    
    
    
    def decodeToTile(self, partitionID, debug=False):
        row    = self.getRowFromPartition(partitionID)
        column = self.getColFromPartition(partitionID)
        level  = self.getLevelFromPartition(partitionID)
        tile   = self.element(row, column, level)        
        return tile
    
    def decodeFromID(self, partitionID, debug=False):
        return decode(partitionID, debug)

    def decode(self, partitionID, debug=False):
        if debug:
            print("Decoding {0}".format(partitionID))

        bbox = self.getBBox(partitionID)
        lat  = sum(x[0] for x in bbox)/2.0
        lng  = sum(x[1] for x in bbox)/2.0
        pos  = self.gps(latitude=lat, longitude=lng)
        ret  = pos.get()
        return ret
    
        
    def decodeFromTile(self, tile, debug=False):
        if debug:
            print("  Row: {0}, Column: {1}, Level: {2}".format(tile.row, tile.column, tile.level))

            
        ## Compute EdgeSize from Level
        edgeSize = self.getEdgeSize(tile.level)
        
        ## Compute Latitude and Subtract Offset
        latitude = (tile.row * edgeSize) - 90.0
        
        ## Compute Latitude and Subtract Offset
        longitude = (tile.col * edgeSize) - 180.0
        
        ## Return tuple of coordinates
        pos = self.gps(latitude, longitude)

        return pos
        


    def maxRow(self, level):
        mxrow = pow(2.0,level)
        return mxrow

    def maxColumn(self, level):
        mxcol = pow(2.0, (level+1))
        return mxcol

    def isValidRow(self, row, level):
        mxrow = self.maxRow(level)
        if row < 0 or row >= mxrow:
            return False
        return True

    def isValidColumn(self, col, level):
        mxcol = self.maxColumn(level)
        if col<0 or col>=mxcol:
            return False
        return True

    
    def getEdgeSize(self, level, debug=False):
        if level is None:
            raise ValueError("Must set level first")
            
        if not isinstance(level, int):
            raise ValueError("Level must be an integer not a {0}".format(type(level)))
            
        rowCount = float(pow(2,level))
        edgesize = 180.0/rowCount
        
        if debug:
            print("EdgeSize/Level = {0} / {1}".format(edgesize, level))
            
        return edgesize
            

    def encodeFromTile(self, tile, debug=False):
        if not isinstance(tile, self.element):
            raise ValueError("Can only encode an element object!")
        row   = tile.row
        col   = tile.col
        level = tile.level
        
        if debug:
            print("Encoding with Level {0}, Row {1}, and Col {2}".format(level, row, col))
            
        partitionId = 0
        partitionId = partitionId | (int(level) << (self.PARTITION_ID_BIT_COUNT - self.LEVEL_BIT_COUNT))
        partitionId = partitionId | (int(row) << (self.PARTITION_ID_BIT_COUNT - (self.LEVEL_BIT_COUNT + self.ROW_BIT_COUNT)))
        partitionId = partitionId | (int(col) << (self.PARTITION_ID_BIT_COUNT - (self.LEVEL_BIT_COUNT + self.ROW_BIT_COUNT + self.COLUMN_BIT_COUNT)))
        return partitionId            

    
    def encode(self, latitude, longitude, level, debug=False):
        
        edgeSize = self.getEdgeSize(level)
        if debug:
            print("Level:   {0}".format(level))
            print("Edge:    {0}".format(edgeSize))
            print("Lat/Lng: {0}".format([latitude, longitude]))
            
        if edgeSize is None:
            col = 0

        ## Set latitude between [0,180]
        ## Set longitude between [0,360]
        wgsLat = float(latitude) + 90.0
        if wgsLat < 0.0 or wgsLat > 180.0:
            raise ValueError("Latitude {0} is not valid".format(latitude))
        wgsLng = float(longitude) + 180.0
        if wgsLng < 0.0 or wgsLng > 360.0:
            raise ValueError("Longitude {0} is not valid".format(longitude))
        row = wgsLat/edgeSize

        if debug:
            print("Row: {0}".format(row))
        #exception: north pole belongs to the row below it since there is not row beyond that.
        if wgsLat >= 180.0:
                row = row - 1

        #2. determine the column:
        col = wgsLng/edgeSize
        if debug:
            print("Col: {0}".format(col))
            
        if not self.isValidRow(row, level):
            raise ValueError("Row {0} produced by level {1} is not valid".format(level))
        if not self.isValidColumn(col, level):
            raise ValueError("Column {0} produced by level {1} is not valid".format(level))

        tile = self.element(row, col, level)
        partitionID = self.encodeFromTile(tile)
        if debug:
            print("Parition ID: {0}".format(partitionID))
            
        return partitionID
