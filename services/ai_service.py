import json
import datetime
import re


# -----------------------------
# Normalize natural dates → YYYY-MM-DD
# -----------------------------
def normalize_due_date(due_text):

    if not due_text:
        return ""

    due_text = due_text.lower().strip()
    today = datetime.date.today()

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    months = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
    }

    # ----------------------------------
    # tomorrow
    # ----------------------------------
    if "tomorrow" in due_text:
        return (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # ----------------------------------
    # in X days
    # ----------------------------------
    match = re.search(r"in (\d+) days", due_text)
    if match:
        days = int(match.group(1))
        return (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    # ----------------------------------
    # next weekday
    # ----------------------------------
    for day, number in weekdays.items():
        if f"next {day}" in due_text:
            days_ahead = number - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + datetime.timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # ----------------------------------
    # plain weekday (exact only)
    # ----------------------------------
    for day, number in weekdays.items():
        if due_text == day:
            days_ahead = number - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + datetime.timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # ----------------------------------
    # Formats like: 2026-02-19
    # ----------------------------------
    try:
        parsed = datetime.datetime.strptime(due_text, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except:
        pass

    # ----------------------------------
    # Formats like: 19/02/2026 or 19-02-2026
    # ----------------------------------
    match = re.search(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})", due_text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return datetime.date(year, month, day).strftime("%Y-%m-%d")

    # ----------------------------------
    # Formats like: Feb 19 or February 19
    # ----------------------------------
    match = re.search(r"([a-z]+)\s+(\d{1,2})", due_text)
    if match:
        month_word = match.group(1)
        day = int(match.group(2))

        if month_word in months:
            month = months[month_word]
            year = today.year
            return datetime.date(year, month, day).strftime("%Y-%m-%d")

    # ----------------------------------
    # Formats like: 19 Feb
    # ----------------------------------
    match = re.search(r"(\d{1,2})\s+([a-z]+)", due_text)
    if match:
        day = int(match.group(1))
        month_word = match.group(2)

        if month_word in months:
            month = months[month_word]
            year = today.year
            return datetime.date(year, month, day).strftime("%Y-%m-%d")

    # ----------------------------------
    # If nothing matched → return raw
    # (Capture page will handle missing date)
    # ----------------------------------
    return ""


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def organize_task(client, user_input):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
You are an academic task extractor.

Extract all academic tasks from the user's message.

Allowed task types (must choose ONLY one of these):
- Exam
- Quiz
- Assignment
- Project
- Lab
- Presentation

If the task does not clearly match one of these,
default to "Assignment".

Return ONLY valid JSON.

Format:
[
  {
    "task_name": "",
    "type": "",
    "due": ""
  }
]

Rules:
- If no due date is mentioned, set "due" to "".
- NEVER guess dates.
- NEVER use today's date.
- Do NOT include explanations.
- Do NOT include markdown.
- Return JSON only.
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    # Remove markdown if model wraps in ```json
    if content.startswith("```"):
        content = content.split("```")[1]

    tasks = json.loads(content)

    # Normalize safely
    for task in tasks:
        raw_due = task.get("due", "").strip()

        if raw_due == "":
            task["due"] = ""
        else:
            task["due"] = normalize_due_date(raw_due)

    return tasks

# -----------------------------
# BREAK ASSIGNMENT INTO STEPS
# -----------------------------
def generate_assignment_plan(client, requirements_text):

    prompt = f"""
You are helping a university student plan their assignment.

Break the assignment into 3 to 6 clear study steps.

Each step should represent a logical part of completing the assignment.

Return only the steps as separate lines.

Assignment:
{requirements_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You help students break assignments into study steps."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    steps_text = response.choices[0].message.content.strip()

    steps = []

    for line in steps_text.split("\n"):
        line = line.strip()

        if line:
            steps.append(line)

    return steps


# -----------------------------
# DISTRIBUTE STEPS ACROSS DAYS
# -----------------------------
def distribute_steps(steps, due_date):

    due = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()

    study_plan = {}

    for i, step in enumerate(steps):

        study_day = due - datetime.timedelta(days=(len(steps) - i))

        study_plan[str(study_day)] = step

    return study_plan
