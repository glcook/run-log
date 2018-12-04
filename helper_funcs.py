def null_to_zero(form_input):
    """ Takes form input and checks for empty string.
        Returns zero if empty string is found, otherwise
        returns the input.

        null_to_zero('') --> 0
        null_to_zero(15) --> 15
        """

    if form_input is None or form_input == '':
        form_input = 0
    else:
        form_input = form_input

    return form_input

def time_to_string(db_time):
    """ Takes run duration in seconds from database
        and returns a string in the form of HH:MM:SS if
        number from db is non-zero. If number is zero,
        returns string NA.

        time_to_string(4800) --> 01:20:00
        time_to_string(0) --> NA
        """

    if db_time == 0:
        return "NA"

    else:
        raw_minutes = int(db_time / 60)
        seconds = round(db_time % 60)

        if db_time < 3600:
            hours = 0
            minutes = raw_minutes

        else:
            hours = int(db_time / 3600)
            minutes = raw_minutes % 60

        return str(hours) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

def time_to_pace(db_time):
    """ Takes average pace per mile in seconds and
        returns the pace in minutes and seconds in
        string form of "MM:SS" if minutes is a two-
        digit number and "M:SS" if minutes is single-
        digit. If db_time is None, returns NA.

        time_to_pace(521) --> 8:42
        time_to_pace(822) --> 13:42
        """
    if db_time is None:
        return "NA"

    else:
        time_with_zeros = time_to_string(db_time)
        return time_with_zeros.lstrip('0:')
