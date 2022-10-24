import copy
import xlsxwriter
import argparse
import numpy as np
import pandas as pd

#s sheet must include interacting-inner protein interactions with the sorted interacting protein IDS in the first column
#s3 must include the interactions between only the interacting proteins.
#In s3, the symmetrical interactions must be also listed, which means the row number is twice the number of interactions.

parser = argparse.ArgumentParser(description='PIN_Connectivity')

parser.add_argument('-i', type=int,  help='Interacting protein number')
parser.add_argument('-t', type=int,  help='Total protein number')
parser.add_argument('-f', type=str,  help='File name')
parser.add_argument('-s1', type=str,  help='Sheet of direct interactions of interacting proteins with non-interacting proteins')
parser.add_argument('-s2', type=str,  help='Sheet of interactions of non-interacting proteins')
parser.add_argument('-s3', type=str,  help='Sheet of interactions of interacting proteins')
parser.add_argument('-s4', type=str,  help='Score sheet')
parser.add_argument('-cn', type=int,  help='Top contributor number')
parser.add_argument('-r', type=str,  help='Name of the result file')


args = parser.parse_args()


def Get_Connections(int_protein_number,  di_sheet_name, oi_sheet_name ):


    df = pd.read_excel(args.f, sheet_name=di_sheet_name, header=None)
    M=df.values.tolist()
    df2= pd.read_excel(args.f, sheet_name=oi_sheet_name, header=None)
    I1=df2.values.tolist()


    Interacting=list(range(1,int_protein_number+1))

    C=[]
    Final=[]
    C0=[]

    for i in range(0,len(Interacting)):
        list1 = []
        to_erase=[]
        for j in M:

            if j[0]>i+1:
                break

            if j[0]==i+1:
                list1.append(int(j[1]))
                to_erase.append(j)


        C0.append(list1)
        for a in to_erase:
            M.remove(a)



    for m in range(0,len(Interacting)):
        count=1

        C.clear()
        C.append(C0[m])
        t = 0
        I=copy.deepcopy(I1)


        while count>=1 and len(I)!=0:
            new_list = []

            count = 0
            for k in C[t]:


                remove_list=[]
                for j in I:

                    if j[0]==k:
                        count+=1


                        new_list.append(int(j[1]))

                        remove_list.append(j)


                    elif j[1]==k:
                        count += 1

                        new_list.append(int(j[0]))
                        remove_list.append(j)

                for element in remove_list:
                    I.remove(element)

            new_list=list(dict.fromkeys(new_list))
            C.append(new_list)

            t+=1

        for i in range(len(C)):
            for item in C[i]:
                if (m+1)!=item:
                    Final.append([str(m+1)+","+str(item),i+1])

    return Final


def Score_Calculation(data, int_protein_number, type):

    column_values = ['interaction', 'degree']
    df = pd.DataFrame(data=data,    columns=column_values)
    table = pd.pivot_table(df,  index='interaction', values='degree', aggfunc= np.min)


    df_final=pd.DataFrame(table)

    interaction_pairs=df_final.index.values
    df_final=np.array(df_final)

    array=[]
    for i in range(0,len(interaction_pairs)):
        separate_protein_ids=interaction_pairs[i].split(",")
        array.append([int(separate_protein_ids[0]), int(separate_protein_ids[1]), df_final[i][0]])

    array=np.array(array)
    array = array[array[:, 0].argsort()]
    processed_PR_scores=[]

    contribution=[]

    for i in range(0,len(interaction_pairs)):
        processed_PR_scores.append([array[i][0],PR_Scores[array[i][1]-1]/array[i][2]])
        if type==1:
            contribution.append([array[i][0],array[i][1],float(PR_Scores[array[i][1]-1]/array[i][2])])

    if type==1:
        protein_id = 1
        contributors=[]
        #print(len(contribution))
        #print(contribution[0][0])
        i=0
        while i<len(contribution):
            contributors_row=[]
            while contribution[i][0]==protein_id:
                #print(i)
                contributors_row.append([contribution[i][1],contribution[i][2]])
                i+=1
                if i>=len(contribution):
                    break
            contributors_row=np.array(contributors_row)
            contributors.append(contributors_row)
            protein_id+=1

        contributors=np.array(contributors)
        #print("c",contributors)
        top_contributors=[]
        top_number=args.cn
        for row in contributors:
            #row=np.array(row)
            #print("r",row)
            if len(row)==0:
                top_contributors.append([])
            elif len(row)<top_number:
                top_contributors.append(row[:,0])
            else:
                row = row[row[:, 1].argsort()[::-1]]
                print(row)
                top_contributors.append(row[:,0][:top_number])

        top_contributors=np.array(top_contributors)
        print("*",top_contributors)


    column_values = ['InteractingProtein', 'Score']
    df3 = pd.DataFrame(data=processed_PR_scores,    columns=column_values)
    table2 = pd.pivot_table(df3,  index='InteractingProtein', values='Score', aggfunc= np.sum)

    df_final=pd.DataFrame(table2)
    ids=df_final.index.values
    df_final=np.array(df_final)
    array=[]

    j = 0
    for i in range(1,int_protein_number+1):

        if i in ids:

            array.append([i, df_final[j][0]])
            j+=1
        else:
            array.append([i,0])

    if type==1:
        return array, top_contributors
    else:
        return array


df = pd.read_excel(args.f, sheet_name=args.s4, header=None)
PR_Scores= df.values.tolist()

print("Running")

Inner_connections=Get_Connections(args.i,  args.s1, args.s2)
Interacting_protein_connections=Get_Connections(args.i,  args.s3,args.s3)

array_1, top_contributors=Score_Calculation(Inner_connections, args.i, 1)
array_2=Score_Calculation(Interacting_protein_connections,args.i, 2)

workbook = xlsxwriter.Workbook(args.r)
sheet0 = workbook.add_worksheet("Scores")
sheet0.write(0,0,"Interacting Protein ID")
sheet0.write(0,1, "Overall Score")

for i in range(args.i):
    sheet0.write(i+1, 0, i+1)
    sheet0.write(i+1,1,array_1[i][1] + array_2[i][1])

sheet1=workbook.add_worksheet("Contributors")
sheet1.write(0,0,"Interacting Protein ID")
sheet1.write(0,1,"Intracellular Contributors")

for i in range(args.i):
    sheet1.write(i+1,0,i+1)
    for j in range(len(top_contributors[i])):
        sheet1.write(i+1, j+1, top_contributors[i][j])


workbook.close()

print("Finished")