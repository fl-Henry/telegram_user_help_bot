from random import randint

user_info_list = [0, 1, 2, 3, 4, 5, 6]
index = randint(0, len(user_info_list) - 1)
print(index)
user_info = user_info_list[index]
print(user_info)