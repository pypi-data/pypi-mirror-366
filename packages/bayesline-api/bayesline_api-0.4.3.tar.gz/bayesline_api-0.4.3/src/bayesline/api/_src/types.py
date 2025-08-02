import datetime as dt
from typing import Any, Literal, Sequence

import polars as pl

IdType = Literal[
    "bayesid",
    "ticker",
    "composite_figi",
    "cik",
    "cusip8",
    "cusip9",
    "isin",
    "sedol6",
    "sedol7",
    "proxy",
    "name",
]
DNFFilterExpression = tuple[str, str, Any]
DNFFilterExpressions = list[DNFFilterExpression | Sequence[DNFFilterExpression]]

DateLike = str | dt.date | dt.datetime


def to_date(arg: DateLike) -> dt.date:
    """Cast a date-like object to a date.

    Parameters
    ----------
    arg : DateLike
        The date-like object to cast.

    Returns
    -------
    dt.date
        The date.
    """
    if isinstance(arg, dt.date):
        return arg
    elif isinstance(arg, dt.datetime):
        return arg.date()
    elif isinstance(arg, str):
        try:
            return pl.Series([arg]).str.to_date().to_list()[0]
        except pl.exceptions.ComputeError as e:
            raise ValueError(f"Could not cast string to date: '{arg}'") from e
    else:
        raise ValueError(f"Invalid date-like object: {arg}")


def to_maybe_date(arg: DateLike | None) -> dt.date | None:
    """Cast a date-like object, empty string or None to a date or None.

    Parameters
    ----------
    arg : DateLike | None
        The date-like object to cast.

    Returns
    -------
    dt.date | None
        The date or None.
    """
    if arg is None or arg == "":
        return None
    else:
        return to_date(arg)


def to_date_string(arg: DateLike) -> str:
    """Cast a date-like object to a date string.

    Parameters
    ----------
    arg : DateLike
        The date-like object to cast.

    Returns
    -------
    str
        The date string.
    """
    return to_date(arg).isoformat()


def to_maybe_date_string(arg: DateLike | None) -> str | None:
    """Cast a date-like object, empty string or None to a date string or None.

    Parameters
    ----------
    arg : DateLike | None
        The date-like object to cast.

    Returns
    -------
    str | None
        The date string or None.
    """
    if arg is None or arg == "":
        return None
    else:
        return to_date_string(arg)
