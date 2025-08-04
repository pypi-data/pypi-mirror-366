import os
from fastmcp import FastMCP
from pydantic import BaseModel
from datetime import datetime, timedelta
from pydexcom import Dexcom

DEXCOM_USERNAME = os.getenv("DEXCOM_USERNAME")
DEXCOM_PASSWORD = os.getenv("DEXCOM_PASSWORD")

dexcom = Dexcom(username=DEXCOM_USERNAME, password=DEXCOM_PASSWORD)

mcp = FastMCP("Dexcom MCP Server")


class GlucoseReading(BaseModel):
    reported_at: datetime
    value: int
    unit: str = "mg/dL"
    trend_arrow: str
    trend_description: str


@mcp.tool(
    description="Fetches the most recent glucose reading from the Dexcom Share website."
)
def get_latest_glucose_reading() -> GlucoseReading:
    """Fetches the most recent glucose reading from the Dexcom Share website."""
    latest_reading = dexcom.get_latest_glucose_reading()
    if latest_reading is None:
        raise Exception("No glucose reading found")
    return GlucoseReading(
        reported_at=latest_reading.datetime,
        value=latest_reading.value,
        unit="mg/dL",
        trend_arrow=latest_reading.trend_arrow,
        trend_description=latest_reading.trend_description,
    )


@mcp.tool(
    description="Fetches prior 24 hours of glucose readings from the Dexcom Share website."
)
def get_glucose_readings() -> list[GlucoseReading]:
    """Fetches prior 24 hours of glucose readings from the Dexcom Share website."""
    readings = dexcom.get_glucose_readings()
    return [
        GlucoseReading(
            reported_at=reading.datetime,
            value=reading.value,
            unit="mg/dL",
            trend_arrow=reading.trend_arrow,
            trend_description=reading.trend_description,
        )
        # reverse the list to get the most recent reading last
        for reading in readings[::-1]
    ]


def main() -> None:
    """Run the dexcom MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
