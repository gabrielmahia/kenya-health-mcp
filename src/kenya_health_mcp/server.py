"""KenyaHealthMCP — Kenya health data MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kenya-health-mcp")

# SHIF replaced NHIF in October 2024: 2.75% of gross, minimum KES 300, no cap, paid by the employee only (no employer match).
# Rates are from consistent secondary sources (law-firm and payroll-provider summaries) checked on 2026-10-04, not the SHA primary text.
SHIF_RATE = 0.0275
SHIF_MINIMUM_KES = 300.0

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
        "en": "Maternity care is now provided through the Social Health Authority (SHA), which replaced NHIF in 2024. The NHIF-era Linda Mama programme is no longer a separate scheme. Reported arrangement: antenatal and postnatal visits through the Primary Healthcare Fund at levels 2 and 3, delivery through SHIF, with prior SHA registration. Reports about details conflict; verify with SHA (sha.go.ke) before relying on any of it.",
        "sw": "Huduma za uzazi sasa zinatolewa kupitia Mamlaka ya Afya ya Jamii (SHA), iliyochukua nafasi ya NHIF mwaka 2024. Mpango wa Linda Mama wa enzi za NHIF si mpango tofauti tena. Utaratibu unaoripotiwa: kliniki za kabla na baada ya kujifungua kupitia Hazina ya Huduma ya Afya ya Msingi (ngazi ya 2 na 3), kujifungua kupitia SHIF, na usajili wa SHA kabla ya kujifungua. Ripoti kuhusu maelezo zinatofautiana; thibitisha na SHA (sha.go.ke) kabla ya kutegemea.",
    },
    "emergency": {
        "en": "Article 43(3): The State shall provide appropriate social security to persons who are unable to support themselves and their dependants.",
        "sw": "Kifungu 43(3): Serikali itatoa usalama wa kijamii unaofaa kwa watu wasio na uwezo wa kujitegemea.",
    },
}


def _shif(gross_salary_kes: float) -> float:
    return max(SHIF_MINIMUM_KES, round(gross_salary_kes * SHIF_RATE, 2))


@mcp.tool()
def get_shif_contribution(gross_salary_kes: float) -> dict:
    """
    Get the monthly Social Health Insurance Fund (SHIF) contribution for a gross salary in Kenya Shillings.
    SHIF replaced NHIF in October 2024: 2.75% of gross, minimum KES 300, no cap, paid by the employee only.
    gross_salary_kes: Monthly gross salary in KES
    """
    if gross_salary_kes <= 0:
        return {"error": "gross_salary_kes must be greater than zero"}
    contribution = _shif(gross_salary_kes)
    return {
        "gross_salary_kes": gross_salary_kes,
        "employee_contribution_kes": contribution,
        "employer_match_kes": 0.0,
        "total_monthly_kes": contribution,
        "rate": "2.75% of gross, minimum KES 300, no cap, employee only",
        "source": "Social Health Insurance Act 2023 (rates from secondary summaries, checked 2026-10-04; not the SHA primary text)",
        "note": "Verify current rates at sha.go.ke",
    }


@mcp.tool()
def get_nhif_contribution(gross_salary_kes: float) -> dict:
    """
    DEPRECATED NAME. NHIF was repealed and replaced by SHIF in October 2024; this returns the SHIF contribution.
    Use get_shif_contribution. gross_salary_kes: Monthly gross salary in KES
    """
    result = get_shif_contribution(gross_salary_kes)
    result["deprecated"] = "NHIF no longer exists; this tool name is kept for compatibility and returns the SHIF contribution. Use get_shif_contribution."
    return result


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
    Get the Kenya antenatal care schedule and how maternity care is covered now that SHA has replaced NHIF (Linda Mama status below).
    Includes ANC visit schedule, postnatal care, newborn vaccines, and birth registration.
    """
    return {
        "programme": "Maternity care under SHA (the NHIF-era Linda Mama programme is no longer a separate scheme)",
        "coverage": "Reported: antenatal and postnatal visits through the Primary Healthcare Fund (levels 2 and 3); delivery through SHIF; prior SHA registration required. Reports conflict on details; verify with SHA (sha.go.ke).",
        "status_checked": "2026-10-04, from news and explainer sources, not the SHA primary text",
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
