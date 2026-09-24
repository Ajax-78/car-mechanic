
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.response import diagnose_with_ai
import json


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST method is allowed"
            },
            status=405
        )

    try:
        data = json.loads(request.body)

        message = data.get("message", "")
        conversation = data.get("history", [])
        conversation_id = data.get("conversation_id")

        if not message:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Message is required"
                },
                status=400
            )

        # Call Gemini
        ai_reply = diagnose_with_ai(
            conversation=conversation,
            user_message=message
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Chat response generated successfully",
                "data": {
                    "conversation_id": conversation_id,
                    "user_message": message,
                    "reply": ai_reply
                }
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON"
            },
            status=400
        )

    except Exception as error:
        print("CHAT ERROR:", error)

        return JsonResponse(
            {
                "success": False,
                "message": "Failed to generate AI response",
                "error": str(error)
            },
            status=500
        )
@csrf_exempt
def upload_media(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST method is allowed"
            },
            status=405
        )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {
                "success": False,
                "message": "No file uploaded"
            },
            status=400
        )

    return JsonResponse(
        {
            "success": True,
            "message": "File uploaded successfully",
            "file": {
                "name": uploaded_file.name,
                "size": uploaded_file.size,
                "content_type": uploaded_file.content_type
            }
        },
        status=201
    )


@csrf_exempt
def diagnosis(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST method is allowed"
            },
            status=405
        )

    try:
        data = json.loads(request.body)

        conversation_id = data.get("conversation_id")

        if not conversation_id:
            return JsonResponse(
                {
                    "success": False,
                    "message": "conversation_id is required"
                },
                status=400
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Diagnosis generated",
                "diagnosis": {
                    "issue": "Initial inspection required",
                    "severity": "medium",
                    "explanation": "More information about the car symptoms is required.",
                    "recommendation": "Please provide details about the symptoms.",
                    "confidence": 0.50
                }
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON"
            },
            status=400
        )


@csrf_exempt
def create_booking(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST method is allowed"
            },
            status=405
        )

    try:
        data = json.loads(request.body)

        required_fields = [
            "customer_name",
            "phone",
            "preferred_date",
            "preferred_time",
            "problem_description"
        ]

        missing_fields = [
            field for field in required_fields
            if not data.get(field)
        ]

        if missing_fields:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Required fields are missing",
                    "missing_fields": missing_fields
                },
                status=400
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Mechanic booking created successfully",
                "booking": {
                    "id": 1,
                    "customer_name": data["customer_name"],
                    "phone": data["phone"],
                    "preferred_date": data["preferred_date"],
                    "preferred_time": data["preferred_time"],
                    "problem_description": data["problem_description"],
                    "status": "pending"
                }
            },
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON"
            },
            status=400
        )


def get_booking(request, booking_id):
    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "Only GET method is allowed"
            },
            status=405
        )

    return JsonResponse(
        {
            "success": True,
            "booking": {
                "id": booking_id,
                "status": "pending"
            }
        },
        status=200
    )

