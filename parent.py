import random
import music
import radio
from microbit import *


pin0.set_touch_mode(pin0.CAPACITIVE)  # activation des 3 pin en tant que touche
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)


icons_flamme = Image("00000:" "00800:" "08880:" "88888:" "08880")
icons_flocons = Image("80808:" "08880:" "88088:" "08880:" "80808")
icons_milk = Image("00800:" "08080:" "08080:" "08080:" "08880:")
icons_light = Image("00800:" "08880:" "88888:" "08880:" "00800:")
icons_temperature = Image("00800:" "08888:" "00800:" "00800:" "00088:")
icons_sound = Image("08888:" "08008:" "08008:" "88088:" "88088:")
icons_musiquemode = Image("00800:" "00800:" "00800:" "08800:" "08800:")
icons_state = Image("88888:" "88888:" "88888:" "88888:" "88888:")


milk_quantity = 0
listening_mode = 0
menu_mode = 1


def hashing(string):
    """
    Hachage d'une chaîne de caractères fournie en paramètre.
    Le résultat est une chaîne de caractères.
    Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.
    :param (str) string: la chaîne de caractères à hacher
    :return (str): le résultat du hachage
    """

    def to_32(value):
        """
        Fonction interne utilisée par hashing.
        Convertit une valeur en un entier signé de 32 bits.
        Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.


        :param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
        :return (int): entier signé de 32 bits représentant 'value'
        """
        value = value % (2**32)
        if value >= 2**31:
            value = value - 2**32
        value = int(value)
        return value

    if string:
        x = ord(string[0]) << 7
        m = 1000003
        for c in string:
            x = to_32((x * m) ^ ord(c))
        x ^= len(string)
        if x == -1:
            x = -2
        return str(x)
    return ""


def vigenere(message, key, decryption=False):
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        # Letters encryption/decryption
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord("A"))
            else:
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord("A"))
            # Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        # Digits encryption/decryption
        elif char.isdigit():
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text


def send_packet(key, message_type, message):
    """
    Envoi de données fournies en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit


    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
        :return none
    """
    packet = "{}|{}|{}".format(message_type, str(len(message)), message)  # format T|L|V
    encrypted_packet = vigenere(packet, key)
    radio.send(encrypted_packet)
    return encrypted_packet


def unpack_data(encrypted_packet, key):
    """
    Déballe et déchiffre les paquets reçus via l'interface radio du micro:bit
    Cette fonction renvoit les différents champs du message passé en paramètre


    :param (str) encrypted_packet: Paquet reçu
           (str) key:              Clé de chiffrement
        :return (srt)type:             Type de paquet
            (int)length:           Longueur de la donnée en caractères
            (str) message:         Données reçue
    """
    return vigenere(encrypted_packet, key, decryption=True)


def receive_packet(packet_received, key):
    """
    Traite les paquets reçus via l'interface radio du micro:bit
    Cette fonction utilise la fonction unpack_data pour renvoyer les différents champs du message passé en paramètre
    Si une erreur survient, les 3 champs sont retournés vides


    :param (str) packet_received: Paquet reçue
           (str) key:              Clé de chiffrement
        :return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractère
            (str) message:         Données reçue
    """
    decrypted_packet = unpack_data(packet_received, key)
    return decrypted_packet.split("|")


# Calculate the challenge response
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection envoyé par l'autre micro:bit


    :param (str) challenge:            Challenge reçu
        :return (srt)challenge_response:   Réponse au challenge
    """


# Respond to a connexion request by sending the hash value of the number received
def respond_to_connexion_request(key):
    """
    Réponse au challenge initial de connection avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide


    :param (str) key:                   Clé de chiffrement
        :return (srt) challenge_response:   Réponse au challenge
    """


def menu():
    images = [icons_milk, icons_light, icons_temperature, icons_sound, icons_state]
    value = ""
    current_index = 0

    # Generate a key
    key = hashing("1")  # Replace with the actual seed

    while True:
        image = images[current_index]
        display.show(image)
        if button_a.was_pressed():
            value = image
            select_option(value, key)

        if button_b.was_pressed():
            current_index += 1
            sleep(100)

        if current_index >= len(images):
            current_index = 0

        if pin_logo.is_touched():
            sleep(1000)
            return listening_mode

        sleep(100)


def select_option(value, key):
    if value == icons_milk:
        milk_quantity = set_milk_quantity()
        send_packet(key=key, message_type="1", message=str(milk_quantity))
    elif value == icons_light:
        handle_night_light()
    elif value == icons_temperature:
        get_temperature()
    elif value == icons_sound:
        play_sound()
    elif value == icons_state:
        get_state()
    return


def set_milk_quantity():
    global milk_quantity
    display.show(str(milk_quantity))
    sleep(500)
    while True:
        if pin0.is_touched():
            milk_quantity = 0
            display.show(str(milk_quantity))
            sleep(500)
        if pin1.is_touched():
            milk_quantity += 1
            display.show(str(milk_quantity))
            sleep(500)
        if pin2.is_touched():
            milk_quantity += 2
            display.show(str(milk_quantity))
            sleep(500)
        if button_a.was_pressed():
            if milk_quantity > 0:
                milk_quantity -= 1
            display.show(str(milk_quantity))
            sleep(500)
        if pin_logo.is_touched():
            break
    return milk_quantity


def handle_night_light():
    while True:
        if button_a.was_pressed():
            message = "activate_light"
            send_packet(key=hashing("1"), message_type="0", message=message)
            display.show(Image.YES)
            sleep(1000)
        if button_b.was_pressed():
            message = "deactivate_light"
            send_packet(key=hashing("1"), message_type="0", message=message)
            display.show(Image.NO)
            sleep(1000)
        if pin_logo.is_touched():
            break
    return


def get_temperature():
    send_packet(key=hashing("1"), message_type="0", message="send_temperature")
    sleep(1000)
    message_type, message_length, message = receive_packet(packet_received=radio.receive(), key=hashing("1"))
    display.scroll(message)
    return


def play_sound():
    while True:
        if button_a.was_pressed():
            display.show("M")
            while True:
                sleep(100)
                if pin0.is_touched():
                    display.show("1")
                    send_packet(key=hashing("1"), message_type="2", message="melody_1")
                    sleep(1000)
                if pin1.is_touched():
                    display.show("2")
                    send_packet(key=hashing("1"), message_type="2", message="melody_2")
                    sleep(1000)
                if pin2.is_touched():
                    display.show("3")
                    send_packet(key=hashing("1"), message_type="2", message="melody_3")
                    sleep(1000)
                if button_a.was_pressed():
                    break

        if button_b.was_pressed():
            send_packet(key=hashing("1"), message_type="0", message="play_noise")
            display.show("B")
            sleep(1000)
        if pin_logo.is_touched():
            break
    return


def get_state():
    while True:
        if button_a.was_pressed():
            send_packet(key=hashing("1"), message_type="0", message="send_state")
            sleep(1000)
            message_type, message_length, message = receive_packet(radio.receive(), hashing("1"))
            if message == "asleep":
                display.show(Image.ASLEEP)
                sleep(1000)
            elif message == "agitated":
                display.show(Image.MEH)
                sleep(1000)
            elif message == "very agitated":
                music.play(music.POWER_DOWN)
                display.show(Image.NO)
                sleep(1000)
        if pin_logo.is_touched():
            break
    return


def listen():
    display.show("P")
    while True:
        sleep(100)
        if pin_logo.is_touched():
            sleep(1000)
            return menu_mode

        packet = receive_packet(radio.receive(), hashing("1"))
        if len(packet) < 3:
            sleep(1000)
            continue
        message_type, message_length, message = packet

        sleep(100)


def main():
    radio.on()
    radio.config(group=3)
    display.show("P")

    current_state = listening_mode

    while True:
        if current_state == listening_mode:
            current_state = listen()
        elif current_state == menu_mode:
            current_state = menu()


main()
