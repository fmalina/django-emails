from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from emails.forms import EmailPreferenceForm
from emails.models import Email, MailoutCategory, MailoutUser

User = get_user_model()


@login_required
def preferences(request, user_pk=None):
    user = request.user
    if user_pk and user.is_staff:
        user = get_object_or_404(User, pk=int(user_pk))

    subs = MailoutUser.objects.filter(user=user)
    form = EmailPreferenceForm(request.POST or None,
                initial={'choices': [s.category.key for s in subs]})

    if form.is_valid():
        for s in subs:
            s.delete()
        for cat in form.cleaned_data['choices']:
            c = MailoutCategory.objects.get(key=cat)
            s = MailoutUser(user=user, category=c)
            s.save()
        messages.success(request, 'Your preferences were updated.')

    return render(request, 'emails/preferences.html', {
        'form': form,
        'u': user
    })


def unsubscribe(request, user_pk, pk, category):
    """Unsubscribe view.

    Checks that email user matches user and proceeds to unsubscribe.
    """
    unsubscribe_user = get_object_or_404(User, pk=user_pk)
    email = get_object_or_404(Email, pk=pk)
    if email.to == unsubscribe_user:
        c = MailoutCategory.objects.get(key=category)
        try:
            s = MailoutUser.objects.get(user=unsubscribe_user, category=c)
            s.delete()
            messages.success(request,
                             'You were unsubscribed from %s.' % c.title.lower())
        except MailoutUser.DoesNotExist:
            messages.info(request, 'You are no longer subscribed.')
    return redirect(unsubscribe_user)
