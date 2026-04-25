from pathlib import Path
from typing import Optional, Tuple

import geopandas as gpd
import pandas as pd
import pypsa
import yaml


def read_params(params_file: str = "../params.yaml") -> dict:
    """Load YAML parameters used by notebooks."""
    with open(params_file, "r") as configfile:
        return yaml.safe_load(configfile)


def load_regions(
    params: dict,
    prefix: str = "",
    name: str = "",
    region_tag: Optional[str] = None,
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load onshore/offshore region files from resources folder."""
    base_dir = Path(params["rootpath"]) / "resources"
    if prefix:
        base_dir = base_dir / prefix
    if name:
        base_dir = base_dir / name

    if region_tag:
        file_regions_onshore = f"regions_onshore_{region_tag}.geojson"
        file_regions_offshore = f"regions_offshore_{region_tag}.geojson"
    else:
        file_regions_onshore = "regions_onshore.geojson"
        file_regions_offshore = "regions_offshore.geojson"

    gdf_regions_onshore = gpd.read_file(base_dir / file_regions_onshore)
    gdf_regions_offshore = gpd.read_file(base_dir / file_regions_offshore)

    return gdf_regions_onshore, gdf_regions_offshore


def load_nuts(
    params: dict,
    spatial_domain: str = "ES",
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load NUTS2 and NUTS3 geometries with the same filters used in notebooks."""
    path_nuts = (
        Path(params["rootpath"])
        / "data"
        / "eu_nuts2021"
        / "archive"
        / "2021-01-01"
        / "ref-nuts-2021-01m.geojson"
    )

    where_r = "NUTS_ID NOT LIKE 'ES63%' AND NUTS_ID NOT LIKE 'ES64%' AND NUTS_ID NOT LIKE 'ES70%'"
    where_es = "CNTR_CODE = 'ES'" if spatial_domain == "ES" else ""
    where_common = " AND ".join(filter(None, [where_r, where_es]))

    file_nuts2 = "NUTS_RG_01M_2021_4326_LEVL_2.geojson"
    file_nuts3 = "NUTS_RG_01M_2021_4326_LEVL_3.geojson"

    gdf_nuts2 = gpd.read_file(path_nuts / file_nuts2, where=f"LEVL_CODE = 2 AND {where_common}")
    gdf_nuts3 = gpd.read_file(path_nuts / file_nuts3, where=f"LEVL_CODE = 3 AND {where_common}")

    return gdf_nuts2, gdf_nuts3


def load_network(
    params: dict,
    filename: str,
    prefix: str = "",
    name: str = "",
    location: str = "resources",
) -> pypsa.Network:
    """Load a PyPSA network from resources/results/<prefix>/<name>/networks."""
    base_dir = Path(params["rootpath"]) / location
    if prefix:
        base_dir = base_dir / prefix
    if name:
        base_dir = base_dir / name

    network_path = base_dir / "networks" / filename
    return pypsa.Network(network_path)


def load_file_csv(
    params: dict,
    filename: str,
    prefix: str = "",
    name: str = "",
    location: str = "resources",
    folder: str = "",
    **read_csv_kwargs,
) -> pd.DataFrame:
    """Load a CSV file from <location>/<prefix>/<name>/<folder>/<filename>."""
    base_dir = Path(params["rootpath"]) / location
    if prefix:
        base_dir = base_dir / prefix
    if name:
        base_dir = base_dir / name
    if folder:
        base_dir = base_dir / folder

    csv_path = base_dir / filename
    return pd.read_csv(csv_path, **read_csv_kwargs)
