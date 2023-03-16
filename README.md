# PlantPTMViewer-converters

This repository holds a Python script to convert MaxQuant outputted PTM files to a tab-delimited summary that can be copied in the ExperimentTemplate excel sheet for submission to the Plant PTM Viewer (https://www.psb.ugent.be/webtools/ptm-viewer/).

Simply download the Python script and use the following syntax (adapting the input to your file): 
<code>MaxQuant_converter.py Phospho (STY)Sites.txt</code>
This will generate an ouput file 'Phospho (STY)Sites_PlantPTMViewer.txt' that extracted the input for the Plant PTM Viewer submission.

Additional conversion scripts for other data processing pipelines can be provided by request.
