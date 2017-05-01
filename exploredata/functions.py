import pandas as pd
import numpy as np
import re

#Guess most likely separator for csv files
def test_sep(line):
	n1=len(line.split(";"))
	n2=len(line.split(","))
	n3=len(line.split(","))
	if n1>n2:
		sep=";"
	elif n2>n3:
		sep=","
	elif n3>1:
		sep="\t"
	else:
		sep=' '
	print(line.split(sep))
	return sep

#Load file with options
def handle_uploaded_file(data, types=False):
	if data.header==True :
		header=0
	else:
		header=None
	if data.index_col==True:
		index_col=0
	else:
		index_col=None
	data.file.open()
	file_format=data.title.split(".")[-1]
	if file_format in ["csv", "txt"]:
		firstl=str(data.file.readline())
		sep=test_sep(firstl)
		print('sep = '+sep)
		data.file.seek(0)
		df=pd.read_csv(data.file, sep=sep, header=header, index_col=index_col)
	elif file_format=="xlsx":
		df=pd.read_excel(data.file, header=header, index_col=index_col)
	if types:
		for var in data.variable_set.all():
			if var.type in ['QT', 'QL_OR']:
				df[var.name]=pd.to_numeric(df[var.name], errors='raise')
			else :
				df[var.name]=df[var.name].astype(str)
	data.file.close()
	return(df)

#Guess if variables should be interpreted as numeric or factor
def default_type(values):
	if len(np.unique(values))==2:
		return('B')
	elif np.dtype(values)=='float64' or np.dtype(values)=='int64':
		return('QT')
	else:
		return('QL')

#Build easy-to-display data summary
def depict(data, types=False):
	#Detect/select numeric variables
	df=handle_uploaded_file(data, types=types)
	qtvar_names=[]
	for name in list(df):
		if np.dtype(df[name])=='float64' or np.dtype(df[name])=='int64':
			qtvar_names+=[name]
	print("Quanti Vars : ", qtvar_names)
	#Describe numeric variables in summary
	df[qtvar_names]=df[qtvar_names].astype(np.double)
	summary=df[qtvar_names].describe()
	stats=summary.index
	if qtvar_names==[]:
		summary={}
	else:
		summary={ stat : round(summary.loc[stat], 2) for stat in stats}
	#Render frequencies for other variables
	col_names=list(df)
	qlvar_names = list(set(col_names) - set(qtvar_names))
	print("Quali Vars : ", qlvar_names)
	summary2=[]
	if qlvar_names!=[]:
		min_n_features=min([len(df[name].value_counts()) for name in qlvar_names])
		for i in range(min_n_features) :
			line=[]
			for name in qlvar_names:
				line+=[df[name].value_counts().index[i], str(round(df[name].value_counts()[i]/sum(df[name].value_counts())*100, 2))+"%"]
			summary2+=[line]
	return summary, qtvar_names, summary2, qlvar_names

def convert(df, variables, target=False, convert_target=True):
	regressors=[]
	for var in variables:
		if var.type in ["B", "QL"]:
			dummy_ranks = pd.get_dummies(df[var.name], prefix = var.name+'_')
			dummy_ranks.index=df.index
			del dummy_ranks[list(dummy_ranks)[-1]]
			if var.name==target and convert_target:
				del df[var.name]
				dummy_ranks=dummy_ranks[list(dummy_ranks)[0]]
				dummy_ranks=pd.DataFrame(dummy_ranks.values, columns=var.name)
				df=pd.merge(df, dummy_ranks, how= 'left', left_index=True, right_index =True)
			elif var.name!=target:
				del df[var.name]
				regressors+=list(dummy_ranks)
				df=pd.merge(df, dummy_ranks, how= 'left', left_index=True, right_index =True)
		elif var.name!=target:
		 	regressors+=[var.name]
	return df, regressors
