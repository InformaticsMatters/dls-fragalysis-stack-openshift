// Fragalysis Graph Processing

params.origin = 'origin.smi'
params.shredSize = 2000
params.chunkSize = 10

origin = file(params.origin)

// Shreds a file into smaller parts (keeping the header)
process headShred {

    container 'xchem/fragalysis:0.0.7'

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
// We could remove the individual 10-sample 'fragment' files at the end of the
// process by running 'rm -rf output_*' along wiht the other clean-up operations
// keeping them will be valuable for any further analysis on 'interesting'
// (especially fast or especially slow) steps.
//
// We generate a timing file to record the start time of each step in
// the following process - the time to split, process each chunk, deduplicate
// and then clean-up.
process cgd {

    container 'xchem/fragalysis:0.0.7'
    publishDir 'results/', mode: 'copy'
    errorStrategy 'retry'
    maxRetries 3

    input:
    file part from origin_parts

    output:
    file '*.nodes'
    file '*.edges'
    file '*.attributes'
    file '*.timing'

    shell:
    '''
    echo doing-!{part},$(date +"%d/%m/%Y %H:%M:%S") > timing
    python /usr/local/fragalysis/frag/network/scripts/split_input.py \
        --input !{part} --chunk_size !{params.chunkSize} --output ligands_part
    for chunk in ligands_part*.smi; do
        echo ${chunk},$(date +"%d/%m/%Y %H:%M:%S") >> timing
        python /usr/local/fragalysis/frag/network/scripts/build_db.py \
            --input ${chunk} --base_dir output_${chunk%.*}
    done
    echo deduplicating,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    find . -name nodes.txt -print | xargs awk '!x[$0]++' > !{part}.nodes
    find . -name edges.txt -print | xargs awk '!x[$0]++' > !{part}.edges
    find . -name attributes.txt -print | xargs awk '!x[$0]++' > !{part}.attributes
    echo removing-output,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    #rm !{part}
    #rm ligands_part*.smi
    echo done-!{part},$(date +"%d/%m/%Y %H:%M:%S") >> timing
    mv timing !{part}.timing
    '''

}