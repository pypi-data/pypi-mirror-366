from typing import *
import asyncio
import logging
import traceback
import sys
from functools import reduce
import jon as JON
import copy
import os
import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from .config import DEBUG, NODEENV
from .utils import getLang
from .exception import EncryptionError


class BinaryEncode:
    _lang: str = 'fr'
    _debug: bool = DEBUG
    def __init__(self, key_size=256, mode=AES.MODE_CBC, lang = 'fr', debug: bool = DEBUG):
        self._debug = debug if type(debug) == bool else True
        self._lang = getLang(lang)
    
    def encrypt(self, val):
        try:
            return int(str(val).encode('utf-8').hex(), 16)
        except:
            stack = traceback.format_exc()
            trace = sys.exc_info()[2]
            raise EncryptionError(stack, file = __name__, debug = DEBUG)
    def decrypt(self, val):
        try:
            return bytes.fromhex((hex(int(val))[2:])).decode('utf-8')
        except:
            stack = traceback.format_exc()
            trace = sys.exc_info()[2]
            raise EncryptionError(stack, file = __name__, debug = DEBUG)
class AESEncryptor:
    _lang: str = 'fr'
    _debug: bool = DEBUG
    def __init__(self, key_size=256, mode=AES.MODE_CBC, lang = 'fr', debug: bool = DEBUG):
        """
        Initialise l'encrypteur AES avec une taille de clé spécifique.
        
        Args:
            key_size (int): Taille de la clé en bits (128, 192 ou 256)
            mode: Mode d'opération AES (par défaut: CBC)
        """
        self._debug = debug if type(debug) == bool else True
        self._lang = getLang(lang)
        if key_size not in [128, 192, 256]:
            raise EncryptionError({
                "fr": "La taille de clé doit être 128, 192 ou 256 bits",
                "en": "The key size must be 128, 192 or 256 bits",
            }[self._lang])
        
        self.key_size = key_size
        self.mode = mode
    
    def generate_key(self):
        """Génère une clé aléatoire de la taille spécifiée"""
        return get_random_bytes(self.key_size // 8)
    def generate_fixed_key(self, password: str) -> bytes:
        """
        Génère une clé AES fixe à partir d'une chaîne de caractères.
        
        Args:
            password (str): La chaîne de caractères (mot de passe) à utiliser
            
        Returns:
            bytes: Clé AES de la taille demandée
        """
        key_size: int = self.key_size
        if key_size not in [128, 192, 256]:
            raise EncryptionError({
                "fr": "La taille de clé doit être 128, 192 ou 256 bits",
                "en": "The key size must be 128, 192 or 256 bits",
            }[self._lang])
        
        # Convertir le mot de passe en bytes si ce n'est pas déjà fait
        password_bytes = password.encode('utf-8')
        
        # Utilisation de SHA-256 pour une dérivation simple (pour les cas simples)
        # Pour une meilleure sécurité, utiliser PBKDF2 ou scrypt (voir version améliorée ci-dessous)
        hash_obj = hashlib.sha256(password_bytes)
        full_key = hash_obj.digest()
        
        # Prendre seulement les bytes nécessaires
        key = full_key[:key_size // 8]
        return key
    def generate_secure_fixed_key(self, password: str, salt: bytes = None, iterations: int = 100000) -> bytes:
        """
        Génère une clé AES de manière sécurisée à partir d'une chaîne de caractères.
        
        Args:
            password (str): Le mot de passe à utiliser
            salt (bytes): Sel pour la dérivation (aléatoire si None)
            iterations (int): Nombre d'itérations pour PBKDF2
            
        Returns:
            bytes: Clé AES dérivée
            bytes: Sel utilisé (utile pour la régénération)
        """
        key_size: int = self.key_size
        if key_size not in [128, 192, 256]:
            raise EncryptionError({
                "fr": "La taille de clé doit être 128, 192 ou 256 bits",
                "en": "The key size must be 128, 192 or 256 bits",
            }[self._lang])
        
        if salt is None:
            salt = os.urandom(16)  # Sel de 16 bytes
        
        key = PBKDF2(password, salt, dkLen=key_size//8, count=iterations, hmac_hash_module=hashlib.sha256)
        return key, salt
    
    def encrypt(self, plaintext, key, iv=None):
        """
        Encrypte le texte en utilisant AES avec la clé fournie.
        
        Args:
            plaintext (str or bytes): Texte à encrypter
            key (bytes): Clé d'encryption
            iv (bytes): Vecteur d'initialisation (si None, généré aléatoirement)
            
        Returns:
            dict: Dictionnaire contenant:
                - 'ciphertext': Texte encrypté (base64)
                - 'iv': Vecteur d'initialisation (base64)
                - 'key_size': Taille de la clé utilisée
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
            
        if len(key) != self.key_size // 8:
            raise EncryptionError({
                "fr": f"La clé doit être de taille {self.key_size} bits ({self.key_size//8} bytes)",
                "en": f"The key must be {self.key_size} bits in size ({self.key_size//8} bytes)",
            }[self._lang])
            
        if iv is None:
            iv = get_random_bytes(AES.block_size)
        elif len(iv) != AES.block_size:
            raise EncryptionError({
                "fr": f"IV doit être de taille {AES.block_size} bytes",
                "en": f"IV must be {AES.block_size} bytes in size",
            }[self._lang])
            
        cipher = AES.new(key, self.mode, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'key_size': self.key_size
        }
    
    def decrypt(self, ciphertext, key, iv):
        """
        Décrypte le texte encodé en AES.
        
        Args:
            ciphertext (str or bytes): Texte encrypté (base64)
            key (bytes): Clé d'encryption
            iv (bytes): Vecteur d'initialisation (base64)
            
        Returns:
            str: Texte décrypté
        """
        if isinstance(ciphertext, str):
            ciphertext = base64.b64decode(ciphertext.encode('utf-8'))
            
        if isinstance(iv, str):
            iv = base64.b64decode(iv.encode('utf-8'))
            
        if len(key) != self.key_size // 8:
            raise EncryptionError({
                "fr": f"La clé doit être de taille {self.key_size} bits ({self.key_size//8} bytes)",
                "en": f"The key must be {self.key_size} bits in size ({self.key_size//8} bytes).",
            }[self._lang])
            
        cipher = AES.new(key, self.mode, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return plaintext.decode('utf-8')