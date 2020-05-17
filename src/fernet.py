import argparse
from cryptography.fernet import Fernet

def encrypt(password, private_key):
    p_key = Fernet(private_key)
    return p_key.encrypt(password.encode("utf-8"))

def decrypt(public_key, private_key):
    p_key = Fernet(private_key)
    return p_key.decrypt(public_key.encode("utf-8"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate and encrypt wallet password')
    parser.add_argument('--gen-privkey', dest='privatekey', action='store_true', help='generate private key')
    parser.add_argument('--encrypt', dest='password', action='store', help='encrypt wallet with private key')
    parser.add_argument('--decrypt', dest='decrypt', action='store', help='decrypt wallet with private key')
    args = parser.parse_args()

    if args.privatekey:
        print("Generating private key...")
        with open("WPK.key", 'w') as p_key:
            p_key.write(Fernet.generate_key().decode("utf-8"))
        print("Complete! WPK.key created")

    elif args.password:
        print("Encrypting password with private key")
        with open("WPK.key", "r") as p_key:
            print(f"Encrypted string: {encrypt(args.password, p_key.readline())}")
        print("Complete!")

    elif args.decrypt:
        print("Decrypting password with private key")
        with open("WPK.key", "r") as p_key:
            print(f"Decrypted string: {decrypt(args.decrypt, p_key.readline())}")
        print("Complete!")