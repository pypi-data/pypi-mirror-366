from datetime import datetime, timezone
from operator import itemgetter

import polars as pl
import aiohttp
import pytz
import asyncio
import logging
import io_connect.constants as c
from typing import List, Optional, Union, Tuple, Dict, Literal
from typeguard import typechecked
from io_connect.utilities.store import ERROR_MESSAGE, Logger, AsyncLogger

from dateutil import parser


@typechecked
class AsyncDataAccess:
    __version__ = c.VERSION

    def __init__(
        self,
        user_id: str,
        data_url: str,
        ds_url: str,
        on_prem: Optional[bool] = False,
        tz: Optional[Union[pytz.BaseTzInfo, timezone]] = c.UTC,
        log_time: Optional[bool] = False,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize an AsyncDataAccess instance for asynchronous sensor data operations.

        Args:
            user_id (str): The API key or user ID for accessing the API.
            data_url (str): The URL of the data server.
            ds_url (str): The URL of the data source.
            on_prem (Optional[bool], optional): Specifies whether the data server is on-premises. Defaults to False.
            tz (Optional[Union[pytz.BaseTzInfo, timezone]], optional): The timezone for timestamp conversions.
                    Accepts a pytz timezone object or a datetime.timezone object.
                    Defaults to UTC.
            log_time (Optional[bool], optional): Whether to log response times for API calls. Defaults to False.
            logger (Optional[logging.Logger], optional): Custom logger instance. If None, a default logger is used.

        Notes:
        -----
        - This is the asynchronous version of DataAccess, all I/O operations must be awaited
        - Uses aiohttp for HTTP requests instead of requests library
        - Metadata must be pre-fetched for calibration and alias operations
        - All async methods should be called with await keyword
        """
        self.user_id = user_id
        self.data_url = data_url
        self.ds_url = ds_url
        self.on_prem = on_prem
        self.tz = tz
        self.log_time = log_time
        self.logger = AsyncLogger(logger)
        self._sync_logger = Logger(logger)  # Keep sync logger for sync methods

    async def get_user_info(self, on_prem: Optional[bool] = None) -> dict:
        """
        Fetches user information from the API asynchronously.

        Args:
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            dict: A dictionary containing user information.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> user_info = await data_access.get_user_info(on_prem=True)
            >>> print(user_info)

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_USER_INFO_URL.format(protocol=protocol, data_url=self.data_url)

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers={"userID": self.user_id}, ssl=False
                ) as response:
                    response.raise_for_status()
                    response_content = await response.json()

            if "data" not in response_content:
                raise aiohttp.ClientError("Data not found in response")

            return response_content["data"]

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return {}

        except (TypeError, ValueError) as e:
            print(f"[Type Error] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[Exception] {e}")
            return {}

    async def get_device_details(self, on_prem: Optional[bool] = None) -> pl.DataFrame:
        """
        Fetch details of all devices from the API asynchronously.

        Args:
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            pl.DataFrame: DataFrame containing details of all devices.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> device_details_df = await data_access.get_device_details(on_prem=True)
            >>> print(device_details_df)

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_DEVICE_DETAILS_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers={"userID": self.user_id}, ssl=False
                ) as response:
                    response.raise_for_status()
                    response_content = await response.json()

            if "data" not in response_content:
                raise aiohttp.ClientError("Data not found in response")

            # Convert data to DataFrame
            df = pl.DataFrame(response_content["data"])

            return df

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            print(f"[Type Error] {type(e).__name__}: {e}")
            return pl.DataFrame()

        except Exception as e:
            print(f"[Exception] {e}")
            return pl.DataFrame()

    async def get_device_metadata(
        self, device_id: str, on_prem: Optional[bool] = None
    ) -> dict:
        """
        Fetches metadata for a specific device asynchronously.

        Args:
            device_id (str): The identifier of the device.
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            dict: Metadata for the specified device.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> metadata = await data_access.get_device_metadata(device_id="device123", on_prem=True)
            >>> print(metadata)
            {'id': 'device123', 'name': 'Device XYZ', 'location': 'Room A', ...}

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_DEVICE_METADATA_URL.format(
                protocol=protocol, data_url=self.data_url, device_id=device_id
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers={"userID": self.user_id}, ssl=False
                ) as response:
                    response.raise_for_status()
                    response_content = await response.json()

            if "data" not in response_content:
                raise aiohttp.ClientError("Data not found in response")

            return response_content["data"]

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return {}

        except (TypeError, ValueError) as e:
            print(f"[Type Error] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[Exception] {e}")
            return {}

    def time_to_unix(
        self, time: Optional[Union[str, int, datetime]] = None
    ) -> int:
        """
        Convert a given time to Unix timestamp in milliseconds.

        Parameters:
        ----------
        time : Optional[Union[str, int, datetime]]
            The time to be converted. It can be a string in ISO 8601 format, a Unix timestamp in milliseconds, or a datetime object.
            If None, the current time in the specified timezone (`self.tz`) is used.

        Returns:
        -------
        int
            The Unix timestamp in milliseconds.

        Raises:
        ------
        ValueError
            If the provided Unix timestamp is not in milliseconds or if there are mismatched offset times between `time` timezone and `self.tz`.

        Notes:
        -----
        - If `time` is not provided, the method uses the current time in the timezone specified by `self.tz`.
        - If `time` is already in Unix timestamp format (in milliseconds), it is validated and returned directly.
        - If `time` is provided as a string, it is parsed into a datetime object.
        - If the datetime object doesn't have timezone information, it is assumed to be in the timezone specified by `self.tz`.
        - The method ensures consistency in timezone information between `time` and `self.tz` before converting to Unix timestamp.
        - Unix timestamps must be provided in milliseconds format (> 10 digits).

        Example:
        -------
        >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
        >>> unix_time = data_access.time_to_unix('2023-06-14T12:00:00Z')
        >>> print(unix_time)
            1686220800000
        """
        # If time is not provided, use the current time in the specified timezone
        if time is None:
            return int(datetime.now(self.tz).timestamp() * 1000)

        # If time is already in Unix timestamp format
        if isinstance(time, int):
            if time <= 0 or len(str(time)) <= 10:
                raise ValueError(
                    "Unix timestamp must be a positive integer in milliseconds, not seconds."
                )
            return int(time)

        # If time is in string format, convert it to a datetime object
        if isinstance(time, str):
            time = parser.parse(time, dayfirst=False, yearfirst=True)

        # If the datetime object doesn't have timezone information, assume it's in self.tz timezone
        if time.tzinfo is None:
            if isinstance(self.tz, pytz.BaseTzInfo):
                # If tz is a pytz timezone, localize the datetime
                time = self.tz.localize(time)
            else:
                # If tz is a datetime.timezone object, replace tzinfo
                time = time.replace(tzinfo=self.tz)

        elif self.tz.utcoffset(time.replace(tzinfo=None)) != time.tzinfo.utcoffset(
            time
        ):
            raise ValueError(
                f"Mismatched offset times between time: ({time.tzinfo.utcoffset(time)}) and self.tz:({self.tz.utcoffset(time.replace(tzinfo=None))})"
            )

        # Return datetime object after converting to Unix timestamp
        return int(time.timestamp() * 1000)

    def __get_cleaned_table(
        self,
        df: pl.DataFrame,
        alias: bool,
        cal: bool,
        device_id: str,
        sensor_list: list,
        on_prem: bool,
        unix: bool,
        metadata: Optional[dict] = None,
        pivot_table: Optional[bool] = True,
    ) -> pl.DataFrame:
        """
        Clean and preprocess a DataFrame containing time-series sensor data.

        Parameters:
        ----------
        df : pl.DataFrame
            The input DataFrame containing sensor data with columns 'time', 'sensor', and 'value'.

        alias : bool
            Flag indicating whether to apply sensor aliasing based on device configuration.

        cal : bool
            Flag indicating whether to apply calibration to sensor values.

        device_id : str
            The identifier for the device from which sensor data is collected.

        sensor_list : list
            A list of sensor IDs or names to filter and process from the DataFrame.

        on_prem : bool
            Flag indicating whether the data is retrieved from an on-premises server or not.

        unix : bool
            Flag indicating whether to convert 'time' column to Unix timestamp format in milliseconds.

        metadata : Optional[dict], default=None
            Additional metadata related to sensors or calibration parameters.

        pivot_table : Optional[bool], default=True
            Flag indicating whether to pivot the DataFrame to have sensors as columns.

        Returns:
        -------
        pl.DataFrame
            A cleaned and preprocessed DataFrame with columns adjusted based on the provided parameters.

        Notes:
        -----
        - The method assumes the input DataFrame (`df`) has columns 'time', 'sensor', and 'value'.
        - It converts the 'time' column to datetime format and sorts the DataFrame by 'time'.
        - The DataFrame is pivoted to have sensors as columns, indexed by 'time'.
        - Sensor list is filtered to include only sensors present in the DataFrame.
        - Calibration (`cal=True`) adjusts sensor values based on calibration parameters fetched from the server.
        - Sensor aliasing (`alias=True`) replaces sensor IDs or names with user-friendly aliases.
        - If `unix=True`, the 'time' column is converted to Unix timestamp format in milliseconds.
        - Timezone conversion is applied to 'time' column if `unix=False`, using the timezone (`self.tz`) specified during class initialization.
        - The method returns the cleaned and processed DataFrame suitable for further analysis or export.
        - This method is kept synchronous as it only processes data locally.
        """

        if pivot_table:
            # Ensure time column is in datetime format
            df = df.with_columns([
                pl.col("time").str.strptime(pl.Datetime, format=None, strict=False).alias("time")
            ])
            df = df.sort("time")

            # Pivot DataFrame
            df = df.pivot(values="value", index="time", columns="sensor").fill_null(strategy="forward")

            # Filter sensor list to include only present sensors
            available_columns = df.columns
            sensor_list = [sensor for sensor in sensor_list if sensor in available_columns]

        # Note: This remains synchronous as it only processes data locally
        print(f"[Processing] Applying calibration: {cal}, alias: {alias}")
        
        # Apply calibration if required
        if cal:
            df, metadata = self.__get_calibration(
                device_id=device_id,
                sensor_list=sensor_list,
                metadata=metadata,
                df=df,
                on_prem=on_prem,
            )

        # Apply sensor alias if required
        if alias:
            df, metadata = self.get_sensor_alias(
                device_id=device_id,
                df=df,
                sensor_list=sensor_list,
                on_prem=on_prem,
                metadata=metadata,
            )

        # Convert time to Unix timestamp if required
        if unix:
            df = df.with_columns([
                pl.col("time").map_elements(lambda x: int(x.timestamp() * 1000), return_dtype=pl.Int64).alias("time")
            ])
        else:
            # Convert time column to timezone
            df = df.with_columns([
                pl.col("time").dt.convert_time_zone(str(self.tz)).alias("time")
            ])
        
        print(f"[Data] Processed DataFrame shape: {df.shape}")
        return df

    def get_sensor_alias(
        self,
        device_id: str,
        df: pl.DataFrame,
        on_prem: Optional[bool] = None,
        sensor_list: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> Tuple[pl.DataFrame, Dict]:
        """
        Applies sensor aliasing to the DataFrame columns.

        This method retrieves sensor aliases from metadata and renames DataFrame columns
        accordingly, appending the sensor ID to the alias for clarity.

        Args:
            device_id (str): The ID of the device.
            df (pl.DataFrame): DataFrame containing sensor data.
            on_prem (bool): Whether the data is on-premise.
            sensor_list (list): List of sensor IDs.
            metadata (Optional[dict]): Metadata containing sensor information.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> metadata = await data_access.get_device_metadata("TEST_DEVICE")
            >>> device_details_df, metadata = data_access.get_sensor_alias(df=df, device_id="TEST_DEVICE", metadata=metadata)
            >>> print(device_details_df)

        Returns:
            pl.DataFrame: DataFrame with renamed columns.
            dict: Updated metadata with sensor information.

        Notes:
        -----
        - This method is kept synchronous as it only processes data locally.
        - For the async version, metadata must be pre-fetched asynchronously before calling this method.
        """
        # If on_prem is not provided, use the default value from the class attribute
        if on_prem is None:
            on_prem = self.on_prem

        # If metadata is not provided, it should be fetched asynchronously before calling this method
        if metadata is None:
            raise ValueError("Metadata must be provided for async version")

        if sensor_list is None:
            sensor_list = df.columns

        # Create a dictionary mapping sensor IDs to sensor names
        sensor_map = {
            item["sensorId"]: "{} ({})".format(item["sensorName"], item["sensorId"])
            for item in metadata["sensors"]
            if item["sensorId"] in sensor_list
        }

        # Rename the DataFrame columns using the constructed mapping
        df = df.rename(sensor_map)

        return df, metadata

    def __get_calibration(
        self,
        device_id: str,
        sensor_list: list,
        df: pl.DataFrame,
        on_prem: bool = False,
        metadata: Optional[dict] = None,
    ) -> Tuple[pl.DataFrame, Dict]:
        """
        Applies calibration to sensor data in the DataFrame.

        This method extracts calibration parameters from metadata and applies them to the
        corresponding sensor data in the DataFrame.

        Args:
            device_id (str): The ID of the device.
            sensor_list (list): List of sensor IDs.
            df (pl.DataFrame): DataFrame containing sensor data.
            on_prem (bool): Whether the data is on-premise. Defaults to False.
            metadata (Optional[dict]): Metadata containing calibration parameters.

        Returns:
            pl.DataFrame: DataFrame with calibrated sensor data.
            dict: Updated metadata with calibration information.

        Notes:
        -----
        - This method is kept synchronous as it only processes data locally.
        - For the async version, metadata must be pre-fetched asynchronously before calling this method.
        """
        # If metadata is not provided, it should be fetched asynchronously before calling this method
        if metadata is None:
            raise ValueError("Metadata must be provided for async version")

        # Define default calibration values
        default_values = {"m": 1.0, "c": 0.0, "min": float("-inf"), "max": float("inf")}

        # Extract sensor calibration data from metadata
        data = metadata.get("params", {})

        # Iterate over sensor_list to apply calibration
        for sensor in sensor_list:
            if sensor not in df.columns:
                continue
                
            # Extract calibration parameters for the current sensor
            params = {
                param["paramName"]: param["paramValue"]
                for param in data.get(sensor, [])
            }
            cal_values = {}

            # Populate cal_values with extracted parameters or defaults if not available
            for key in default_values:
                try:
                    cal_values[key] = float(params.get(key, default_values[key]))
                except Exception:
                    cal_values[key] = default_values[key]

            if cal_values != default_values:
                # Apply calibration using polars
                df = df.with_columns([
                    pl.col(sensor).cast(pl.Float64, strict=False)
                    .map_elements(lambda x: max(min(cal_values["m"] * x + cal_values["c"], cal_values["max"]), cal_values["min"]) if x is not None else None, return_dtype=pl.Float64)
                    .alias(sensor)
                ])

        return df, metadata

    async def get_dp(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        n: int = 1,
        cal: Optional[bool] = True,
        end_time: Optional[Union[str, int, datetime]] = None,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Retrieve and process data points (DP) from sensors for a given device asynchronously.

        Args:
            device_id (str): The ID of the device.
            sensor_list (Optional[List], optional): List of sensor IDs. If None, all sensors for the device are used.
            end_time (Optional[Union[str, int, datetime]], optional): The end time for data retrieval.
                Defaults to None.
            n (int, optional): Number of data points to retrieve. Defaults to 1.
            cal (bool, optional): Whether to apply calibration. Defaults to True.
            alias (bool, optional): Whether to apply sensor aliasing. Defaults to False.
            unix (bool, optional): Whether to return timestamps in Unix format. Defaults to False.
            on_prem (Optional[bool], optional): Whether the data source is on-premise.
                If None, the default value from the class attribute is used. Defaults to None.

        Returns:
            pl.DataFrame: DataFrame containing retrieved and processed data points.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.get_dp("XYZ",sensor_list= ['X'],n=1,alias=True,cal=True,end_time=1685767732710,unix=False)
            >>> print(df)

        Raises:
            ValueError: If parameter 'n' is less than 1.
            Exception: If no sensor data is available.
            Exception: If max retries for data fetching from api-layer are exceeded.
            TypeError: If an unexpected type error occurs during execution.
            aiohttp.ClientError: If an error occurs during HTTP request.
            Exception: For any other unexpected exceptions raised during execution.
        """
        try:
            metadata = None

            # Validate input parameters
            if n < 1:
                raise ValueError("Parameter 'n' must be greater than or equal to 1")

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            # Fetch metadata if sensor_list is not provided
            if sensor_list is None:
                metadata = await self.get_device_metadata(device_id, on_prem)
                sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

            # Ensure sensor_list is not empty
            if not sensor_list:
                raise Exception("No sensor data available.")

            # Convert end_time to Unix timestamp
            end_time = self.time_to_unix(end_time)

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            # Construct API URL for data retrieval
            url = c.GET_DP_URL.format(protocol=protocol, data_url=self.data_url)

            df = pl.DataFrame()

            retry = 0
            # with Logger(self.logger, "Total Data Polling time:", self.log_time):
            for sensor in sensor_list:
                cursor = {"end": end_time, "limit": n}

                while cursor["end"]:
                    try:
                        params = {
                            "device": device_id,
                            "sensor": sensor,
                            "eTime": cursor["end"],
                            "lim": cursor["limit"],
                            "cursor": "true",
                        }
                        # with Logger(
                        #     self.logger, f"API {url} response time:", self.log_time
                        # ):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, params=params, ssl=False) as response:
                                response.raise_for_status()
                                response_content = await response.json()

                        # Check for errors in the API response
                        if "success" in response_content:
                            raise aiohttp.ClientError("API response indicates failure")

                        data = response_content["data"]
                        df = pl.concat([df, pl.DataFrame(data)])
                        cursor = response_content["cursor"]

                    except Exception as e:
                        retry += 1
                        error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
                        # self.logger.error(
                        #     f"[{type(e).__name__}] Retry Count: {retry}, {e}"
                        #     + error_message
                        # )

                        # Retry with exponential backoff
                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            raise Exception(
                                "Max retries for data fetching from api-layer exceeded."
                                + error_message
                            )

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                # Ensure metadata is available for processing
                if metadata is None:
                    metadata = await self.get_device_metadata(device_id, on_prem)
                    
                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            print(f"[Type Error] {type(e).__name__}: {e}")
            return pl.DataFrame()

        except Exception as e:
            print(f"[Exception] {e}")
            return pl.DataFrame()

    # async def get_firstdp(
    #     self,
    #     device_id: str,
    #     sensor_list: Optional[List] = None,
    #     cal: Optional[bool] = True,
    #     start_time: Union[str, int, datetime] = None,
    #     n: Optional[int] = 1,
    #     alias: Optional[bool] = False,
    #     unix: Optional[bool] = False,
    #     on_prem: Optional[bool] = None,
    # ) -> pl.DataFrame:
    #     """
    #     Fetches the first data point after a specified start time for a given device and sensor list asynchronously.

    #     Parameters:
    #     - start_time (Union[str, int, datetime]): The start time for the query (can be a string, integer, or datetime).
    #     - device_id (str): The ID of the device.
    #     - sensor_list (Optional[List]): List of sensor IDs to query data for. Defaults to all sensors if not provided.
    #     - n (Optional[int]): Number of data points to retrieve. Defaults to 1.
    #     - cal (bool): Flag indicating whether to perform calibration on the data. Defaults to True.
    #     - alias (bool): Flag indicating whether to use sensor aliases in the DataFrame. Defaults to False.
    #     - unix (bool): Flag indicating whether to return timestamps as Unix timestamps. Defaults to False.
    #     - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.

    #     Returns:
    #     - pl.DataFrame: The DataFrame containing the retrieved data points.

    #     Example:
    #         >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
    #         >>> df = await data_access.get_firstdp(device_id="XYZ",sensor_list= ['X'],alias=True,cal=True,start_time=1685767732710,unix=False)
    #         >>> print(df)

    #     Exceptions Handled:
    #     - TypeError: Raised when there is a type mismatch in the input parameters.
    #     - aiohttp.ClientError: Raised when there is an issue with the HTTP request.
    #     - Exception: General exception handling for other errors.
    #     """
    #     try:
    #         metadata = None

    #         # Validate input parameters
    #         if n < 1:
    #             raise ValueError("Parameter 'n' must be greater than or equal to 1")

    #         df_devices = await self.get_device_details(on_prem=on_prem)

    #         # Check if the device is added in the account
    #         if device_id not in df_devices["devID"].to_list():
    #             raise Exception(f"Message: Device {device_id} not added in account")

    #         # Fetch metadata if sensor_list is not provided
    #         if sensor_list is None:
    #             metadata = await self.get_device_metadata(device_id, on_prem)
    #             sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

    #         # Ensure sensor_list is not empty
    #         if not sensor_list:
    #             raise Exception("No sensor data available.")

    #         # Convert start_time to Unix timestamp
    #         start_time = self.time_to_unix(start_time)

    #         # If on_prem is not provided, use the default value from the class attribute
    #         if on_prem is None:
    #             on_prem = self.on_prem
    #         protocol = "http" if on_prem else "https"

    #         # Construct API URL for data retrieval
    #         url = c.GET_FIRST_DP.format(protocol=protocol, data_url=self.data_url)

    #         df = pl.DataFrame()

    #         retry = 0

    #         # with Logger(self.logger, "Total Data Polling time:", self.log_time):
    #         for sensor in sensor_list:
    #             cursor = {"start": start_time, "limit": n}

    #             while cursor["start"]:
    #                 try:
    #                     params = {
    #                         "device": device_id,
    #                         "sensor": sensor,
    #                         "sTime": cursor["start"],
    #                         "lim": cursor["limit"],
    #                         "cursor": "true",
    #                     }
    #                     print(f"[API Call] {params}")
    #                     # with Logger(
    #                     #     self.logger, f"API {url} response time:", self.log_time
    #                     # ):
    #                     async with aiohttp.ClientSession() as session:
    #                         async with session.get(url, params=params, ssl=False) as response:
    #                             response.raise_for_status()
    #                             response_content = await response.json()

    #                     print(f"[API Response] {type(response_content)}: {response_content}")

    #                     # Check for errors in the API response
    #                     if "success" in response_content:
    #                         raise aiohttp.ClientError("API response indicates failure")

    #                     # Handle different response structures
    #                     if isinstance(response_content, list):
    #                         # If response is a list, treat it as data directly
    #                         data = response_content
    #                         cursor = {"start": None}  # Stop the loop
    #                     elif isinstance(response_content, dict):
    #                         # If response is a dict, extract data and cursor
    #                         data = response_content.get("data", [])
    #                         cursor = response_content.get("cursor", {"start": None})
    #                     else:
    #                         raise ValueError(f"Unexpected response type: {type(response_content)}")

    #                     if data:
    #                         df = pl.concat([df, pl.DataFrame(data)])
                        
    #                     print(f"[Data] Retrieved {len(data) if data else 0} records")

    #                 except Exception as e:
    #                     retry += 1
    #                     error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
    #                     # self.logger.error(
    #                     #     f"[{type(e).__name__}] Retry Count: {retry}, {e}"
    #                     #     + error_message
    #                     # )

    #                     # Retry with exponential backoff
    #                     if retry < c.MAX_RETRIES:
    #                         sleep_time = (
    #                             c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
    #                         )
    #                         await asyncio.sleep(sleep_time)
    #                     else:
    #                         raise Exception(
    #                             "Max retries for data fetching from api-layer exceeded."
    #                             + error_message
    #                         )

    #         # Process retrieved data if DataFrame is not empty
    #         if not df.is_empty():
    #             # Ensure metadata is available for processing
    #             if metadata is None:
    #                 metadata = await self.get_device_metadata(device_id, on_prem)
                    
    #             df = self.__get_cleaned_table(
    #                 df=df,
    #                 alias=alias,
    #                 cal=cal,
    #                 device_id=device_id,
    #                 sensor_list=sensor_list,
    #                 on_prem=on_prem,
    #                 unix=unix,
    #                 metadata=metadata,
    #             )

    #         return df

    #     except aiohttp.ClientError as e:
    #         error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
    #         print(f"[API Error] {error_message}")
    #         return pl.DataFrame()

    #     except (TypeError, ValueError) as e:
    #         print(f"[Type Error] {type(e).__name__}: {e}")
    #         return pl.DataFrame()

    #     except Exception as e:
    #         print(f"[Exception] {e}")
    #         return pl.DataFrame()

    async def data_query(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        start_time: Union[str, int, datetime] = None,
        end_time: Optional[Union[str, int, datetime]] = None,
        cal: Optional[bool] = True,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Queries and retrieves sensor data for a given device within a specified time range asynchronously.

        Parameters:
        - device_id (str): The ID of the device.
        - start_time (Union[str, int, datetime]): The start time for the query (can be a string, integer, or datetime).
        - end_time (Optional[Union[str, int, datetime]]): The end time for the query (can be a string, integer, or datetime). Defaults to None.
        - sensor_list (Optional[List]): List of sensor IDs to query data for. Defaults to all sensors if not provided.
        - cal (bool): Flag indicating whether to perform calibration on the data. Defaults to True.
        - alias (bool): Flag indicating whether to use sensor aliases in the DataFrame. Defaults to False.
        - unix (bool): Flag indicating whether to return timestamps as Unix timestamps. Defaults to False.
        - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.
        - metadata : Optional[dict], default=None
            Additional metadata related to sensors or calibration parameters.

        Returns:
        - pl.DataFrame: The DataFrame containing the queried sensor data.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.data_query("XYZ",sensor_list = ["X","Y"],end_time=1717419975210,start_time=1685767732000,alias=True)
            >>> print(df)

        Exceptions Handled:
        - TypeError: Raised when there is a type mismatch in the input parameters.
        - aiohttp.ClientError: Raised when there is an issue with the HTTP request.
        - Exception: General exception handling for other errors.
        """
        try:
            metadata = None

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            # Fetch metadata if sensor_list is not provided
            if sensor_list is None:
                metadata = await self.get_device_metadata(device_id, on_prem)
                sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

            # Ensure sensor_list is not empty
            if not sensor_list:
                raise Exception("No sensor data available.")

            # Resolve on_prem to a boolean value
            if on_prem is None:
                on_prem = self.on_prem

            # Convert timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )
    
            # Use influxdb method for data retrieval
            df = await self.__influxdb(
                device_id=device_id,
                sensor_list=sensor_list,
                start_time=start_time_unix,
                end_time=end_time_unix,
                on_prem=on_prem,
            )

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                # Ensure metadata is available for processing
                if metadata is None:
                    metadata = await self.get_device_metadata(device_id, on_prem)
                    
                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except Exception as e:
            print(f"[Exception] {e}")
            return pl.DataFrame()

    async def __influxdb(
        self,
        device_id: str,
        sensor_list: List,
        start_time: int,
        end_time: int,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Private method to query InfluxDB for sensor data asynchronously using cursor-based pagination.

        This method fetches sensor data from the InfluxDB API with cursor-based pagination to handle
        large datasets efficiently. It implements retry logic with exponential backoff for robust
        data retrieval.

        Args:
            device_id (str): The ID of the device to query data for.
            sensor_list (List): List of sensor IDs to retrieve data from.
            start_time (int): The start time in Unix timestamp format (milliseconds).
            end_time (int): The end time in Unix timestamp format (milliseconds).
            on_prem (Optional[bool]): Whether to use on-premises server. If None, uses class default.

        Returns:
            pl.DataFrame: DataFrame containing the retrieved sensor data with columns 'time', 'sensor', and 'value'.

        Notes:
        -----
        - Uses cursor-based pagination to fetch data in batches defined by c.CURSOR_LIMIT
        - Implements retry logic with exponential backoff (c.RETRY_DELAY) up to c.MAX_RETRIES
        - Continues fetching data while cursor["start"] and cursor["end"] are available
        - Returns empty DataFrame if no data is found or if all retries are exhausted
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            url = c.INFLUXDB_URL.format(protocol=protocol, data_url=self.data_url)

            # Initialize cursor for data retrieval
            cursor = {"start": start_time, "end": end_time}

            sensor_values = ",".join(sensor_list)
            retry = 0
            df = pl.DataFrame()

            headers = {"userID": self.user_id}
            
            # with Logger(self.logger, "Total Data Polling time:", self.log_time):
            while cursor["start"] and cursor["end"]:
                try:
                    # Set the request parameters using cursor values
                    params = {
                        "device": device_id,
                        "sensor": sensor_values,
                        "sTime": cursor["start"],
                        "eTime": cursor["end"],
                        "cursor": "true",
                        "limit": c.CURSOR_LIMIT,
                    }

                    # with Logger(self.logger, f"API {url} response time:", self.log_time):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, params=params, ssl=False) as response:
                            response.raise_for_status()
                            response_content = await response.json()

                    # Check for errors in the API response
                    if "success" in response_content:
                        raise aiohttp.ClientError("API response indicates failure")

                    data = response_content["data"]
                    cursor = response_content["cursor"]

                    # Append the fetched data to the DataFrame
                    df = pl.concat([df, pl.DataFrame(data)])

                except Exception as e:
                    retry += 1
                    error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
                    # self.logger.error(
                    #     f"[{type(e).__name__}] Retry Count: {retry}, {e}"
                    #     + error_message
                    # )

                    # Retry with exponential backoff
                    if retry < c.MAX_RETRIES:
                        sleep_time = (
                            c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        raise Exception(
                            "Max retries for data fetching from api-layer exceeded."
                            + error_message
                        )

            return df

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return pl.DataFrame()

        except Exception as e:
            print(f"[Exception] {e}")
            return pl.DataFrame()

    async def get_load_entities(
        self, on_prem: Optional[bool] = None, clusters: Optional[list] = None
    ) -> list:
        """
        Fetches load entities from an API asynchronously, handling pagination and optional filtering by cluster names.

        Args:
            on_prem (Optional[bool]): Specifies whether to use on-premise settings for the request.
                                      Defaults to None, which uses the class attribute `self.on_prem`.
            clusters (Optional[list]): A list of cluster names to filter the results by.
                                       Defaults to None, which returns all clusters.

        Returns:
            list: A list of load entities. If clusters are provided, only entities belonging to the specified clusters are returned.

        Raises:
            Exception: If no clusters are provided or if the maximum retry limit is reached.
            TypeError, ValueError, aiohttp.ClientError: For other request-related exceptions.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")

            >>> # Fetch all load entities using on-premise settings
            >>> all_entities = await data_access.get_load_entities()

            >>> # Fetch load entities and filter by specific cluster names
            >>> specific_clusters = await data_access.get_load_entities(clusters=["cluster1", "cluster2"])

            >>> # Fetch load entities using on-premise settings, but no specific clusters
            >>> on_prem_entities = await data_access.get_load_entities(on_prem=True)

        """
        try:
            # Validate clusters input
            if clusters is not None and len(clusters) == 0:
                raise Exception("No clusters provided.")
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            page_count = 1
            cluster_count = None
            retry = 0

            result = []

            # Construct API URL for data retrieval
            url = c.GET_LOAD_ENTITIES.format(
                protocol=protocol,
                data_url=self.data_url,
            )
            headers = {"userID": self.user_id}

            while True:
                try:
                    # with Logger(
                    #     self.logger, f"API {url} response time:", self.log_time
                    # ):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url + f"/{self.user_id}/{page_count}/{cluster_count}",
                            headers=headers,
                            ssl=False,
                        ) as response:
                            response.raise_for_status()
                            response_data = await response.json()

                    if "error" in response_data:
                        # self.logger.error(f"API Error: {response_data}")
                        return []

                    # Extend result with retrieved response_data
                    result.extend(response_data["data"])

                    total_count = response_data["totalCount"]
                    clusters_recieved = len(result)

                    # Break the loop if all clusters have been received
                    if clusters_recieved == total_count:
                        break

                    # Update for next page
                    page_count += 1
                    cluster_count = total_count - clusters_recieved

                except Exception as e:
                    retry += 1
                    error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
                    # self.logger.error(
                    #     f"[{type(e).__name__}] Retry Count: {retry}, {e}"
                    #     + error_message
                    # )
                    if retry < c.MAX_RETRIES:
                        sleep_time = c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                        await asyncio.sleep(sleep_time)
                    else:
                        raise Exception(
                            "Max retries for data fetching from api-layer exceeded."
                            + error_message
                        )
            # Filter results by cluster names if provided
            if clusters is not None:
                return [item for item in result if item["name"] in clusters]

            return result

        except aiohttp.ClientError as e:
            error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"
            print(f"[API Error] {error_message}")
            return []

        except (TypeError, ValueError) as e:
            # self.logger.error(f"[EXCEPTION] {type(e).__name__}: {e}")
            return []

        except Exception as e:
            # self.logger.error(f"[EXCEPTION] {e}")
            return [] 