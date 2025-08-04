import pandas as pd
import os

SCENARIO_DESCRIPTIONS = {
    "1️⃣ N/N": "N et N identiques",
    "2️⃣ base/gap": "Base (A/C/G/T) alignée sur gap (-)",
    "3️⃣ base/base": "Base alignée sur base",
    "4️⃣ gap/N": "Gap aligné sur N",
    "5️⃣ gap/base": "Gap aligné sur base",
    "6️⃣ N/base": "N aligné sur base",
    "7️⃣ base/N": "Base alignée sur N",
    "8️⃣ N/gap": "N aligné sur gap"
}

def augment_table(input_file="combined_scenarios_counts1.csv", output_prefix="combined_scenarios_augmented"):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"❌ Fichier introuvable : {input_file}")

    df = pd.read_csv(input_file)

    if "Scenario" not in df.columns:
        raise ValueError("❌ Le fichier ne contient pas de colonne 'Scenario'")

    # Ajouter colonnes Description et Total
    df["Description"] = df["Scenario"].map(SCENARIO_DESCRIPTIONS)
    cols_to_sum = df.columns.difference(["Scenario", "Description"])
    df["Total"] = df[cols_to_sum].sum(axis=1)

    # Export CSV, TSV, XLSX
    df.to_csv(f"{output_prefix}.csv", index=False)
    df.to_csv(f"{output_prefix}.tsv", index=False, sep="\t")
    df.to_excel(f"{output_prefix}.xlsx", index=False)

    print(f"✅ Fichiers exportés : {output_prefix}.csv / .tsv / .xlsx")
    return df
