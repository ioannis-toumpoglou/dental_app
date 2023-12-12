from django import forms

from .models import Patient, MedicalHistory, DentalHistory, Appointment, TreatmentPlan, Financial, Odontogram


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5})}


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        exclude = ['patient']


class DentalHistoryForm(forms.ModelForm):
    class Meta:
        model = DentalHistory
        exclude = ['patient']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['patient']
        widgets = {
            'notes': forms.Textarea(attrs={'style': 'width: 100%;', 'rows': '3'})}


class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        exclude = ['patient']
        widgets = {
            'treatment_plan_notes': forms.Textarea(attrs={'style': 'width: 100%;', 'rows': '7'})}


MOUTH_CHOICES = (
    ('default', 'default'),
    ('black_1', 'black_1'),
    ('black_2', 'black_2'),
    ('black_3', 'black_3'),
    ('black_4', 'black_4'),
    ('black_5', 'black_5'),
    ('brown_1', 'brown_1'),
    ('brown_2', 'brown_2'),
    ('brown_3', 'brown_3'),
    ('brown_4', 'brown_4'),
    ('brown_5', 'brown_5'),
    ('yellow_1', 'yellow_1'),
    ('yellow_2', 'yellow_2'),
    ('yellow_3', 'yellow_3'),
    ('yellow_4', 'yellow_4'),
    ('yellow_5', 'yellow_5'),
    ('endo_top', 'endo_top'),
    ('extracted_top', 'extracted_top'),
    ('for_extraction', 'for_extraction'),
    ('implant_top', 'implant_top'),
    ('endo_side', 'endo_side'),
    ('extracted_side', 'extracted_side'),
    ('implant_side', 'implant_side'),
)


class Tooth11Form(forms.ModelForm):
    tooth_11 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_11', ]


class Tooth12Form(forms.ModelForm):
    tooth_12 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_12', ]


class Tooth13Form(forms.ModelForm):
    tooth_13 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_13', ]


class Tooth14Form(forms.ModelForm):
    tooth_14 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_14', ]


class Tooth15Form(forms.ModelForm):
    tooth_15 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_15', ]


class Tooth16Form(forms.ModelForm):
    tooth_16 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_16', ]


class Tooth17Form(forms.ModelForm):
    tooth_17 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_17', ]


class Tooth18Form(forms.ModelForm):
    tooth_18 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_18', ]


class Tooth21Form(forms.ModelForm):
    tooth_21 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_21', ]


class Tooth22Form(forms.ModelForm):
    tooth_22 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_22', ]


class Tooth23Form(forms.ModelForm):
    tooth_23 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_23', ]


class Tooth24Form(forms.ModelForm):
    tooth_24 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_24', ]


class Tooth25Form(forms.ModelForm):
    tooth_25 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_25', ]


class Tooth26Form(forms.ModelForm):
    tooth_26 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_26', ]


class Tooth27Form(forms.ModelForm):
    tooth_27 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_27', ]


class Tooth28Form(forms.ModelForm):
    tooth_28 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_28', ]


class Tooth31Form(forms.ModelForm):
    tooth_31 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_31', ]


class Tooth32Form(forms.ModelForm):
    tooth_32 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_32', ]


class Tooth33Form(forms.ModelForm):
    tooth_33 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_33', ]


class Tooth34Form(forms.ModelForm):
    tooth_34 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_34', ]


class Tooth35Form(forms.ModelForm):
    tooth_35 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_35', ]


class Tooth36Form(forms.ModelForm):
    tooth_36 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_36', ]


class Tooth37Form(forms.ModelForm):
    tooth_37 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_37', ]


class Tooth38Form(forms.ModelForm):
    tooth_38 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_38', ]


class Tooth41Form(forms.ModelForm):
    tooth_41 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_41', ]


class Tooth42Form(forms.ModelForm):
    tooth_42 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_42', ]


class Tooth43Form(forms.ModelForm):
    tooth_43 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_43', ]


class Tooth44Form(forms.ModelForm):
    tooth_44 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_44', ]


class Tooth45Form(forms.ModelForm):
    tooth_45 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_45', ]


class Tooth46Form(forms.ModelForm):
    tooth_46 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_46', ]


class Tooth47Form(forms.ModelForm):
    tooth_47 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_47', ]


class Tooth48Form(forms.ModelForm):
    tooth_48 = forms.MultipleChoiceField(
        choices=MOUTH_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Odontogram
        fields = ['tooth_48', ]


class FinancialForm(forms.ModelForm):
    class Meta:
        model = Financial
        exclude = ['treatment']
