from django import forms

class OrderCancellationForm(forms.Form):
    reason = forms.CharField(
        widget = forms.Textarea(attrs={
            'class' : 'form-control',
            'placeholder' : 'Please provide reason for cancellation..',
            'rows' : 4,
        }),
        label='Cancellation Reason',
        max_length=500,
        required=True
    )

class ReturnReasonForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Provide a reason for return...',
            'rows': 4,
        }),
        label='Return Reason',
        max_length=500,
        required=True
    )  