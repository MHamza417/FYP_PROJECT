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
    Configure Gemini and select an available model
    that supports generateContent.
    """

    api_key = config("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    genai.configure(api_key=api_key)

    # Get models available for this API key
    available_models = []

    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            available_models.append(model.name)

    if not available_models:
        raise RuntimeError(
            "No Gemini model available for generateContent "
            "with this API key."
        )

    # Prefer Gemini Flash models
    flash_models = [
        model
        for model in available_models
        if "flash" in model.lower()
    ]

    if flash_models:
        selected_model = flash_models[0]
    else:
        selected_model = available_models[0]

    print("Available Gemini models:", available_models)
    print("Selected Gemini model:", selected_model)

    return genai.GenerativeModel(selected_model)


class AnalyzeReportView(APIView):

    def post(self, request):

        try:
            # Get ZAP report JSON
            data = request.data

            project_name = data.get(
                "site",
                "IntelliSecOps Project"
            )

            # Get available Gemini model
            model = get_gemini_model()

            # Create prompt
            prompt = f"""
You are a cybersecurity expert.

Analyze the following OWASP ZAP security report.

Provide:

1. Executive summary
2. Total vulnerabilities
3. Critical and high-risk vulnerabilities
4. Medium and low-risk vulnerabilities
5. Explanation of important security issues
6. Recommended fixes
7. Overall security assessment

OWASP ZAP Report:

{json.dumps(data, indent=2)}
"""

            # Send report to Gemini
            response = model.generate_content(prompt)

            # Get Gemini response
            gemini_text = response.text

            if not gemini_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            # Save report in database
            report_obj = VulnerabilityReport.objects.create(
                project_name=project_name,
                raw_json_report=data,
                gemini_analysis=gemini_text
            )

            return Response(
                {
                    "status": "success",
                    "message": (
                        "Report analyzed and saved successfully!"
                    ),
                    "report_id": report_obj.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            print(
                "Gemini API Error:",
                str(e)
            )

            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# Home API

@api_view(["GET"])
def home(request):

    return Response(
        {
            "message": (
                "Welcome to Nexus Technologies API"
            ),
            "status": "success"
        }
    )


# Services API

@api_view(["GET"])
def service_list(request):

    services = Service.objects.all()

    serializer = ServiceSerializer(
        services,
        many=True
    )

    return Response(
        serializer.data
    )


# Projects API

@api_view(["GET"])
def project_list(request):

    projects = Project.objects.all()

    serializer = ProjectSerializer(
        projects,
        many=True
    )

    return Response(
        serializer.data
    )


# Team API

@api_view(["GET"])
def team_list(request):

    team = Team.objects.all()

    serializer = TeamSerializer(
        team,
        many=True
    )

    return Response(
        serializer.data
    )


# Contact Submission API

@api_view(["POST"])
@permission_classes([AllowAny])
def contact_submit(request):

    serializer = ContactMessageSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "message": (
                    "Message saved successfully!"
                ),
                "status": "success"
            },
            status=201
        )

    print(
        "VALIDATION ERRORS:",
        serializer.errors
    )

    return Response(
        {
            "message": "Validation failed",
            "status": "error",
            "errors": serializer.errors
        },
        status=400
    )


# GitHub Webhook API

@api_view(["POST"])
@permission_classes([AllowAny])
def github_webhook(request):

    print(
        "GitHub Webhook Received:",
        request.data
    )

    return Response(
        {
            "message": (
                "Webhook received successfully!"
            ),
            "status": "success"
        },
        status=200
    )