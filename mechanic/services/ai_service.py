def should_use_ai(
    message,
    topic,
    has_media=False,
    follow_up_complete=False
):

    if has_media:
        return True

    if topic is None:
        return False

    if follow_up_complete:
        return True

    return False
