from django import forms
from django.utils.translation import gettext_lazy as _
from .statics import FIELDS_DICT, FIELDS_REQUIRED_DICT
from django.forms.utils import ErrorDict, ErrorList
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
import copy
import json


class BaseGenericForm:
    sections = []
    options = {}

    @staticmethod
    def _get_fields(sections):
        sections = [] if not sections else [
            fff for f in sections for ff in f.get('section_list', []) for fff in ff.get('fields', [])
        ]
        return sections

    def as_sections(self):
        return self._html_section_output(
            normal_row='<div %(wrapper_id_attr)s %(html_class_attr)s %(data_attr)s>%(label)s %(help_text)s %(field)s %(errors)s</div>',
            checkbox_row='<div %(wrapper_id_attr)s %(html_class_attr)s %(data_attr)s>%(help_text)s %(field)s %(label)s %(errors)s</div>',
            clearablefileinput_row='<div %(wrapper_id_attr)s %(html_class_attr)s %(data_attr)s>%(help_text)s %(field)s %(label)s %(errors)s <div id="file-upload-filename" class="form-field__uploaded"></div></div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <div class="help-text">%s</div>',
            errors_on_separate_row=True)

    def _html_section_output(self, normal_row, checkbox_row, clearablefileinput_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        "Output HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors()  # Errors that should be displayed above all fields.
        output, sections_output, hidden_fields = [], {}, []
        sections = copy.deepcopy(self.sections)

        for name, field in self.fields.items():
            html_class_attr = ''
            data_attr = ''
            row = normal_row
            bf = self[name]
            wrapper_id = ' id="form-field-%s"' % name
            bf_type = bf.field.widget.__class__.__name__.lower()
            bf_is_empty = not bool(bf.value())
            rules = self.options.get('rules', {}).get(name)
            if rules:
                data_attr = " data-decorator='form-rule' data-rule-data='%s' " % (
                    json.dumps(rules),
                )

            if bf_type == 'checkboxinput':
                row = checkbox_row
            if bf_type == 'clearablefileinput':
                row = clearablefileinput_row

            # Escape and cache in local variable.
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(
                        [_('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)}
                         for e in bf_errors])
                hidden_fields.append(str(bf))
            else:
                # Create a 'class="..."' attribute if the row should have any
                # CSS classes applied.
                css_classes = bf.css_classes('form-field form-field--%s%s%s%s%s' % (
                    bf_type,
                    ' form-field--step-required' if FIELDS_REQUIRED_DICT.get(bf.name) else '',
                    ' form-field--complete' if not bf_is_empty else '',
                    ' form-field--error' if bf_errors else '',
                    ' form-field--empty' if bf_is_empty else '',
                ))
                # css_classes += ' form-field form-field--%s' % bf_type
                if css_classes:
                    html_class_attr = ' class="%s"' % css_classes
                if bf.label:
                    label = conditional_escape(bf.label)
                    if bf.field.required or FIELDS_REQUIRED_DICT.get(bf.name):
                        label = '%s *' % label
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % field.help_text
                else:
                    help_text = ''
                obj = {
                    'errors': error_row % str(bf_errors),
                    'label': label,
                    'field': bf,
                    'name': name,
                    'help_text': help_text,
                    'html_class_attr': html_class_attr,
                    'data_attr': data_attr,
                    'wrapper_id_attr': wrapper_id,
                    'css_classes': css_classes,
                    'field_type': bf_type,
                    'field_step_complete': not FIELDS_REQUIRED_DICT.get(bf.name) or not bf_is_empty,
                    'verbose_name': bf.label,
                }
                sections_output[name] = {
                    'rendered': mark_safe(row % obj),
                    'object': obj
                }
        if top_errors:
            output.insert(0, error_row % top_errors)

        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = ''.join(hidden_fields)
            output.append(str_hidden)

        section_with_fields = [dict((k, v if not isinstance(v, list) else [
                dict((kk, vv if not isinstance(vv, list) else [
                    sections_output.get(sss, {}) for sss in vv
                ]) for kk, vv in ss.items()) for ss in v
            ]) for k, v in section.items()) for section in sections]
        for section in section_with_fields:
            section['step_complete'] = True
            for k, v in section.items():
                if isinstance(v, list):
                    for ss in v:
                        sub_step_complete = not bool([kk for kk, vv in ss.items() if isinstance(vv, list) and [sss for sss in vv if not sss.get('object', {}).get('field_step_complete')]])
                        ss['step_complete'] = sub_step_complete
                        if not sub_step_complete:
                            section['step_complete'] = False

        return {
            'errors': mark_safe('\n'.join(output)),
            'hidden_fields': mark_safe(''.join(hidden_fields)),
            'sections': section_with_fields
        }


class GenericForm(BaseGenericForm, forms.Form):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None, sections=[]):

        self.sections = sections

        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)

        for f in self._get_fields(self.sections):
            self.fields[f] = FIELDS_DICT[f]


class GenericModelForm(BaseGenericForm, forms.ModelForm):

    def save(self, commit=True):
        return super().save(commit)

    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop('path')
        form_config = kwargs.pop('form_config')
        super().__init__(*args, **kwargs)
        self.fields = {}
        self.sections = form_config.get('sections', [])
        self.form_config_slug = form_config.get('form_config_slug')
        self.federation_types = form_config.get('federation_types', [])
        self.options = form_config.get('options', {})
        exclude_fields = self.options.get('exclude_fields', [])

        for f in self._get_fields(self.sections):
            if f not in exclude_fields:
                self.fields[f] = FIELDS_DICT.get(f)
