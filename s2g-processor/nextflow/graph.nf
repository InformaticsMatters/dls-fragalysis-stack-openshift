// Fragalysis Graph Processing

params.origin = 'origin.smi'
// A shred of 70,000 creates just enough files for 8 72-core machines
// to run the smilesSplit in one shot on each core.
params.shredSize = 70000
params.chunkSize = 25

origin = file(params.origin)

// Shreds a file into smaller parts (keeping the header)
process headShred {

    container 'xchem/fragalysis:0.0.5'

    input:
    file origin

    output:
    file 'origin_part_*.smi' into origin_parts mode flatten

    """
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        -i $origin -o origin_part -s $params.shredSize
    """

}

// Splits and canonicalises the input SMILES file into 'chunks'
process smilesSplit {

    container 'xchem/fragalysis:0.0.5'

    input:
    file part from origin_parts

    output:
    file 'ligands_part*' into ligand_parts mode flatten
    
    """
    python /usr/local/fragalysis/frag/network/scripts/split_input.py \
        --input $part --chunk_size $params.chunkSize --output ligands_part
    """

}

// Builds the graph for each canonicalised split part.
// The output of each process is a node, edge and attributes text file.
process graph {

    container 'xchem/fragalysis:0.0.5'

    errorStrategy 'retry'

    input:
    file part from ligand_parts
	
    """
    python /usr/local/fragalysis/frag/network/scripts/build_db.py \
        --input $part --base_dir ${part.name.replace('ligands', 'output')[0..-5]}
    """

}
