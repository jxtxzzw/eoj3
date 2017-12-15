from django import forms
from tagging.models import Tag

from polygon.models import RepositorySource, RepositoryTest
from problem.models import Problem
from utils import random_string
from utils.multiple_choice_field import CommaSeparatedMultipleChoiceField


class ProblemEditForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'alias', 'time_limit', 'memory_limit', 'description', 'input', 'output',
                  'hint', 'source']
        error_messages = {
        }
        widgets = {
            'description': forms.Textarea(attrs={'class': 'markdown'}),
            'input': forms.Textarea(attrs={'class': 'markdown'}),
            'output': forms.Textarea(attrs={'class': 'markdown'}),
            'hint': forms.Textarea(attrs={'class': 'markdown'}),
        }

    tags = CommaSeparatedMultipleChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProblemEditForm, self).__init__(*args, **kwargs)
        new_order = ['title', 'alias', 'time_limit', 'memory_limit', 'description',
                     'input', 'output', 'hint', 'tags', 'source']
        self.fields = type(self.fields)((k, self.fields[k]) for k in new_order)
        if self.instance:
            self.fields['tags'].initial = ','.join(map(str, self.instance.tags))
            self.fields['tags'].choices = [(i, i) for i in Tag.objects.all()]

    def clean(self):
        cleaned_data = super().clean()
        used_tag = []
        if 'tags' in cleaned_data:
            for tag in cleaned_data['tags']:
                if Tag.objects.filter(name=tag).exists():
                    used_tag.append(tag)
        cleaned_data['tags'] = ', '.join(used_tag)
        if ',' not in cleaned_data['tags']:
            cleaned_data['tags'] = "\"%s\"" % cleaned_data['tags']
        return cleaned_data


class SourceEditForm(forms.ModelForm):
    class Meta:
        model = RepositorySource
        exclude = ['modified', 'author', 'workspace', 'problem', 'length']


class TestCreateForm(forms.ModelForm):
    class Meta:
        model = RepositoryTest
        fields = ['manual_output_lock', 'show_in_samples', 'show_in_pretests', 'show_in_tests', 'description',
                  'case_number', 'group']

    input = forms.CharField(widget=forms.Textarea, required=False)
    output = forms.CharField(widget=forms.Textarea, required=False)
    generate_cmd = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        new_order = ['case_number', 'input', 'output', 'generate_cmd', 'description', 'group',
                     'manual_output_lock', 'show_in_samples', 'show_in_pretests', 'show_in_tests', ]
        self.fields = type(self.fields)((k, self.fields[k]) for k in new_order)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        return cleaned_data
