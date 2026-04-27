"""KenyaHealthMCP — Kenya health data MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kenya-health-mcp")

NHIF_RATES = [
    (5999,150),(7999,300),(11999,400),(14999,500),(19999,600),(24999,750),
    (29999,850),(34999,900),(39999,950),(44999,1000),(49999,1100),(59999,1200),
    (69999,1300),(79999,1400),(89999,1500),(99999,1600),(float("inf"),1700),
]

FACILITIES = {
    "Nairobi": [
        {"name":"Kenyatta National Hospital","level":6,"phone":"020 272 6300","type":"National Referral"},
        {"name":"Mama Lucy Kibaki Hospital","level":4,"phone":"020 558 0040","type":"County"},
        {"name":"Mbagathi District Hospital","level":4,"phone":"020 271 2413","type":"County"},
    ],
    "Mombasa": [{"name":"Coast General Teaching & Referral Hospital","level":5,"phone":"041 231 4201","type":"Regional Referral"}],
    "Kisumu": [{"name":"Jaramogi Oginga Odinga Teaching & Referral Hospital","level":5,"phone":"057 202 1153","type":"Regional Referral"}],
    "Nakuru": [{"name":"Nakuru Level 5 Hospital","level":5,"phone":"051 221 0285","type":"Regional Referral"}],
    "Eldoret": [{"name":"Moi Teaching & Referral Hospital","level":6,"phone":"053 203 3471","type":"Regional Referral"}],
    "Garissa": [{"name":"Garissa County Referral Hospital","level":5,"phone":"046 202 1002","type":"County Referral"}],
    "Turkana": [{"name":"Lodwar County Referral Hospital","level":5,"phone":"054 221 021","type":"County Referral"}],
}

RIGHTS = {
    "healthcare": {
        "en": "Article 43(1)(a): Every person has the right to the highest attainable standard of health, including the right to healthcare services.",
        "sw": "Kifungu 43(1)(a): Kila mtu ana haki ya kiwango cha juu zaidi cha afya, ikiwemo haki ya huduma za afya.",
    },
    "maternal": {
        "en": "Linda Mama Programme: Free maternity services at all public health facilities — delivery, postnatal care, and newborn care. No payment required.",
        "sw": "Mpango wa Linda Mama: Huduma za uzazi bure katika vituo vyote vya afya vya umma. Hakuna malipo yanayohitajika.",
    },
    "emergency": {
        "en": "Article 43(3): The State shall provide appropriate social security to persons who are unable to support themselves and their dependants.",
        "sw": "Kifungu 43(3): Serikali itatoa usalama wa kijamii unaofaa kwa watu wasio na uwezo wa kujitegemea.",
    },
}


@mcp.tool()
def get_nhif_contribution(gross_salary_kes: float) -> dict:
    """
    Get the NHIF/SHA monthly contribution for a given gross salary in Kenya Shillings.
    Returns employee contribution, employer match, and total monthly cost.
    gross_salary_kes: Monthly gross salary in KES
    """
    contribution = next(amt for ceiling, amt in NHIF_RATES if gross_salary_kes <= ceiling)
    return {
        "gross_salary_kes": gross_salary_kes,
        "employee_contribution_kes": contribution,
        "employer_match_kes": contribution,
        "total_monthly_kes": contribution * 2,
        "source": "NHIF Act / SHA Act 2023",
        "note": "Verify current rates at nhif.or.ke or sha.go.ke",
    }


@mcp.tool()
def find_facility(county: str, level: int = 0) -> dict:
    """
    Find public health facilities in a Kenya county.
    county: Kenya county name e.g. Nairobi, Mombasa, Kisumu, Nakuru
    level: KEPH facility level — 4=District, 5=Regional Referral, 6=National Referral (0=all)
    """
    county_clean = county.strip().title()
    facilities = FACILITIES.get(county_clean, [])
    if level:
        facilities = [f for f in facilities if f["level"] == level]
    return {
        "county": county_clean,
        "facilities": facilities,
        "note": f"{'No facility data for ' + county_clean + '. ' if not facilities else ''}Call county health department or 0800 720 021 (free).",
        "emergency_line": "0800 720 021 (free 24hr)",
        "ambulance": "999 or 0800 723 253",
        "source": "Ministry of Health Kenya facility registry",
    }


@mcp.tool()
def get_maternal_protocol() -> dict:
    """
    Get Kenya antenatal care schedule and Linda Mama free maternity programme details.
    Includes ANC visit schedule, postnatal care, newborn vaccines, and birth registration.
    """
    return {
        "programme": "Linda Mama Free Maternity",
        "coverage": "Free delivery, postnatal care, and newborn care at ALL public facilities",
        "antenatal_visits": [
            {"visit": 1, "timing": "Before 12 weeks", "focus": "Booking, blood tests, HIV, tetanus, iron+folic"},
            {"visit": 2, "timing": "20 weeks",         "focus": "Ultrasound, growth check, dental"},
            {"visit": 3, "timing": "26 weeks",         "focus": "Blood pressure, baby position, PMTCT"},
            {"visit": 4, "timing": "30 weeks",         "focus": "Iron/folic, birth plan discussion"},
            {"visit": 5, "timing": "36 weeks",         "focus": "Final position check, birth preparedness"},
            {"visit": 6, "timing": "38-40 weeks",      "focus": "Pre-labour assessment"},
        ],
        "postnatal_visits": ["6 hours", "6 days", "6 weeks"],
        "newborn_vaccines": [
            "Birth: BCG + OPV0",
            "6 weeks: DPT-HepB-Hib + OPV1 + PCV + Rota",
            "10 weeks: DPT-HepB-Hib + OPV2 + PCV + Rota",
            "14 weeks: DPT-HepB-Hib + OPV3 + PCV + IPV",
            "9 months: Measles + Yellow Fever",
            "18 months: Measles booster",
        ],
        "birth_registration": "Within 6 months at nearest Civil Registry — free of charge",
        "source": "Ministry of Health Kenya / Linda Mama Programme",
    }


@mcp.tool()
def get_health_right(topic: str = "healthcare", language: str = "en") -> dict:
    """
    Get Kenya constitutional health rights under Article 43 of the Constitution of Kenya 2010.
    topic: healthcare, maternal, emergency
    language: en (English) or sw (Kiswahili)
    """
    topic_lower = topic.lower().strip()
    for key, texts in RIGHTS.items():
        if key in topic_lower or topic_lower in key:
            return {
                "topic": key,
                "right": texts.get(language, texts["en"]),
                "source": "Constitution of Kenya 2010, Article 43",
                "related": "Article 53 covers children's rights to health care",
            }
    return {
        "error": f"Topic '{topic}' not found.",
        "available_topics": list(RIGHTS.keys()),
        "hint": "Try: healthcare, maternal, emergency",
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
