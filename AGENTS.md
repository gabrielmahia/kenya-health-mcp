# AGENTS.md — KenyaHealthMCP

Kenya health data MCP server (4th MCP in portfolio).

## Tools
- get_shif_contribution(gross_salary_kes)  (NHIF was replaced by SHIF in October 2024)
- get_nhif_contribution(gross_salary_kes)  (deprecated alias of the above)
- find_facility(county, level)
- get_maternal_protocol()
- get_health_right(topic, language)

## Rules
- Data/information only — never diagnose
- Always cite source (MOH, Social Health Insurance Act 2023, Constitution of Kenya 2010)
- Emergency number: 0800 720 021 (free, 24hr)
- Respond bilingually when language=sw
