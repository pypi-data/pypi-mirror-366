import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.style.use('ggplot')

def plot_scenarios(input_file="combined_scenarios_augmented.csv", output_prefix="scenarios", fig_types=["bar", "heat"]):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"❌ Fichier introuvable : {input_file}")

    df = pd.read_csv(input_file)

    if "bar" in fig_types:
        # 🔹 Barplot multi-souche
        df_bar = df.set_index("Scenario").drop(columns=["Description", "Total"], errors="ignore").T
        df_bar.plot(kind="bar", figsize=(12, 6))
        plt.title("Comparaison des scénarios entre souches")
        plt.xlabel("Souche")
        plt.ylabel("Nombre de cas")
        plt.tight_layout()
        bar_path = f"{output_prefix}_barplot.png"
        plt.savefig(bar_path)
        print(f"✅ Barplot sauvegardé : {bar_path}")
        plt.close()

    if "heat" in fig_types:
        # 🔸 Heatmap de divergence
        df_heat = df.set_index("Scenario").drop(columns=["Description", "Total"], errors="ignore")
        plt.figure(figsize=(10, 6))
        sns.heatmap(df_heat.T, annot=True, fmt='g', cmap="coolwarm", cbar_kws={'label': 'Nombre de cas'})
        plt.title("Heatmap des scénarios de variation")
        plt.xlabel("Scénario")
        plt.ylabel("Souche")
        plt.tight_layout()
        heat_path = f"{output_prefix}_heatmap.png"
        plt.savefig(heat_path)
        print(f"✅ Heatmap sauvegardée : {heat_path}")
        plt.close()
