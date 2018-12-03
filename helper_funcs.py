def null_to_zero(form_input):
    """Takes form input and checks for empty string.
        Returns zero if empty string is found, otherwise
        returns the input.

        null_to_zero('') --> 0
        null_to_zero(15) -- 15 """

    if form_input is None or form_input == '':
        form_input = 0
    else:
        form_input = form_input

    return form_input
