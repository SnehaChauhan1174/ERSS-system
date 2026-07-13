from datetime import datetime

# Hindi dictionary mappings for dates
MONTHS_HI = {
    1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल",
    5: "मई", 6: "जून", 7: "जुलाई", 8: "अगस्त",
    9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर"
}

DAYS_HI = {
    0: "सोमवार", 1: "मंगलवार", 2: "बुधवार", 3: "गुरुवार",
    4: "शुक्रवार", 5: "शनिवार", 6: "रविवार"
}

# Sleek SVG Icons
# 'stroke="currentColor"' forces the icon to match the grey text color defined in your CSS
CALENDAR_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -3px; margin-right: 6px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>"""

CLOCK_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -3px; margin-right: 6px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>"""

def get_formatted_datetime(lang="en"):
    """Returns the current date and time formatted with SVG icons for the given language."""
    now = datetime.now()
    
    # Format time (e.g., 01:03 AM)
    time_str = f"{CLOCK_ICON}{now.strftime('%I:%M %p')}"
    
    if lang == "hi":
        day_name = DAYS_HI[now.weekday()]
        month_name = MONTHS_HI[now.month]
        date_str = f"{CALENDAR_ICON}{day_name}, {now.day} {month_name} {now.year}"
    else:
        date_str = f"{CALENDAR_ICON}{now.strftime('%A, %B %d, %Y')}"
        
    return f"{date_str} &nbsp;&nbsp;|&nbsp;&nbsp; {time_str}"