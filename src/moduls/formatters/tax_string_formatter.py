def tax_str_formatter(tax_data, period_dates, total_tax, space, max_key, total_entries, total_label):
    header = f"Total {total_label}: {total_entries}\nTotal Tax: {total_tax} isk"

    if period_dates:
        header += f"\nPeriod: {period_dates[0]} - {period_dates[1]}"

    title_word = total_label[:-1]

    l_f_space = ""
    r_f_space = ""
    end_symbol = ""

    for _ in range(int((max_key - len(title_word)) / 2)):
        l_f_space += " "

    for _ in range(max_key - (len(l_f_space) + len(title_word))):
        r_f_space += " "

    tax_str_first = f"|  {l_f_space}{title_word}{r_f_space}  |    Tax  "
    end_simbol_range = len(space) - len(tax_str_first)
    for _ in range(end_simbol_range - 1):
        end_symbol += " "
    else:
        end_symbol += "|"

    tax_str_second = "|" + space[1:-1] + "|"
    tax_str = f"{tax_str_first}{end_symbol}\n{tax_str_second}\n"

    for item in tax_data:
        tax_str += item

    return [header, tax_str]
