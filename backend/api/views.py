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


def ask_gemini(prompt):
    """
    Shared helper: sends a prompt to Gemini and safely returns text,
    falling back to a placeholder if the API fails or quota is hit.
    """
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text or "Analysis generated placeholder."
    except Exception as ai_err:
        print("AI Generation Skipped due to Quota/Error:", str(ai_err))
        return (
            "AI Analysis unavailable due to API quota limits or network issue. "
            "Please check the raw JSON report data for complete vulnerability details."
        )


# --- OWASP ZAP Report Analysis ---

class AnalyzeReportView(APIView):
    """
    Receives OWASP ZAP JSON report, summarizes it, sends to Gemini
    for analysis, and stores the result.
    """

    def post(self, request):

        try:
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

            gemini_text = ask_gemini(prompt)

            # Save report in database
            report_obj = VulnerabilityReport.objects.create(
                project_name=str(project_name),
                raw_json_report=data,
                gemini_analysis=gemini_text,
                scan_type="ZAP",
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


# --- SQLMap Report Analysis (NEW) ---

class AnalyzeSQLMapReportView(APIView):
    """
    Receives SQLMap scan output (JSON), summarizes it, sends to Gemini
    for analysis, and stores the result — same pattern as the ZAP view.

    Expected payload example (adjust to whatever your SQLMap wrapper/script
    actually sends — SQLMap itself doesn't emit clean JSON by default, so
    this assumes you parse its output into a JSON list first, e.g.:

    {
        "target": "http://13.63.222.33/api/analyze-report/?id=1",
        "findings": [
            {
                "parameter": "id",
                "type": "boolean-based blind",
                "title": "SQL Injection",
                "payload": "id=1 AND 1=1"
            },
            ...
        ]
    }
    """

    def post(self, request):

        try:
            data = request.data

            project_name = data.get("target", "IntelliSecOps Project")
            findings = data.get("findings", [])

            report_payload = findings if findings else data

            prompt = f"""
You are a cybersecurity expert specializing in database security.

Analyze the following SQLMap scan findings:

{json.dumps(report_payload, indent=2)}

Provide:
1. Executive summary
2. Total injection points found
3. Type of SQL injection (boolean-based, time-based, union-based, etc.)
4. Risk severity assessment
5. Explanation of how each vulnerability could be exploited
6. Recommended fixes (parameterized queries, ORM usage, input validation, etc.)
7. Overall database security assessment
"""

            gemini_text = ask_gemini(prompt)

            report_obj = VulnerabilityReport.objects.create(
                project_name=str(project_name),
                raw_json_report=data,
                gemini_analysis=gemini_text,
                scan_type="SQLMap",
            )

            return Response(
                {
                    "status": "success",
                    "message": "SQLMap report analyzed and saved successfully!",
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


# --- Grafana Metrics API (UPDATED: now includes scan_type breakdown) ---

@api_view(["GET"])
@permission_classes([AllowAny])
def grafana_metrics_api(request):
    """
    Endpoint for Grafana to fetch vulnerability metrics/summary from SQLite database.
    Now separates ZAP vs SQLMap findings so both scanners show up on the dashboard.
    """
    reports = VulnerabilityReport.objects.all().order_by("-created_at")
    total_reports = reports.count()

    vulnerability_counts = {}
    scan_type_counts = {"ZAP": 0, "SQLMap": 0}

    for report in reports:
        scan_type = getattr(report, "scan_type", "ZAP") or "ZAP"
        scan_type_counts[scan_type] = scan_type_counts.get(scan_type, 0) + 1

        raw_data = report.raw_json_report

        if scan_type == "ZAP":
            sites = raw_data.get("site", []) if isinstance(raw_data, dict) else []
            if isinstance(sites, list):
                for site_item in sites:
                    for alert in site_item.get("alerts", []):
                        vuln_name = alert.get("name", "Unknown Vulnerability")
                        vulnerability_counts[vuln_name] = vulnerability_counts.get(vuln_name, 0) + 1
            elif isinstance(raw_data, list):
                for alert in raw_data:
                    vuln_name = alert.get("name", "Unknown Vulnerability")
                    vulnerability_counts[vuln_name] = vulnerability_counts.get(vuln_name, 0) + 1

        elif scan_type == "SQLMap":
            findings = raw_data.get("findings", []) if isinstance(raw_data, dict) else []
            for finding in findings:
                vuln_name = finding.get("title", "SQL Injection")
                vulnerability_counts[vuln_name] = vulnerability_counts.get(vuln_name, 0) + 1

    # Grafana JSON plugin ke liye direct flat list banayein
    data = [
        {
            "metric": "Total Scans",
            "value": total_reports
        },
        {
            "metric": "ZAP Scans",
            "value": scan_type_counts.get("ZAP", 0)
        },
        {
            "metric": "SQLMap Scans",
            "value": scan_type_counts.get("SQLMap", 0)
        },
    ]

    for key, value in vulnerability_counts.items():
        data.append({
            "metric": key,
            "value": value
        })

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