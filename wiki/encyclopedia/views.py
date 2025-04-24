from django.shortcuts import render, redirect
from django import forms
from django.http import HttpResponseRedirect
from . import util
from django.urls import reverse
from django.contrib import messages



class CreatePageForm(forms.Form):
    entry_name = forms.CharField(label="Entry Name", max_length=100)
    entry_content = forms.CharField(
        label="Entry Content",
        widget=forms.Textarea(attrs={
            "rows": 4,
            "cols": 10,
            "placeholder": "Content goes here",
            "style": "resize:vertical;" 
        })
    )


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title):
    return render(request, "encyclopedia/title.html", {
        "title": title,
        "entry": util.get_entry(title)
    })

def search(request):
    query = request.GET.get('q')
    results = []
    if util.get_entry(query):
        return redirect(f'/wiki/{query}')
    else:
        entries = util.list_entries()
        for entry in entries:
            if query.lower() in entry.lower():
                results.append(entry)
        
        return render(request, "encyclopedia/search_results.html", {
            "query": query,
            "results": results
        })
    
def create(request):
    if request.method == "POST":
        form = CreatePageForm(request.POST)
        if form.is_valid():
            entry_name = form.cleaned_data["entry_name"]
            if not entry_name:
                messages.error(request, 'Please provide the entry name!')
            entry_content = form.cleaned_data["entry_content"]
            if not entry_content:
                messages.error(request, 'Please provide the entry content!')
            check_entry = util.get_entry(entry_name)
            if check_entry:
                messages.error(request, f'An entry titled "{entry_name}" already exists.')
                return render(request, "encyclopedia/create.html", {
                "form": form
            })
            else:
                util.save_entry(entry_name, entry_content)
                messages.success(request, f'Entry "{entry_name}" was created successfully.')
                return HttpResponseRedirect(reverse("encyclopedia:index"))
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })
    return render(request, "encyclopedia/create.html", {
        "form": CreatePageForm()
    })