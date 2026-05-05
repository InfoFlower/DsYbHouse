from random import randint

class Link_Users:
    def __init__(self):
        self.USER_LINKS = {}
    
    def add_link(self, passphrase, user):
        self.USER_LINKS[passphrase] = user
    
    def get_user(self, passphrase):
        return self.USER_LINKS[passphrase]
    
    def get_passphrase(self, user):
        for passphrase, linked_user in self.USER_LINKS.items():
            if linked_user == user:
                return passphrase
        return None
    
def generate_passphrase(length=12):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    passphrase = ''.join(characters[randint(0, len(characters) - 1)] for _ in range(length))
    return passphrase