import json

def atelier_get_participation_count(member_id: int):
    """
    Get the count of participations for a member.

    Args:
        member_id (int): The ID of the member.

    Returns:
        int: The count of participations.
    """
    with open("./participations.json", "r") as file:
        data = json.load(file)

    participations = data["participations"]
    participation_ids = [
        participation_id
        for participation_ids_list in participations.values()
        if participation_ids_list is not None
        for participation_id in participation_ids_list
    ]
    return participation_ids.count(member_id)