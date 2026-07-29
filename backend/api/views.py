import json
from google import genai

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


def get_gemini_client():
    """
    Configure and return the modern Google GenAI client.
    """
    api_key = config("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    # Using the new google-genai client
    client = genai.Client(api_key=api_key)
    return client


class AnalyzeReportView(APIView):

    def post(self, request):

        try:
            # Get ZAP report JSON
            data = request.data

            project_name = data.get(
                "site",
                "IntelliSecOps Project"
            )

            # Get GenAI client
            client = get_gemini_client()

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

            # Send report to Gemini using modern SDK
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

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