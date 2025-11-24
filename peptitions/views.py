from django.shortcuts import render, redirect, HttpResponse, get_object_or_404 # type: ignore
from django.contrib.auth import login, authenticate, logout # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test # type: ignore
from .forms import *
from .models import *
from django.contrib.auth.forms import AuthenticationForm # type: ignore
from django.contrib import messages # type: ignore
from django.utils import timezone # type: ignore
from datetime import timedelta
from django.db.models import Count, F # type: ignore
from django.db.models import Q # type: ignore


# --------- Authentications / Home  -------
def index(request):
    return render(request, "peptitions/homePage/index.html")


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after registration
            return redirect("index")
    else:
        form = UserRegisterForm()
    return render(request, "peptitions/homePage/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Redirect based on role
            if user.is_staff or user.is_superuser:  
                return redirect("dashboard")  # Django admin dashboard
            else:
                return redirect("board")  # Your custom user dashboard
    else:
        form = AuthenticationForm()

    return render(request, "peptitions/homePage/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting superusers
    if user.is_superuser:
        messages.error(request, "You cannot delete an admin user.")
        return redirect("user-list")

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("user-list")


# --- Dashboard View ---
@login_required
def dashboard_view(request):
    total_petitions = Petition.objects.count()
    pending_petitions = Petition.objects.filter(status="pending").count()
    total_users = User.objects.count()

    recent_petitions = Petition.objects.order_by("-created_at")[:3]

    # ✅ Chart data (group petitions by status)
    petition_status_data = (
        Petition.objects.values("status")
        .annotate(count=Count("id"))
    )

    statuses = [item["status"].capitalize() for item in petition_status_data]
    counts = [item["count"] for item in petition_status_data]

    context = {
        "total_petitions": total_petitions,
        "pending_petitions": pending_petitions,
        "total_users": total_users,
        "recent_petitions": recent_petitions,
        "statuses": statuses,
        "counts": counts,
    }
    return render(request, "peptitions/adminPage/dashboard.html", context)


@login_required
def petition_list(request):
    petitions = Petition.objects.all().order_by("-created_at")  # newest first

    if request.method == "POST":
        form = PetitionForm(request.POST, request.FILES)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user  # assuming you have a FK to User
            petition.save()
            return redirect("petition_list")  # refresh list after creation
    else:
        form = PetitionForm()

    return render(request, "peptitions/adminPage/petition-list.html", {
        "petitions": petitions,
        "form": form
    })


def petition_detail(request, pk):
    petition = get_object_or_404(Petition, id=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approved":
            petition.status = "approved"
            petition.save()
            messages.success(request, f'Petition "{petition.title}" has been approved.')
        elif action == "rejected":
            petition.status = "rejected"
            petition.save()
            messages.success(request, f'Petition "{petition.title}" has been rejected.')
        elif action == "delete":
            # Delete the petition
            petition_title = petition.title
            petition.delete()
            messages.success(request, f'Petition "{petition_title}" has been permanently deleted.')
            return redirect("petition-list")  # redirect to list page after deletion
        
        return redirect("petition-list")  # redirect to list page after action

    context = {"petition": petition}
    return render(request, "peptitions/adminPage/petition-detail.html", context)


@login_required
def user_list(request):
    users = User.objects.all() 
    one_week_ago = timezone.now() - timedelta(days=7)
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(last_login__isnull=False).count(),  # Simplified
        'new_this_week': users.filter(created_at__gte=one_week_ago).count(),
        'total_petitions': Petition.objects.count(),
    }
    return render(request, "peptitions/adminPage/user-list.html", context)


@login_required
def search_p(request):
    query = request.GET.get('q', '')
    petitions = Petition.objects.all()

    if query:
        petitions = Petition.objects.filter(
            Q(title__icontains = query)|
            Q(description__icontains=query)
        )
    context = {
        'petitions': petitions,
        'query': query,
        'results_count': petitions.count()
    }
    return render(request, "peptitions/adminPage/search-p.html", context)



# --- User Dashboard View ---
@login_required
def board_view(request):
    # Get IDs of petitions signed by the current user
    signed_petitions = Signature.objects.filter(
        user=request.user
    ).values_list("petition_id", flat=True)

    # Only approved petitions, excluding the ones already signed
    petitions = Petition.objects.filter(
        status="approved"
    ).exclude(id__in=signed_petitions).order_by("-created_at")
    
    # Calculate statistics for the dashboard AND sidebar
    total_petitions = petitions.count()
    my_signatures = Signature.objects.filter(user=request.user).count()
    my_petitions_count = Petition.objects.filter(created_by=request.user).count()
    trending_petitions = petitions.filter(current_signatures__gte=100).count()
    
    context = {
        "petitions": petitions,
        "total_petitions": total_petitions,
        "my_signatures": my_signatures,
        "my_petitions_count": my_petitions_count,
        "trending_petitions": trending_petitions,
    }
    return render(request, "peptitions/userPage/board.html", context)


# --- User Views ---
@login_required
def user_petitions(request):
    # ✅ Only show petitions that are approved/active
    petitions = Petition.objects.filter(status="approved").order_by("-created_at")

    # Calculate statistics for the template
    total_petitions = petitions.count()
    total_signatures = sum(p.current_signatures for p in petitions)
    nearly_complete = petitions.filter(current_signatures__gte=F('target_signatures') * 0.8).count()
    urgent_petitions = petitions.filter(deadline__lte=timezone.now() + timedelta(days=3)).count() if hasattr(Petition, 'deadline') else 0

    # Calculate sidebar statistics for ALL user pages
    my_signatures = Signature.objects.filter(user=request.user).count()
    my_petitions_count = Petition.objects.filter(created_by=request.user).count()

    context = {
        "petitions": petitions,
        "total_petitions": total_petitions,
        "total_signatures": total_signatures,
        "nearly_complete": nearly_complete,
        "urgent_petitions": urgent_petitions,
        "my_signatures": my_signatures,
        "my_petitions_count": my_petitions_count,
    }
    return render(request, "peptitions/userPage/petition_list.html", context)


@login_required
def my_petitions(request):
    petitions = Petition.objects.filter(created_by=request.user).order_by("-created_at")
    
    # Calculate statistics for the page itself
    total_petitions = petitions.count()
    pending_petitions = petitions.filter(status='pending').count()
    approved_petitions = petitions.filter(status='approved').count()
    rejected_petitions = petitions.filter(status='rejected').count()
    
    # Calculate sidebar statistics
    my_signatures = Signature.objects.filter(user=request.user).count()
    my_petitions_count = total_petitions  # This is already calculated above
    
    if request.method == "POST":
        form = PetitionForm(request.POST, request.FILES)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user
            petition.status = "pending"  # ✅ always pending until admin approves
            petition.save()
            return redirect("my_petitions")
    else:
        form = PetitionForm()

    context = {
        "petitions": petitions,
        "form": form,
        "total_petitions": total_petitions,
        "pending_petitions": pending_petitions,
        "approved_petitions": approved_petitions,
        "rejected_petitions": rejected_petitions,
        # Sidebar stats
        "my_signatures": my_signatures,
        "my_petitions_count": my_petitions_count,
    }
    return render(request, "peptitions/userPage/my_petitions.html", context)


@login_required
def sign_petition(request, petition_id):
    petition = Petition.objects.get(id=petition_id, status="approved")  # ✅ only approved petitions can be signed
    Signature.objects.get_or_create(user=request.user, petition=petition)
    petition.current_signatures = petition.signatures.count()
    petition.save()
    return redirect("user_petitions")


@login_required
def signed_petitions(request):
    signatures = Signature.objects.filter(user=request.user).select_related("petition").order_by('-signed_at')
    petitions = [sig.petition for sig in signatures]  # extract petitions
    
    # Calculate statistics for the page
    total_signed = len(petitions)
    active_petitions = len([p for p in petitions if p.status == 'approved'])
    successful_petitions = len([p for p in petitions if p.current_signatures >= p.target_signatures])
    
    # Count signatures from this month
    current_month = timezone.now().month
    current_year = timezone.now().year
    recent_signatures = Signature.objects.filter(
        user=request.user,
        signed_at__month=current_month,
        signed_at__year=current_year
    ).count()
    
    # Calculate sidebar statistics
    my_signatures = total_signed  # This is already calculated above
    my_petitions_count = Petition.objects.filter(created_by=request.user).count()
    
    context = {
        "petitions": petitions,
        "total_signed": total_signed,
        "active_petitions": active_petitions,
        "successful_petitions": successful_petitions,
        "recent_signatures": recent_signatures,
        # Sidebar stats
        "my_signatures": my_signatures,
        "my_petitions_count": my_petitions_count,
    }
    return render(request, "peptitions/userPage/signed_petitions.html", context)