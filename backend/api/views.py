import json
import google.generativeai as genai

from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import VulnerabilityReport, Service, Project, Team, ContactMessage
from .serializers import (
    ServiceSerializer,
    ProjectSerializer,
    TeamSerializer,
    ContactMessageSerializer,
)


def get_gemini_model():
    """
    Picks a currently-available Gemini model instead of a hardcoded name.
    Google retires/renames models frequently, so we ask the API which
    models this key can actually use, and prefer a 'flash' model
    (cheaper/faster) if one is available.
    """
    genai.configure(api_key=config("GEMINI_API_KEY"))

    available = [
        m.name for m in genai.list_models()
        if "generateContent" in m.supported_generation_methods
    ]

    if not available:
        raise RuntimeError("No Gemini models with generateContent support are available for this API key.")

    flash_models = [m for m in available if "flash" in m.lower()]
    chosen = flash_models[0] if flash_models else available[0]

    return genai.GenerativeModel(chosen)


class AnalyzeReportView(APIView):
    def post(self, request):
        try:
            data = request.data
            project_name = data.get("site", "IntelliSecOps Project")

            # Gemini AI configuration - dynamically picks an available model
            model = get_gemini_model()

            prompt = f"""
            Analyze the following OWASP ZAP security report JSON and provide
            a summary of vulnerabilities along with actionable fix suggestions:

            {json.dumps(data, indent=2)}
            """

            response = model.generate_content(prompt)
            gemini_text = response.text

            # Save report and AI analysis to database
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
        return Response({
            "message": "Message saved successfully!",
            "status": "success"
        }, status=201)

    print("VALIDATION ERRORS:", serializer.errors)

    return Response({
        "message": "Validation failed",
        "status": "error",
        "errors": serializer.errors
    }, status=400)


# GitHub Webhook API
@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    print("GitHub Webhook Received:", request.data)

    return Response({
        "message": "Webhook received successfully!",
        "status": "success"
    }, status=200)