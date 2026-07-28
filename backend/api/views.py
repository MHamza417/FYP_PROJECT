import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VulnerabilityReport
import google.generativeai as genai
import os

class AnalyzeReportView(APIView):
    def post(self, request):
        try:
            data = request.data
            project_name = data.get("site", "IntelliSecOps Project")
            
            # Gemini AI configuration
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            Analyze the following OWASP ZAP security report JSON and provide a summary of vulnerabilities 
            along with actionable fix suggestions:
            {json.dumps(data, indent=2)}
            """
            
            response = model.generate_content(prompt)
            gemini_text = response.text
            
            # Save to database
            report_obj = VulnerabilityReport.objects.create(
                project_name=project_name,
                raw_json_report=data,
                gemini_analysis=gemini_text
            )
            
            return Response({
                "status": "success",
                "message": "Report analyzed and saved successfully!",
                "report_id": report_obj.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
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