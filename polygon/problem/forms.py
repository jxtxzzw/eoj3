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


class TestCreateForm(forms.Form):
    create_method = forms.ChoiceField(choices=(
        ('manual', 'Add a case via manual input and output (optional)'),
        ('input', 'Upload an archive with input files'),
        ('match', 'Upload an archive with matched "in" and "out"'),
        ('gen', 'Add cases via generator commands'),
    ))
    case_order = forms.CharField(initial='$', max_length=10, label='Add this after #',
                                 help_text='Use $ to number test cases automatically')
    upload = forms.FileField(required=False)
    input = forms.CharField(widget=forms.Textarea, required=False)
    output = forms.CharField(widget=forms.Textarea, required=False)
    generate_cmd = forms.CharField(widget=forms.Textarea, required=False, label='Generate commands',
                                   help_text='Use name + args, such as "gen 2 3 5"\n'
                                             'If your generator generates several files to the working directory '
                                             'at the same time, you should specify the file names, \nsuch as "'
                                             'gen 2 3 5 > {1.in, 2.in, 3.in, input.txt}"')
    description = forms.CharField(widget=forms.Textarea, required=False)
    group = forms.CharField(widget=forms.TextInput, required=False)
    manual_output_lock = forms.BooleanField(label='Lock this output (to prevent overwrite)', required=False)
    show_in_samples = forms.BooleanField(required=False)
    show_in_pretests = forms.BooleanField(required=False)
    show_in_tests = forms.BooleanField(initial=True, required=False)
