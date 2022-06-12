import pandas as pd
from datetime import datetime
from django.contrib.auth.models import User
from api.models import UserInfo
import os


def register_users(delete_users: list, temp_table: str):
    cols = ["last_name", "first_name", "patronymic", "balance", "generated_username"]
    df = pd.read_csv("media/tables/" + temp_table, usecols=cols)
    # df = pd.read_csv("../../storage/tables/" + temp_table, usecols=cols)
    df = df[~df["generated_username"].isin(delete_users)]
    user_info = df.to_dict()

    for i in df.index:
        user = User.objects.create_user(username=user_info["generated_username"][i],
                                        password="tempPas_" + user_info["generated_username"][i])
        UserInfo.objects.create(user_id=user, balance=user_info["balance"][i],
                                first_name=user_info["first_name"][i],
                                last_name=user_info["last_name"][i],
                                patronymic=user_info["patronymic"][i],
                                )
    os.remove("media/tables/" + temp_table)

    # main_table_path = "../../storage/tables/Пользователи из загруженных таблиц.xlsx"
    main_table_path = "media/tables/Пользователи из загруженных таблиц.xlsx"
    registered_users = pd.read_excel(main_table_path, usecols=[*cols, "date"], engine='openpyxl')
    df["date"] = [str(datetime.now().date())] * len(df)

    pd.concat([registered_users, df]).to_excel(main_table_path, engine='openpyxl')

    return "Successfully!"
