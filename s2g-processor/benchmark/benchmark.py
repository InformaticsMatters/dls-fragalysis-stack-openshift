#!/usr/bin/env python

from neo4j.v1 import GraphDatabase
import os
import time

addr = os.environ['BENCHMARK_NEO4J_ADDR']
password = os.environ['BENCHMARK_NEO4J_PASSWORD']

uri = 'bolt://%s:7687' % addr
user = 'neo4j'

smiles_set = [
    'CC(C)C(=O)Nc1cccc(C#N)c1',
    'CN1CCN(c2ccc(C#N)cc2)CC1',
    'CC(CO)(CO)NC(=O)Nc1ccccc1',

    'CN(CC(O)CNCc1cc(F)cc(F)c1)C(=O)Cn1cccn1',
    'O=C(NC1CCN(C(=O)C2CC23CC3)CC1)c1cn[nH]c(=O)c1',
    'Cc1c[nH]c(C(=O)N2CC(NC(=O)c3cnccn3)CC2C)n1',
    'CC1CC(C(=O)N2CCC2CN(C)C(=O)c2ccnn2C)C1',
    'CC(C)C(=O)NC1CCN(C(=O)CCCc2ccccc2)CC1O',
    'O=C(Nc1cc(Cl)ccc1Cl)C1CCCCN1C(=O)c1cnn(CCO)c1',
    'CCn1cc(C(=O)N2CCC(CNC(=O)C3(C)CCC3)CC2)nn1',
    'Cn1cc(Nc2nnc(-c3ccc(Cl)cc3)n2CCc2cn[nH]c2)cn1',
    'COC(C(=O)NCC1CN(Cc2conc2C)CCO1)C1CC1',
    'Cc1ccc(Sc2ncccc2C(=O)N2CCC(O)CC2)cc1C',
    'Cc1cc(C2CCCN2c2ccc(C#N)cc2Cl)no1',
    'CCN(C(=O)C1CCC1)C1CCN(C(=O)C23CCC(CC2)C3(C)C)C1',
    'CCC(C)C(=O)NCC1CCN(C(=O)CC2(C)CCCC2)CC1',
    'N#Cc1ccc(CNCC(O)CNC(=O)c2csnn2)c(F)c1',
    'NC(=O)CN1C2CCCC1CN(C(=O)c1cccnc1)C2',
    'CC(C)c1oncc1C(=O)Nc1ccccn1',
    'CCc1onc(C)c1CNCC1CCN(C(=O)C(C)(C)CC)CC1',
    'O=C(NCC1COCCN1C(=O)c1cn[nH]c1)C1CC12CCOCC2',
    'CCCn1cc(C(=O)N2CCC(NC(=O)c3ccc(=O)[nH]n3)C2)nn1',
    'CC(C)C(CCN(C)C(=O)C1CC1)NC(=O)c1n[nH]c2c1CCCC2',
    'CC(c1cccc(Cl)c1F)N1CC(N(C)C(=O)C2CCC2)C1',
    'CC(C)(C(=O)N1CCC(Nc2cnc(C#N)cn2)CC1)C(F)(F)F',
    'c1cc(-c2nnc(N3CCCC3)n2CC2CCCO2)co1',
    'CCc1onc(C)c1CS(=O)Cc1cccc(F)c1',
    'Cn1cc(CNC(=O)NCc2cccnc2N2CCOCC2)cn1',
    'CCc1cc(C(=O)N2CCOC(C(C)NC(=O)c3c[nH]nn3)C2)[nH]n1',
    'O=C(NCC(CO)NC(=O)c1coc2ccccc12)c1ccoc1',
    'CCCCC(=O)N1CCOC(CNC(=O)C(C)(C)C(F)(F)F)C1',
    'CC1(C)CN(C(=O)C(Oc2cc(Cl)ccc2Cl)c2ccccc2)CC1O',
    'Cc1nc(C2CC2)sc1C(=O)N1CCN(C(=O)CCC2CC2)CC1',
    'Cc1ccc(C(=O)Nc2ccc(-c3ccon3)cc2)cc1C',
    'CC(CC(N)=O)C(=O)N1CC(Nc2ncc(Cl)cn2)C(C)(C)C1',
    'CCC(CC)NC(=O)c1nnc(N(C)Cc2cc(C)on2)n1CCc1c[nH]c2cc(F)ccc12',
    'Cc1noc2ncnc(NC3CCN(C(=O)CCN(C)C)CC3)c12',
    'Cc1cc(C)nc(N2CCCN(C(=O)CCS(C)(=O)=O)CC2)n1',
    'Cc1nn(C)c(C)c1CC(=O)N1CC(NC(=O)c2cnc(C)n2C)C1',
    'O=C(NC1CCCN(C(=O)c2ccco2)C1)c1cnn2ccncc12',
    'CCOC(=O)C(NC(=O)C(C)SCc1nc2ccccc2c(=O)[nH]1)C1CCOCC1',
    'C=CCN(C(=O)Nc1ccc2c(c1)CCO2)C(C)C',
    'CCc1nnc(N2CC(=O)N(C)CC2C)n1Cc1c(F)cccc1Cl',
    'O=C(NC1CN(Cc2nc(-c3ccccc3)cs2)C1)c1cn[nH]c1',
    'CC(CN(C)C(=O)C1CNC(=O)N1)NCc1cccc(Cl)c1',
    'CCOC(C)C(=O)NCCc1ccc(CNC(=O)c2ccoc2)cc1',
    'Cc1nc(CCn2c(-c3ccccc3F)nnc2N2CCOC(C)(C)C2)cs1',
    'Cc1cccc(C(C)N2CCC(CNC(=O)c3c[nH]cc3C)C2)c1',
    'COc1ccc(C)cc1NC(=O)c1cc(C)nc2c1cnn2Cc1cccs1',
    'CN(C(=O)Cn1cccn1)C1CN(C(=O)c2cn(C)cn2)C1',
    'CC1C(NC(=O)c2cn[nH]c2)CCN1C(=O)CN1CCCC1=O',
    'CC(C)N1CCC(N2CCCC(CNC(=O)C3(C)CCCC3)C2)C1=O',
    'CCOc1cccc(C(=O)NC(C)(C)c2ccccc2C)c1',
    'CC(NC(=O)CC(C)(C)C)C(=O)NC1CN(C(=O)c2cn[nH]c2)C1',
    'CCN(CCNC(=O)CCCC(C)=O)C(=O)c1ccccn1',
    'CCc1nnc(N2CCOC(COC)C2)n1CC(C)Oc1ccccc1C',
    'CCC1CN(C(CC)C(=O)N(C)Cc2ccccc2)CCO1',
    'CC(C(=O)N1CC(O)(CNC(=O)c2cccc(F)c2)C1)C1CC1',
    'Cc1ccc(CNCC(O)CNC(=O)C2CCOCC2)c(C)c1',
    'O=C(CC1CCCCC1)NCc1ccc(CN2CCC(O)CC2)cc1',
    'CCC1CCCCC1C(=O)N1CC(O)(CNC(=O)c2ccncc2)C1',
    'Cc1ccc(C(=O)NC2CCN(C(=O)NC(C)(C)C)CC2)s1',
    'Cc1cccc(C(=O)Nc2ccnn2Cc2ccccc2F)c1',
    'CCCC(=O)N1CCCN(C(=O)C2CCCCC2OC)CC1',
    'Cc1cnc(C(=O)N2CCCN(C(=O)Cn3cnnn3)CC2)c(C)c1',
    'CCOc1cc(CCCn2nnnc2N2CCOC(C)C2)ccc1OC',
    'Cc1ccc(CCCN(C)CC(C)NC(=O)c2ccoc2)cc1',
    'CCc1nnc(CNc2cc(C)n(-c3ccccc3)n2)o1',
    'CC(C(=O)N1CCC(CNCC(N)=O)CC1)c1ccc(Cl)s1',
    'CC1CCCCN1S(=O)(=O)c1cc(Cl)ccc1OCC1CC1',
    'CC(NC(=O)COCc1cccnc1)C(C)NC(=O)c1c[nH]nn1',
    'COc1ccc(NC(=O)Cn2nc(-c3ccccc3)oc2=O)cc1',
    'O=C(Cn1cccn1)NCC1CC(NCC2CCOC2)C1',
    'COc1cnc(C2CCCN2S(=O)(=O)c2c(C)n[nH]c2C)[nH]c1=O',
    'COC1(CNC(=O)NCc2cnn(C)c2)CCSC1',
    'O=C(COc1ccccc1)Nc1ccc(OCc2cccc(F)c2)c(F)c1',
    'Cn1cc(N2CCC(NC(=O)C(C)(C)c3ccccc3)C2=O)cn1',
    'CCC(c1ccccc1)N1CC(C(C)NC(=O)c2ccn(C)n2)C1',
    'CC(C(=O)NC1CC1)N1CCC(CNC(=O)CC(C)(C)O)C1',
    'O=C(NCC1CCCCC1NC(=O)C1CC2(CC2)C1)c1cscn1',
    'CC(C)(C)C(=O)NCC(=O)NCC1CCN(C(=O)c2ccoc2)C1',
    'Cc1ccccc1Cc1nnc(N2CCC(C#N)CC2)n1CCNC(=O)c1cccs1',
    'O=C(NC1CC(=O)N(CCOc2ccccc2)C1)c1cnn(CCO)c1',
    'CC(C)CCN1CCN(C(=O)c2cccc(-n3cncn3)n2)CC1',
    'COC(C(=O)N1CCC(C(C)NC(=O)c2ccoc2C)CC1)C1CC1',
    'CC(NCc1ccn(C2CCCC2)n1)C(C)NC(=O)Cn1cccn1',
    'CC(CN(C)C(=O)Cc1ccsc1)NCc1cscn1',
    'COCC1=CCN(C(=O)NCc2c(Cl)cccc2Cl)CC1',
    'Cc1cc2[nH]nc(NC(=O)c3ccc(Cl)cc3)c2c(=O)n1C',
    'CC(C)Cc1ccc(CCCC(=O)NC2(C(N)=O)CCCC2)cc1',
    'Cn1nccc1C(=O)NC1CCCN(C(=O)C2=CCCC2)C1',
    'CCCCC(C)C(=O)NCC1CCCN1C(=O)c1cscn1',
    'Cc1n[nH]c(C)c1S(=O)(=O)Nc1ccc(OCc2cccc(C#N)c2)cc1',
    'CCc1cnc(CN(C)c2nnc(-c3ccc(C#N)cc3)n2CC2CCOCC2)s1',
    'CC(C)N1CCN(Cc2ccccc2OC(F)(F)F)CC1',
    'Br.Brc1ccc(CNC2=NCCCN2)cc1',
    'O=C(CN1CCC(NC(=O)C2CC2)C1)NCc1cccnc1',
    'Cc1cccc(C(=O)NCCN(C)C(=O)CCc2ccncc2)n1',
    'C1CC(NC2CC3CC2C2CC32)CN1',
    'CN(CC(C)(C)CNC(=O)c1ccccc1F)C(=O)C1CCC1(C)C',
    'Cc1nccc(N2CCCN(C(=O)c3c[nH]nc3C3CC3)CC2)n1',
    'CCc1noc(C)c1C(=O)NC(CNC(=O)C1CC1(F)F)C1CC1',
    'COCC(C)C(=O)N1CCN(Cc2noc(-c3ccoc3)n2)CC1'
]

driver = GraphDatabase.driver(uri, auth=(user, password))

cypher = "MATCH (sta:F2 {smiles:'%s'})-[nm:F2EDGE]-(mid:F2)-[ne:F2EDGE]-(end:EM)" \
         " where  abs(sta.hac-end.hac) <= 3 and abs(sta.chac-end.chac) <= 1" \
         " and sta.smiles <> end.smiles RETURN sta, nm, mid, ne, end" \
         " order by split(nm.label, '|')[4], split(ne.label, '|')[2]"

accumulated_time_millis = 0
accumulated_results = 0
largest_query = 0
largest_query_smiles = ''
longest_query = 0
longest_query_smiles = ''

def run_query(tx, smiles_str):
    cypher_str = cypher % smiles_str
    return tx.run(cypher_str)

with driver.session() as session:
    for smiles in smiles_set:

        q_start_time = time.time() * 1000

        results = session.read_transaction(run_query, smiles)

        q_finish_time = time.time() * 1000
        q_elapsed = int(q_finish_time - q_start_time)
        accumulated_time_millis += q_elapsed

        print('-')
        print(q_elapsed)

        num_results = 0
        for _ in results:
            num_results += 1
        accumulated_results += num_results
        print(num_results)
        if num_results > largest_query:
            largest_query = num_results
            largest_query_smiles = smiles

        if q_elapsed > longest_query:
            longest_query = q_elapsed
            longest_query_smiles = smiles

# Summarise...

num_queries = len(smiles_set)
average_query_time_millis = accumulated_time_millis / num_queries
print('---')
print('Queries:          %d' % num_queries)
print('Total results:    %d' % accumulated_results)
print('Largest query:    %d "%s"' % (largest_query, largest_query_smiles))
print('Longest query:    %dmS "%s"' % (longest_query, longest_query_smiles))
print('Total query Time: %dmS' % accumulated_time_millis)
print('Avg query Time:   %dmS' % int(round(average_query_time_millis)))
