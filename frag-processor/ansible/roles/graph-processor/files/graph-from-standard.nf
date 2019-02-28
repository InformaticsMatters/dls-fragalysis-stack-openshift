// Fragalysis Graph Processing
// Compilation of graph files from Informatics Matters 'standard' files.

params.origin = 'standardised-compounds.tab.gz'
params.shredSize = 200
params.chunkSize = 10
params.limit = 0

origin = file(params.origin)

// Shreds a standard file into smaller parts
// (replicating the header)
process headShred {

    container 'informaticsmatters/fragalysis:0.0.22'
    publishDir 'results/', mode: 'copy', pattern: 'standardized_input.smi.gz'

    input:
    file origin

    output:
    file 'origin_part_*.smi' into origin_parts mode flatten

    """
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        -i ${params.origin} -o origin_part -s ${params.shredSize} \
        -l ${params.limit}
    """

}

// CGD ... Chunk/Graph/Deduplicate.
//
// This process...
// - Splits file into 'chunks'.
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
// to optimise the CPU.
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

    container 'informaticsmatters/fragalysis:0.0.22'
    publishDir 'results/', mode: 'copy'
    errorStrategy 'retry'
    maxRetries 3

    input:
    file part from origin_parts

    output:
    file '*.nodes.gz'
    file '*.edges.gz'
    file '*.attributes.gz'
    file '*.build-network.log.gz'
    file '*.timing.gz'

    shell:
    '''
    echo doing-!{part},$(date +"%d/%m/%Y %H:%M:%S") > timing
    export ENABLE_BUILD_NETWORK_LOG=1
    export LC_ALL=C
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        -i !{part} -o ligands_part -s !{params.chunkSize}
    for chunk in ligands_part*.smi; do
        echo ${chunk},$(date +"%d/%m/%Y %H:%M:%S") >> timing
        python /usr/local/fragalysis/frag/network/scripts/build_db_from_standard.py \
            --input ${chunk} --base_dir output_${chunk%.*} --non_isomeric
    done
    echo deduplicating,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    find . -name nodes.txt | xargs cat | sort --temporary-directory=$HOME/tmp -u | gzip > !{part}.nodes.gz
    find . -name edges.txt | xargs cat | sort --temporary-directory=$HOME/tmp -u | gzip > !{part}.edges.gz
    find . -name attributes.txt | xargs cat | sort --temporary-directory=$HOME/tmp -u | gzip > !{part}.attributes.gz
    find . -name build-network.log | xargs cat | gzip > !{part}.build-network.log.gz
    echo removing-output,$(date +"%d/%m/%Y %H:%M:%S") >> timing
    rm !{part}
    rm ligands_part*.smi
    echo done-!{part},$(date +"%d/%m/%Y %H:%M:%S") >> timing
    gzip timing
    mv timing.gz !{part}.timing.gz
    '''

}
