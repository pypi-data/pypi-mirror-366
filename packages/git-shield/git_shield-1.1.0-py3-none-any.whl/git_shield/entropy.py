import math


def shannon_entropy(data: str) -> float:
    """

    Calculate the Shannon entropy of a given string.

    Args:
        data (str) : The string to calculate the entropy for.

    Returns:
        float: Shannon entropy value

    """
    if data == "":
        return 0.0

    frequency = {}
    for char in data:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1
    print(f"frequency= {frequency}")

    entropy = 0.0
    length = len(data)
    print(f"length= {length}")

    for count in frequency.values():
        p_x = count / length
        print(f"p_x= {p_x}")
        entropy -= p_x * math.log2(p_x)
    return entropy


def is_high_entropy_string(data: str, threshold: float = 4.0) -> bool:
    """
    Check if the string is considered high-entropy.

    Args:
        data (str): String to evaluate.
        threshold (float): Entropy threshold. Default = 4.0

    Returns:
        bool: True if entropy >= threshold.
    """
    return shannon_entropy(data) >= threshold
