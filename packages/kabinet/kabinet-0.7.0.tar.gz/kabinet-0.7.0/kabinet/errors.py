"""Errors for the Kabinet module."""


class NoKabinetFound(Exception):
    """No kabinet found in the current context.

    This error is raised when a function that requires a kabinet
    is called without a kabinet in the current context.
    """
