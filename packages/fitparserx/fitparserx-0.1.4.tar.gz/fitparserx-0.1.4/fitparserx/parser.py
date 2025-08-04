from garmin_fit_sdk import Decoder, Stream
import numpy as np
import pandas as pd
import os
from pathlib import Path
import datetime
import pytz
from inspect import signature
import warnings

UNIX_GARMIN_DIFF = 631065600 # The difference between the UNIX and Garmin epochs
                             # used for time measurements

class FitParser:

    _allowed_metrics = {"heart_rate":"monitoring_mesgs",
                        "stress_level":"stress_level_mesgs",
                        "respiration_rate":"respiration_rate_mesgs"}

    # In the decoded messages metrics don't have consistent key labels
    _time_labels = {"stress_level":"stress_level_time",
                    "respiration_rate":"timestamp"}
    
    _value_labels = {"stress_level":"stress_level_value",
                     "respiration_rate":"respiration_rate"}
    
    def __init__(self, path=None, *, email=None, mode="all"):
        """
        Parameters
        -----------------------------------------------
        path: str | Path | None
            The path is scanned for the relevant .fit files. 
            
            mode ='all':
                If the path is not selected, the ./data/ directory 
                is checked, and if it doesn't exist the current working
                directory is used. The parser goes over the list of
                files of the form {email}*.fit.
            mode ='day'
                In the mode for a single day data, the parser
                looks for the *WELLNESS.fit files.
                
        email: str
            Specify the user email (this is the email used
            when exporting the Garmin data).

        mode: {'all', 'day'}
            'all'(default) -> grabs {email}*.fit files given by path (or ./data/
                            or cwd in this order if path is not specified)
            'day' -> grabs the single day data which come in the *WELLNESS.fit form

        Raises FileNotFoundError or ValueError on bad input.
        """

        if path is not None and Path(path).is_file():
            self.files = [Path(path)]
            
        # First look in ./data/, if it doesn't exist, fallback to CWD   
        elif path is None:
            # Default search directory
            data_dir = Path.cwd()/"data" 
            source_dir = data_dir if data_dir.is_dir() else Path.cwd()
        else:
            source_dir = Path(path)
            if not source_dir.is_dir():
                raise FileNotFoundError(f"Expected a directory at {source_dir!r}")

        # Collect files into a list depending on the mode
        if mode == "all":
            if email is None:
                raise ValueError("Email is required when mode='all'")
            search_pattern = f"{email}*.fit"
        elif mode == "day":
            search_pattern = "*WELLNESS.fit"
        else:
            raise ValueError("Mode must be either 'all' or 'day'.")

        if Path(path).is_dir():
            self.directory = source_dir
            files = list(source_dir.glob(search_pattern))
            if not files:
                raise FileNotFoundError(
                    f"No files matching {search_pattern!r} in {source_dir!r}"
                )
            self.files = sorted(files) # Sort for reproducibility

        self.mode = mode

    def _read_wrapper(self, decoder: Decoder, **kwargs):
        """ 
        Decoder.read() wrapper method that converts
        the positional arguments into keyword arguments
        and raises warnings for non-existent arguments.
        """
        sig = signature(decoder.read)

        
        #_______Default values_______#
    
        # apply_scale_and_offset = True,
        # convert_datetimes_to_dates = True,
        # convert_types_to_strings = True,
        # enable_crc_check = True,
        # expand_sub_fields = True,
        # expand_components = True,
        # merge_heart_rates = True,
        # mesg_listener = None,
        # decode_mode = DecodeMode.NORMAL
    
        accepted = {
            k:v for k, v in kwargs.items()
            if k in sig.parameters
        }

        not_accepted = [
            k for k in kwargs if k not in sig.parameters
        ]

        if not_accepted:
            warnings.warn(
                f"Arguments not valid: {', '.join(not_accepted)}",
                category = UserWarning,
                stacklevel = 2 # Warnings raised on the level of the wrapper function
            )
    
        return decoder.read(**accepted)
    
    def parse_to_raw(self, **read_kwargs):
        """
        Outputs the raw data as obtained from garmin_fit_sdk
        in the form of the dictionary. The filenames are the
        keys of the dictionary.
        """
        
        raw_messages = {}
        all_errors = {}

        for path in self.files:
            try:
                stream = Stream.from_file(path)
                decoder = Decoder(stream)
                messages, errors = self._read_wrapper(decoder)
                raw_messages[path.name] = messages
                all_errors[path.name] = errors
                
            except Exception as error:
                warnings.warn(f"Failed to decode {path.name}: {error}",
                              category = UserWarning,
                              stacklevel=2)

        return raw_messages, all_errors

    def _parse_entry(self, **read_kwargs):
        """
        Outputs the raw data as obtained from garmin_fit_sdk
        in the form of the dictionary. The filenames are the
        keys of the dictionary.
        """

        for path in self.files:
            try:
                stream = Stream.from_file(path)
                decoder = Decoder(stream)
                messages, _ = self._read_wrapper(decoder)
                yield messages
                
            except Exception as error:
                warnings.warn(f"Failed to decode {path.name}: {error}",
                              category = UserWarning,
                              stacklevel=2)

    def _parse_hr(self, file, fill=None, add_state=False):
        """
        Parses through a file dictionary entry with the key named
        'monitoring_mesgs'. Looks for the full timestamp and records
        it. This is used as a base time. The message time comes with
        the timestamp_16 from which the appropriate datetime object
        is extracted.

        add_state: Bool
        ------------------------------------------------------------
        If True, adds the activity_type (such as 'sedentary' or
        'walking'). Missing times are filled with the
        last recorded activity.

        Returns: List[datetime], List[int] 
        -------------------------------------------------------------
            Datetimes: Calculated with respect to a specific timezone
            Heart rates: Given as integers
        """

        try:
            base_time = self._find_base_time(file["monitoring_mesgs"])
        except Exception as e:
            return [], []

        datetimes = []
        heart_rates = []
        states = []
        
        current_time = base_time
        current_state = "NaN"
        
        for messg in file["monitoring_mesgs"]:
            current_time = messg.get("timestamp",
                                     current_time) # Defaults to previous time
            hr = messg.get("heart_rate")
            ts_16 = messg.get("timestamp_16")

            if add_state:
                current_state = messg.get("activity_type", current_state)
                
            # hr and ts_16 keys always come together
            if current_time is None or hr is None:
                continue
                
            if hr:
                hr = hr if hr>0 else self._fill(fill, hr)
                heart_rates.append(hr)
                datetimes.append(self._convert_garmin_to_real(current_time, ts_16))
                if add_state:
                    states.append(current_state)

        return datetimes, heart_rates, states

    def _fill(self, fill, val):
        """
        Fill according to chosen fill strategy.
        """
        if fill==np.nan:
            return np.nan
        
        return val

    
    def _find_base_time(self, messages):
        """
        Looks for the first proper timestamp to use as the starting base_time.
        """
        for messg in messages:
            if "timestamp" in messg.keys():
                base_time = messg["timestamp"]
                return base_time

        raise ValueError(f"Key 'timestamp' not found in the list.")

    def _parse_metric(self, file, metric,
                      datetimes, fill=None):
        """
        Checks if the datetime from the message list is present
        in the datetimes for the given metric.
        If it is, adds the metric value to the list.
        If it is not, fills the entry with np.nan.
        """
        metric_messages = file[FitParser._allowed_metrics[metric]]

        # Associate datetime to a value
        metric_records = {messg[FitParser._time_labels[metric]]:
                          messg[FitParser._value_labels[metric]]
                          for messg in metric_messages}

        if fill:
            metric_vals = []
            for dt in datetimes:
                val = metric_records.get(dt, np.nan)
                if val > 0:
                    metric_vals.append(val)
                else:
                    metric_vals.append(self._fill(val, fill))
            return metric_vals
            
        return [metric_records.get(dt, np.nan) for dt in datetimes]

    
    def _timezone_adjustment(self, datetimes, timezone):
        return [dt.astimezone(timezone) for dt in datetimes]
    
    def to_dataframe(self, add_metrics=None, add_state=False,
                     fill=None, timezone="UTC", **read_kwargs):
        """
        Creates a dataframe from .fit data suitable for
        data analysis.
        
        Parameters:
        ---------------------------------------------
        add_metrics: list[str] | None
            The list of columns to include in the DataFrame.
            'datetime' and 'heart_rate' as the base PPG metric
            are always included.
            The options are 'stress_level' and 'respiration_rate'.
            If None, the 'heart_rate' is the only represented metrics.
        
        add_state: Bool
            Adds the column which specifies the activity_type at
            all times, e.g. 'sedentary', 'walking'.

        fill: None | np.nan | {to be implemented: 'connect'}
            When choosing the other two columns choose the
            strategy for interpolating the missing data.
            
            Defaults to None. Missing data is given by 0
            for 'heart_rate', -1 for 'respiration_rate',
            and -2 for 'stress_level'.
            np.nan: Modifies invalid values to np.nan.
            {connect}: Fills with the last valid value. If
            there is none fills with np.nan.


        Returns:
        ----------------------------------------------
        DataFrame where the first column are calculated
        dates and times of records. The other columns are
        determined by the 'add_metrics' parameter.
        """

        if add_metrics is None:
            metrics = ['heart_rate']
        else:
            invalid = set(add_metrics) - set(FitParser._allowed_metrics.keys())
            if invalid:
                raise KeyError(f"Invalid metric(s) requested: {invalid}")
            metrics = ['heart_rate']+add_metrics

        # Merge datetime and metrics dictionaries into one:
        data = {"datetime":[], "heart_rate":[]}
        if add_metrics:
            data = {**data, **{metric:[] for metric in add_metrics}}
        if add_state:
            data = {**data, **{"activity_type":[]}}

        for file in self._parse_entry(**read_kwargs):
            # The heart rate is treated separately since it also
            # provides datetimes that other columns are based on
            if FitParser._allowed_metrics['heart_rate'] in file.keys():

                datetimes, heart_rates, states = self._parse_hr(file, fill=fill,
                                                        add_state=add_state)

                data['datetime'].extend(datetimes)
                data['heart_rate'].extend(heart_rates)
                
                if add_state:
                    data['activity_type'].extend(states)
            
            if add_metrics:
                for metric in add_metrics:
                    if FitParser._allowed_metrics[metric] in file.keys():

                        metric_vals = self._parse_metric(file, metric,
                                                         datetimes, fill=fill)
                        data[metric].extend(metric_vals)

        
        if timezone!='UTC': 
            data['datetime']=self._timezone_adjustment(data['datetime'],
                                                        timezone=pytz.timezone(timezone))

        fit_df = pd.DataFrame(data)
        self.metrics = metrics
            
        return fit_df

    def to_numpy(self, add_metrics=None, add_state=False,
                 fill=None, timezone="UTC", **read_kwargs):
        """
        Creates the DataFrame using the .to_dataframe method.
        Converts the DataFrame into the NumPy array.
        """

        fit_df = self.to_dataframe(add_metrics=add_metrics, add_state=add_state,
                                   fill=fill, timezone=timezone, **read_kwargs)
        
        return fit_df.to_numpy()

    def _convert_garmin_to_real(self, base_time, timestamp_16):
        """
        Arguments:
        -------------------------------------------------------
        base_time is a datetime object provided occasionally by
        the message in the .fit file.
        
        timestamp_16 is a 2 byte unsigned integer that
        represents the lower two bytes of the Garmin timestamp.
        This is the usual format used for memory efficiency.
        
        The Garmin time is calculated with respect to the
        data and time that is ~20yrs after the UNIX time.

        Returns:
        -------------------------------------------------------
        The datetime object calculated for the particular timezone 
        """
        
        timestamp_unix = int(datetime.datetime.timestamp(base_time))
        timestamp_garmin = timestamp_unix - UNIX_GARMIN_DIFF

        timestamp_garmin_low16 = timestamp_garmin & 0xffff

        message_timestamp = timestamp_garmin
        message_timestamp += (timestamp_16-timestamp_garmin_low16) & 0xffff

        message_timestamp_unix = message_timestamp + UNIX_GARMIN_DIFF
    
        try: 
            return datetime.datetime.fromtimestamp(message_timestamp_unix,
                                                   tz=pytz.timezone('UTC'))
        
        except OverflowError:
            return None
