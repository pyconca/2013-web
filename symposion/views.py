import hashlib
import random

from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

import account.views

import symposion.forms
from symposion.reviews.models import Review, ReviewAssignment


class SignupView(account.views.SignupView):
    
    form_class = symposion.forms.SignupForm
    form_kwargs = {
        "prefix": "signup",
    }
    
    def create_user(self, form, commit=True):
        user_kwargs = {
            "first_name": form.cleaned_data["first_name"],
            "last_name": form.cleaned_data["last_name"]
        }
        return super(SignupView, self).create_user(form, commit=commit, **user_kwargs)

    def generate_username(self, form):
        def random_username():
            h = hashlib.sha1(form.cleaned_data["email"]).hexdigest()[:25]
            # don't ask
            n = random.randint(1, (10 ** (5 - 1)) - 1)
            return "%s%d" % (h, n)
        while True:
            try:
                username = random_username()
                User.objects.get(username=username)
            except User.DoesNotExist:
                break
        return username


class LoginView(account.views.LoginView):

    form_class = account.forms.LoginEmailForm
    form_kwargs = {
        "prefix": "login",
    }


@login_required
def dashboard(request):
    if request.session.get("pending-token"):
        return redirect("speaker_create_token", request.session["pending-token"])
    unvoted_proposal_assignments = set([
        review_assignment
        for review_assignment in ReviewAssignment.objects.filter(user=request.user)
        if Review.objects.filter(
            user=request.user, proposal=review_assignment.proposal).count() == 0])
    return render(request, "dashboard.html", {
        'unvoted_proposal_assignments': unvoted_proposal_assignments})
