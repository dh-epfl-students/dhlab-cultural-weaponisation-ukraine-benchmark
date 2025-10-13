# ===============================
# Libraries and imports
# ===============================

import pandas as pd
import numpy as np
import os
from pathlib import Path

# ===============================
# Functions
# ===============================

def load_LLM_results():
    
    csv_folder = Path("datas/raw/LLM_Results")

    dfs = [pd.read_csv(f) for f in csv_folder.glob("*.csv")]
    dfs_named = {f.stem: pd.read_csv(f) for f in csv_folder.glob("*.csv")}

    dfs_weaponised = [df[df['weaponised'] == 'Weaponised'].reset_index(drop=True) for df in dfs]

    dfs_weaponised = [df for df in dfs_weaponised if not df.empty]

    dfs_weaponised_named = {
        name: df[df['weaponised'] == 'Weaponised'].reset_index(drop=True)
        for name, df in dfs_named.items()
        if not df[df['weaponised'] == 'Weaponised'].empty
    }

    return dfs_weaponised

def load_fg_w2():

    finegrained_weaponisation2 = pd.read_csv("datas/raw/Finegrained_LLM/FG_W2/finegrained_weaponisation2.csv")

    return finegrained_weaponisation2

def load_any_csv(path):
    return pd.read_csv(path)

def update_csv(filename: str, df: pd.DataFrame) -> None:
    """
    Save the edited dataframe to the 'data/interim' folder.

    Parameters
    ----------
    filename : str
        Name of the file to save (e.g., 'fg_w2_after_json_text.csv')
    df : pd.DataFrame
        The dataframe you want to save.
    """
    # Resolve path to interim folder
    root_dir = Path(__file__).resolve().parents[1]
    interim_path = root_dir / "data" / "interim"
    interim_path.mkdir(parents=True, exist_ok=True)

    # Full file path
    full_path = interim_path / filename

    # Save dataframe
    df.to_csv(full_path, index=False, encoding="utf-8")

    print(f"✅ Saved updated data to: {full_path}")