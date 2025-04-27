from django.shortcuts import render, redirect
from django import forms
from django.http import HttpResponseRedirect
from . import util
from django.urls import reverse
from django.contrib import messages
import random
import markdown2


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
    entry = util.get_entry(title)
    if entry:
        html_content = markdown2.markdown(entry)
        return render(request, "encyclopedia/title.html", {
            "title": title,
            "entry": html_content
        })
    else:
        messages.error(request, 'Page requested does not exist')
        return HttpResponseRedirect(reverse("encyclopedia:index"))

def search(request):
    query = request.GET.get('q')
    if util.get_entry(query):
        return redirect(f'/wiki/{query}')
    else:
        results = []
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

def edit(request, title):
    entry = util.get_entry(title)

    if entry == None:
        messages.error(request, 'Page not found!')
        return HttpResponseRedirect(reverse("encyclopedia:index"))
    form = CreatePageForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            updated_content = form.cleaned_data["entry_content"]
            util.save_entry(title, updated_content)
            messages.success(request, f'Entry "{title}" has been updated.')
            return redirect("encyclopedia:title", title=title)
    else:
        form = CreatePageForm(initial={
            "entry_name": title,
            "entry_content": entry
        })
    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title
    })

def random_page(request):
    entries = util.list_entries()
    if entries:
        random_title = random.choice(entries)
        return redirect("encyclopedia:title", title=random_title)
    else:
        messages.error(request, 'No entries in encyclopedia!')
        return HttpResponseRedirect(reverse("encyclopedia:index"))