from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Models aur Serializers imports
from .models import Service, Project, Team, ContactMessage
from .serializers import (
    ServiceSerializer,
    ProjectSerializer,
    TeamSerializer,
    ContactMessageSerializer,
)


# Home API
@api_view(['GET'])
def home(request):
    return Response({
        "message": "Welcome to Nexus Technologies API",
        "status": "success"
    })


# Services API
@api_view(['GET'])
def service_list(request):
    services = Service.objects.all()
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


# Projects API
@api_view(['GET'])
def project_list(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


# Team API
@api_view(['GET'])
def team_list(request):
    team = Team.objects.all()
    serializer = TeamSerializer(team, many=True)
    return Response(serializer.data)


# Contact Submission API
@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Message saved successfully!", "status": "success"}, status=201)
    
    print("VALIDATION ERRORS:", serializer.errors)
    return Response({"message": "Validation failed", "status": "error", "errors": serializer.errors}, status=400)


# GitHub Webhook API (Added to fix the import error)
@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    print("GitHub Webhook Received:", request.data)
    return Response({
        "message": "Webhook received successfully!",
        "status": "success"
    }, status=200)