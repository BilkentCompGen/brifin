import xlrd
import xlsxwriter
import argparse


parser = argparse.ArgumentParser(description='C Parameter Calculation')

parser.add_argument('-i', type=int,  help='Interaction number')
parser.add_argument('-f', type=str,  help='File name')
parser.add_argument('-s', type=str,  help='Sheet name')

args = parser.parse_args()
file = args.f


interaction_number = args.i


wb = xlrd.open_workbook(file)
sheet = wb.sheet_by_name(args.s)


pairs=[]

for i in range(0,interaction_number):
    pairs.append([i+1, int(sheet.cell_value(i,0)),int(sheet.cell_value(i,1))])


pair_edge_matrix=[]

for i in range(0,interaction_number):
    row=[]
    for j in range(0, interaction_number):
        if pairs[i][1]==pairs[j][1] or pairs[i][2]==pairs[j][2]:
            value=1
        else:
            value=0
        row.append(value)
    pair_edge_matrix.append(row)

workbook = xlsxwriter.Workbook("Parameter_c.xlsx")
sheet2 = workbook.add_worksheet("c_parameter")

for i in range(0, interaction_number):
    for j in range(0,interaction_number):
        sheet2.write(i, j, pair_edge_matrix[i][j])


workbook.close()

