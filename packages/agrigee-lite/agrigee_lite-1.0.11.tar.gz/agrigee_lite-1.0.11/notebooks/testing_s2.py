import ee
import geopandas as gpd
import pandas as pd

import agrigee_lite as agl

ee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com", project="ee-mateuspsilva")

gdf = gpd.read_parquet("data/whole_brazil_sampled.parquet")
gdf = gdf[
    [
        "geometry",
        "plot_id",
        "varda_id",
        "ha",
        "CD_MUN",
        "CD_MICRO",
        "CD_MESO",
        "percentage",
        "year",
        "crop_class",
        "start_date",
        "end_date",
    ]
]

gdf["start_date"] = pd.to_datetime(gdf.year.apply(lambda x: f"{x - 1}-10-01"))
gdf["end_date"] = pd.to_datetime(gdf.year.apply(lambda x: f"{x}-10-01"))

gdf = gdf.sample(25000, random_state=42).reset_index(drop=True)

s2_sat = agl.sat.Sentinel2(use_sr=False)
l7_sat = agl.sat.Landsat7(use_sr=False)
l8_sat = agl.sat.Landsat8(use_sr=False)
l9_sat = agl.sat.Landsat9(use_sr=False)
modis_sat = agl.sat.Modis8Days()
s1_asc_sat = agl.sat.Sentinel1()
s1_desc_sat = agl.sat.Sentinel1(ascending=False)
palsar_sat = agl.sat.PALSAR2ScanSAR()

# s2_sits = agl.get.multiple_sits(gdf, s2_sat)
# l7_sits = agl.get.multiple_sits(gdf, l7_sat)
# l8_sits = agl.get.multiple_sits(gdf, l8_sat)
# l9_sits = agl.get.multiple_sits(gdf, l9_sat)
# modis_sits = agl.get.multiple_sits(gdf, modis_sat)

# s1_asc_sits = agl.get.multiple_sits(gdf, s1_asc_sat)
# s1_desc_sits = agl.get.multiple_sits(gdf, s1_desc_sat)
palsar_sits = agl.get.multiple_sits(gdf, palsar_sat)
