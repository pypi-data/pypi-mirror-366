from __future__ import annotations

import operator
from collections import Counter
from typing import TYPE_CHECKING, ClassVar

import pycountry
from polykit.text import color

if TYPE_CHECKING:
    from iplooker.lookup_result import IPLookupResult


class IPFormatter:
    """Format IP results returned by lookups."""

    # Variations of United States country names to be standardized
    USA_NAMES: ClassVar[set[str]] = {
        "us",
        "usa",
        "united states",
        "united states of america",
    }

    # Variations of Washington, D.C. region names to be standardized
    REGION_NAMES: ClassVar[set[str]] = {
        "washington, d.c.",
        "district of columbia",
        "d.c.",
        "dc",
    }

    # Variations of city names to be standardized
    CITY_NAMES: ClassVar[set[str]] = {
        "washington d.c.",
        "washington d.c. (northeast washington)",
        "washington d.c. (northwest washington)",
        "new york city",
    }

    # Omit these values entirely if they start with "Unknown"
    OMIT_IF_UNKNOWN: ClassVar[set[str]] = {"region", "isp", "org"}

    def __init__(self, ip_address: str):
        self.ip_address: str = ip_address

    def format_lookup_result(self, result: IPLookupResult) -> dict[str, str]:
        """Convert an IPLookupResult to the expected output format."""
        country = self.standardize_country(result.country or "")
        region, city = self.standardize_region_and_city(result.region or "", result.city or "")
        isp_org = self.standardize_isp_and_org(result.isp or "", result.org or "")

        # Build location string based on available data
        location_parts = []
        if city:
            location_parts.append(city)
        if region:
            location_parts.append(region)
        if country:
            location_parts.append(country)

        location = ", ".join(location_parts) if location_parts else "Unknown Location"

        formatted_data = {"source": result.source, "location": location}
        if isp_org:
            formatted_data["ISP_Org"] = isp_org

        # Add security information if available
        if security_info := self.get_security_info(result):
            formatted_data["security"] = ", ".join(security_info)

        return formatted_data

    def get_security_info(self, result: IPLookupResult) -> list[str]:
        """Get security information from the IPLookupResult."""
        security_info = []

        if result.is_vpn is True:
            if result.vpn_service:
                security_info.append(f"is a VPN ({result.vpn_service})")
            else:
                security_info.append("is a VPN service")

        if result.is_proxy is True:
            security_info.append("is a proxy IP")

        if result.is_tor is True:
            security_info.append("is a Tor IP")

        if result.is_datacenter is True:
            security_info.append("comes from a hosting provider")

        if result.is_anonymous is True and not security_info:
            security_info.append("is anonymous")

        return security_info

    def print_consolidated_results(self, results: list[dict[str, str]]) -> None:
        """Print consolidated results with sources that report the same data grouped together."""
        # Count occurrences of each location
        result_count = Counter()
        security_data = {}

        for result in results:
            location = result["location"]
            isp_org = result.get("ISP_Org", "")
            security = result.get("security", "")

            line = f"{location}" + (f" ({isp_org})" if isp_org else "")
            result_count[line] += 1

            if security:  # Collect security info separately for consolidation
                if line not in security_data:
                    security_data[line] = set()
                security_data[line].add(security)

        # Sort by count (descending)
        sorted_locations = sorted(result_count.items(), key=operator.itemgetter(1), reverse=True)

        # Print consolidated results
        for line, count in sorted_locations:
            if count > 1:
                print(f"• {color(f'{count} sources:', 'blue')} {line}")
            else:  # Find the source for this unique result
                source = next(
                    r["source"]
                    for r in results
                    if f"{r['location']}"
                    + (f" ({r.get('ISP_Org', '')})" if r.get("ISP_Org") else "")
                    == line
                )
                print(f"• {color(source + ':', 'blue')} {line}")

            # Print security information if available
            if line in security_data:
                for security_info in sorted(security_data[line]):
                    print(f"  {color('  Security:', 'yellow')} {security_info}")

    def standardize_country(self, country: str) -> str:
        """Standardize the country name."""
        if len(country) == 2 and country.upper() != "US":
            try:
                country_obj = pycountry.countries.get(alpha_2=country.upper())
                return country_obj.name if country_obj is not None else country
            except (AttributeError, KeyError):
                return country
        return "US" if country.lower() in self.USA_NAMES else country

    def standardize_region_and_city(self, region: str, city: str) -> tuple[str, str]:
        """Standardize the region and city names."""
        if region.lower() in self.REGION_NAMES:
            region = "DC"
        if city.lower() in self.CITY_NAMES:
            city = "Washington" if "washington" in city.lower() else "New York"
        return region, city

    def standardize_isp_and_org(self, isp: str, org: str) -> str | None:
        """Standardize the ISP and organization names."""
        original_isp = isp
        original_org = org

        if "comcast" in isp.lower():
            isp = "Comcast"
        if "comcast" in org.lower():
            org = "Comcast"

        if isp and isp not in {"Unknown ISP", ""}:
            if org and org not in {"Unknown Org", ""}:
                return isp if original_isp.lower() == original_org.lower() else f"{isp} / {org}"
            return isp
        return org if org and org not in {"Unknown Org", ""} else None
