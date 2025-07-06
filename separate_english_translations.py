import csv

input_file = 'flashcards-output/final_sino_native_list.csv'
output_file = 'flashcards-output/final_sino_native_list_separate_english_translations.csv'

with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames.copy()

    # Modify fieldnames
    fieldnames[fieldnames.index('english_translations')] = 'english_translation'
    fieldnames.append('english_more_translations')

    rows = []
    for row in reader:
        translations = row['english_translations'].split('; ')
        if translations:
            row['english_translation'] = translations[0]
            row['english_more_translations'] = '; '.join(translations[1:])
        else:
            row['english_translation'] = ''
            row['english_more_translations'] = ''
        del row['english_translations']
        rows.append(row)

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
