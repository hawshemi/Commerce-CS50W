from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Watchlist, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().filter(active = True),
        "bids": Bid.objects.all(),
        "header": "This is where you see all the active listings."
    })

def inactive(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().filter(active = False),
        "bids": Bid.objects.all(),
        "header": "This is where you see all the inactive listings."
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

def create(request):
    
    if request.method == "POST":
        
        if not request.user.is_authenticated:
            return render(request, "auctions/create.html", {
                "message": "You can't make a listing without logging in."
            })
        
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        img_url = request.POST['img_url']
        category = request.POST['category']
        user = request.user
        
        l = Listing.objects.create(title = title,
                              category = category,
                              starting_bid = starting_bid,
                              description = description,
                              img_url = img_url,
                              user = user)
        l.save()
        
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/create.html")

def listing(request, listing_id):
    l = Listing.objects.filter(id = listing_id).first()
    b = Bid.objects.filter(listing = l)
    c = Comment.objects.filter(listing = l)
    
    highest_bid = l.starting_bid
    
    if b is not None:
        
        for bid in b:
            if bid.value > highest_bid:
                highest_bid = bid.value
        
    #in case a bid or a commetn is posted
    if request.method == 'POST':
        value = request.POST.get('bid_price', None)
        user = request.user
        listing = Listing.objects.filter(id = listing_id).first()
        comment = request.POST.get('comment', None)
        
        try:
            value = int(value)
        except:
            value = None
        
        if comment is not None:
            c = Comment.objects.create(content = comment, user = user, listing = listing)
            c.save()
            
            return HttpResponseRedirect(reverse('listing', args = [listing_id]))
        
        if value is not None:
            if int(value) < highest_bid:
                
                return HttpResponseRedirect(reverse('listing', args = [listing_id]))
            
            b = Bid.objects.create(value = int(value), user = user, listing = listing)
            b.save()
            
            bs = Bid.objects.filter(listing = listing).exclude(value = value)
            bs.delete()
            
            return HttpResponseRedirect(reverse('listing', args = [listing_id]))
        
        if value is None and comment is None:
            return render(request, "auctions/error.html", {
                "error": "Either make a comment or bid."
            })
        
    return render(request, "auctions/listing.html", {
        "listing": l,
        "highest_bid": highest_bid,
        "min_bid": (highest_bid + 1),
        "comments": c
    })
    
def categories(request):
    l = []
    li = Listing.objects.all()
    
    for listing in li:
        if listing.category:
            if listing.category not in l:
                l.append(listing.category)
                
    return render(request, "auctions/categories.html", {
        "categories": l
    })

def category_listing(request, category):
    l = Listing.objects.all().filter(category = category)
    return render(request, "auctions/category_listing.html", {
        "listings": l
    })

def toggle_watchlist(request, listing_id):
    
    user = request.user
    l = Listing.objects.filter(id = listing_id).first()
    
    w = Watchlist.objects.filter(user = user, listing = l).first()
    
    if w is None:
        wl = Watchlist.objects.create(user = user,
                                      listing = l)
        wl.save()
        return HttpResponseRedirect(reverse("watchlist"))
    
    w.delete()
    return HttpResponseRedirect(reverse("watchlist"))

@login_required
def watchlist(request):
    
    user = request.user
    wl = Watchlist.objects.filter(user = user)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": wl
    })

@login_required
def close(request, listing_id):
    
    l = Listing.objects.filter(id = listing_id).first()
    b = Bid.objects.filter(listing = l).first()
    
    if l.user == request.user and not b is None:
        l.active = False
        l.winner = b.user
        
        l.save()
        
        return HttpResponseRedirect(reverse('index'))
    
    elif l.user == request.user and b is None:
        l.active = False
        
        l.save()
        
        return HttpResponseRedirect(reverse('index'))
    
    else:
        return render(request, "auctions/error.html", {
            "error": "You cannot close other's listings."
        })