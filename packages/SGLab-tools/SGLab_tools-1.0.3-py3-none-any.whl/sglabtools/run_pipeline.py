import os
from sglabtools import transform, mask, count, merge

def run_all(sample_file):
    """
    Exécution complète du pipeline pour chaque paire Ref vs Lx définie dans sample.txt
    Étapes :
    1. Vérification des fichiers .fasta
    2. Alignement avec minimap2
    3. Extraction des différences
    4. Application des masques
    5. Comptage des scénarios
    6. Fusion finale
    """
    with open(sample_file, 'r') as f:
        next(f)  # Ignorer l'entête
        for line in f:
            ref, lx = line.strip().split()
            print(f"\n🧬 Traitement : {ref} vs {lx}")
            ref_fa = f"{ref}.fasta"
            lx_fa = f"{lx}.fasta"
            if not os.path.exists(ref_fa) or not os.path.exists(lx_fa):
                print(f"❌ Fichier manquant : {ref_fa} ou {lx_fa}")
                continue

            # Étape 1 : Alignement
            paf_file = f"alignments_{ref}_{lx}.paf"
            os.system(f"minimap2 -x asm5 -c {ref_fa} {lx_fa} > {paf_file}")
            print(f"✅ Alignement produit : {paf_file}")

            # Étape 2 : Extraction des différences
            table = transform.paf_to_table(ref_fa, lx_fa, paf_file)

            # Étape 3 : Masquage BED
            masked = mask.apply_mask(table, f"{ref}.bed", f"{lx}.bed")

            # Étape 4 : Comptage des scénarios
            count.count_scenarios(masked)

    # Étape 5 : Fusion finale
    merge.merge_counts()
    print("\n📊 Fusion des scénarios complétée.")
