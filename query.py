import re


def extract_keywords(prompt):
    words = re.findall(r"\b\w+\b", prompt.lower())
    return [word for word in set(words) if len(word) > 2]


def find_related_data(prompt, data, limit=5):
    keywords = extract_keywords(prompt)
    related_data = []

    for item in data:
        match_count = 0
        matched_sections = []

        if any(keyword in item.get("title", "").lower() for keyword in keywords):
            match_count += 1

        for section in item.get("sections", []):
            if any(keyword in section.get("title", "").lower() for keyword in keywords):
                matched_sections.append(
                    {"number": section.get("number"), "title": section.get("title")}
                )
                match_count += 1

        if match_count > 0:
            related_data.append(
                {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "date": item.get("date"),
                    "match_count": match_count,
                }
            )

    related_data = sorted(related_data, key=lambda x: x["match_count"], reverse=True)
    return related_data[:limit]
