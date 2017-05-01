import re
import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.cluster import KMeans
import statsmodels.api as sm
from .functions import handle_uploaded_file, default_type, depict, convert

#Linear model
def lin_model(modele):
	df=handle_uploaded_file(modele.data, types=True)
	target=modele.target.name
	df, regressors=convert(df, modele.data.variable_set.all(), target)
	X=sm.add_constant(df[regressors].values, prepend=False)
	regr=sm.OLS(df[target].values, X).fit()
	#print(regr.summary())
	coef=[["Intercept" , round(regr.params[0],3),  str(round(regr.pvalues[0]*100, 2))+"%"]]
	regressors=[re.sub(r"__", " = ", var_name) for var_name in regressors]
	for i in range(len(regressors)):
		coef+=[[regressors[i], round(regr.params[i+1],3), str(round(regr.pvalues[i+1]*100,2))+"%"]]
	output = {'coeff' : coef, 'mse' :  round(regr.mse_resid,3), 'AdjRsquared' : str(round(regr.rsquared_adj*100,2))+"%",
	 "fisher" : [round(regr.fvalue,3), str(round(regr.f_pvalue*100, 2))+"%"]}
	return output

def knn(modele):
	df=handle_uploaded_file(modele.data, types=True)
	target=modele.target.name
	df, regressors=convert(df, modele.data.variable_set.all(), target, convert_target=False)
	print(df.head())
	X_train, X_test, Y_train, Y_test = train_test_split( df[regressors].values, df[target].values, test_size=modele.test_size/100)
	classifieur=KNeighborsClassifier().fit(X_train, Y_train)
	Y_test_pred=classifieur.predict(X_test)
	features=np.unique(df[target].values)
	confu_mat=confusion_matrix(Y_test, Y_test_pred, labels=features)
	n=len(features)
	confu_mat_out=[]
	for i in range(n):
		line_tot=sum(confu_mat[i])
		if line_tot>0:
			confu_mat_out+=[[features[i]]+[str(round(confu_mat[i][j]/line_tot*100, 2))+"%" for j in range(n)]]
		else :
			confu_mat_out+=[[features[i]]+["0%" for j in range(n)]]
	output= {"confu" : confu_mat_out, "score_train" : str(round(classifieur.score(X_train, Y_train)*100, 2))+"%",
	"score_test" : str(round(classifieur.score(X_test, Y_test)*100, 2))+"%", "features" : features}
	return output

def km(modele):
	df=handle_uploaded_file(modele.data, types=True)
	df, regressors=convert(df, modele.data.variable_set.all(), target=False)

	cluster=KMeans().fit(df.values)
	centers=cluster.cluster_centers_
	print(centers[0])
	n=len(centers)
	table_out=[]
	for i in range(n):
		line=["Cluster "+str(i)]
		line+=list(centers[i])
		table_out.append(line)
	score = cluster.score(df.values)
	output= {"table" : table_out, "score" : str(round(score*100, 2))+"%", "features" : list(df)}
	return output
