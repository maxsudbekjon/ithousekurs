import random

def generate_verification_code(length=6):
    return str(random.randint(10**(length-1), 10**length - 1))