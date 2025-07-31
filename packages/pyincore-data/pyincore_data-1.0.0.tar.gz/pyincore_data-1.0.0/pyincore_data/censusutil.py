# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import requests
import os
import pandas as pd
import geopandas as gpd
import urllib.request
import shutil
import time
from pyincore import Dataset
from zipfile import ZipFile

from pyincore_data.censusviz import CensusViz
from pyincore_data.utils.datautil import DataUtil
from pyincore_data import globals as pyincore_globals

logger = pyincore_globals.LOGGER


class CensusUtil:
    """Utility methods for Census data and API"""

    @staticmethod
    def get_census_data(
        state: str = None,
        county: str = None,
        year: str = None,
        data_source: str = None,
        columns: str = None,
        geo_type: str = None,
        data_name: str = None,
    ):
        """Create json and pandas DataFrame for census api request result.

        Args:
            state (str): A string of state FIPS with comma separated format. e.g, '41, 42' or '*'
            county (str): A string of county FIPS with comma separated format. e.g, '017,029,045,091,101' or '*'
            year (str): Census Year.
            data_source (str): Census dataset name. Can be found from https://api.census.gov/data.html
            columns (str): Column names for request data with comma separated format.
                e.g, 'GEO_ID,NAME,P005001,P005003,P005004,P005010'
            geo_type (str): Name of geo area. e.g, 'tract:*' or 'block%20group:*'
            data_name (str): Optional for getting different dataset. e.g, 'component'

        Returns:
            dict, obj, obj: A json list, a dataframe for census api result,
                and pyincore dataset

        """
        # create census api data url
        data_url = CensusUtil.generate_census_api_url(
            state, county, year, data_source, columns, geo_type, data_name
        )

        api_json, api_df = CensusUtil.request_census_api(data_url)

        # convert df to dataset
        timestr = time.strftime("%Y%m%d-%H%M%S")
        csv_name = "api_" + str(timestr) + ".csv"
        print("csv saved as " + csv_name)
        api_df.to_csv(csv_name)
        out_dataset = Dataset.from_file(csv_name, data_type="ergo:censusdata")
        out_dataset.format = "table"
        out_dataset.metadata["format"] = "table"

        return api_json, api_df, out_dataset

    @staticmethod
    def generate_census_api_url(
        state: str = None,
        county: str = None,
        year: str = None,
        data_source: str = None,
        columns: str = None,
        geo_type: str = None,
        data_name: str = None,
    ):
        """Create url string to access census data api.

        Args:
            state (str): A string of state FIPS with comma separated format. e.g, '41, 42' or '*'
            county (str): A string of county FIPS with comma separated format. e.g, '017,029,045,091,101' or '*'
            year (str): Census Year.
            data_source (str): Census dataset name. Can be found from https://api.census.gov/data.html
            columns (str): Column names for request data with comma separated format.
                e.g, 'GEO_ID,NAME,P005001,P005003,P005004,P005010'
            geo_type (str): Name of geo area. e.g, 'tract:*' or 'block%20group:*'
            data_name (str): Optional for getting different dataset. e.g, 'component'

        Returns:
            string: A string for representing census api url

        """
        # check if the state is not none
        if state is None:
            error_msg = "State value must be provided."
            logger.error(error_msg)
            raise Exception(error_msg)

        if geo_type is not None:
            if county is None:
                error_msg = (
                    "State and county value must be provided when geo_type is provided."
                )
                logger.error(error_msg)
                raise Exception(error_msg)

        # Set up url for Census API
        base_url = f"https://api.census.gov/data/{year}/{data_source}"
        if data_name is not None:
            base_url = f"https://api.census.gov/data/{year}/{data_source}/{data_name}"

        data_url = f"{base_url}?get={columns}"
        if county is None:  # only state is provided. There shouldn't be any geo_type
            data_url = f"{data_url}&for=state:{state}"
        else:  # county has been provided and there could be geo_type or not
            if geo_type is None:
                data_url = f"{data_url}&in=state:{state}&for=county:{county}"
            else:
                data_url = (
                    f"{data_url}&for={geo_type}&in=state:{state}&in=county:{county}"
                )

        return data_url

    @staticmethod
    def request_census_api(data_url):
        """Request census data to api and gets the output data

        Args:
            data_url (str): url for obtaining the data from census api
        Returns:
            dict, object: A json list and a dataframe for census api result

        """
        # Obtain Census API JSON Data
        request_json = requests.get(data_url)

        if request_json.status_code != 200:
            error_msg = "Failed to download the data from Census API. Please check your parameters."
            # logger.error(error_msg)
            raise Exception(error_msg)

        # Convert the requested json into pandas dataframe

        api_json = request_json.json()
        api_df = pd.DataFrame(columns=api_json[0], data=api_json[1:])

        return api_json, api_df

    @staticmethod
    def get_fips_by_state_county(state: str, county: str, year: str = 2010):
        """Get FIPS code by using state and county name.

        Args:
            state (str): State name. e.g, 'illinois'
            county (str): County name. e.g, 'champaign'

        Returns:
            str: A string of FIPS code

        """
        api_url = f"https://api.census.gov/data/{year}/dec/sf1?get=NAME&for=county:*"
        out_fips = None
        api_json = requests.get(api_url)
        query_value = county + " County, " + state
        if api_json.status_code != 200:
            error_msg = "Failed to download the data from Census API. Please look up Google for getting the FIPS code."
            raise Exception(error_msg)

        # content_json = api_json.json()
        df = pd.DataFrame(columns=api_json.json()[0], data=api_json.json()[1:])
        selected_row = df.loc[df["NAME"].str.lower() == query_value.lower()]
        if selected_row.size > 0:
            out_fips = selected_row.iloc[0]["state"] + selected_row.iloc[0]["county"]
        else:
            error_msg = "There is no FIPS code for given state and county combination."
            logger.error(error_msg)
            raise Exception(error_msg)

        return out_fips

    @staticmethod
    def get_fips_by_state(state: str, year: str = 2010):
        """Create Geopandas DataFrame for population dislocation analysis from census dataset.

        Args:
            state (str): State name. e.g, 'illinois'

        Returns:
            obj: A json list of county FIPS code in the given state

        """
        api_url = f"https://api.census.gov/data/{year}/dec/sf1?get=NAME&for=county:*"
        api_json = requests.get(api_url)
        if api_json.status_code != 200:
            error_msg = "Failed to download the data from Census API."
            logger.error(error_msg)
            raise Exception(error_msg)

        # content_json = api_json.json()
        out_fips = api_json.json()

        return out_fips

    @staticmethod
    def get_blockgroupdata_for_dislocation(
        state_counties: list,
        vintage: str = "2010",
        dataset_name: str = "dec/sf1",
        out_csv: bool = False,
        out_shapefile: bool = False,
        out_geopackage: bool = False,
        out_html: bool = False,
        geo_name: str = "geo_name",
        program_name: str = "program_name",
    ):
        """Create Geopandas DataFrame for population dislocation analysis from census dataset.

        Args:
            state_counties (list): A List of concatenated State and County FIPS Codes.
                see full list https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697
            vintage (str): Census Year.
            dataset_name (str): Census dataset name.
            out_csv (bool): Save output dataframe as csv.
            out_shapefile (bool): Save processed census geodataframe as shapefile.
            out_geopackage (bool): Save processed census geodataframe as geopackage
            out_html (bool): Save processed folium map to html.
            geo_name (str): Name of geo area - used for naming output files.
            program_name (str): Name of directory used to save output files.

        Returns:
            obj, dict, obj: A dataframe for dislocation analysis,
            a dictionary containing geodataframe and folium map, and
            a dataset object created by downloaded geo data

        """
        # Variable parameters
        get_vars = "GEO_ID,NAME,P005001,P005003,P005004,P005010"
        # List variables to convert from dtype object to integer
        int_vars = ["P005001", "P005003", "P005004", "P005010"]
        # GEO_ID  = Geographic ID
        # NAME    = Geographic Area Name
        # P005001 = Total
        # P005003 = Total!!Not Hispanic or Latino!!White alone
        # P005004 = Total!!Not Hispanic or Latino!!Black or African American alone
        # P005010 = Total!!Hispanic or Latino

        # Make directory to save output
        if not os.path.exists(program_name):
            os.mkdir(program_name)

        # Make a directory to save downloaded shapefiles - folder will be made then deleted
        shapefile_dir = "shapefiletemp"
        if not os.path.exists(shapefile_dir):
            os.mkdir(shapefile_dir)

        # loop through counties
        appended_countydata = []  # start an empty container for the county data
        for state_county in state_counties:
            # deconcatenate state and county values
            state = state_county[0:2]
            county = state_county[2:5]
            logger.debug("State:  " + state)
            logger.debug("County: " + county)

            # Set up hyperlink for Census API
            api_hyperlink = CensusUtil.generate_census_api_url(
                state, county, vintage, dataset_name, get_vars, "block%20group"
            )

            logger.info("Census API data from: " + api_hyperlink)

            # Obtain Census API JSON Data
            apijson, apidf = CensusUtil.request_census_api(api_hyperlink)
            print(apidf.size)
            # Append county data makes it possible to have multiple counties
            appended_countydata.append(apidf)

        # Create dataframe from appended county data
        cen_blockgroup = pd.concat(appended_countydata, ignore_index=True)

        # Add variable named "Survey" that identifies Census survey program and survey year
        cen_blockgroup["Survey"] = vintage + " " + dataset_name

        # Set block group FIPS code by concatenating state, county, tract and block group fips
        cen_blockgroup["bgid"] = (
            cen_blockgroup["state"]
            + cen_blockgroup["county"]
            + cen_blockgroup["tract"]
            + cen_blockgroup["block group"]
        )

        # To avoid problems with how the block group id is read saving it
        # as a string will reduce possibility for future errors
        cen_blockgroup["bgidstr"] = cen_blockgroup["bgid"].apply(
            lambda x: "BG" + str(x).zfill(12)
        )

        # Convert variables from dtype object to integer
        for var in int_vars:
            cen_blockgroup[var] = cen_blockgroup[var].astype(int)
            print(var + " converted from object to integer")

        # Generate new variables
        cen_blockgroup["pwhitebg"] = (
            cen_blockgroup["P005003"] / cen_blockgroup["P005001"] * 100
        )
        cen_blockgroup["pblackbg"] = (
            cen_blockgroup["P005004"] / cen_blockgroup["P005001"] * 100
        )
        cen_blockgroup["phispbg"] = (
            cen_blockgroup["P005010"] / cen_blockgroup["P005001"] * 100
        )

        appended_countyshp = CensusUtil.download_couty_shapefile(
            state_counties, shapefile_dir
        )

        # Create dataframe from appended county data
        shp_blockgroup = pd.concat(appended_countyshp)

        # Clean Data - Merge Census demographic data to the appended shapefiles
        cen_shp_blockgroup_merged = pd.merge(
            shp_blockgroup,
            cen_blockgroup,
            left_on="GEOID10",
            right_on="bgid",
            how="left",
        )

        # Set paramaters for file save
        save_columns = [
            "bgid",
            "bgidstr",
            "Survey",
            "pblackbg",
            "phispbg",
        ]  # set column names to save

        # ### Explore Data - Map merged block group shapefile and Census data

        bgmap = CensusViz.create_dislocation_ipyleaflet_map_from_gpd(
            cen_shp_blockgroup_merged
        )

        savefile = program_name + "_" + geo_name  # set file name

        if out_html:
            folium_map = CensusViz.create_dislocation_folium_map_from_gpd(
                cen_shp_blockgroup_merged
            )
            CensusViz.save_dislocation_map_to_html(
                folium_map["map"], program_name, savefile
            )

        if out_csv:
            DataUtil.convert_dislocation_pd_to_csv(
                cen_blockgroup, save_columns, program_name, savefile
            )

        if out_shapefile:
            DataUtil.convert_dislocation_gpd_to_shapefile(
                cen_shp_blockgroup_merged, program_name, savefile
            )

        if out_geopackage:
            DataUtil.convert_dislocation_gpd_to_geopackage(
                cen_shp_blockgroup_merged, program_name, savefile
            )

        if not out_shapefile:
            DataUtil.convert_dislocation_gpd_to_shapefile(
                cen_shp_blockgroup_merged, program_name, savefile
            )

        # convert df to dataset
        out_dataset = Dataset.from_file(
            program_name + "/" + savefile + ".shp", data_type="ergo:censusdata"
        )
        out_dataset.format = "shapefile"
        out_dataset.metadata["format"] = "shapefile"

        # clean up shapefile temp directory
        # Try to remove tree; if failed show an error using try...except on screen
        try:
            shutil.rmtree(shapefile_dir)
            if (
                not out_shapefile
                and not out_csv
                and not out_html
                and not out_geopackage
            ):
                shutil.rmtree(program_name)
        except OSError:
            error_msg = (
                "Error: Failed to remove either "
                + shapefile_dir
                + " or "
                + program_name
                + " directory"
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        return cen_blockgroup[save_columns], bgmap, out_dataset

    @staticmethod
    def demographic_factors(state_code, county_code, year, geo_type="tract:*"):
        """Create Geopandas DataFrame for population demographics for a particular county from census dataset.

        Args:
            state_code (int): state FIPS code.
            county_code (int): county FIPS code.
            year (str): Census Year.
            geo_type (str): Name of geo area. e.g, 'tract:*' or 'block%20group:*'

        Returns:
            obj: A dataframe  of population demographics for a particular county

        """

        df_1 = CensusUtil.get_census_data(
            state=state_code,
            county=county_code,
            year=year,
            data_source="acs/acs5",
            columns="GEO_ID,B03002_001E,B03002_003E",
            geo_type=geo_type,
        )[1]
        df_1["factor_white_nonHispanic"] = (
            df_1[["B03002_001E", "B03002_003E"]]
            .astype(int)
            .apply(lambda row: row["B03002_003E"] / row["B03002_001E"], axis=1)
        )

        df_2 = CensusUtil.get_census_data(
            state=state_code,
            county=county_code,
            year=year,
            data_source="acs/acs5",
            columns="B25003_001E,B25003_002E",
            geo_type=geo_type,
        )[1]
        df_2["factor_owner_occupied"] = df_2.astype(int).apply(
            lambda row: row["B25003_002E"] / row["B25003_001E"], axis=1
        )

        df_3 = CensusUtil.get_census_data(
            state=state_code,
            county=county_code,
            year=year,
            data_source="acs/acs5",
            columns="B17021_001E,B17021_002E",
            geo_type=geo_type,
        )[1]
        df_3["factor_earning_higher_than_national_poverty_rate"] = df_3.astype(
            int
        ).apply(lambda row: 1 - row["B17021_002E"] / row["B17021_001E"], axis=1)

        df_4 = CensusUtil.get_census_data(
            state=state_code,
            county=county_code,
            year=year,
            data_source="acs/acs5",
            columns="B15003_001E,B15003_017E,B15003_018E,B15003_019E,B15003_020E,"
            "B15003_021E,B15003_022E,B15003_023E,B15003_024E,B15003_025E",
            geo_type=geo_type,
        )[1]
        df_4["factor_over_25_with_high_school_diploma_or_higher"] = df_4.astype(
            int
        ).apply(
            lambda row: (
                row["B15003_017E"]
                + row["B15003_018E"]
                + row["B15003_019E"]
                + row["B15003_020E"]
                + row["B15003_021E"]
                + row["B15003_022E"]
                + row["B15003_023E"]
                + row["B15003_024E"]
                + row["B15003_025E"]
            )
            / row["B15003_001E"],
            axis=1,
        )

        if geo_type == "tract:*":
            df_5 = CensusUtil.get_census_data(
                state=state_code,
                county=county_code,
                year=year,
                data_source="acs/acs5",
                columns="B18101_001E,B18101_011E,B18101_014E,B18101_030E,B18101_033E",
                geo_type=geo_type,
            )[1]
            df_5["factor_without_disability_age_18_to_65"] = df_5.astype(int).apply(
                lambda row: (
                    row["B18101_011E"]
                    + row["B18101_014E"]
                    + row["B18101_030E"]
                    + row["B18101_033E"]
                )
                / row["B18101_001E"],
                axis=1,
            )

        elif geo_type == "block%20group:*":
            df_5 = CensusUtil.get_census_data(
                state=state_code,
                county=county_code,
                year=year,
                data_source="acs/acs5",
                columns="B01003_001E,C21007_006E,C21007_009E,C21007_013E,C21007_016E",
                geo_type=geo_type,
            )[1]

            df_5["factor_without_disability_age_18_to_65"] = df_5.astype(int).apply(
                lambda row: (
                    row["C21007_006E"]
                    + row["C21007_006E"]
                    + row["C21007_009E"]
                    + row["C21007_013E"]
                )
                / row["C21007_016E"],
                axis=1,
            )

        df_t = pd.concat(
            [
                df_1[["GEO_ID", "factor_white_nonHispanic"]],
                df_2["factor_owner_occupied"],
                df_3["factor_earning_higher_than_national_poverty_rate"],
                df_4["factor_over_25_with_high_school_diploma_or_higher"],
                df_5["factor_without_disability_age_18_to_65"],
            ],
            axis=1,
            join="inner",
        )

        # extract FIPS from geo id
        df_t["FIPS"] = df_t.apply(lambda row: row["GEO_ID"].split("US")[1], axis=1)

        return df_t

    @staticmethod
    def national_ave_values(year, data_source="acs/acs5"):
        """Create Geopandas DataFrame for national population demographics from census dataset.

        Args:
            year (str): Census Year.
            data_source (str): Census dataset name. Can be found from https://api.census.gov/data.html

        Returns:
            list: A list of dictionaries denoting population demographics for the nation

        """

        nav1 = CensusUtil.get_census_data(
            state="*",
            county=None,
            year=year,
            data_source=data_source,
            columns="B03002_001E,B03002_003E",
            geo_type=None,
        )[1]
        nav1 = nav1.astype(int)
        nav1_avg = {
            "feature": "NAV-1: White, nonHispanic",
            "average": nav1["B03002_003E"].sum() / nav1["B03002_001E"].sum(),
        }

        nav2 = CensusUtil.get_census_data(
            state="*",
            county=None,
            year=year,
            data_source=data_source,
            columns="B25003_001E,B25003_002E",
            geo_type=None,
        )[1]
        nav2 = nav2.astype(int)
        nav2_avg = {
            "feature": "NAV-2: Home Owners",
            "average": nav2["B25003_002E"].sum() / nav2["B25003_001E"].sum(),
        }

        nav3 = CensusUtil.get_census_data(
            state="*",
            county=None,
            year=year,
            data_source=data_source,
            columns="B17021_001E,B17021_002E",
            geo_type=None,
        )[1]
        nav3 = nav3.astype(int)
        nav3_avg = {
            "feature": "NAV-3: earning higher than national poverty rate",
            "average": 1 - nav3["B17021_002E"].sum() / nav3["B17021_001E"].sum(),
        }

        nav4 = CensusUtil.get_census_data(
            state="*",
            county=None,
            year=year,
            data_source="acs/acs5",
            columns="B15003_001E,B15003_017E,B15003_018E,B15003_019E,B15003_020E,"
            "B15003_021E,B15003_022E,B15003_023E,B15003_024E,B15003_025E",
            geo_type=None,
        )[1]
        nav4 = nav4.astype(int)
        nav4["temp"] = nav4.apply(
            lambda row: row["B15003_017E"]
            + row["B15003_018E"]
            + row["B15003_019E"]
            + row["B15003_020E"]
            + row["B15003_021E"]
            + row["B15003_022E"]
            + row["B15003_023E"]
            + row["B15003_024E"]
            + row["B15003_025E"],
            axis=1,
        )
        nav4_avg = {
            "feature": "NAV-4: over 25 with high school diploma or higher",
            "average": nav4["temp"].sum() / nav4["B15003_001E"].sum(),
        }

        nav5 = CensusUtil.get_census_data(
            state="*",
            county=None,
            year=year,
            data_source=data_source,
            columns="B18101_001E,B18101_011E,B18101_014E,B18101_030E,B18101_033E",
            geo_type=None,
        )[1]
        nav5 = nav5.astype(int)
        nav5["temp"] = nav5.apply(
            lambda row: row["B18101_011E"]
            + row["B18101_014E"]
            + row["B18101_030E"]
            + row["B18101_033E"],
            axis=1,
        )
        nav5_avg = {
            "feature": "NAV-5: without disability age 18 to 65",
            "average": nav5["temp"].sum() / nav5["B18101_001E"].sum(),
        }

        navs = [nav1_avg, nav2_avg, nav3_avg, nav4_avg, nav5_avg]

        return navs

    @staticmethod
    def download_couty_shapefile(state_county_list, download_dir):
        """Download and extract shapefiles for selected counties.

        Args:
            state_county_list (list): A list of concatenated State and County FIPS Codes.
                see full list https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697
            download_dir (str): Directory to save downloaded shapefiles.

        Returns:
            list: A list of GeoPandas GeoDataFrames containing block groups for all of the selected counties.

        """
        # ### Obtain Data - Download and extract shapefiles
        # The Block Group IDs in the Census data are associated with the Block Group boundaries that can be mapped.
        # To map this data, we need the shapefile information for the block groups in the select counties.
        #
        # These files can be found online at:
        # https://www2.census.gov/geo/tiger/TIGER2010/BG/2010/

        # ### Download and extract shapefiles
        # Block group shapefiles are downloaded for each of the selected counties from
        # the Census TIGER/Line Shapefiles at https://www2.census.gov/geo/tiger.
        # Each counties file is downloaded as a zipfile and the contents are extracted.
        # The shapefiles are reprojected to EPSG 4326 and appended as a single shapefile
        # (as a GeoPandas GeoDataFrame) containing block groups for all the selected counties.
        #
        # *EPSG: 4326 uses a coordinate system (Lat, Lon)
        # This coordinate system is required for mapping with folium.

        appended_countyshp = []  # start an empty container for the county shapefiles

        # loop through counties
        for state_county in state_county_list:
            # county_fips = state+county
            filename = f"tl_2010_{state_county}_bg10"

            # Use wget to download the TIGER Shapefile for a county
            # options -quiet = turn off wget output
            # add directory prefix to save files to folder named after program name
            shapefile_url = (
                "https://www2.census.gov/geo/tiger/TIGER2010/BG/2010/"
                + filename
                + ".zip"
            )
            print(
                (
                    "Downloading Shapefiles for State_County: "
                    + state_county
                    + " from: "
                    + shapefile_url
                ).format(filename=filename)
            )

            zip_file = os.path.join(download_dir, filename + ".zip")
            urllib.request.urlretrieve(shapefile_url, zip_file)

            with ZipFile(zip_file, "r") as zip_obj:
                zip_obj.extractall(path="shapefiletemp")

            # Read shapefile to GeoDataFrame
            gdf = gpd.read_file(f"shapefiletemp/{filename}.shp")

            # Set projection to EPSG 4326, which is required for folium
            gdf = gdf.to_crs(epsg=4326)

            # Append county data
            appended_countyshp.append(gdf)

        return appended_countyshp
