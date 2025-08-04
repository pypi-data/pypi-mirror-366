import typer
from sglabtools import run_pipeline

app = typer.Typer(help="""
SGLab-tools 🧬

Un outil professionnel de comparaison de génomes permettant :
- Alignement pair-à-pair de génomes avec minimap2
- Extraction et classification des différences (SNPs, InDels, gaps, N)
- Application de masques à partir de fichiers BED
- Comptage des scénarios de variation
- Fusion et comparaison multi-génomes
- Enrichissement des résultats et visualisation graphique

Développé par Etienne Ntumba Kabongo (Université de Montréal)
Sous la direction de :
- Prof. Dr. Simon Grandjean Lapierre
- Prof. Dr. Martin Smith

Exemples d’usage :
$ sglab run sample.txt                            # Exécute tout le pipeline
$ sglab count --input fichier.tsv                 # Compte les scénarios sur un fichier TSV
$ sglab mask --input fichier.tsv --ref REF.bed --query L1.bed
$ sglab merge                                     # Fusionne les fichiers de scénarios
$ sglab plot --input fichier.csv --output-prefix nom --fig bar,heat   # Visualisation personnalisée
""")

@app.command("run")
def run_pipeline_cmd(sample_file: str = typer.Argument(..., help="Fichier TSV contenant les paires Ref / Lx")):
    """Lancer le pipeline complet (alignement + transformation + masque + comptage + fusion)"""
    run_pipeline.run_all(sample_file)

@app.command("mask")
def mask_cmd(
    input: str = typer.Option(..., "--input", help="Fichier TSV des différences initiales"),
    ref: str = typer.Option(..., "--ref", help="Fichier BED de la souche de référence"),
    query: str = typer.Option(..., "--query", help="Fichier BED de la souche comparée")
):
    """Appliquer les masques BED à un fichier de différences"""
    from sglabtools.mask import apply_mask
    apply_mask(input, ref, query)

@app.command("count")
def count_cmd(input: str = typer.Option(..., "--input", help="Fichier TSV de différences masquées")):
    """Compter les scénarios de variation à partir d’un fichier TSV"""
    from sglabtools.count import count_scenarios
    count_scenarios(input)

@app.command("merge")
def merge_cmd():
    """Fusionner tous les fichiers de scénarios en un seul tableau comparatif"""
    from sglabtools.merge import merge_counts
    merge_counts()

@app.command("plot")
def plot_cmd(
    input: str = typer.Option("combined_scenarios_augmented.csv", "--input", help="Fichier CSV en entrée (par défaut: combined_scenarios_augmented.csv)"),
    output_prefix: str = typer.Option("scenarios", "--output-prefix", help="Préfixe des fichiers de sortie (.csv, .png, etc.)"),
    fig: str = typer.Option("bar,heat", "--fig", help="Type de figures à générer: bar, heat ou les deux (ex: --fig bar,heat)")
):
    """
    Enrichit la table de scénarios fusionnée :
    - Ajoute les colonnes 'Description' et 'Total'
    - Exporte les fichiers .csv / .tsv / .xlsx
    - Génère un barplot comparatif et/ou une heatmap de divergence
    """
    from sglabtools.augment import augment_table
    from sglabtools.plot import plot_scenarios

    df = augment_table(input_file=input, output_prefix=output_prefix)
    plot_scenarios(input_file=f"{output_prefix}.csv", output_prefix=output_prefix, fig_types=fig.split(","))

if __name__ == "__main__":
    app()
