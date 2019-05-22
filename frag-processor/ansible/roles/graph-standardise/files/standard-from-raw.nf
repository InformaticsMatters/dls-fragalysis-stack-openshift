// Fragalysis 'Raw to Standard' Processing
// Converts raw vendor data into the (our) standard format.
// The vendor data (often in more than one file with a common prefix and header)
// is 'joined' then 'shredded' for parallel conversion before all the
// standard results are 'joined' to form a final 'grand standard' file.
//
// - rawJoin
// - rawShred
// - rawStandardise (xN)
// - standardJoin

// You *must* define the raw prefix and the raw standardisation type,
// which may not be obvious from the files. At the moment the
// following 'types' ars supported...
//
// - senp7
// - molport
// - enamine
//
// The 'type' is the phrase between the 'standardise_' and '_compounds' part
// of the Python script name (e.g. 'senp7' for 'standardise_senp7_compounds.py')
params.rawPrefix = 'set-me'
params.rawType = 'set-me'

// The number of raw/vendor molecules to process in one 'shred'
params.shredSize = 50000
// Limit the processing to a number of molecules from the joined raw set.
// 0 implies skip none and no limit.
params.skip = 0
params.limit = 0

// A channel of all the raw files,
// presented to the initial 'rawJoin' stage as a list...
rawFiles = Channel.fromPath( './' + params.rawPrefix + '*' ).toList()

// Join multiple raw files (with common headers)
// ----
//
// The output of this stage is a file ('raw_join.gz')
// which has all the raw molecules in it with a header
// taken from one of the raw files.
process rawJoin {

    container 'informaticsmatters/fragalysis:0.0.41'
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

// Shred the 'joined' raw file into smaller parts (replicating the header)
// -----
//
// The output of this stage is a number of files,
// each of which is a small 'slice' of the input file.
// The output files each have a header, replicated
// from the input file.
process rawShred {

    container 'informaticsmatters/fragalysis:0.0.41'
    publishDir 'results/', mode: 'copy'

    input:
    file raw from raw_join

    output:
    file 'raw_shred_*.gz' into raw_shreds mode flatten

    """
    python /usr/local/fragalysis/frag/network/scripts/header_shred.py \
        ${raw} raw_shred ${params.shredSize} --compress \
        --skip ${params.skip} --limit ${params.limit}
    rm ${raw}
    """

}

// Standardise ... a slice of the raw data
// -----------
//
// The output of this stage is a standard file,
// formed from the content of a raw shred.
process rawStandardise {

    container 'informaticsmatters/fragalysis:0.0.41'
    publishDir 'results/', mode: 'copy'

    input:
    file shred from raw_shreds

    output:
    file '*.standardised-compounds.tab.gz' into standards

    shell:
    '''
    python /usr/local/fragalysis/frag/network/scripts/standardise_!{params.rawType}_compounds.py \
        . raw_shred !{shred} --output-is-prefix
    rm !{shred}
    '''

}

// Join ... all the standard files together (replicating one header)
// ----
//
// The output of this stage is a single standard file,
// formed from the content of each standard file produced
// by the prior stage.
process standardiseJoin {

    container 'informaticsmatters/fragalysis:0.0.41'
    publishDir 'results/', mode: 'copy'

    input:
    file standard from standards.toList()

    output:
    file 'standardised-compounds.tab.gz'

    """
    python /usr/local/fragalysis/frag/network/scripts/header_join.py \
        . raw_shred_ standardised-compounds.tab
    """

}
