from django.shortcuts import render, render_to_response, get_list_or_404, get_object_or_404, HttpResponseRedirect,HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .models import *


def post_category_popup(request):
    form = PostCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_title");</script>' % (instance.pk, instance))
    context = locals()
    return render(request, 'blog/popups/category_popup.html', context)

@csrf_exempt
def get_category_id(request):
    if request.is_ajax():
        category_title = request.GET['category_title']
        category_id = PostCategory.objects.get(title=category_title).id
        data = {'category_id':category_id}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse('/')






