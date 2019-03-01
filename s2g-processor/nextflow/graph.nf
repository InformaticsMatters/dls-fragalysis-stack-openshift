// Fragalysis Graph Processing

params.origin = 'origin.smi.gz'
params.shredSize = 1000
params.chunkSize = 25
params.sLimit = 0 // zero means process all
params.sMaxHac = 36

origin = file(params.origin)

// Standardize and shreds a file into smaller parts
// (replicating the header)
process headShred {

    container 'informaticsmatters/fragalysis:0.0.17'
    publishDir 'results/', mode: 'copy', pattern: 'standardized_input.smi.gz'

    input:
    file origin

    output:
    file 'origin_part_*.smi' into origin_parts mode flatten
    file 'standardized_input.smi.gz'

    """
    python /usr/local/fragalysis/frag/network/scripts/standardizer.py \
        --max-hac ${params.sMaxHac} --limit ${params.sLimit} \
        --id-column -4 --id-prefix REAL ${params.origin}
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        -i output_1.smi -o origin_part -s ${params.shredSize}
    mv output_1.smi standardized_input.smi
    gzip standardized_input.smi
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
// process by running 'rm -rf output_*' along with the other clean-up operations
// keeping them will be valuable for any further analysis on 'interesting'
// (especially fast or especially slow) steps.
//
// We generate a timing file to record the start time of each step in
// the following process - the time to split, process each chunk, deduplicate
// and then clean-up.
process cgd {

    container 'informaticsmatters/fragalysis:0.0.17'
    publishDir 'results/', mode: 'copy'
    errorStrategy 'retry'
    maxRetries 3

    input:
    file part from origin_parts

    output:
    file '*.nodes.gz'
    file '*.edges.gz'
    file '*.attributes.gz'
    file '*.timing.gz'

    shell:
    '''
    echo doing-!{part},$(date +"%d/%m/%Y %H:%M:%S") > timing
    export LC_ALL=C
    python /usr/local/fragalysis/frag/network/scripts/split_input.py \
        --input !{part} --chunk_size !{params.chunkSize} --output ligands_part
    for chunk in ligands_part*.smi; do
        echo ${chunk},$(date +"%d/%m/%Y %H:%M:%S") >> timing
        python /usr/local/fragalysis/frag/network/scripts/build_db.py \
            --input ${chunk} --base_dir output_${chunk%.*} --non_isomeric
    done
    echo deduplicating,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    find . -name nodes.txt | xargs cat > !{part}.nodes.gz
    find . -name edges.txt | xargs cat | sort --temporary-directory=$HOME/tmp -u | gzip > !{part}.edges.gz
    find . -name attributes.txt | xargs cat | sort --temporary-directory=$HOME/tmp -u | gzip > !{part}.attributes.gz
    echo removing-output,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    rm !{part}
    rm ligands_part*.smi
    echo done-!{part},$(date +"%d/%m/%Y %H:%M:%S") >> timing
    gzip timing
    mv timing.gz !{part}.timing.gz
    '''

}
