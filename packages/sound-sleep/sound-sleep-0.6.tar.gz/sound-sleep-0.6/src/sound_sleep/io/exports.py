import pandas as pd

def save_feature_dicts_to_csv(feature_dicts, output_path):
    df = pd.DataFrame(feature_dicts)
    df.to_csv(output_path, index=False)