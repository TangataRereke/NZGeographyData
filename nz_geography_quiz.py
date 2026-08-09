#!/usr/bin/env python3
"""
New Zealand Geography & Emergency Service Quiz Program
Author: Jules
Description: Interactive CLI testing application to prepare for NZ geography tests
             and emergency services research.
"""

import os
import re
import random
import sys

# Color configurations for CLI
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
ENDC = '\033[0m'

def print_header(title):
    print(f"\n{BLUE}{BOLD}{'=' * 60}{ENDC}")
    print(f"{BLUE}{BOLD}  {title}{ENDC}")
    print(f"{BLUE}{BOLD}{'=' * 60}{ENDC}\n")

def normalize_name(s):
    if not s:
        return ""
    # Map te reo Māori macrons to plain Latin characters
    mapping = {
        'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o', 'ū': 'u',
        'Ā': 'a', 'Ē': 'e', 'Ī': 'i', 'Ō': 'o', 'Ū': 'u'
    }
    s = s.lower()
    for k, v in mapping.items():
        s = s.replace(k, v)
    # Remove any non-alphanumeric characters
    return re.sub(r'[^a-z0-9]', '', s)

def parse_markdown_table(filepath):
    """
    Parses a Markdown table from a given file and returns list of dictionaries representing rows.
    """
    if not os.path.exists(filepath):
        return []

    rows = []
    headers = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        # Split by pipe and strip spaces
        parts = [p.strip() for p in line.split('|')[1:-1]]

        # Determine if it's separator row
        if all(re.match(r'^:?-+:?$', p) for p in parts) and parts:
            continue

        if not headers:
            headers = [h.replace(' (Region)', '') for h in parts]
            continue

        # Build dictionary
        if len(parts) == len(headers):
            row_dict = dict(zip(headers, parts))
            # Clean names and clean coordinates
            for k, v in row_dict.items():
                if k in ['Latitude', 'Longitude']:
                    try:
                        # Extract float from coordinate strings
                        m = re.search(r'-?\d+\.\d+', v)
                        row_dict[k] = float(m.group(0)) if m else None
                    except ValueError:
                        row_dict[k] = None
            rows.append(row_dict)

    return rows

def load_geography_data():
    """
    Loads all geographical items (Towns/Cities, Lakes, Rivers/Harbors, Landmarks).
    Adds a 'Category' tag and computes 'Island' dynamically based on Latitude.
    """
    items = []

    # 1. Towns & Cities
    town_files = [
        'data/towns_cities/towns_a_g.md',
        'data/towns_cities/towns_h_n.md',
        'data/towns_cities/towns_o_z.md'
    ]
    for tf in town_files:
        for r in parse_markdown_table(tf):
            r['Category'] = 'Town/City'
            items.append(r)

    # 2. Lakes
    for r in parse_markdown_table('data/waterways/lakes.md'):
        r['Category'] = 'Waterway (Lake)'
        items.append(r)

    # 3. Rivers & Harbors
    for r in parse_markdown_table('data/waterways/rivers_harbors.md'):
        r['Category'] = 'Waterway (River/Harbor)'
        items.append(r)

    # 4. Landmarks (Natural)
    for r in parse_markdown_table('data/landmarks/natural_landmarks.md'):
        r['Category'] = 'Landmark (Natural)'
        items.append(r)

    # 5. Landmarks (Built & Cultural)
    for r in parse_markdown_table('data/landmarks/built_cultural.md'):
        r['Category'] = 'Landmark (Built/Cultural)'
        items.append(r)

    # Post-process: assign Island and make sure required keys are present
    valid_items = []
    for item in items:
        # Standardize key names
        if 'Province(s)' in item and 'Province' not in item:
            item['Province'] = item['Province(s)']
        if 'Police District(s)' in item and 'Police District' not in item:
            item['Police District'] = item['Police District(s)']

        name = item.get('English Name')
        lat = item.get('Latitude')

        if not name or lat is None:
            continue

        # Determine Island based on Province/Region (latitude overlaps in the northern South Island)
        prov = item.get('Province', '').strip()
        if 'Chatham' in prov:
            item['Island'] = 'Chatham Islands'
        elif any(r in prov for r in ['Tasman', 'Nelson', 'Marlborough', 'West Coast', 'Canterbury', 'Otago', 'Southland']):
            item['Island'] = 'South Island'
        else:
            item['Island'] = 'North Island'

        # Ensure Māori Name is present
        m_name = item.get('Māori Name')
        if not m_name or m_name == '-':
            item['Māori Name'] = ''

        valid_items.append(item)

    return valid_items

def get_relative_position_question(items):
    """
    Generates a north/south relationship question.
    """
    # Pick two items from the same island to make it realistic
    island = random.choice(['North Island', 'South Island'])
    filtered = [item for item in items if item['Island'] == island]

    if len(filtered) < 2:
        # Fallback to any if not enough
        filtered = items

    obj1, obj2 = random.sample(filtered, 2)

    # Compare Latitudes (more negative = further south)
    # e.g., -45.8 (Dunedin) is further south than -43.5 (Christchurch)
    is_south = obj1['Latitude'] < obj2['Latitude']
    correct_ans = 'south' if is_south else 'north'

    question = f"Is {BOLD}{obj1['English Name']}{ENDC} north or south of {BOLD}{obj2['English Name']}{ENDC}?"
    hint = f"({obj1['English Name']} is in {obj1.get('Province', 'NZ')}; {obj2['English Name']} is in {obj2.get('Province', 'NZ')})"

    return question, hint, correct_ans

def get_province_question(items):
    item = random.choice(items)
    question = f"What province/region is the {item['Category'].lower()} {BOLD}{item['English Name']}{ENDC} in?"
    correct_ans = item.get('Province', '').strip()
    return question, "", correct_ans

def get_district_question(items):
    item = random.choice(items)
    question = f"What Police District is the {item['Category'].lower()} {BOLD}{item['English Name']}{ENDC} under?"
    correct_ans = item.get('Police District', '').strip()
    return question, "", correct_ans

def get_island_question(items):
    item = random.choice(items)
    question = f"Which island (North Island or South Island) is {BOLD}{item['English Name']}{ENDC} located on?"
    correct_ans = item['Island']
    return question, "", correct_ans

def run_geography_quiz(items):
    print_header("Mode 1: Location & Relationship Quiz")
    print("Type 'q' or 'quit' at any time to return to main menu.\n")

    score = 0
    total = 0
    
    # Build a shuffled pool of questions first
    question_pool = []
    for _ in range(len(items) * 3):  # 3x ensures plenty of variety
        q_type = random.choice(['relative', 'province', 'district', 'island'])
        if q_type == 'relative':
            q, hint, ans = get_relative_position_question(items)
        elif q_type == 'province':
            q, hint, ans = get_province_question(items)
        elif q_type == 'district':
            q, hint, ans = get_district_question(items)
        else:
            q, hint, ans = get_island_question(items)
        if ans:  # only add valid questions
            question_pool.append((q, hint, ans))
    random.shuffle(question_pool)

    for q, hint, ans in question_pool:
        # Choose a question type
        #q_type = random.choice(['relative', 'province', 'district', 'island'])

        if q_type == 'relative':
            q, hint, ans = get_relative_position_question(items)
        elif q_type == 'province':
            q, hint, ans = get_province_question(items)
        elif q_type == 'district':
            q, hint, ans = get_district_question(items)
        else:
            q, hint, ans = get_island_question(items)

        if not ans:
            continue

        print(f"{YELLOW}Question {total + 1}:{ENDC} {q}")
        if hint:
            print(f"  {BLUE}Hint:{ENDC} {hint}")

        user_ans = input(f"Your Answer: ").strip()

        if user_ans.lower() in ['q', 'quit']:
            break

        # Clean answer comparison (case insensitive, loose space check)
        norm_user = user_ans.lower().replace(" ", "")
        norm_correct = ans.lower().replace(" ", "")

        # Also support partially loose matching for regions like "Manawatū-Whanganui" -> "manawatu"
        is_correct = norm_user == norm_correct
        if not is_correct:
            # Let's support secondary easy names like "manawatu" for "Manawatū-Whanganui"
            clean_user = re.sub(r'[^a-zA-Z0-9]', '', norm_user)
            clean_correct = re.sub(r'[^a-zA-Z0-9]', '', norm_correct)
            if clean_user in clean_correct and len(clean_user) >= 5:
                is_correct = True

        if is_correct:
            print(f"{GREEN}✓ Correct!{ENDC}\n")
            score += 1
        else:
            print(f"{RED}✗ Incorrect.{ENDC} The correct answer is: {GREEN}{ans}{ENDC}\n")

        total += 1

    if total > 0:
        print_header("Quiz Finished")
        print(f"Your Score: {score}/{total} ({score/total*100:.1f}%)")
    else:
        print("\nNo questions answered.")

def run_spelling_quiz(items):
    print_header("Mode 2: Geography Spelling Challenge")
    print("Fill in the blank letters in between the first and last letter.")
    print("Type 'q' or 'quit' to return to the main menu.\n")

    score = 0
    total = 0

    # Build a shuffled list of all valid spelling items
    spelling_pool = [item for item in items if len(item['English Name']) >= 4]
    random.shuffle(spelling_pool)

    if not spelling_pool:
        print("No items to spell!")
        return

    for item in spelling_pool:
#        item = random.choice(items)
        name = item['English Name']

        # Exclude names that are too short to quiz effectively (e.g., < 4 letters)
        if len(name) < 4 in name:# or ' ' in name or '/' in name or '-' in name:
            continue

        first = name[0]
        last = name[-1]
        middle_len = len(name) - 2
        blanks = "_" * middle_len

        # Build prompt string, e.g. T____u
        masked_word = f"{first}{blanks}{last} ({len(name)})"

        # Extra helpful details
        desc = item.get('Type / Description') or item.get('Description') or ""
        cat_info = f"{item['Category']}"
        province = item.get('Province', '').strip()
        district = item.get('Police District', '').strip()
        m_name = item.get('Māori Name', '').strip()

        print(f"{YELLOW}Question {total + 1}:{ENDC} Spell this New Zealand {cat_info.lower()}:")
        print(f"  {BOLD}{masked_word}{ENDC}")
        print(f"  {BLUE}Location:{ENDC} {province} region, {district} Police District")
        # Only show Māori Name if it provides a non-trivial hint (i.e. different from English Name)
        if m_name and normalize_name(m_name) != normalize_name(name):
            print(f"  {BLUE}Māori Name:{ENDC} {m_name}")
        if desc:
            print(f"  {BLUE}Description:{ENDC} {desc}")

        user_ans = input(f"Your spelling: ").strip()

        if user_ans.lower() in ['q', 'quit']:
            break

        if user_ans.lower() == name.lower():
            print(f"{GREEN}✓ Absolutely Correct! Spelled perfectly: {BOLD}{name}{ENDC}\n")
            score += 1
        else:
            print(f"{RED}✗ Incorrect spelling.{ENDC} The correct spelling is: {GREEN}{BOLD}{name}{ENDC}\n")

        total += 1

    if total > 0:
        print_header("Spelling Challenge Finished")
        print(f"Your Score: {score}/{total} ({score/total*100:.1f}%)")
    else:
        print("\nNo questions answered.")

def main():
    try:
        items = load_geography_data()
    except Exception as e:
        print(f"{RED}Error loading NZ geographical datasets: {e}{ENDC}")
        sys.exit(1)

    if not items:
        print(f"{RED}No geographical data found! Please make sure files exist in the data/ directory.{ENDC}")
        sys.exit(1)

    while True:
        print_header("New Zealand Geography & Emergency Services Testing Tool")
        print(f"Loaded {GREEN}{len(items)}{ENDC} geographical features.")
        print("Please choose a study mode:")
        print(f" {BOLD}1.{ENDC} Location & Relationship Quiz")
        print(f" {BOLD}2.{ENDC} spelling Challenge (Fill-in-the-blanks)")
        print(f" {BOLD}3.{ENDC} Quit")

        choice = input("\nEnter selection (1-3): ").strip()

        if choice == '1':
            run_geography_quiz(items)
        elif choice == '2':
            run_spelling_quiz(items)
        elif choice == '3' or choice.lower() in ['q', 'quit', 'exit']:
            print(f"\n{GREEN}Kia ora! Good luck studying for your test!{ENDC}\n")
            break
        else:
            print(f"{RED}Invalid option. Please choose 1, 2, or 3.{ENDC}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{GREEN}Kia ora! Exiting geography program...{ENDC}\n")
        sys.exit(0)
