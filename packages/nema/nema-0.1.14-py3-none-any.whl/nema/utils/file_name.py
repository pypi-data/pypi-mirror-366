import uuid


def generate_random_file_name(extension: str):

    base = f"{uuid.uuid4()}"

    if extension:
        return f"{base}.{extension}"

    return base
