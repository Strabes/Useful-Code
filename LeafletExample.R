# Load the libraries
library(dplyr)
library(tidyr)
library(leaflet)
library(rgdal)
library(colorRamps)
library(geosphere)

# Load County shape file
# (Shape files can be downloaded from the U.S. Census website)
pathToShapeFile = ''

countyShapeFiles <- readOGR(pathToShapeFile)
countyShapeFiles@data <- countyShapeFiles@data %>%
  mutate(FIPS_COUNTY = paste(STATEFP,COUNTYFP,sep=""))

# CA FIPS code:
stateFP = "06"

# Subset shape file down to CA
subsetCountyShapeFiles <- subset(countyShapeFiles,countyShapeFiles$STATEFP %in% stateFP)


# Construct color map for deciles of land area
countyColorFunc <- colorQuantile(palette = c("#00FF00","#718E00","#FF0000"),
                                 domain = subsetCountyShapeFiles$ALAND, n=10)

# Create popup text
county_popup <- paste0("<strong>County: </strong>",
                       subsetCountyShapeFiles$NAME,
                       "<br><strong>Land Area: </strong>",
                       subsetCountyShapeFiles$ALAND)

# Create map
leaflet(subsetCountyShapeFiles) %>%
  # Add polygons
  addPolygons(stroke = TRUE, fillOpacity = 0.7,
              smoothFactor = 0.5, weight = 1, color = "Black",
              fillColor =~ countyColorFunc(subsetCountyShapeFiles$ALAND),
              popup = county_popup) %>%
  # Add background tiles
  addTiles() %>%
  # Add legend
  addLegend(position = "bottomright", pal = countyColorFunc,
            values =~ ALAND, opacity = 0.7, title = "Legend")

