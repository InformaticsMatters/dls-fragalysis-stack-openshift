// Fragalysis 'Raw to Standard' Processing
// Converts raw vendor data into the (our) standard format.
// The vendor data (often in more than one file with a common prefix and header)
// is 'joined' then 'shredded' for parallel conversion before all the
// standard results are 'joined' to form a final 'grand standard' file.
//
// - rawJoin
// - rawShred
// - rawStandardise
// - standardJoin

// You *must* define the raw prefix and the raw standardisation type.,
// which may not be obvious form the files
params.rawPrefix = 'set-me'
params.rawType = 'set-me'

// The number of raw/vendor molecules to process in one 'shred'
params.shredSize = 50000
// Limit the processing (in each shred) to a number of molecules.
// 0 implies process all molecules.
params.limit = 0

// A channel of all the raw files,
// presented to the initial 'rawJoin' stage as a list...
rawFiles = Channel.fromPath( './' + params.rawPrefix + '*' ).toList()

// Joins multiple files (with common headers)
process rawJoin {

    container 'informaticsmatters/fragalysis:0.0.23'
    publishDir 'results/', mode: 'copy'

    input:
    file rawFile from rawFiles

    output:
    file 'raw_join.gz' into raw_join

    """
    python /usr/local/fragalysis/frag/network/scripts/header_join.py \
        . ${params.rawPrefix} raw_join
    """

}


// Shreds a 'joined' raw file into smaller parts
// (replicating the header)
process rawShred {

    container 'informaticsmatters/fragalysis:0.0.23'
    publishDir 'results/', mode: 'copy'

    input:
    file raw from raw_join

    output:
    file 'raw_shred_*.gz' into raw_shreds mode flatten

    """
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        ${raw} raw_shred ${params.shredSize} --compress
    rm ${raw}
    """

}

// standardise ... a slice of the raw data.
//
// This process...
// - Standardises a 'shred-size' file of customer data.
process rawStandardise {

    container 'informaticsmatters/fragalysis:0.0.23'
    publishDir 'results/', mode: 'copy'

    input:
    file shred from raw_shreds

    output:
    file '*.standardised-compounds.tab.gz' into standards

    shell:
    '''
    python /usr/local/fragalysis/frag/network/scripts/standardise_!{params.rawType}_compounds.py \
        . raw_shred !{shred} --output-is-prefix \
        --limit !{params.limit}
    rm !{shred}
    '''

}

// standardise ... a slice of the raw data.
//
// This process...
// - Standardises a 'shred-size' file of customer data.
process standardiseJoin {

    container 'informaticsmatters/fragalysis:0.0.23'
    publishDir 'results/', mode: 'copy'
    maxRetries 3

    input:
    file standard from standards.toList()

    output:
    file 'standardised-compounds.tab.gz'

    """
    python /usr/local/fragalysis/frag/network/scripts/header_join.py \
        . raw_shred_ standardised-compounds.tab
    """

}
