# 🧬 SGLab-tools

[![PyPI version](https://img.shields.io/pypi/v/SGLab-tools.svg?color=blue&logo=python&label=PyPI)](https://pypi.org/project/SGLab-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/source-GitHub-black?logo=github)](https://github.com/EtienneNtumba/SGLab-tools)

---

## 🧠 Présentation

**SGLab-tools** est un outil en ligne de commande modulaire et reproductible pour l’analyse comparative de génomes. Il permet de détecter, classifier, filtrer et visualiser les différences nucléotidiques entre des génomes de souches bactériennes (ex. *Mycobacterium tuberculosis*) ou autres organismes.

> 🧑‍💻 Développé par **Etienne Ntumba Kabongo**  
> 🎓 Sous la supervision de **Pr. Simon Grandjean Lapierre** et **Pr. Martin Smith**  
> 🧬 Laboratoires de Simon GrandJEAN LAPIERRE, CRCHUM, Université de Montréal 

---

## 🧠 Fonctionnalités

- 🔁 Alignement pair-à-pair de génomes avec `minimap2`
- 🧬 Extraction automatique des différences (SNPs, gaps, insertions, N)
- 🛡️ Application de masques BED pour ignorer les régions peu fiables
- 📊 Comptage de scénarios évolutifs (8 types)
- 📁 Fusion multi-souches automatique
- 📈 Génération de visualisations (barplots, heatmaps)
- 📄 Exports enrichis : `.csv`, `.tsv`, `.xlsx` avec colonnes `Description`, `Total`
- ⚡ Interface CLI intuitive avec `typer`
- 🔹 Options personnalisables pour `sglab plot` : `--input`, `--output-prefix`, `--fig bar,heat`

---

## 📦 Installation

### Depuis PyPI (recommandé)

```bash
pip install SGLab-tools
```

### Depuis GitHub

```bash
git clone https://github.com/EtienneNtumba/SGLab-tools.git
cd SGLab-tools
pip install .
```

### Prérequis

- Python ≥ 3.8
- Outils externes : [`minimap2`](https://github.com/lh3/minimap2)
- Librairies Python : `typer`, `pandas`, `biopython`, `matplotlib`, `seaborn`, `openpyxl`

---

## 📂 Exemple d'utilisation

### 1. Préparer un fichier `sample.txt` :

```
Ref     L_x
H37Rv   L1
H37Rv   L2
H37Rv   L5
```

Ce fichier définit les comparaisons entre génomes de référence et cibles.

Les fichiers suivants doivent être présents dans le répertoire de travail :

- Séquences : `H37Rv.fasta`, `L1.fasta`, ...
- Masques : `H37Rv.bed`, `L1.bed`, ...

---

### 2. Lancer le pipeline complet

```bash
sglab run sample.txt
```

Génère :

- `*.paf` : alignement
- `*.tsv` : différences
- `*_mask.tsv` : différences filtrées
- `scenarios_table_*.tsv` : scénarios classés
- `combined_scenarios_counts1.csv` : fusion multi-souches

---

### 3. Visualiser et exporter

```bash
sglab plot --input combined_scenarios_counts1.csv --output-prefix resultats --fig bar,heat
```

Résultats :

- `resultats.csv/.tsv/.xlsx`
- `resultats_barplot.png`
- `resultats_heatmap.png`

---

## 🧲 Scénarios détectés

| Code | Scénario     | Description                       |
|------|--------------|-----------------------------------|
| 1️⃣   | N / N        | N et N identiques                 |
| 2️⃣   | base / gap   | Base alignée sur un gap           |
| 3️⃣   | base / base  | Base alignée sur base             |
| 4️⃣   | gap / N      | Gap aligné sur N                  |
| 5️⃣   | gap / base   | Gap aligné sur base               |
| 6️⃣   | N / base     | N aligné sur base                 |
| 7️⃣   | base / N     | Base alignée sur N                |
| 8️⃣   | N / gap      | N aligné sur gap                  |

---

## 💻 Interface CLI (`sglab --help`)

```
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
$ sglab plot --input input.csv --output-prefix figs --fig bar,heat  # Visualisation flexible

Commandes disponibles :
  run     Lancer le pipeline complet
  mask    Appliquer des masques BED
  count   Compter les scénarios
  merge   Fusionner les résultats
  plot    Générer graphiques et exports enrichis
```

---

## 📜 Licence

Ce projet est distribué sous licence [MIT](https://opensource.org/licenses/MIT).

---

## 🙏 Remerciements

Ce projet a été réalisé dans le cadre d’une étude sur la diversité génomique de *Mycobacterium tuberculosis*, au sein du laboratoire du Pr. Simon Grandjean Lapierre et du Pr. Martin Smith. Il vise à proposer un outil reproductible pour l’analyse comparative des génomes bactériens.

---

## 🔗 Liens utiles

- 🔗 [GitHub Repository](https://github.com/EtienneNtumba/SGLab-tools)
- 🛆 [Page PyPI](https://pypi.org/project/SGLab-tools/)
- 🧬 [minimap2](https://github.com/lh3/minimap2)
- 🧪 [Biopython](https://biopython.org/)
- ⚙️ [Typer CLI](https://typer.tiangolo.com/)
