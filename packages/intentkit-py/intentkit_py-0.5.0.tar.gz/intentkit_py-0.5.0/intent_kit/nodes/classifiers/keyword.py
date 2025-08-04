"""Keyword-based classifier module."""


def keyword_classifier(user_input: str, children, context=None, **kwargs):
    """
    A simple classifier that selects the first child whose name appears in the user input.

    Args:
        user_input: The input string to process
        children: List of possible child nodes
        context: Optional context dictionary (unused in this classifier)

    Returns:
        The first matching child node, or None if no match is found
    """
    user_input_lower = user_input.lower()
    for child in children:
        if child.name.lower() in user_input_lower:
            return child
    return None
