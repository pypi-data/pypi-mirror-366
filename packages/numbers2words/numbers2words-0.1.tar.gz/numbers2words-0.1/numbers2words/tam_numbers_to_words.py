import re
from .numbers_list import *
def tam_above_1000(number, length):
    groups = []
    result = ''
    if length % 2 == 0:
        number = number.zfill(length+1)
    tail = number[-3:]
    head = number[:-3]
    head = [head[i:i+2] for i in range(0,len(head),2)]
    while(len(head)>0):
        groups.insert(0,head[-1:][0])
        head = head[:-1]
    groups.append(tail)
    group_length = len(groups)
    for i in groups:
        temp = tam_numbers_to_words_0_to_999(i)
        denomination = 0
        continue_flag = True
        if group_length >= 1:
            denomination = group_length - 1
            group_length -= 1
            if temp == 'பூஜ்யம்':
                continue
            for j in range(group_length,len(groups)):
                if int(groups[j]) == 0:
                    continue_flag = False

        if group_length >= 1 and continue_flag == True:
            result += temp + " " + tamil_name_formation[denomination][1] + " "
        else:
            result += temp + " " + tamil_name_formation[denomination][0] + " "
    return result
def tam_numbers_to_words_0_to_99(number, ispaise=None):
    if not ispaise:
        number = re.sub(r"^0+(?!$)", "", number)
    length = len(number)
    if length == 1:
        if ispaise:
            return tam_10_to_90[str(number)+"0"][0]
        else:
            return tam_0_to_9[str(number)]
    elif length == 2:
        if ispaise:
            number = re.sub(r"^0+(?!$)", "", number)
            if len(number) == 1:
                return tam_0_to_9[str(number)]
            elif int(number) < 20:
                return tam_10_to_19[str(number)][0]
            elif int(number) > 19:
                temp_number = str(number)[0] + '0'
                if int(str(number)[1]) > 0:
                    result = tam_10_to_90[temp_number][1] + ' ' + tam_0_to_9[str(number)[1]]
                else:
                    result = tam_10_to_90[temp_number][0]
                return result
        elif int(number) < 20:
            return tam_10_to_19[str(number)]
        elif int(number) > 19:
            temp_number = str(number)[0] + '0'
            if int(str(number)[1]) > 0:
                result = tam_10_to_90[temp_number][1] + ' ' + tam_0_to_9[str(number)[1]]
            else:
                result = tam_10_to_90[temp_number][0]
            return result
def tam_numbers_to_words_0_to_999(number):
    number = re.sub(r"^0+(?!$)", "", number)
    length = len(str(number))
    temp_number = ''
    if length < 3:
        result = tam_numbers_to_words_0_to_99(number,None)
        return result
    if length == 3:
        if int(str(number)[1]) == 0 and int(str(number)[2]) == 0:
            return tam_100_to_900[str(number)][0]

        elif int(str(number)[1]) == 0 and int(str(number)[2]) != 0:
            result = tam_100_to_900[str(number)[0] + "00"][1] + " " + tam_0_to_9[str(number)[2]]
            return result

        elif int(str(number)[1]) != 0 and int(str(number)[2]) == 0:
            result = tam_100_to_900[str(number)[0] + "00"][1] + ' ' + tam_10_to_90[str(number)[1] + "0"][0]
            return result
        else:

            result = tam_100_to_900[str(number)[0] + "00"][1] + " " + tam_10_to_90[str(number)[1] + "0"][1] + " " + tam_0_to_9[str(number)[2]]
            return result
    if length > 3:
        if number in tamil_named_numbers.keys():
            return "ஒரு " + tamil_named_numbers[number][0]
        else:
            result = tam_above_1000(number, length)
            return result