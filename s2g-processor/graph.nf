/* Example Nextflow pipline that runs Docking using rDock
*/

params.ligands = 'test.smi'
params.chunk = 500
params.graphMaxForks = 8

ligands = file(params.ligands)

/* Splits the input SD file into multiple files of ${params.chunk} records.
* Each file is sent individually to the ligand_parts channel
*/
process sdsplit {

    maxForks 1
	container 'xchem/fragalysis'

	input:
    file ligands

    output:
    file 'ligands_part*' into ligand_parts mode flatten
    
    """
	python /usr/local/fragalysis/frag/network/scripts/split_input.py --input $ligands --chunk_size $params.chunk --output ligands_part
    """
}


/* Builds the graph for each part
 * On a MacBook Pro (15-inch, 2016) 2.7GHz i7 with 2133MHz LPDDR3 Memory
 * the average time to process 500 molecules is 6'45" (1.23 molecules/S)
*/
process graph {

	maxForks params.graphMaxForks
	errorStrategy 'retry'
	container 'xchem/fragalysis'

	input:
    file part from ligand_parts
	
    output:
    file 'output_part*/edges.txt' into docked_parts
    
    """
     python /usr/local/fragalysis/frag/network/scripts/build_db.py --input  $part --base_dir ${part.name.replace('ligands', 'output')[0..-5]} 
    """
}


