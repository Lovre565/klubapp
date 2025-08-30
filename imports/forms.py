from django import forms

class UploadCSVForm(forms.Form):
    file = forms.FileField(help_text="CSV s kolonama: first_name,last_name,dob,position")
    dry_run = forms.BooleanField(initial=True, required=False, widget=forms.HiddenInput)
    payload = forms.CharField(required=False, widget=forms.HiddenInput)  # za commit korak
