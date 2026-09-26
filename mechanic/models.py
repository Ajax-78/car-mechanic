import uuid  # 1. Import Python's built-in uuid module
from django.db import models
from pgvector.django import VectorField


class Conversation(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,  # 2. Pass uuid.uuid4 function as the default generator
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class Media(models.Model):

    MEDIA_TYPES = [
        ("image", "Image"),
        ("audio", "Audio"),
        ("video", "Video"),
    ]

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="media",
        null=True,
        blank=True
    )

    file = models.FileField(
        upload_to="uploads/"
    )

    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class Diagnosis(models.Model):

    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="diagnosis"
    )

    issue = models.CharField(
        max_length=255
    )

    severity = models.CharField(
        max_length=50
    )

    explanation = models.TextField()

    recommendation = models.TextField()

    confidence = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    customer_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    preferred_date = models.DateField()

    preferred_time = models.TimeField()

    problem_description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class KnowledgeDocument(models.Model):

    title = models.CharField(
        max_length=255
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    content = models.TextField()

    source = models.CharField(
        max_length=255,
        blank=True
    )

    embedding = VectorField(
        dimensions=768,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

