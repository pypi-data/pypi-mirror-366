"""
Utilities for handling English Language rules.

"""


def add_indefinite_article(phrase):
    """
    Given a word, choose the appropriate indefinite article (e.g., "a" or "an")
    and add it the front of the word. Matches the original word's
    capitalization.


    Args:
        phrase (str): The phrase to get the appropriate definite article
            for.

    Returns:
        str: Either "an" or "a".
    """
    # Note: Must cast to string because it could be a SandboxResult
    if str(phrase[0]) in "aeiou":
        return "an "+phrase
    elif str(phrase[0]) in "AEIOU":
        return "An "+phrase
    elif phrase[0].lower() == phrase[0]:
        return "a "+phrase
    else:
        return "A "+phrase


def escape_curly_braces(result):
    """ Replaces all occurrences of curly braces with double curly braces. """
    return result.replace("{", "{{").replace("}", "}}")


def safe_repr(obj, short=False, max_length=80) -> str:
    """
    Create a string representation of this object using :py:func:`repr`. If the
    object doesn't have a repr defined, then falls back onto the default
    :py:func:`object.__repr__`. Finally, if ``short`` is true, then the string
    will be truncated to the max_length value.

    Args:
        obj (Any): Any object to repr.
        short (bool): Whether or not to truncate to the max_length.
        max_length (int): How many maximum characters to use, if short is True.
    """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if short and len(result) >= max_length:
        result = result[:max_length] + ' [truncated]...'
    result = result
    return result


def chomp(text):
    """ Removes the trailing newline character, if there is one. """
    if not text:
        return text
    if text[-2:] == '\n\r':
        return text[:-2]
    if text[-1] == '\n':
        return text[:-1]
    return text


def join_list_with_and(items):
    """ Properly format the string with commas (oxford-style) and the word `and`."""
    items = list(items)
    if len(items) < 1:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        pre = ", ".join(items[:-1])
        return f"{pre}, and {items[-1]}"

def inject_line(code, line_number, new_line):
    lines = code.split("\n")
    lines.insert(line_number, new_line)
    return "\n".join(lines)


def render_table(rows, headers=None, separator=" | ", max_width=120):
    """
    Simple function to render table with fixed width.

    TODO: Try to resize table to make it fit comfortably within 120 characters,
        e.g., by removing separators, or by wrapping text.

    Based on: https://stackoverflow.com/a/52247284/1718155
    """
    table = [headers] + rows if headers else rows
    longest_cols = [
        (max([len(str(row[i])) for row in table]))
        for i in range(len(table[0]))
    ]
    total_width = sum(longest_cols) + (len(longest_cols)-1) * len(separator)
    if max_width is not None:
        if total_width > max_width:
            # Maybe we can trim the separator?
            if separator:
                shorter_separator = separator.strip()
                # Oops, we already tried stripping. What about removing it?
                if shorter_separator == separator:
                    shorter_separator = ""
                return render_table(rows, headers, shorter_separator, max_width)
    row_format = separator.join(["{:>" + str(longest_col) + "}"
                                for longest_col in longest_cols])
    result = [row_format.format(*row) for row in table]
    if headers:
        result.insert(1, "="*total_width)
    return "\n".join(result)
