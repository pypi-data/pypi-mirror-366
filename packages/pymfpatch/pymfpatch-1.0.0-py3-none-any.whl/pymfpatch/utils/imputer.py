import torch
import numpy as np
import pandas as pd
from . import neuralnetwork as ntw
from torch import nn
from tqdm import tqdm
from pandas.api import types as pdt
from torch.utils.data import  DataLoader, Subset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .prepfile import DataLoaderEPW, TimeFeatures, WindTransformer, SignedDerivatives
from ..io.parser_utils import merge_header_on_ground_temperatures, format_epw_fields


EPW_COLS = [
    'Data Source and Uncertainty Flags',
    'Dry Bulb Temperature',
    'Dew Point Temperature',
    'Relative Humidity',
    'Atmospheric Station Pressure',
    'Extraterrestrial Horizontal Radiation',
    'Extraterrestrial Direct Normal Radiation',
    'Horizontal Infrared Radiation Intensity',
    'Global Horizontal Radiation',
    'Direct Normal Radiation',
    'Diffuse Horizontal Radiation',
    'Global Horizontal Illuminance',
    'Direct Normal Illuminance',
    'Diffuse Horizontal Illuminance',
    'Zenith Luminance',
    'Wind Direction',
    'Wind Speed',
    'Total Sky Cover',
    'Opaque Sky Cover',
    'Visibility',
    'Ceiling Height',
    'Present Weather Observation',
    'Present Weather Codes',
    'Precipitable Water',
    'Aerosol Optical Depth',
    'Snow Depth',
    'Days Since Last Snowfall',
    'Albedo',
    'Liquid Precipitation Depth',
    'Liquid Precipitation Quantity'
    'u_wind', 'v_wind'
    'wind_dir_sin', 'wind_dir_cos'
]

GRU_VARS = [
    'Dry Bulb Temperature', 'Dew Point Temperature', 'Relative Humidity',
    'Horizontal Infrared Radiation Intensity', 'Atmospheric Station Pressure',
    'wind_dir_sin', 'wind_dir_cos', 'u_wind', 'v_wind', 'Wind Speed',
    'Total Sky Cover', 'Opaque Sky Cover', 'Precipitable Water',
    'Aerosol Optical Depth', 'Snow Depth', 'Global Horizontal Radiation',
]

THRESHOLDS = {
    'Total Sky Cover': 0,
    'Opaque Sky Cover': 0,
    'Ceiling Height': 0,
    'Total Sky Cover': 0,
    'Opaque Sky Cover': 0,
    'Snow Depth': 0.1,
    'Relative Humidity': 0,
    'Global Horizontal Radiation': 0,
    'Liquid Precipitation Depth': 0.1,
}

class WeatherImputer:
    def __init__(
        self,
        path_to_ref: str,
        path_to_stn: str,
        gru_vars: list = GRU_VARS,
        gru_params: dict = ntw.GRU_PARAMS,
        xgb_params: dict = ntw.XGB_PARAMS,
        ground_temp_tol:float = 1.5
    ):

        self.GRU_PARAMS = gru_params
        self.XGB_PARAMS = xgb_params
        self.GRU_VARS = gru_vars
        self.tolerance = ground_temp_tol
       
        self.loader = DataLoaderEPW(path_to_ref, path_to_stn)
        self.result = None

    def _prepare_features(self):
        X = self.loader.reference.copy()
        Y = self.loader.station.copy()
        
        # WIND
        X = WindTransformer.encode_uv(X)
        Y = WindTransformer.encode_uv(Y)
        
        # CLEAN COLUM%NS
        common_cols = set(X.columns) & set(Y.columns)
        identical_columns = [c for c in common_cols if Y[c].equals(X[c])]
        Y = Y.drop(columns=identical_columns, errors = "ignore")

        unusable_cols = X.columns[X.isna().any()].tolist()
        X = X.drop(columns=unusable_cols, errors = "ignore")
        X = SignedDerivatives.add(X, EPW_COLS)
        X = TimeFeatures.apply(X)
        
        overlap = [c for c in X.columns if c in Y.columns]
        if not overlap:
            raise ValueError("No overlapping columns to compute residual.")
        
        # Compute residual on overlapping columns
        residual = Y[overlap].subtract(X[overlap], axis=0)
        
        # Start from Y and replace the overlap with the residual
        Ydiff = Y.copy()
        Ydiff.loc[:, overlap] = residual
        return X, Ydiff
        
    def _post_features(self, Ypred):
        if self.result is None:
            self.result = self.loader.station.copy()
        # WIND
        if ("u_wind" in Ypred.columns) and ("v_wind" in Ypred.columns):
            Ypred = WindTransformer.decode_uv(Ypred)
        
        for c in Ypred.columns:
            if c not in self.result.columns:
                continue  # nothing to match against
        
            target_dtype = self.result[c].dtype
        
            if pdt.is_integer_dtype(target_dtype) or str(target_dtype).startswith("Int"):
                # round then cast; if df0 uses pandas nullable Int64, preserve that
                Ypred[c] = Ypred[c].round()
            Ypred[c] = Ypred[c].astype(target_dtype)
        
        
        for col in self.result.columns.intersection(Ypred.columns):
            mask = self.result[col].isna()
            self.result.loc[mask, col] = Ypred.loc[mask, col]
        
        return self.result
    
    def _gru_model(self):
        # prepare for imputation
        X, Y = self._prepare_features()
        gru_var = [v for v in Y.columns if v in self.GRU_VARS]
    
        SEQ_LEN = self.GRU_PARAMS["seq_len"]
        BATCH_SIZE = self.GRU_PARAMS["batch_size"]
        device = self.GRU_PARAMS["device"]
    
        X_gru, Y_gru = X.copy(), Y[gru_var].copy()
        x_s = StandardScaler().fit(X_gru)
        Xs = pd.DataFrame(x_s.transform(X_gru), index=X_gru.index, columns=X_gru.columns)
        y_s = StandardScaler().fit(Y_gru)
        Ys = pd.DataFrame(y_s.transform(Y_gru), index=Y_gru.index, columns=Y_gru.columns)
    
        ds = ntw.WeatherSequenceDataset(Xs, Ys, SEQ_LEN)
    
        positions = list(range(len(ds)))
        train_pos, val_pos = train_test_split(
            positions,
            test_size=self.GRU_PARAMS["split_validation"],
            random_state=self.GRU_PARAMS["seed"],
        )
        train_loader = DataLoader(
            Subset(ds, train_pos),
            batch_size=BATCH_SIZE,
            shuffle=True,
        )
        val_loader = DataLoader(
            Subset(ds, val_pos),
            batch_size=BATCH_SIZE,
            shuffle=False,
        )
    
        gru_model = ntw.GRUImputer(
            in_dim=Xs.shape[1],
            out_dim=Ys.shape[1],
            hidden=self.GRU_PARAMS["hidden"],
            dropout=self.GRU_PARAMS["dropout"],
        ).to(device)
    
        optimizer = torch.optim.AdamW(
            gru_model.parameters(),
            lr=self.GRU_PARAMS["lr"],
            weight_decay=self.GRU_PARAMS["weight_decay"],
        )
        loss_fn = nn.L1Loss()
        stopper = ntw.EarlyStopping(
            patience=self.GRU_PARAMS["early_stopping_patience"],
            delta=self.GRU_PARAMS["early_stopping_delta"],
        )
    
        for epoch in range(1, self.GRU_PARAMS["epochs"] + 1):
            gru_model.train()
            train_losses = []
            for xb, yb in tqdm(train_loader, desc=f"Epoch {epoch} [train]"):
                xb, yb = xb.to(device), yb.to(device)
                optimizer.zero_grad()
                pred = gru_model(xb)
                loss = loss_fn(pred, yb)
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())
            avg_train = np.mean(train_losses)
    
            gru_model.eval()
            val_losses = []
            with torch.no_grad():
                for xb, yb in val_loader:
                    xb, yb = xb.to(device), yb.to(device)
                    val_losses.append(loss_fn(gru_model(xb), yb).item())
            avg_val = np.mean(val_losses)
            print(f"Epoch {epoch} - train MAE: {avg_train:.4f}, val MAE: {avg_val:.4f}")
    
            stopper(avg_val)
            if stopper.should_stop:
                print(f"Early stopping at epoch {epoch}")
                break
    
        # GRU Inference
        Xn = Xs.values.astype(np.float32)
        if device == "cuda":
            torch.cuda.empty_cache()
            indices = np.arange(SEQ_LEN - 1, len(Xn))
            batch_size_inf = BATCH_SIZE
            preds = []
            with torch.no_grad():
                for i in range(0, len(indices), batch_size_inf):
                    batch_idx = indices[i : i + batch_size_inf]
                    seqs = [Xn[j - SEQ_LEN + 1 : j + 1] for j in batch_idx]
                    xb = torch.from_numpy(np.stack(seqs)).to(device)
                    out = gru_model(xb)
                    preds.append(out.cpu().numpy())
            pred_scaled = np.vstack(preds)
        else:
            gru_model.eval()
            with torch.no_grad():
                arr = []
                for i in range(SEQ_LEN - 1, len(Xn)):
                    arr.append(Xn[i - SEQ_LEN + 1 : i + 1])
                stacked = torch.from_numpy(np.stack(arr)).to(device)
                pred_scaled = gru_model(stacked).cpu().numpy()
    
        # reverse scaling
        diffs = pd.DataFrame(
            y_s.inverse_transform(pred_scaled),
            columns=Ys.columns,
            index=Xs.index[SEQ_LEN - 1 :],
        )
        full_diff = pd.concat(
            [
                pd.DataFrame(
                    np.zeros((SEQ_LEN - 1, len(Ys.columns))),
                    columns=Ys.columns,
                    index=Xs.index[: SEQ_LEN - 1],
                ),
                diffs,
            ]
        )
    
        # apply imputation: for each GRU variable, if it's also in X, add the diff; else, take the diff as the imputed value
        imputed_gru = pd.DataFrame(index=X.index, columns=Ys.columns, dtype=float)
        for col in full_diff.columns:
            if col in X.columns:
                imputed_gru[col] = X[col] + full_diff[col]
            else:
                imputed_gru[col] = full_diff[col]
    
        self._post_features(imputed_gru)

    def _xgb_model(self):
        # XGB Imputation
        X, Y = self._prepare_features()
        xgb_vars = [c for c in Y.columns if c not in self.GRU_VARS]
        
        Y = Y[xgb_vars]
        _Xmaj_ = self.result[[c for c in self.result.columns if c in X.columns and c not in Y.columns]]
        X.update(_Xmaj_)
        
        for var in Y.columns:
            y_var = Y[var]
            X_comp = X.loc[y_var.notna()]; Y_comp = y_var.dropna().to_frame()
            X_part = X.loc[y_var.isna()]    
            sc = StandardScaler().fit(X_comp)
            Xc_s = pd.DataFrame(sc.transform(X_comp), index=X_comp.index, columns=X_comp.columns)
            Xp_s = pd.DataFrame(sc.transform(X_part), index=X_part.index, columns=X_part.columns)
            imp = ntw.XGBImputer(self.XGB_PARAMS)
            imp.fit(Xc_s, Y_comp)
            p = imp.predict(Xp_s)
            if var in THRESHOLDS: p[var]=p[var].mask(p[var]<THRESHOLDS[var],0)
            dt=self.result[var].dtype
            if pdt.is_integer_dtype(dt): p[var]=p[var].round().astype(dt)
            self.result.loc[p.index,var]=p[var]

    def _post_process(self):
        # Final adjustments
        for c,t in THRESHOLDS.items(): self.result[c]=self.result[c].mask(self.result[c]<t,0)
        self.result['Data Source and Uncertainty Flags']='*?*?*?*?*?*?*?*?*?*?*?*?*'
        self.result['Global Horizontal Illuminance']=110*self.result['Global Horizontal Radiation']
        self.result['Direct Normal Illuminance']=105*self.result['Direct Normal Radiation']
        self.result['Diffuse Horizontal Illuminance']=119*self.result['Diffuse Horizontal Radiation']
        self.result['Present Weather Observation']=0
        self.result['Present Weather Codes']=999999999
        self.result['Liquid Precipitation Quantity']=1
        # Days since last snowfall
        dt = pd.to_datetime(
            self.result['Year'].astype(str).str.zfill(4)
            + self.result['Month'].astype(str).str.zfill(2)
            + self.result['Day'].astype(str).str.zfill(2)
            + (self.result['Hour']-1).astype(str).str.zfill(2)
            + self.result['Minute'].astype(str).str.zfill(2),
            format='%Y%m%d%H%M'
        )
        mask = self.result['Snow Depth']>0
        last = dt.where(mask).ffill().fillna(dt.iloc[0]-pd.Timedelta(days=1))
        self.result['Days Since Last Snowfall']=(dt-last).dt.days
    
        # Sort from past to present before writing
        self.result.sort_values(
            by=['Year','Month','Day','Hour','Minute'],
            inplace=True
        )
    
        # Merge with a 1.5°C tolerance
        self.new_header_station = merge_header_on_ground_temperatures(self.loader.header_station, self.loader.header_reference, tolerance = self.tolerance)
        self.result = format_epw_fields(self.result)

    def process(self):
        print("-------------- start --------------")
        print("... use GRU for temporal prediction")
        self._gru_model()
        print("... use XGB for regression")
        self._xgb_model()
        print("... post-processing")
        self._post_process()
        print("--------------- end ---------------")

    def write(self, opath:str = 'imputed_weather.epw'):
        with open(opath, 'w', encoding='utf-8', newline='') as f:
            # write header block as-is
            f.write(self.new_header_station)
            f.write('\n')
            # write data rows without pandas header, avoid extra blank lines
            self.result.to_csv(f, index=False, header=False)
    
        print(f'Imputed weather saved to {opath}')