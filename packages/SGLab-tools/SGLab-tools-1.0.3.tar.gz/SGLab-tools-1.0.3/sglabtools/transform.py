from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import os

def parse_fasta(fasta_path):
    return {record.id: str(record.seq) for record in SeqIO.parse(fasta_path, "fasta")}

def parse_paf(paf_file):
    blocks = []
    with open(paf_file) as f:
        for line in f:
            fields = line.strip().split('\t')
            qstart, qend = int(fields[7]), int(fields[8])
            tstart, tend = int(fields[2]), int(fields[3])
            strand = fields[4]
            blocks.append((qstart, qend, tstart, tend, strand))
    return sorted(blocks, key=lambda x: x[0])

def generate_alignment(query_seq, target_seq, blocks):
    aligned_q, aligned_t = [], []
    q_pos, t_pos = 0, 0
    for qstart, qend, tstart, tend, strand in blocks:
        gap_q = query_seq[q_pos:qstart]
        gap_t = target_seq[t_pos:tstart]
        max_len = max(len(gap_q), len(gap_t))
        aligned_q.append(gap_q.ljust(max_len, '-'))
        aligned_t.append(gap_t.ljust(max_len, '-'))
        aligned_q.append(query_seq[qstart:qend])
        aligned_t.append(target_seq[tstart:tend])
        q_pos = qend
        t_pos = tend
    tail_q = query_seq[q_pos:]
    tail_t = target_seq[t_pos:]
    max_len = max(len(tail_q), len(tail_t))
    aligned_q.append(tail_q.ljust(max_len, '-'))
    aligned_t.append(tail_t.ljust(max_len, '-'))
    return ''.join(aligned_q), ''.join(aligned_t)

def detect_differences(seq1, seq2, id1, id2, output):
    """Compare deux séquences alignées de même longueur ou non, et écrit les différences."""
    with open(output, "w") as out:
        out.write(f"Position\tType\t{id1}\t{id2}\n")
        ref_pos = 1
        max_len = max(len(seq1), len(seq2))
        for i in range(max_len):
            base1 = seq1[i] if i < len(seq1) else "-"
            base2 = seq2[i] if i < len(seq2) else "-"
            if base1 == base2:
                if base1 != "-":
                    out.write(f"{ref_pos}\tMatch\t{base1}\t{base2}\n")
                    ref_pos += 1
                else:
                    out.write(f"{ref_pos}\tUnaligned\t{base1}\t{base2}\n")
            else:
                if base1 == "-":
                    out.write(f"{ref_pos}\tInsertion\t{base1}\t{base2}\n")
                elif base2 == "-":
                    out.write(f"{ref_pos}\tDeletion\t{base1}\t{base2}\n")
                    ref_pos += 1
                else:
                    out.write(f"{ref_pos}\tSNP\t{base1}\t{base2}\n")
                    ref_pos += 1

def paf_to_table(ref_fasta, query_fasta, paf_file):
    ref_dict = parse_fasta(ref_fasta)
    query_dict = parse_fasta(query_fasta)
    ref_id = list(ref_dict.keys())[0]
    query_id = list(query_dict.keys())[0]
    ref_seq = ref_dict[ref_id]
    query_seq = query_dict[query_id]
    blocks = parse_paf(paf_file)
    aligned_query, aligned_ref = generate_alignment(query_seq, ref_seq, blocks)
    out_table = f"tables_{ref_id}_{query_id}.tsv"
    detect_differences(aligned_ref, aligned_query, ref_id, query_id, out_table)
    return out_table
