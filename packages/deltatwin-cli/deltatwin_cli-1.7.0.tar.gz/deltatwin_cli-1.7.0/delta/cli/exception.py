import click


class DeltaTwinUnauthorized(click.ClickException):
    """
        Unauthorized access to resources
    """
    pass


class DeltaTwinServiceError(click.ClickException):
    """
        DeltaTwin service Error
    """
    pass


class DeltaTwinServiceNotFound(click.ClickException):
    """
        DeltaTwin service Error
    """
    pass


class DeltaTwinResourceNotFound(click.ClickException):
    """
        DeltaTwin service Error
    """
    pass
