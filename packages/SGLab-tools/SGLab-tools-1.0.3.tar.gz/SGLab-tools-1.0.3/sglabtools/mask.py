def load_bed_intervals(bed_file):
    intervals = []
    with open(bed_file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            start, end = int(parts[1]), int(parts[2])
            intervals.append((start + 1, end))
    return intervals

def is_masked(position, intervals):
    return any(start <= position <= end for (start, end) in intervals)

def apply_mask(differences_file, bed_ref, bed_query):
    output_file = differences_file.replace(".tsv", "_mask.tsv")
    ref_intervals = load_bed_intervals(bed_ref)
    query_intervals = load_bed_intervals(bed_query)
    with open(differences_file) as fin, open(output_file, 'w') as fout:
        fout.write(fin.readline().strip() + "\n")
        for line in fin:
            fields = line.strip().split('\t')
            if len(fields) != 4:
                continue
            pos = int(fields[0])
            base_ref = fields[2]
            base_query = fields[3]
            if is_masked(pos, ref_intervals): base_ref = "N"
            if is_masked(pos, query_intervals): base_query = "N"
            fout.write(f"{pos}\t{fields[1]}\t{base_ref}\t{base_query}\n")
    print(f"✅ Fichier masqué généré : {output_file}")
    return output_file
