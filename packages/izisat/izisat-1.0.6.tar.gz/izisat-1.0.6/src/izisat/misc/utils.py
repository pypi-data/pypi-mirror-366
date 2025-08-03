from loguru import logger
from pathlib import Path
from datetime import datetime

class Utils:
    def __init__(self):
        pass
    
    
    def construct_query_for_sentinel2_products(self, footprint: str, start_date: str, end_date: str, cloud_cover_percentage: str, type, 
              platform_name: str):
        """
        Create a query for downloading Sentinel data based on specified parameters.

        Parameters:
        ------------
        footprint: str
            The spatial geometry (POLYGON) of the area of interest.
        start_date: str
            The start date for the time range of interest in the format 'YYYY-MM-DD'.
        end_date: str
            The end date for the time range of interest in the format 'YYYY-MM-DD'.
        cloud_cover_percentage: str
            The maximum allowable cloud cover percentage.
        type: str or list
            Type of MSI to download
        platform_name: str, optional
            The name of the Sentinel platform (default: 'SENTINEL-2').

        Returns:
        params: str
            The query string for downloading Sentinel data.
        """
        
        logger.info("Creating query to download Sentinel data...")
        try:
            if footprint and start_date and end_date and platform_name and cloud_cover_percentage and type: 
                footprint = footprint.replace(" ", "%20")
                if isinstance(type, str):
                    params = f"?&$filter=(Collection/Name%20eq%20%27{platform_name}%27%20and%20(Attributes/OData.CSC.StringAttribute/any(att:att/Name%20eq%20%27instrumentShortName%27%20and%20att/OData.CSC.StringAttribute/Value%20eq%20%27MSI%27)%20and%20Attributes/OData.CSC.DoubleAttribute/any(att:att/Name%20eq%20%27cloudCover%27%20and%20att/OData.CSC.DoubleAttribute/Value%20le%20{cloud_cover_percentage})%20and%20(contains(Name,%27{type}%27)%20and%20OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27)))%20and%20Online%20eq%20true)%20and%20ContentDate/Start%20ge%20{start_date}T00:00:00.000Z%20and%20ContentDate/Start%20lt%20{end_date}T23:59:59.999Z&$orderby=ContentDate/Start%20desc&$expand=Attributes&$count=True&$top=50&$expand=Assets&$skip=0"
                    logger.success("Query created successfully")
                    return params
                elif isinstance(type, list):
                    params = f"?&$filter=(Collection/Name%20eq%20%27{platform_name}%27%20and%20(Attributes/OData.CSC.StringAttribute/any(att:att/Name%20eq%20%27instrumentShortName%27%20and%20att/OData.CSC.StringAttribute/Value%20eq%20%27MSI%27)%20and%20Attributes/OData.CSC.DoubleAttribute/any(att:att/Name%20eq%20%27cloudCover%27%20and%20att/OData.CSC.DoubleAttribute/Value%20le%20{cloud_cover_percentage})%20and%20((contains(Name,%27{type[0]}%27)%20and%20OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27))%20or%20(contains(Name,%27{type[1]}%27)%20and%20OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27))))%20and%20Online%20eq%20true)%20and%20ContentDate/Start%20ge%20{start_date}T00:00:00.000Z%20and%20ContentDate/Start%20lt%20{end_date}T23:59:59.999Z&$orderby=ContentDate/Start%20desc&$expand=Attributes&$count=True&$top=50&$expand=Assets&$skip=0"
                    logger.success("Query created successfully")
                    return params
                else: 
                    raise ValueError("Please provide valid values for type.")
            else:
                raise ValueError("Please provide valid values for all required parameters.")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise
        
    def retrieve_products_info(self, products):
        """
        Retrieve information about Sentinel products.

        Parameters:
        -----------
        products: list
            List of Sentinel products, each represented as a dictionary.

        Returns:
        ---------
        list:
            A list containing information about each product. Each element in the list is a sublist with the following format:
            [product_id, product_name, product_s3path, product_origin_date, product_tile, product_platform_name, product_type]
        """
        result_list = []
        logger.info(f"Retrieving information about {len(products)} products...")

        for i, product in enumerate(products):
            logger.info(f"Retrieving information about product {i+1}")
            product_id = product['Id']
            product_name = product['Name']
            product_s3path = product["S3Path"]
            product_origin_date = product['ContentDate']['End']

            # Creating output directory to save downloaded data
            product_tile = product_name.split("_")[5]
            product_platform_name = product_s3path.split('/')[2]
            product_type = product_name.split('_')[1][-3:]

            # Append product information to the result list
            result_list.append([product_id, product_name, product_s3path, product_origin_date, product_tile, product_platform_name, product_type])
            logger.success(f"ID, Name, S3Path, Origin Date, Tile, Plataform Name and Type successfully retrieved for product {i+1}")

        logger.success("Information successfully retrieved for all products. A list with these informations were created!")
        return result_list
    
    def modify_string(self, url):
        """
        Modify a URL by replacing the last occurrence of "Nodes" with "$value".

        Parameters:
        -----------
        url: str
            The input URL to be modified.

        Returns:
        ---------
        modified_url: str
            The modified URL with the last "Nodes" replaced by "$value".
        ValueError
            If "Nodes" is not found in the input URL.
    """
        last_nodes_index = url.rfind("Nodes")

        if last_nodes_index != -1:
        # Remove the last "Nodes" and replace it with "/$value"
            modified_url = url[:last_nodes_index] + "$value"
            return modified_url
        else:
            raise ValueError("Error: 'Nodes' not found in the URL")

    def generate_sentinel2_band_paths_nested_by_tile(self, download_folder: str, products: list[list[str]]) -> dict[str, dict[str, str]]:
        """
        Gera dicionário aninhado com caminhos das bandas Sentinel-2, agrupados por data e tile (fuso).

        Retorna:
            {
                "2025-04-13_T23": {
                    "B02": "/.../T23KKV_20250413T132251_B02_10m.jp2",
                    "B03": "/.../T23KKV_..._B03_10m.jp2",
                    ...
                },
                ...
            }
        """
        from collections import defaultdict
        result = {}
        grouped = defaultdict(list)
        for variables in products:
            date_obj = datetime.fromisoformat(variables[3].replace("Z", ""))
            date_str = date_obj.strftime("%Y-%m-%d")
            tile = variables[4]            # Ex: T23KKV
            tile_id = tile[1:3]            # Pega apenas o fuso "23"
            sensor = variables[5]
            product_level = variables[6]
            year = f"{date_obj.year}"
            month = f"{date_obj.month:02}"
            day = f"{date_obj.day:02}"
            timestamp_part = variables[1].split("_")[2]  # Ex: 20250413T132251

            #bands = ["B02", "B03", "B04", "B08"]
            bands_dict = {
                "B01": 60,
                "B02": 10,
                "B03": 10,
                "B04": 10,
                "B05": 20,
                "B06": 20,
                "B07": 20,
                "B08": 10,
                "B8A": 20,
                "B09": 60,
                "B10": 60,
                "B11": 20,
                "B12": 20,
            }
            bands = ["B01", "B02", "B03","B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12", "datMask"]
            base_path = Path(download_folder) / sensor / year / month / day / tile / product_level
            band_paths = {
                band: str(base_path / f"{bands_dict[band]}m" / f"{tile}_{timestamp_part}_{band}_{bands_dict[band]}m.jp2")
                for band in bands if band != "datMask"
            }

            key = f"{date_str}_T{tile_id}"  # Ex: 2025-04-13_T23
            result[key] = band_paths
            
            for key, bands in result.items():
                date = key.split('_')[0]
                grouped[date].append(bands)

        return grouped
    