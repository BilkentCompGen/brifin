# BriFin

Prerequisites
-------------
*Python 3.5 or higher versions
*xlsxwriter, numpy, pandas, xlrd, copy and gurobipy modules 

To calculate the importance scores of the contact proteins and find the top intracellular contributors (non-interacting cell proteins) of their scores, Score_Calculator.py is used. It takes an input file including interactions, and calculates intracellular importance scores of the contact proteins of each cell.
This code is run for each cell. In the input Excel file, there are four sheets. Three sheets (s1, s2, s3) include interactions and the final sheet (s4) include PageRank scores (or any other relevant score) of the proteins. Interactions are written by using two columns and using the model IDs of the proteins. 
The first sheet (s1) includes the direct interactions of the interacting proteins with non-interacting proteins. The first column has to include the IDs of the interacting proteins, and the interactions have to be sorted by the IDs in the first column.
The second sheet (s2) includes the interactions between the non-interacting proteins. The third sheet (s3) includes the interactions between the interacting proteins. In the third sheet, the interaction list has to be doubled by the symmetrical interactions. Assigning smallest IDs to the interacting proteins is recommended. Command to run Score_Calculator.py is:

python Score_Calculator.py -i ContactProteinNumber -t TotalProteinNumber -f FileName -s1 Sheet1Name -s2 Sheet2Name -s3 Sheet3Name -s4 Sheet4Name -r ResultFileName -cn TopContributorNumber

After the score calculation step for each cell, raw parameters of the ILP model are obtained. The ILP model is based on the contact protein pairs, and it has two parameters, which are inverse scores of the contact protein pairs (s) and a binary parameter denoting whether a pair covers an interaction between the cells (c).

After determining contact protein pairs of two interacting cells, their model scores (s) are calculated by the following steps (no code is used for this):
1) Normalization (min-max) of the scores of the contact proteins in the pair that belong to different cells 
2) Finding the inverse of the sum of the normalized scores for each pair

To obtain c parameter, PairCoverParameter.py is used. It takes a file as input which includes intercellular interactions represented by model IDs of the proteins. The first column includes the model ID of the protein of cell 1 and the second column includes the model ID of the protein of cell 2. It generates the c parameter matrix in a file named "Parameter_c.xlsx". The command to run PairCoverParameter.py is:

python PairCoverParameter.py -i PairNumber -f FileName -s SheetName

At the last step, Pair_ILP_Model.py is run with an Excel sheet including s and c parameters. It outputs the model IDs of the selected protein pairs to an Excel file, and is run with the following command:

python Pair_ILP_Model.py -i InteractionNumber -p PairNumber -f FileName -s1 Sheet_of_c_parameter -s2 Sheet_of_s_parameter -r ResultFileName -a Desired_alpha_value

Header is not used in any of the input files.
