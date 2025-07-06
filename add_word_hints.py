import csv
from collections import defaultdict

input_file = 'flashcards-output/final_sino_native_list.csv'
output_file = 'flashcards-output/final_sino_native_list_hanja_hints.csv'

# Step 1: Read all rows
with open(input_file, 'r', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

# Step 1.5: Remove duplicates by hanja
seen_hanja = set()
filtered_rows = []
for row in rows:
    hanja_val = row.get('hanja', '').strip()
    if hanja_val == '':
        # Keep rows with empty hanja always
        filtered_rows.append(row)
    else:
        # For non-empty hanja, keep only first occurrence
        if hanja_val not in seen_hanja:
            seen_hanja.add(hanja_val)
            filtered_rows.append(row)

rows = filtered_rows

# Step 2: Prepare new fieldnames
fieldnames = reader.fieldnames.copy()
fieldnames[fieldnames.index('english_translations')] = 'english_translation'
fieldnames.append('english_more_translations')
fieldnames.append('hanja_left_hint')
fieldnames.append('hanja_right_hint')
fieldnames.append('hint_hanja')

# Step 3: Group by Hangul word
word_groups = defaultdict(list)
for row in rows:
    key = row['word']
    word_groups[key].append(row)

# Step 4: Generate hints
for group in word_groups.values():
    if len(group) > 1:
        hanjas = [row['hanja'] for row in group]
        hangul = group[0]['word']
        word_len = len(hangul)

        for row in group:
            current = row['hanja']
            left_hints = []
            right_hints = []
            full_hints = []

            for other in hanjas:
                if current == other:
                    continue

                min_len = min(len(current), len(other))
                # If hanja lengths are different, fall back to full hint
                if len(current) != len(other):
                    full_hints.append(f"{hangul}({current})")
                    continue

                diff_indices = [i for i in range(len(current)) if current[i] != other[i]]
                
                if len(diff_indices) == len(current):
                    # Completely different hanja → use hint_hanja
                    full_hints.append(f"{current}")
                    continue

                for idx in diff_indices:
                    diff_char = current[idx]
                    if idx == 0:
                        left_hints.append(diff_char)
                    elif idx == word_len - 1:
                        right_hints.append(diff_char)
                    elif word_len == 3:
                        right_hints.append(f"{diff_char}-")
                    elif word_len == 4:
                        if idx == 1:
                            left_hints.append(f"-{diff_char}")
                        elif idx == 2:
                            right_hints.append(f"{diff_char}-")
                        else:
                            left_hints.append(f"{hangul}([{current}])")
                            right_hints.append(f"{hangul}([{current}])")
                    else:
                        right_hints.append(f"{hangul}([{current}])")

            # Assign appropriate hint field
            if full_hints:
                row['hint_hanja'] = ', '.join(sorted(set(full_hints)))
                row['hanja_left_hint'] = ''
                row['hanja_right_hint'] = ''
            else:
                row['hint_hanja'] = ''
                row['hanja_left_hint'] = ', '.join(sorted(set(left_hints)))
                row['hanja_right_hint'] = ', '.join(sorted(set(right_hints)))
    else:
        group[0]['hanja_left_hint'] = ''
        group[0]['hanja_right_hint'] = ''
        group[0]['hint_hanja'] = ''

# Step 5: Process English translations
for row in rows:
    translations = row['english_translations'].split('; ')
    row['english_translation'] = translations[0] if translations else ''
    row['english_more_translations'] = '; '.join(translations[1:]) if len(translations) > 1 else ''
    del row['english_translations']

# Step 6: Write output CSV
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
