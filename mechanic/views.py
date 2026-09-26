import json
import traceback
import uuid

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.genai.errors import APIError

from .models import Conversation, Message
from .services.api_service import generate_mechanic_response
from .services.rag_service import build_context, search_knowledge


def is_car_related(text):
    keywords = [
        "car", "vehicle", "auto", "engine", "brake", "brakes", "battery", "tyre", "tire", 
        "wheel", "oil", "coolant", "radiator", "transmission", "gear", "clutch", 
        "steering", "suspension", "alternator", "starter", "overheating", "mechanic", 
        "dashboard", "check engine", "leak", "smell", "noise", "sound", "spark",
        "sensor", "light", "smoke", "drive", "miles", "code", "diagnostic"
    ]
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def is_dangerous(text):
    safety_keywords = [
        "brake failure", "brakes failed", "steering failure", "fuel leak", 
        "fuel leakage", "car fire", "vehicle fire", "smoke from engine", 
        "wheel coming off", "wheel fell off", "severe overheating"
    ]
    text = text.lower()
    return any(keyword in text for keyword in safety_keywords)


def get_conversation_history(conversation):
    messages = (
        Message.objects
        .filter(conversation=conversation)
        .order_by("-created_at")[:10]
        .values_list("role", "content")
    )
    # Reverse to keep chronological order
    history = [f"{role}: {content}" for role, content in reversed(list(messages))]
    return "\n".join(history)


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST method is allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)
        message_text = data.get("message", "").strip()
        conversation_id = data.get("conversation_id")

        if not message_text:
            return JsonResponse(
                {"success": False, "message": "Message is required"},
                status=400
            )

        # --------------------------------
        # 1. Get or create conversation safely
        # --------------------------------
        if conversation_id:
            try:
                # Convert string to UUID object to validate format
                valid_uuid = uuid.UUID(str(conversation_id))
                conversation = Conversation.objects.get(id=valid_uuid)
            except (ValueError, ValidationError, Conversation.DoesNotExist):
                return JsonResponse(
                    {"success": False, "message": "Invalid or non-existent conversation_id"},
                    status=404
                )
        else:
            conversation = Conversation.objects.create()

        # --------------------------------
        # 2. Save user message
        # --------------------------------
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=message_text
        )

        # --------------------------------
        # 3. Check car-related question
        # --------------------------------
        if not is_car_related(message_text):
            reply = (
                "I'm an AI car mechanic assistant. "
                "I can help with car troubleshooting, maintenance, diagnostics and repairs. "
                "Please ask me a vehicle-related question."
            )

            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=reply
            )

            return JsonResponse(
                {
                    "success": True,
                    "conversation_id": str(conversation.id),
                    "message": reply,
                    "rag_used": False
                }
            )

        # --------------------------------
        # 4. Safety check
        # --------------------------------
        if is_dangerous(message_text):
            reply = (
                "This may be a safety-critical problem. "
                "Please stop driving the vehicle if it is safe to do so and have it inspected by a "
                "qualified mechanic. Do not continue driving if braking, steering, fuel leakage or severe "
                "overheating is involved."
            )

            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=reply
            )

            return JsonResponse(
                {
                    "success": True,
                    "conversation_id": str(conversation.id),
                    "message": reply,
                    "rag_used": False,
                    "safety_warning": True
                }
            )

        # --------------------------------
        # 5. Retrieve relevant knowledge & history
        # --------------------------------
        documents = search_knowledge(message_text, limit=5)
        context = build_context(documents)
        history = get_conversation_history(conversation)

        # --------------------------------
        # 6. Gemini + RAG Generation with Error Handling
        # --------------------------------
        try:
            ai_result = generate_mechanic_response(
                question=message_text,
                context=context,
                conversation_history=history
            )
        except APIError as api_err:
            print("Gemini API Error:", api_err)
            return JsonResponse(
                {
                    "success": False,
                    "message": "The AI mechanic service is currently experiencing high demand. Please try again in a moment.",
                    "error": str(api_err)
                },
                status=503
            )

        # --------------------------------
        # 7. Format response content
        # --------------------------------
        if ai_result.get("follow_up_question"):
            reply = ai_result["follow_up_question"]
        else:
            reply = ai_result.get(
                "explanation",
                "Please provide more information about the vehicle problem."
            )
            recommendation = ai_result.get("recommendation")
            if recommendation:
                reply += f"\n\nRecommendation:\n{recommendation}"

        # --------------------------------
        # 8. Save assistant response
        # --------------------------------
        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=reply
        )

        # --------------------------------
        # 9. Return Response
        # --------------------------------
        return JsonResponse(
            {
                "success": True,
                "conversation_id": str(conversation.id),
                "message": reply,
                "diagnosis": ai_result,
                "rag_used": True,
                "sources": [
                    {
                        "title": doc["title"],
                        "category": doc["category"],
                        "distance": doc["distance"]
                    }
                    for doc in documents
                ]
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON body"},
            status=400
        )
    except Exception as error:
        print("Chat endpoint error:", error)
        traceback.print_exc()
        return JsonResponse(
            {"success": False, "message": str(error)},
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