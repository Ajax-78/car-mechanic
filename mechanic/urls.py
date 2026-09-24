
from django.urls import path
from . import views


urlpatterns = [
    # Chat
    path("chat/", views.chat, name="chat"),

    # Media upload
    path("upload/", views.upload_media, name="upload-media"),

    # Diagnosis
    path("diagnosis/", views.diagnosis, name="diagnosis"),

    # Booking
    path("booking/", views.create_booking, name="create-booking"),

    # Get booking
    path(
        "booking/<int:booking_id>/",
        views.get_booking,
        name="get-booking"
    ),
]

