import hashlib
passs = hashlib.sha256("root".encode()).hexdigest()
print(passs)
