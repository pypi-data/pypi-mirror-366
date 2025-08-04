import pandas as pd
import numpy as np
from ..io.parser_utils import parse_epw_with_nans

TO_DROP = [
            'Data Source and Uncertainty Flags',
            'Global Horizontal Illuminance',
            'Present Weather Observation',
            'Present Weather Codes',
            'Days Since Last Snowfall',
            'Liquid Precipitation Quantity'
        ]

class DataLoaderEPW:
    """
    Load and align EPW weather files by filling columns that are entirely NaN
    in one DataFrame with the corresponding column from the other.
    """
    def __init__(self, ref_path: str, stn_path: str):
        self.reference, self.header_reference = parse_epw_with_nans(ref_path)
        self.station, self.header_station = parse_epw_with_nans(stn_path)

        # Align station to reference's structure/units/etc.
        self.reference = self._canonical_hourly_df_from_epw(self.reference)
        self.station   = self._canonical_hourly_stn_from_ref(self.station, self.reference)
        
        self._fill_mutual_nan_columns()

    def _canonical_hourly_df_from_epw(self, df: pd.DataFrame) -> pd.DataFrame:
        # Build hourly grid and canonical time cols from EPW components
        df = df.copy()
        df["Hour"] = df["Hour"] - 1  # to 0-based for datetime
        dt = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
        target_index = pd.date_range(start=dt.min().floor("h"), end=dt.max().ceil("h"), freq="h")
    
        df = df.assign(datetime=dt).set_index("datetime")
        hourly = df.resample("h").first().reindex(target_index)
    
        hourly["Year"] = hourly.index.year
        hourly["Month"] = hourly.index.month
        hourly["Day"] = hourly.index.day
        hourly["Hour"] = hourly.index.hour + 1  # back to EPW 1..24
        hourly["Minute"] = hourly.index.minute
    
        return hourly.reset_index(drop=True)
    
    def _canonical_hourly_stn_from_ref(self, df_stn: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
        """
        Resample station to the exact hourly span of df_ref and rebuild its time columns.
        """
        # Derive reference grid
        ref = df_ref.copy()
        ref["Hour"] = ref["Hour"] - 1
        ref_dt = pd.to_datetime(ref[["Year", "Month", "Day", "Hour", "Minute"]])
        target_index = pd.date_range(start=ref_dt.min().floor("h"), end=ref_dt.max().ceil("h"), freq="h")
    
        # Station: resample/reindex to that grid
        stn = df_stn.copy()
        stn["Hour"] = stn["Hour"] - 1
        stn_dt = pd.to_datetime(stn[["Year", "Month", "Day", "Hour", "Minute"]])
        stn = stn.assign(datetime=stn_dt).set_index("datetime")
        hourly = stn.resample("h").first().reindex(target_index)
    
        # Rebuild EPW time columns
        hourly["Year"] = hourly.index.year
        hourly["Month"] = hourly.index.month
        hourly["Day"] = hourly.index.day
        hourly["Hour"] = hourly.index.hour + 1
        hourly["Minute"] = hourly.index.minute
    
        return hourly.reset_index(drop=True)

    def _fill_mutual_nan_columns(self) -> None:
        """
        For columns that are all-NaN in one DataFrame but not in the other,
        copy the non-NaN column over.
        """
        ref = self.reference.drop(columns=TO_DROP, errors='ignore')
        stn = self.station.drop(columns=TO_DROP, errors='ignore')


        ref_all_nan = {c for c in ref.columns if ref[c].isna().all()}
        stn_all_nan = {c for c in stn.columns if stn[c].isna().all()}

        # Columns missing in reference but present in station
        for col in ref_all_nan - stn_all_nan:
            ref[col] = stn[col]

        # Columns missing in station but present in reference
        for col in stn_all_nan - ref_all_nan:
            stn[col] = ref[col]

        # Assign back in case references need to stay consistent
        self.reference = ref
        self.station = stn



class TimeFeatures:
    """
    Add cyclical time-based features.
    """
    @staticmethod
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        ts = pd.to_datetime({
            'year': df['Year'], 'month': df['Month'], 'day': df['Day'],
            'hour': df['Hour'] - 1
        })
        doy = ts.dt.dayofyear
        hod = ts.dt.hour
        season = ((ts.dt.month % 12) // 3).astype(int)
        df['season'], df['doy'], df['hod'] = season, doy, hod
        df['season_sin'], df['season_cos'] = np.sin(2*np.pi*season/4), np.cos(2*np.pi*season/4)
        df['doy_sin'], df['doy_cos'] = np.sin(2*np.pi*doy/365.25), np.cos(2*np.pi*doy/365.25)
        df['hod_sin'], df['hod_cos'] = np.sin(2*np.pi*hod/24), np.cos(2*np.pi*hod/24)
        return df

class WindTransformer:
    """
    Encode/decode wind direction and u/v components.
    All methods accept `drop=True` (default) to remove the source columns used in the transformation.
    """
    @staticmethod
    def encode_direction(df: pd.DataFrame, direction_col: str = "Wind Direction", drop: bool = True) -> pd.DataFrame:
        df = df.copy()
        rad = np.deg2rad(df[direction_col].astype(float))
        df["wind_dir_sin"] = np.sin(rad)
        df["wind_dir_cos"] = np.cos(rad)
        if drop:
            df = df.drop(columns=[direction_col])
        return df

    @staticmethod
    def decode_direction(df: pd.DataFrame, sin_col: str = "wind_dir_sin", cos_col: str = "wind_dir_cos", drop: bool = True) -> pd.DataFrame:
        df = df.copy()
        rad = np.arctan2(df[sin_col], df[cos_col])
        deg = (np.rad2deg(rad) + 360) % 360
        df["Wind Direction"] = deg.round().astype("int64")
        if drop:
            df = df.drop(columns=[sin_col, cos_col])
        return df

    @staticmethod
    def encode_uv(
        df: pd.DataFrame,
        speed: str = "Wind Speed",
        direction: str = "Wind Direction",
        drop: bool = True,
    ) -> pd.DataFrame:
        df = df.copy()
        theta = np.deg2rad(df[direction].astype(float))
        spd = df[speed].astype(float)
        df["u_wind"] = -spd * np.sin(theta)
        df["v_wind"] = -spd * np.cos(theta)
        if drop:
            df = df.drop(columns=[speed, direction])
        return df

    @staticmethod
    def decode_uv(
        df: pd.DataFrame,
        u_col: str = "u_wind",
        v_col: str = "v_wind",
        drop: bool = True,
    ) -> pd.DataFrame:
        df = df.copy()
        u = df[u_col].astype(float)
        v = df[v_col].astype(float)
        df["Wind Speed"] = np.hypot(u, v)
        deg = (np.rad2deg(np.arctan2(-u, -v)) + 360) % 360
        df["Wind Direction"] = deg.round().astype("int64")
        if drop:
            df = df.drop(columns=[u_col, v_col])
        return df

class SignedDerivatives:
    """
    Add signed left/right derivative features.
    """
    @staticmethod
    def add(df: pd.DataFrame, cols: list) -> pd.DataFrame:
        df = df.copy(); df.sort_index(inplace=True)
        for c in cols:
            if c in df.columns:
                left = df[c] - df[c].shift(1)
                right = df[c].shift(-1) - df[c]
                df[f'{c}_ld'] = np.sign(left).fillna(0).astype(np.int8)
                df[f'{c}_rd'] = np.sign(right).fillna(0).astype(np.int8)
        return df