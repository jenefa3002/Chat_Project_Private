from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import PrivateMessage, UserStatus
from django.shortcuts import render
from django.contrib.auth.models import User

@login_required
@csrf_exempt
def delete_message(request, message_id):
    try:
        message = get_object_or_404(PrivateMessage, id=message_id, sender=request.user)
        if message.is_deleted:
            return JsonResponse({'error': 'Message already deleted'}, status=400)
        message.is_deleted = True
        message.save()
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class LoginRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        # Redirect superusers to the 'superuser_users.html' page and others to 'regularuser_users.html'
        if request.user.is_superuser:
            return redirect('users')  # Adjust the redirect URL for superusers
        else:
            return redirect('other_users')

def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users')
        else:
            return render(request, 'chat/login.html', {'error': 'Invalid credentials'})

    return render(request, 'chat/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})


@csrf_exempt
def save_message(request):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
            message = PrivateMessage.objects.create(
                user=user,
                sender=request.user,  # Add sender
                content=message_content
            )
            return JsonResponse({'status': 'success', 'message_id': message.id}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def user_list_view(request):
    users = User.objects.all()
    if request.user.is_superuser:
        users = User.objects.all()  # All users for superusers
    else:
        users = User.objects.filter(is_superuser=True)  # Only superusers for regular users
    return render(request, 'chat/users.html', {'users': users})

@login_required
def chat_view(request, username):
    user = request.user
    recipient = get_object_or_404(User, username=username)  # Fixed
    messages = PrivateMessage.objects.filter(
        Q(sender=user, recipient=recipient) | Q(sender=recipient, recipient=user)
    ).order_by('timestamp')
    users = User.objects.all()
    return render(request, 'chat/chat.html', {
        'messages': messages,
        'user': user,
        'recipient': recipient,
        'users': users,
        'online_users': UserStatus.objects.filter(is_online=True)
    })

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)
        return JsonResponse({'file_url': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def screenshare_view(request):
    return render(request, 'chat/chat.html')

def users_view(request):
    return render(request, 'chat/users.html')


@login_required
def fetch_new_messages(request, username):
    user = request.user
    messages = PrivateMessage.objects.filter(
        Q(sender__username=username, recipient=user.username) |
        Q(sender=user.username, recipient__username=username)
    ).order_by('-timestamp')

    message_data = [{
        'sender': message.sender.username,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%H:%M')
    } for message in messages]

    return JsonResponse({'messages': message_data})


@login_required
def screen_share(request):
    return render(request, 'chat.html')