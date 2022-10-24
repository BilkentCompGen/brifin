import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import xlsxwriter
import argparse


parser = argparse.ArgumentParser(description='PPI Pair Model')
parser.add_argument('-i', type=int, help='Interaction Number')
parser.add_argument('-p', type=int,  help='Pair Number')
parser.add_argument('-f', type=str,  help='Filename')
parser.add_argument('-s1', type=str,  help='C parameter sheet')
parser.add_argument('-s2', type=str,  help='S parameter sheet')
parser.add_argument('-r', type=str,  help='Result Filename')
parser.add_argument('-a', type=float)

args = parser.parse_args()

p_n=args.p
i_n=args.i
alpha=args.a


print("Total number of pairs", args.p)

print("Alpha is", args.a)

P = [i for i in range(1,p_n+1)]

I = [i for i in range(1,i_n+1)]


file=args.f


s_df= pd.read_excel(file, sheet_name=args.s2, header=None)
s = s_df.to_numpy()

c_df= pd.read_excel(file, sheet_name=args.s1, header=None)
c = c_df.to_numpy()

min_desired_coverage=args.i*alpha


print("Minimum number of interactions to be covered", min_desired_coverage)

model_helper=gp.Model('M_model')

x=model_helper.addVars(P, vtype=GRB.BINARY,name="x")
y=model_helper.addVars(I, vtype=GRB.BINARY,name="y")


print("Variables created")


model_helper.modelSense=GRB.MINIMIZE
model_helper.setObjective(sum(x[p]*s[p-1] for p in P))


c1=model_helper.addConstrs(x[p]*c[p-1,i-1]<= y[i] for p in P for i in I)

c2=model_helper.addConstr(sum(y[i] for i in I)>=min_desired_coverage)

c3=model_helper.addConstrs(y[i]<= sum(x[p]*c[p-1,i-1] for p in P) for i in I)


model_helper.optimize()
model_helper.printAttr('x')


solution_dict={}

for i in I:
    solution_dict[i]=x[i].X

workbook = xlsxwriter.Workbook(args.r)

worksheet = workbook.add_worksheet('Selected Pair IDs')

row=0

for i in solution_dict:
    if solution_dict[i]==1:
        worksheet.write(row, 0, i)
        row += 1

workbook.close()

