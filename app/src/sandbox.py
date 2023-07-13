
answers = {
    "/get_lost_count": "На данный момент количество пользователей, которые ожидают ответа на свои вопросы: {users_number} .\n\nЧтобы отобразить следующего пользователя с нерешенными вопросами воспользуйтесь клавиатурой с командами в нижней части экрана или используйте команду /next_user ."
}
user_info_list = ["sd", "sdf"]
text = str(answers.get("/get_lost_count")).format(**{"users_number": len(user_info_list)})
print(text)
