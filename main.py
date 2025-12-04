import csv
import re

try:
    with open("phonebook_raw.csv", encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)
except FileNotFoundError as e:
    print(f"Ошибка: файл 'phonebook_raw.csv' не найден. {e}")
    exit(1)
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")
    exit(1)


def format_phone(phone):
    pattern = (
        r"[\s\-\(]*(\+?7|8)?[\s\-\(]*(\d{3})[\s\-\)]*(\d{3})"
        r"[\s\-\)]*(\d{2})[\s\-\)]*(\d{2})[\s\-\(]*(доб\.?)?"
        r"[\.\s\-]?\s*(\d+)?[\s\)]*"
    )
    repl = r"+7(\2)\3-\4-\5"
    if "доб." in phone:
        repl += r" доб.\7"
    formatted = re.sub(pattern, repl, phone)
    return formatted.strip()


header = contacts_list[0]
data = contacts_list[1:]

contacts_dict = {}

for row in data:
    # print(len(row))
    while len(row) < 7:
        row.append("")  # Дополняем до 7 на всякий случай
    # print(row[:3])
    full_name = " ".join(row[:3]).strip().split()
    lastname = full_name[0] if len(full_name) > 0 else ""
    firstname = full_name[1] if len(full_name) > 1 else ""
    surname = full_name[2] if len(full_name) > 2 else ""
    organization = row[3] if len(row) > 3 else ""
    position = row[4] if len(row) > 4 else ""
    phone = format_phone(row[5]) if len(row) > 5 else ""
    email = row[6] if len(row) > 6 else ""

    key = (lastname, firstname)

    if key not in contacts_dict:
        contacts_dict[key] = [
            lastname,
            firstname,
            surname,
            organization,
            position,
            phone,
            email,
        ]
    else:
        existing = contacts_dict[key]  # берём сохранённую запись
        for i, value in enumerate([surname, organization, position, phone, email]):
            if value and not existing[i + 2]:
                existing[i + 2] = value

# Финальный список
final_contacts_list = [header[:7]]
final_contacts_list.extend(contacts_dict.values())
final_contacts_list.sort(key=lambda x: x[0])  # Сортировка по алфавиту

# pprint(final_contacts_list)

try:
    with open("phonebook.csv", "w", encoding="utf-8", newline="") as f:
        datawriter = csv.writer(f, delimiter=",")
        datawriter.writerows(final_contacts_list)
except Exception as e:
    print(f"Ошибка при записи файла: {e}")
    exit(1)
