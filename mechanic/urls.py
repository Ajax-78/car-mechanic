
from django.urls import path
from . import views


urlpatterns = [

    path(
        "chat/",
        views.chat,
        name="chat"
    ),

    path(
        "upload/",
        views.upload_media,
        name="upload-media"
    ),

    path(
        "diagnosis/",
        views.diagnosis,
        name="diagnosis"
    ),

    path(
        "booking/",
        views.create_booking,
        name="create-booking"
    ),

    path(
        "booking/<int:booking_id>/",
        views.get_booking,
        name="get-booking"
    ),
]


