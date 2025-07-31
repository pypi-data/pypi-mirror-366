from pygeoboundaries_geolab import get_gdf
import geopandas as gpd

# TODO: check if commit is out of date (https://api.github.com/repos/wmgeolab/geoBoundaries/commits/main) and if so, regenerate gdf

gdf = get_gdf('ALL', ['UNSDG-subregion', 'worldBankIncomeGroup', 'maxAreaSqKM'])
gdf = gdf.drop(columns=['shapeISO', 'shapeID', 'shapeGroup', 'shapeType'])
gdf = gpd.GeoDataFrame(gdf, geometry=gdf['geometry'])
gdf = gdf.set_geometry('geometry').set_crs(4326)
gdf.to_csv('src/safe_earth/data/strata/gdf_territory_region_income.csv', index=False)
gdf.to_file('src/safe_earth/data/strata/territory_region_income.geojson', driver='GeoJSON') # TODO: users don't need this to be done
