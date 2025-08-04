import os
import pandas as pd
import re

def merge_counts():
    """
    Fusionne tous les fichiers de type scenarios_table_H37Rv_<SAMPLE>_mask.tsv
    en un seul fichier CSV combiné basé sur la colonne 'Scenario'.
    """
    pattern = r"scenarios_table_H37Rv_(.+)_mask\.tsv"
    files = [f for f in os.listdir('.') if re.fullmatch(pattern, f)]

    if not files:
        print("❌ Aucun fichier de scénarios trouvé à fusionner.")
        return

    merged_df = None
    for file in sorted(files):
        match = re.fullmatch(pattern, file)
        if not match:
            continue
        sample = match.group(1)
        try:
            df = pd.read_csv(file, sep='\t', usecols=["Scenario", "Count"])
            df.rename(columns={"Count": sample}, inplace=True)
        except Exception as e:
            print(f"⚠️ Erreur de lecture dans {file} : {e}")
            continue

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="Scenario", how="outer")

    if merged_df is not None and not merged_df.empty:
        output_file = "combined_scenarios_counts1.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"✅ Fichier fusionné sauvegardé : {output_file}")
    else:
        print("❌ Aucune donnée valide à fusionner.")
