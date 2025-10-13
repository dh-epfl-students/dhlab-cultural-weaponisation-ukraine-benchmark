from dataset import load_fg_w2
from dataset import load_LLM_results
from implementation import extract_after, generate_ngrams, check_global
from pathlib import Path
import pandas as pd

def main():

    dfs_weaponised = load_LLM_results()

    print(len(dfs_weaponised))

if __name__ == "__main__":
    main()

"""
from pathlib import Path
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent
data_path = root_dir / "datas" / "interim" / "fg_w2_after_json_text.csv"

fg_w2_after_json_text = pd.read_csv(data_path)
"""