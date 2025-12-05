import csv
import re


INPUT_FILE_NAME = "phonebook_raw.csv"
OUTPUT_FILE_NAME = "phonebook.csv"

# Чтение входного CSV-файла
try:
    with open(INPUT_FILE_NAME, encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)
except FileNotFoundError as e:
    print(f"Ошибка: файл '{INPUT_FILE_NAME}' не найден. {e}")
    exit(1)
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")
    exit(1)


def format_phone_number(phone_number):
    """
    Форматирует телефонный номер в едином стандарте: +7(XXX)XXX-XX-XX [доб.XXXX].

    Поддерживает форматы:
        - 8(999)123-45-67
        - +7 999 123 45 67
        - 8-999-123-45-67 доб.123
        - и другие варианты с пробелами, скобками, дефисами.

    Args:
        phone_number (str): Исходный телефонный номер.

    Returns:
        str: Отформатированный номер.
    """
    pattern = (
        r"[\s\-\(]*(\+?7|8)?[\s\-\(]*(\d{3})[\s\-\)]*(\d{3})"
        r"[\s\-\)]*(\d{2})[\s\-\)]*(\d{2})[\s\-\(]*(доб\.?)?"
        r"[\.\s\-]?\s*(\d+)?[\s\)]*"
    )
    repl = r"+7(\2)\3-\4-\5"
    if "доб." in phone_number:
        repl += r" доб.\7"
    formatted = re.sub(pattern, repl, phone_number)
    return formatted.strip()


def parse_contact_row(contact_row):
    """
    Преобразует "сырую" строку контакта в нормализованный формат.

    - Дополняет строку до 7 полей, если не хватает.
    - Разбивает ФИО из первых трёх полей.
    - Форматирует телефон.
    - Возвращает ключ (фамилия, имя) и полный контакт.

    Args:
        contact_row (list): Строка контакта из CSV (список строк).

    Returns:
        tuple[tuple[str, str], list[str]]: Ключ (lastname, firstname) и
            список полей контакта:
            [lastname, firstname, surname, organization, position, phone, email]
    """
    contact_row = (contact_row + [""] * 7)[:7]  # дополняем до 7

    full_name = " ".join(contact_row[:3]).strip().split()
    lastname = full_name[0] if len(full_name) > 0 else ""
    firstname = full_name[1] if len(full_name) > 1 else ""
    surname = full_name[2] if len(full_name) > 2 else ""

    return (lastname, firstname), [
        lastname,
        firstname,
        surname,
        contact_row[3],  # organization
        contact_row[4],  # position
        format_phone_number(contact_row[5]),  # phone
        contact_row[6],  # email
    ]


# Основная логика: объединение дубликатов по (фамилии, имени)
header = contacts_list[0]
data = contacts_list[1:]

contacts_dict = {}

for row in data:
    key, contact_data = parse_contact_row(row)

    if key not in contacts_dict:
        contacts_dict[key] = contact_data
    else:
        existing_contact = contacts_dict[key]
        # Обновляем surname, org, pos, phone, email (индексы 2-6)
        for i in range(2, 7):
            if contact_data[i] and not existing_contact[i]:
                existing_contact[i] = contact_data[i]

# Финальный список
final_contacts_list = [header[:7]]
final_contacts_list.extend(contacts_dict.values())
final_contacts_list.sort(key=lambda x: x[0])  # Сортировка по фамилии

# Запись в файл CSV
try:
    with open(OUTPUT_FILE_NAME, "w", encoding="utf-8", newline="") as f:
        datawriter = csv.writer(f, delimiter=",")
        datawriter.writerows(final_contacts_list)
except Exception as e:
    print(f"Ошибка при записи файла: {e}")
    exit(1)
