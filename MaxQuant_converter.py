#!/usr/bin/env python

"""Converter of MaxQuant site table to input compatible with The Plant PTM Viewer template submissions.
See https://www.psb.ugent.be/webtools/ptm-viewer/submit.php for downloading this template."""

__author__      = "Patrick Willems"
__copyright__   = "Copyright 2023"
__email__       = "willems533@gmail.com"

import os, sys, re
from os import path

###Modification dictionary
PTM_type = {
    'Phospho (STY)': 'ph',
    'Oxidation (M)': 'mo',
    'GlyGly (K)': 'ub',
    'Acetyl (K)': 'ac',
    'Acetyl (K)': 'ac',
}

###Preliminary checks for input file
#Check if argument provided
if len(sys.argv) == 1: sys.exit('##ERROR: No input file specified, usage: \'MaxQuant_converter.py <xxxSites.txt>\'\n\nFor instance: MaxQuant_converter.py Phospho (STY)Sites.txt\nThis will return as output Phospho (STY)Sites_PlantPTMViewer.txt whose (tab-delimited) content can be pasted in the template Excel sheet.')
else: input_f = sys.argv[1]

#Check if file exists
if not path.exists(input_f): sys.exit('##ERROR: Specified input file does not exist, double-check the provided path.')

#Check if necessary information in file
f = open(input_f,'r')
header_line = next(f)
headers = header_line.split('\t')
colIndex = {}
for i in range(len(headers)):
    if headers[i] == 'PEP': colIndex.update({'PEP': i})                         #Posterior error probability                         
    elif headers[i] == 'Score': colIndex.update({'score': i})                   #MaxQuant score
    elif headers[i] == 'Mass error [ppm]': colIndex.update({'mass_error': i})   #Mass error    
    elif re.match(r'.+ Probabilities$',headers[i]):                             #Localisation probabilities
        colIndex.update({'loc_prob': i}) 
        mod = re.match(r'(.+) Probabilities$',headers[i]).group(1)
        if mod in PTM_type: mod = PTM_type[mod]                      #Replace with PTM viewer modification abbreviation

#Our scripts requires the localisation probabilities          
if 'loc_prob' not in colIndex: sys.exit('##ERROR: No localisation probability header found in the file (e.g. Phospho (STY) Probabilities), please retain the full file or contact us whether your headers do not correspond as anticipated here in the script.')

PTM = {}
for line in f:
    line = line.rstrip()
    columns = line.split('\t')
    loc_prob = columns[colIndex['loc_prob']]
    plain_pep = re.sub(r'[^A-Z]','',loc_prob)
    if 'score' in colIndex: score = columns[colIndex['score']]
    else: score = 'NA'
    if 'mass_error' in colIndex: mass_error = columns[colIndex['mass_error']]
    else: mass_error = 'NA'
    if 'PEP' in colIndex: PEP = columns[colIndex['PEP']]
    else: PEP = 'NA'
    while '(' in loc_prob:
        pos = loc_prob.find('(')
        aa = loc_prob[pos-1]
        prob = re.search(r'\(([^A-Z]+)\)',loc_prob).group(1)
        loc_prob = loc_prob.replace('('+prob+')','',1)
        #Peptide sequence and position as unique keys, keep the one (i) highest localisation probability or (ii) if equal loc prob, the one with highest MaxQuant score:
        id = plain_pep + str(pos)    
        if id not in PTM:       
            PTM.update({id: {'PEP': PEP, 'score': score, 'mass_error': mass_error, 'plain_pep': plain_pep, 'pos': pos, 'prob': prob, 'aa': aa}})
        elif float(prob) > float(PTM[id]['prob']):
            PTM.update({id: {'PEP': PEP, 'score': score, 'mass_error': mass_error, 'plain_pep': plain_pep, 'pos': pos, 'prob': prob, 'aa': aa}})
        elif float(prob) == float(PTM[id]['prob']) and score != 'NA' and float(score) > float(PTM[id]['score']):
            PTM.update({id: {'PEP': PEP, 'score': score, 'mass_error': mass_error, 'plain_pep': plain_pep, 'pos': pos, 'prob': prob, 'aa': aa}})

print('#INFO: Retrieved a total of',str(len(PTM)),'modified peptide sites')
output_f = input_f.replace('.txt','_PlantPTMViewer.txt')
out = open(output_f,'w')
out.write('Peptide sequence\tPTM Type\tModified AA\tPosition in pep\tLocalization Prob\tIdentification Score\tPosterior Error Probability (PEP)\tMass error (ppm)\n')
for id in PTM:
    out.write(PTM[id]['plain_pep']+'\t'+mod+'\t'+PTM[id]['aa']+'\t'+str(PTM[id]['pos'])+'\t'+PTM[id]['prob'])
    if PTM[id]['score'] != 'NA': out.write('\t'+PTM[id]['score'])
    else: out.write('\t')
    if PTM[id]['PEP'] != 'NA': out.write('\t'+PTM[id]['PEP'])
    else: out.write('\t')
    if PTM[id]['mass_error'] != 'NA': out.write('\t'+PTM[id]['mass_error']+'\n')
    else: out.write('\t\n')
