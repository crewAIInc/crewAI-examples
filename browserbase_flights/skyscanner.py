# https://www.skyscanner.net/transport/flights/sof/ber/240521

from crewai_tools import tool
from typing import Optional


@tool("SkyScanner tool")
def skyscanner(
    departure: str, destination: str, date: int, return_date: Optional[int] = 0
) -> str:
    """
    Generates a SkyScanner URL for flights between departure and destination on the specified date.

    :param departure: The IATA code for the departure airport (e.g., 'sof' for Sofia)
    :param destination: The IATA code for the destination airport (e.g., 'ber' for Berlin)
    :param date: The date of the flight in the format 'yymmdd'
    :return_date: Only for two-way tickets. The date of return flight in the format 'yymmdd'
    """
    return f"https://www.skyscanner.net/transport/flights/{departure}/{destination}/{date}/{return_date}"
