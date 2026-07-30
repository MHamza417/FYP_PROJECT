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

            # --- TOKEN OPTIMIZATION ---
            alerts_summary = []
            
            sites = data.get("site", [])
            if isinstance(sites, list):
                for site_item in sites:
                    for alert in site_item.get("alerts", []):
                        alerts_summary.append({
                            "risk": alert.get("riskdesc"),
                            "name": alert.get("name"),
                            "description": alert.get("desc"),
                            "solution": alert.get("solution")
                        })
            
            report_payload = alerts_summary if alerts_summary else data
            gemini_text = ""

            try:
                # Get GenAI client & create prompt
                client = get_gemini_client()

                prompt = f"""
You are a cybersecurity expert.

Analyze the following OWASP ZAP security report summary:

{json.dumps(report_payload, indent=2)}

Provide:
1. Executive summary
2. Total vulnerabilities count
3. Critical and high-risk vulnerabilities
4. Medium and low-risk vulnerabilities
5. Explanation of important security issues
6. Recommended fixes
7. Overall security assessment
"""

                # Send report to Gemini using modern SDK
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                gemini_text = response.text

            except Exception as ai_err:
                print("AI Generation Skipped due to Quota/Error:", str(ai_err))
                gemini_text = (
                    "AI Analysis unavailable due to API quota limits or network issue. "
                    "Please check the raw JSON report data for complete vulnerability details."
                )

            if not gemini_text:
                gemini_text = "Analysis generated placeholder."

            # Save report in database
            report_obj = VulnerabilityReport.objects.create(
                project_name=str(project_name),
                raw_json_report=data,
                gemini_analysis=gemini_text
            )

            return Response(
                {
                    "status": "success",
                    "message": "Report analyzed and saved successfully!",
                    "report_id": report_obj.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("Server Error:", str(e))
            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# --- Grafana Metrics API ---
# --- Grafana Metrics API ---
@api_view(["GET"])
@permission_classes([AllowAny])
def grafana_metrics_api(request):
    """
    Endpoint for Grafana to fetch vulnerability metrics/summary from SQLite database.
    """
    reports = VulnerabilityReport.objects.all().order_by("-created_at")
    
    total_reports = reports.count()
    
    # Vulnerability types breakdown (JSON raw data se extract karne ke liye)
    vulnerability_counts = {}
    
    for report in reports:
        raw_data = report.raw_json_report
        # Handle ZAP or custom report structure safely
        sites = raw_data.get("site", []) if isinstance(raw_data, dict) else []
        if isinstance(sites, list):
            for site_item in sites:
                for alert in site_item.get("alerts", []):
                    vuln_name = alert.get("name", "Unknown Vulnerability")
                    vulnerability_counts[vuln_name] = vulnerability_counts.get(vuln_name, 0) + 1
        elif isinstance(raw_data, list):
            # Agar summary list saved hai
            for alert in raw_data:
                vuln_name = alert.get("name", "Unknown Vulnerability")
                vulnerability_counts[vuln_name] = vulnerability_counts.get(vuln_name, 0) + 1

    # Format for Grafana charts (Pie/Donut chart compatible structure)
    chart_data = [
        {"vulnerability": key, "count": value} 
        for key, value in vulnerability_counts.items()
    ]

    data = {
        "total_scans": total_reports,
        "vulnerability_breakdown": chart_data,
        "recent_projects": [report.project_name for report in reports[:5]],
        "reports_summary": [
            {
                "id": report.id,
                "project_name": report.project_name,
                "created_at": getattr(report, "created_at", None),
            }
            for report in reports
        ]
    }
    return Response(data, status=status.HTTP_200_OK)

# Home API

@api_view(["GET"])
def home(request):

    return Response(
        {
            "message": "Welcome to Nexus Technologies API",
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
                "message": "Message saved successfully!",
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
            "message": "Webhook received successfully!",
            "status": "success"
        },
        status=200
    )