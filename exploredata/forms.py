from .models import Data, Variable, Modeliz
from django import forms


class DataForm(forms.ModelForm):
    class Meta:
        model=Data
        fields=["file", "header", "index_col"]


class VariableForm(forms.ModelForm):
    class Meta:
        model=Variable
        fields=["type", "istarget"]


class ModelizForm(forms.ModelForm):
    class Meta:
        model=Modeliz
        fields=["name", "test_size", "intercept", "n_neighbors", "n_clusters"]
    def clean(self):
        name = self.cleaned_data.get('name')
        predictive_models=['L', 'K']
        if name in predictive_models:
            self.fields['test_size'].required=True
        else:
            self.cleaned_data['test_size'] = 0
        if name =='L':
            self.fields['intercept'].required=True
        elif name=='K':
            self.fields['n_neighbors'].required=True
        elif name=='KM':
            self.fields['n_clusters'].required=True
        return self.cleaned_data
