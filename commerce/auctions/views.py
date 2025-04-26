from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Auction, Bids, Comments
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class CreateAuction(forms.Form):
    title = forms.CharField(
        label="Title", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    starting_bid = forms.DecimalField(
        label="Starting Bid", 
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    image_url = forms.URLField(
        label="Image URL (optional)", 
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    category = forms.CharField(
        label="Category (optional)",
        required=False,
        max_length=64, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

class BidListing(forms.Form):
    bid_amount = forms.DecimalField(
        label="Bid Amount", 
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', "placeholder": "Bid"})
    )

class CreateComment(forms.Form):
    comment = forms.CharField(
        label="Comment", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "Comment"})
    )

class WatchlistForm(forms.Form):
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')])


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateAuction(request.POST)
        if form.is_valid():
            auction = Auction(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                starting_bid=form.cleaned_data["starting_bid"],
                final_price=form.cleaned_data["starting_bid"],
                image_url=form.cleaned_data["image_url"],
                category=form.cleaned_data["category"],
                owner = request.user
            )
            auction.save()

            return HttpResponseRedirect(reverse("index"))

    else:
        form = CreateAuction()

    
    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def listing(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    comments = Comments.objects.filter(listing=auction)
    form = BidListing()
    comment_form = CreateComment()
    watchlist_form = WatchlistForm()
    return render(request, "auctions/listing.html", {
        "auction": auction,
        "form": form,
        "comments": comments,
        "comment_form": comment_form,
        "watchlist_form": watchlist_form

    })

@login_required
def bid(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        form = BidListing(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data["bid_amount"]

            current_price = auction.final_price
            
            if bid_amount <= current_price:
                return HttpResponseRedirect(reverse("index"))
            
            Bids.objects.create(
                amount=bid_amount,
                user=request.user,
                listing=auction
            )

            auction.final_price = bid_amount
            auction.save()

            return HttpResponseRedirect(reverse("listing", args=[auction.id]))
    else:
        return HttpResponseRedirect(reverse("listing", args=[auction.id]))
    

@login_required
def close_auction(request, auction_id):
    if request.method == "POST":
        try:
            auction = Auction.objects.get(pk=auction_id)
        except:
            messages.error(request, "No Auction Found")
            return HttpResponseRedirect(reverse("index"))
        if auction.is_active:
            if request.user == auction.owner:
                auction.is_active = False
                try:
                    highest_bid = auction.bids.order_by('-amount').first()
                    auction.winner = highest_bid.user
                except:
                    messages.error(request, "No one has bidded. Cannot Close Auction")
                    return HttpResponseRedirect(reverse("listing", args=[auction.id]))
                auction.save()
                messages.success(request, "Auction closed successfully!")
            else:
                messages.error(request, "No Permission to close auction")
                return HttpResponseRedirect(reverse("index"))
        else:
            messages.info(request, "Auction is already closed.")

    return HttpResponseRedirect(reverse("listing", args=[auction.id]))


@login_required
def create_comment(request, auction_id):
    if request.method == "POST":
        try:
            auction = Auction.objects.get(pk=auction_id)
        except:
            messages.error(request, "No Auction Found")
            return HttpResponseRedirect(reverse("index"))
        form = CreateComment(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            Comments.objects.create(
                    comment=comment,
                    user=request.user,
                    listing=auction
                )
            messages.success(request, "Comment posted successfully!")
            return HttpResponseRedirect(reverse("listing", args=[auction.id]))
        else:
            messages.error(request, "Invalid form data.")
            return HttpResponseRedirect(reverse("listing", args=[auction.id]))
    return HttpResponseRedirect(reverse("index"))


@login_required
def manage_watchlist(request, auction_id):
    if request.method == "POST":
        try:
            auction = Auction.objects.get(pk=auction_id)
        except:
            messages.error(request, "No Auction Found")
            return HttpResponseRedirect(reverse("index"))
        form = WatchlistForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            user = request.user
            if action == "add":
                user.watchlist.add(auction)
                messages.success(request, "Added to Watchlist!")
            elif action == "remove":
                user.watchlist.remove(auction)
                messages.success(request, "Removed from Watchlist!")
        else:
            messages.error(request, "Invalid form.")
        return HttpResponseRedirect(reverse("listing", args=[auction.id]))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    user = request.user
    watchlist_auctions = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist_auctions
    })



def categories(request):
    categories = Auction.objects.filter(category__isnull=False).values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category):
    auctions = Auction.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "category": category,
        "auctions": auctions
    })
