from django.db import models
from .modelization import lin_model, knn, km
from .functions import handle_uploaded_file, default_type, depict
import pandas as pd
import numpy as np

class Data(models.Model):

    file= models.FileField(upload_to='uploads/')
    title=models.CharField(max_length=30)
    header = models.BooleanField(default=False)
    index_col = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def create(self):
        self.title=self.file.name
        self.save()

    def getdf(self):
        return(handle_uploaded_file(self))



class Variable(models.Model):
    data=models.ForeignKey(Data)
    name=models.CharField(max_length=30)
    type=models.CharField(max_length=3,
    choices = ([('B', 'Binaire'),
    ('QT', 'Quantitative'),
    ('QL', 'Categorielle'),
    ('QL_OR', 'Categorielle ordonnee'), ]))
    istarget = models.BooleanField()
    def create(self, data, name):
        self.data = data
        self.name= name
        self.type=default_type(self.values)
    def __str__(self):
        return self.name

class Modeliz(models.Model):
    data=models.ForeignKey(Data)
    name=models.CharField(max_length=3,
    choices = ([('L', "Linear"), ('K', "K-Nearest Neighbors"), ('KM', "K-Means"),]))
    test_size=models.IntegerField(choices=((i,str(i)+"%" ) for i in range(51)), blank=True,
    help_text="Only required if a predictive model is selected.")
    target=models.ForeignKey(Variable,  blank=True, null=True)
    intercept=models.NullBooleanField(blank=True, null=True)
    n_neighbors=models.IntegerField(blank=True, null=True)
    n_clusters=models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name
    def create(self):
        if self.name=="L":
            output = lin_model(self)
            template="linear.html"
        elif self.name=="K":
            output = knn(self)
            template="knn.html"
        elif self.name=="KM":
            output = km(self)
            template="km.html"
        return output, template
