KEYWORDS = {
    "battery": [
        "car won't start",
        "battery",
        "dead battery",
        "clicking sound"
    ],

    "brakes": [
        "brake",
        "braking",
        "squeaking",
        "grinding"
    ],

    "engine": [
        "engine",
        "overheating",
        "smoke",
        "misfire"
    ],

    "tyres": [
        "tyre",
        "tire",
        "puncture",
        "flat"
    ],

    "oil": [
        "oil",
        "engine oil",
        "oil leak"
    ]
}


def detect_vehicle_topic(text):

    text = text.lower()

    for category, keywords in KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return None

def get_basic_response(category):

    responses = {

        "battery": (
            "A no-start condition can be related to the battery, "
            "starter motor, or charging system. "
            "Do you hear a clicking sound when you turn the key?"
        ),

        "brakes": (
            "Brake noise can have several causes, including "
            "worn brake pads or rotor issues. "
            "Does the noise happen only when braking?"
        ),

        "tyres": (
            "A flat tyre should be inspected before driving. "
            "Is the tyre completely deflated or slowly losing pressure?"
        ),

        "oil": (
            "An oil leak should be inspected because continued "
            "driving with low engine oil can damage the engine. "
            "Can you tell me where the oil appears to be leaking?"
        ),
    }

    return responses.get(category)