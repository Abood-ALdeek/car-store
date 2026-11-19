from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Hidden trap field: real people leave it empty, spam bots fill it in.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = sum(ch.isdigit() for ch in phone)
        if digits < 7:
            raise forms.ValidationError("رقم غير صحيح / Invalid number")
        return phone

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
