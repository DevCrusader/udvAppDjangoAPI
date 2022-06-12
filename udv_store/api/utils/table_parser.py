import pandas as pd
from math import isnan
from .transliterator import transliterate as tr
from django.contrib.auth.models import User
from datetime import datetime


# 1 test
# request = rq.request_2
# file_ = "fio_and_balance_in_one_str.csv"
# file_ = "fio_and_balance_not_in_one_str.csv"
# file_ = "table.xlsx"
# file_ = "fio_without_balance.csv"
# file_ = "fio_in_rows_and_balance.csv"
# file_ = "fio_in_rows_and_balance_not_in_on_str.csv"
# file_ = "fio_in_rows_without_balance.csv"

def generate_username(*args):
    username = tr('_'.join(*args))
    users_with_same_username = User.objects.filter(username__startswith=username)
    if users_with_same_username.exists():
        username += "_" + str(users_with_same_username.count())
    return username


def parse_data_from_file(table_file, request: dict, excel: bool, csv: bool):
    if not excel and not csv:
        return "Загруженный файл имеет неправильный формат"

    cols = []
    result = []
    cur_dict = {}

    def add_fio_to_dict(dict_: dict, in_one_column: bool, row_values: pd.Series):
        if in_one_column:
            fio_order = {}
            for index, char in enumerate(request["fio_order"].lower()):
                param = "first_name" if char in ["и", "И"] else "last_name" \
                    if char in ["ф", "Ф"] else "patronymic" if char in ["о", "О"] else ""
                fio_order[param] = index
            split_fio = row_values[first_col_name].rstrip().rsplit()
            for key in ["last_name", "first_name", "patronymic"]:
                dict_[key] = split_fio[fio_order[key]]
        else:
            for i, value in enumerate(["last_name", "first_name", "patronymic"]):
                dict_[value] = row_values[cols[i]]

    if request["fio_in_one_column"]:
        cols.append(request["fio_column_name"])
    else:
        for key in ["last_name", "first_name", "patronymic"]:
            cols.append(request["fio_columns_name"][key])

    if request["table_have_balance"]:
        cols.append(request["balance_column_name"])

    df = pd.DataFrame()
    if excel:
        df = pd.read_excel(table_file, usecols=cols)
    if csv:
        df = pd.read_csv(table_file, usecols=cols)

    first_col_name = cols[0]

    if request["table_have_balance"] and not request["fio_and_balance_in_one_row"]:
        for index, row in df.iterrows():
            if type(row[first_col_name]) != float:
                add_fio_to_dict(cur_dict, request["fio_in_one_column"], row)
            else:
                cur_dict["balance"] = row[cols[-1]] if not isnan(row[cols[-1]]) else 0
                result.append(cur_dict)
                cur_dict = {}
    else:
        for index, row in df.iterrows():
            add_fio_to_dict(cur_dict, request["fio_in_one_column"], row)
            if request["fio_and_balance_in_one_row"]:
                cur_dict["balance"] = row[cols[-1]] if not isnan(row[cols[-1]]) else 0
            else:
                cur_dict["balance"] = 0
            result.append(cur_dict)
            cur_dict = {}

    for item in result:
        item["generated_username"] = generate_username([item["last_name"].lower(),
                                                        item["first_name"][0], item["patronymic"][0]])

        # item["generated_password"] = "tempPas_" + item["generated_username"]

    temporary_table_name = "tempTable_" + str(datetime.now()) + ".csv"
    pd.DataFrame(data=result).to_csv("media/tables/" + temporary_table_name)

    # table_to_request = result.copy()

    dict_to_request = [
        {
            "first_name": item["first_name"],
            "last_name": item["last_name"],
            "patronymic": item["patronymic"],
            "username": item["generated_username"]
        } for item in result
    ]

    return {"resulted_data": dict_to_request, "temporary_table_name": temporary_table_name}
