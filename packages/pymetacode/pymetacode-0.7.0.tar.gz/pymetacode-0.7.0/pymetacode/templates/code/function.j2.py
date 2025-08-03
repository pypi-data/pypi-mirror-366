

def {{ function.name }}():
    """
    One sentence (on one line) describing the function.

    More description comes here...

    Parameters
    ----------
    param : :class:`None`
        Short description

    Returns
    -------
    param : :class:`None`
        Short description


    {% if package.version != '0.1' %}
    .. versionadded:: {{ package.version }}
    {% endif %}

    """
    pass

