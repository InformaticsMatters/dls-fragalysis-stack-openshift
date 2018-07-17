// Fragalysis Graph Processing

params.origin = 'origin.smi'
params.shredSize = 2000
params.chunkSize = 10

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

// CGD ... Chunk/Graph/Deduplicate.
//
// This process...
// - Splits (and canonicalises the input SMILES) file into 'chunks'.
// - Runs graph processing on each chunk to generate node/edges/attributes.
// - Deduplicates the nodes/edges/attributes
//   (and finally removes the original graph files).
//
// We chunk and process all the chunks in one process to balance container
// lifetime and the task velocity stress in Nextflow.
// Prior to this, with a chunk size of 25, the jobs were efficient but did
// not run for long - causing (we think) Nextflow to struggle while it managed
// too many tasks starting and stopping. The sweet-spot for graph analysis
// (at the moment) is a chunk size of 10 molecules which
// is fast (per molecule) but not enough make the container live long enough
// to optimise the CPU. So here we do 200 10-molecule chunks in succession
// so it looks like a very efficient 2000-chunk process which should
// take around 30 minutes (on average) to process.
//
// We generate a timing.log file to record the start time of each step in
// the following process - the time to split, process each chunk, deduplicate
// and clean-up.
process cgd {

    container 'xchem/fragalysis:0.0.5'

    input:
    file part from origin_parts

    output:
    file 'nodes' into node_parts
    file 'edges' into edge_parts
    file 'attributes' into attribute_parts
    file 'timing.log' into timing_parts

    shell:
    '''
    echo doing-!{part},$(date +"%d/%m/%Y %H:%M:%S") > timing.log
    python /usr/local/fragalysis/frag/network/scripts/split_input.py \
        --input !{part} --chunk_size !{params.chunkSize} --output ligands_part
    for chunk in ligands_part*.smi; do
        echo ${chunk},$(date +"%d/%m/%Y %H:%M:%S") >> timing.log
        python /usr/local/fragalysis/frag/network/scripts/build_db.py \
            --input ${chunk} --base_dir output_${chunk%.*}
    done
    echo deduplicating,$(date +"%d/%m/%Y %H:%M:%S") >> timing.log
    find . -name nodes.txt -print | xargs awk '!x[$0]++' > nodes
    find . -name edges.txt -print | xargs awk '!x[$0]++' > edges
    find . -name attributes.txt -print | xargs awk '!x[$0]++' > attributes
    echo removing-output,$(date +"%d/%m/%Y %H:%M:%S") >> timing.log
    rm -rf output_*
    echo done-!{part},$(date +"%d/%m/%Y %H:%M:%S") >> timing.log
    '''

}
