from web.organizations.models import Organization
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from .forms import *
from web.users.auth import auth_test
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from web.users.auth import user_passes_test
from django.views.decorators.http import require_http_methods
import json
from web.users.statics import REDACTIE


@user_passes_test(auth_test, user_type=REDACTIE)
def manage_timeline(request):
    organization_list = Organization.objects.all()
    Moment_FormSet = modelformset_factory(Moment, form=MomentForm, extra=1, can_delete=True)
    if request.method == 'POST':
        formset = Moment_FormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            instances = formset.save()
            for instance in instances:
                instance.save()
            for object in formset.deleted_objects:
                object.delete()
            return HttpResponseRedirect(reverse('manage_timeline'))

    else:
        formset = Moment_FormSet()
    return render(request, 'timeline/manage_moments.html', {
        'moment_form_set': formset,
        'form': MomentForm(),
        'organization_list': organization_list,
    })


@require_http_methods(["POST"])
@user_passes_test(auth_test, user_type=REDACTIE)
def update_moment(request):
    status_code = 400
    message = 'error'
    if request.is_ajax():
        m = dict((k, v) for k, v in json.loads(request.body).items())
        instance = {'instance': get_object_or_404(Moment, id=int(m.get('id', 0)))} if m.get('id') else {}
        form = MomentForm(m, **instance)
        if form.is_valid():
            instance = form.save()
            status_code = 200 if m.get('id') else 201
            message = instance.to_dict()
        else:
            status_code = 422
            message = form.errors
    return JsonResponse({'message': message}, status=status_code)


@require_http_methods(["POST"])
@user_passes_test(auth_test, user_type=REDACTIE)
def delete_moment(request):
    status_code = 400
    message = 'error'
    if request.is_ajax():
        m = dict((k, v) for k, v in json.loads(request.body).items())
        instance = get_object_or_404(Moment, id=int(m.get('id', 0)))
        instance.delete()
        status_code = 200
        message = {'deleted': instance.id}
    return JsonResponse({'message': message}, status=status_code)


@require_http_methods(["POST"])
@user_passes_test(auth_test, user_type=REDACTIE)
def create_moment(request):
    status_code = 400
    message = 'error'
    if request.is_ajax():
        model_dict = dict((k, v) for k, v in json.loads(request.body).items())
        form = MomentForm(model_dict)
        if form.is_valid():
            instance = form.save()
            status_code = 201
            message = {'id': instance.id}
        else:
            status_code = 422
            message = form.errors
    return JsonResponse({'message': message}, status=status_code)


@require_http_methods(["POST"])
@user_passes_test(auth_test, user_type=REDACTIE)
def order_timeline(request):
    if request.is_ajax():
        data = json.loads(request.body)
        data_dict = dict(('%s' % o['id'], o['order']) for o in data)
        moment_list = [{'m': m, 'order': data_dict['%s' % m.id]} for m in Moment.objects.filter(id__in=[o['id'] for o in data])]
        for moment in moment_list:
            moment['m'].order = moment['order']
        Moment.objects.bulk_update([m['m'] for m in moment_list], ['order'])
        return JsonResponse({'message': 'Data is saved'}, status=200)
    return JsonResponse({'message': 'error'}, status=400)


