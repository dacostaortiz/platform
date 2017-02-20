from django import forms

class UploadBatchForm(forms.Form):
    dev_id = forms.CharField(max_length=50)
    profile = forms.CharField(max_length=50)
    dev_time = forms.CharField(max_length=50)
    chksum = forms.CharField(max_length=50)
    filename = forms.CharField(max_length=50)
    raw = forms.FileField()
