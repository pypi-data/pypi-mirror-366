import pandas as pd

def count_scenarios(input_file):
    df = pd.read_csv(input_file, sep='\t')
    col_h37rv = df.iloc[:, 2].astype(str).str.upper()
    col_lx = df.iloc[:, 3].astype(str).str.upper()
    valid_bases = {"A", "C", "G", "T"}
    counts = {
        "1️⃣ N/N": 0, "2️⃣ base/gap": 0, "3️⃣ base/base": 0, "4️⃣ gap/N": 0,
        "5️⃣ gap/base": 0, "6️⃣ N/base": 0, "7️⃣ base/N": 0, "8️⃣ N/gap": 0
    }

    for b1, b2 in zip(col_h37rv, col_lx):
        if b1 == "N" and b2 == "N": counts["1️⃣ N/N"] += 1
        elif b1 in valid_bases and b2 == "-": counts["2️⃣ base/gap"] += 1
        elif b1 in valid_bases and b2 in valid_bases: counts["3️⃣ base/base"] += 1
        elif b1 == "-" and b2 == "N": counts["4️⃣ gap/N"] += 1
        elif b1 == "-" and b2 in valid_bases: counts["5️⃣ gap/base"] += 1
        elif b1 == "N" and b2 in valid_bases: counts["6️⃣ N/base"] += 1
        elif b1 in valid_bases and b2 == "N": counts["7️⃣ base/N"] += 1
        elif b1 == "N" and b2 == "-": counts["8️⃣ N/gap"] += 1

    sample = input_file.split("_")[-2]
    df_out = pd.DataFrame({
        "Scenario": list(counts.keys()),
        "Count": list(counts.values())
    })
    output = f"scenarios_table_H37Rv_{sample}_mask.tsv"
    df_out.to_csv(output, sep='\t', index=False)
    print(f"✅ Résultats enregistrés dans {output}")
    return output
