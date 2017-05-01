from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import DataForm, VariableForm, ModelizForm
from .models import Data, Modeliz
import pandas as pd
import numpy as np
from .functions import handle_uploaded_file, default_type, depict

def index(request):
    if request.method == 'POST':
        state=request.session.get("step")
        if state==1 or state==2 :
            pk=request.session.get("id")
            instance=Data.objects.get(pk=pk)
            df=handle_uploaded_file(instance)
            vars_forms={var : VariableForm(request.POST, prefix=var) for var in list(df)}
            instance_vars={var.name : var for var in instance.variable_set.all()}
            target=''
            for  varname in vars_forms.keys():
                if not vars_forms[varname].is_valid():
                    return summary(request)
                elif state==1:
                    var=vars_forms[varname].save(commit=False)
                    var.data=instance
                    var.name=varname
                    var=vars_forms[varname].save()
                else :
                    vars_forms[varname]=vars_forms[varname].clean()
                    instance_vars[varname].type=vars_forms[varname]['type']
                    instance_vars[varname].istarget=vars_forms[varname]['istarget']
                    instance_vars[varname].save()
            instance_vars={var.name : var for var in instance.variable_set.all()}
            target=''
            for var in instance_vars.values():
                if var.istarget==True:
                    target=var

            modform=ModelizForm(request.POST, prefix="modelling")
            if not modform.is_valid():
                print(modform)
                return summary(request)
            else:
                modele=modform.save(commit=False)
                modele.data=instance
                if target!='' :
                    modele.target=target
                modele=modform.save()
                request.session["step"]=2
                request.session["model"]=modele.pk
                return modelling(request)

        else:
            form = DataForm(request.POST, request.FILES)
            if form.is_valid():
                data=form.save()
                data.create()
                request.session["id"]=data.pk
                request.session["step"]=1
                return summary(request)
    else:
        form = DataForm()
        request.session["step"]=0
    return render(request, 'index.html', {'form': form})

def summary(request):
    pk=request.session.get("id")
    data=Data.objects.get(pk=pk)
    df=handle_uploaded_file(data)
    summary, qtvar_names, summary2, qlvar_names=depict(data)
    dico_forms={}
    for var in list(df):
        form=VariableForm(prefix=var)
        form.fields['type'].initial = default_type(df[var])
        dico_forms[var]=form
    form = ModelizForm(prefix="modelling")
    return render(request, 'formats.html', {'dico_forms': dico_forms,'model_form': form, 'summary':summary, 'summary2':summary2, "quanti":qtvar_names, "quali":qlvar_names})

def modelling(request):
    pk=request.session.get("id")
    data=Data.objects.get(pk=pk)
    sk=request.session.get("model")
    modele=Modeliz.objects.get(pk=sk)
    output, template=modele.create()
    dico_forms={}
    for variable in data.variable_set.all():
        var=variable.name
        form=VariableForm(prefix=var)
        form.fields['type'].initial = variable.type
        form.fields['istarget'].initial= variable.istarget
        dico_forms[var]=form
    output["dico_forms"]=dico_forms
    model_form = ModelizForm(prefix="modelling")
    model_form.fields['name'].initial=modele.name
    output["model_form"]= model_form
    summary, qtvar_names, summary2, qlvar_names=depict(data, types=True)
    output["summary"]= summary
    output["quanti"]= qtvar_names
    output["summary2"]= summary2
    output["quali"]= qlvar_names
    return render(request, template, output)
