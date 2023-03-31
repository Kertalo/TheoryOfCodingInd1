import PIL.Image
from PIL import Image
import numpy as np

NAME_MAIN_IMAGE = "main.png"
NAME_SECRET_IMAGE = "secret.png"
NAME_OUT_MAIN_IMAGE = "out_main.png"
NAME_OUT_SECRET_IMAGE = "out_secret.png"


def FindH(method):
    H = []
    for i in range(0, method):
        a = []
        for j in range(1, 2 ** method):
            a.append(int(bin(2 ** method + j)[i + 3]))
        H.append(a)
    return H


def ImageToArray(name):
    return np.array(Image.open(name).convert("RGB"))


def Syndrome(container, message, h_matrix):
    method = len(h_matrix)
    syndrome = 0
    message_int = 0
    while len(message) < method:
        message.append(0)
    for i in range(0, method):
        message_int += 2 ** (method - i - 1) * message[i]
        a = 0
        for j in range(0, 2 ** method - 1):
            a += h_matrix[i][j] * container[j]
        syndrome += 2 ** (method - i - 1) * (a % 2)

    if syndrome != 0:
        container[syndrome - 1] = 1 if container[syndrome - 1] == 0 else 0
    if message_int != 0:
        container[message_int - 1] = 1 if container[message_int - 1] == 0 else 0

    return container


def SyndromeForGetSecret(container, h_matrix):
    method = len(h_matrix)
    message = []
    for i in range(0, method):
        a = 0
        for j in range(0, 2 ** method - 1):
            a += h_matrix[i][j] * container[j]
        message.append(a % 2)
    return message


# Встраивание
def Embed(name_main, name_secret, method):
    main = ImageToArray(name_main)
    secret = ImageToArray(name_secret)

    H = FindH(method)

    message = []
    for i in range(0, len(secret)):
        a = []
        for j in range(0, len(secret[0])):
            for k in range(0, 3):
                for t in range(7, -1, -1):
                    a.append(int(secret[i, j][k] / (2 ** t)) % 2)
        message.append(a)

    for i in range(0, len(secret)):
        current_main = []
        first_index = (0, 0)
        for j in range(0, len(main[0])):
            current_main.append(main[i, j][0] % 2)
            current_main.append(main[i, j][1] % 2)
            current_main.append(main[i, j][2] % 2)
            if len(current_main) >= 2 ** method - 1:
                current_secret = message[i][0:method]
                del message[i][0:method]
                edit_current_main = Syndrome(current_main[0:2 ** method - 1], current_secret, H)
                current_main = current_main[2 ** method - 1:]
                for k in range(first_index[0], j + 1):
                    for t in range(first_index[1], 3):
                        pop_message = edit_current_main.pop(0)
                        if main[i, k][t] % 2 != pop_message:
                            if main[i, k][t] % 2 == 0:
                                main[i, k][t] += 1
                            else:
                                main[i, k][t] -= 1
                        if len(edit_current_main) == 0:
                            break
                    first_index = (first_index[0], 0)
                first_index = (j, 3 - len(current_main))
                if len(message[i]) == 0:
                    break

    Image.fromarray(main).save(NAME_OUT_MAIN_IMAGE)


# Извлечение
def Extract(name_out_main, name_out_secret, method, size):
    main = ImageToArray(name_out_main)
    H = FindH(method)

    secret_bits = []
    for i in range(0, size[1]):
        a = []
        current_main = []
        for j in range(0, len(main[0])):
            current_main.append(main[i, j][0] % 2)
            current_main.append(main[i, j][1] % 2)
            current_main.append(main[i, j][2] % 2)

            if len(current_main) >= 2 ** method - 1:
                #print(current_main[0:2 ** method - 1])
                current_secret = SyndromeForGetSecret(current_main[0:2 ** method - 1], H)
                #print("2_" + str(current_secret) + str(i) + " " + str(j))
                current_main = current_main[2 ** method - 1:]
                for k in range(0, method):
                    a.append(current_secret[k])
                if len(a) == 8 * 3 * size[0]:
                    break
        secret_bits.append(a)
    #print(secret_bits)

    secret = np.array(PIL.Image.new('RGB', size))
    for i in range(0, len(secret_bits)):
        p = 0
        color = 0
        color_type = 0
        byte = 8
        #pixels = []
        #colors = []
        for j in range(0, len(secret_bits[i])):
            byte -= 1
            color += 2 ** byte * secret_bits[i][j]
            if byte == 1:
                byte = 8
                if p >= size[0]:
                    break
                secret[i][p][color_type] = color
                color_type += 1
                #colors.append(color)
                color = 0
                if color_type == 3:
                    p += 1
                    color_type = 0
                    #pixels.append(colors)
                    #colors = []
        #secret.append(pixels)
    #secret_rgb = np.asarray(secret)
    #im = PIL.Image.new('RGB', size)
    #print(secret_rgb)
    #secret_rgb = np.asarray(im)
    Image.fromarray(secret).save(name_out_secret)


Embed(NAME_MAIN_IMAGE, NAME_SECRET_IMAGE, 4)
Extract(NAME_OUT_MAIN_IMAGE, NAME_OUT_SECRET_IMAGE, 4, (14, 11))
H = FindH(3)
# print(Syndrome([0, 1, 0, 1, 0, 1, 0], [0, 0, 0], H))
# print(SyndromeForGetSecret([1, 0, 0, 1, 1, 0, 1], H))
