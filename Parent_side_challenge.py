from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

pin0.set_touch_mode(pin0.CAPACITIVE)     #activation des 3 pin en tant que touche
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)

def generate_key(seed):                  
    return hashing(seed)                   #grace au hashing on génére une key différente a partir d'une seed identique aux 2 microbit 

"""
Type des messages

0 = challenge
1 = lait
2 = bruits 
3 = température
4 = light_level


"""





#Initialisation des variables du micro:bit
radio.on()
radio.config(group=3)
connexion_established = False
key = generate_key(13)
connexion_key = None
nonce_list = set()
baby_state = 0
set_volume(100)

flamme = Image("00000:"
               "00500:"
               "05550:"
               "55555:"
               "05550")
flocons = Image("50505:"
                "05550:"
                "55055:"
                "05550:"
                "50505")
compteur_de_lait = Image("00500:"
                         "50005:"
                         "50005:"
                         "50005:"
                         "55555:")
luminosité_auto = Image("00500:"
                        "05550:"
                        "55555:"
                        "05550:"
                        "00500:")
temperature = Image("00500:"
                    "05555:"
                    "00500:"
                    "00500:"
                    "00055:")
hors_de_portée = Image("00500:"
                       "00500:"
                       "00500:"
                       "00000:"
                       "00500:")
musique_bruits = Image("05555:"
                       "05005:"
                       "05005:"
                       "55055:"
                       "55055:")
musiquemode = Image("00500:"
                    "00500:"
                    "00500:"
                    "05500:"
                    "05500:")

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
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
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
        #Letters encryption/decryption
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
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
    
def send_packet(key, type, content):
    """
    Envoi de données fournies en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit

    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
	:return none
    """
    packet = f"{type}|{len(content)}|{content}"             #le packet est initialisé sous format T|L|V
    encrypted_packet = vigenere(packet, key)               #on chiffre le packet 
    radio.send(str(encrypted_packet))                     #le packet chiffré est envoyé 
#Unpack the packet, check the validity and return the type, length and content
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
    decrypted_packet = vigenere(encrypted_packet, key)                   #decrypter le message recu
    decrypted_packet.split("|")                                  #on sépare et remet au format T|L|V
    for type, length, message in decrypted_packet:            #on crée une boucle pour pouvoir ensuite renvoyer les éléments du decrypted_packet
        return f"type: {type}"
        return f"length: {int(length)}"
        return f"message: {message}"
    
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
    packet_received = unpack_data(radio.received(), key)  
    try:    
        if packet_received:
            for i in packet_received :
                real_packet =  f"{i}|{i+1}|{i+2}"
            return real_packet
    except:
        return " | | "

#Calculate the challenge response
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection envoyé par l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """
    challenge = vigenere("tentative de connexion", key)         #décryptage du challenge recu 
    if challenge == "connexion":
         challenge_response = "réussie"
    send_packet(key, 0, challenge_response)                   #reponse au challenge crypté 

#Respond to a connexion request by sending the hash value of the number received
def respond_to_connexion_request(key):
    """
    Réponse au challenge initial de connection avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                   Clé de chiffrement
	:return (srt) challenge_response:   Réponse au challenge
    """

    send_packet(key, 6, key )   #la clé de base est deja hachée donc on va juste l'envoyer ???
    


def menu():
    lst = [compteur_de_lait, luminosité_auto, temperature, musique_bruits]
    value = []
    stop = False
    for i in lst:
        while not button_a.was_pressed():
            display.scroll(i, delay=90, monospace=True)
            if button_b.was_pressed():
                value.clear()
                value.append(i)
                stop = True
                break
            elif button_a.is_pressed():
                stop = True
                break
        
    if value and value[0] == compteur_de_lait:
        lait()
    elif value and value[0] ==luminosité_auto: #PAS OPERATIONNEL
        light_lvl_menu()
    elif value and value[0] == temperature:
        temp()
    elif value and value[0] == musique_bruits:
        musique_et_bruits()


def compteur_de_lait():
    milk_doses = 0
    if pin0.is_touched():
        milk_doses = 0  
        display.show("0") 
        sleep(500) 
    elif pin1.is_touched():
        milk_doses += 1 
        display.show(str(milk_doses))
        sleep(500)
    elif pin2.is_touched:
        if milk_doses > 0:
            milk_doses += 2
    elif boutton_a.is_touched():
        if milk_doses > 0:
            milk_doses _= 1
        display.show(str(milk_doses))
        sleep(500)



def main():
    if message.received():
        packet_receive = receive_packet(message.receive(), key)        #déballe le message recu 
        if packet_receive[1] == 0:                                    #vérifie à chque fois le type du message 
                calculate_challenge_response(packet_receive[2])
                respond_to_connexion_request(key)
        elif packet_receive[1] == 1:
             lait()
        elif packet_receive[2] == 2:
             musique_et_bruits()
        elif packet_receive[3] == 3:
             temp()
    elif pin_logo.is_touched():
        if out_of_range():
            break
        else:
            menu()

