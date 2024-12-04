#!/usr/bin/python3
#var/teamcity/data/config/projects/_Root/pluginData/secure
from Crypto.Cipher import DES3
from codecs import decode
from sys import argv

# Given ciphertext
ciphertext1 = "zxxc9da77e51f3a3f32fea352d8a7c6ba4c4823bf82ad5d3e66e9010541d46d6cb48833a5bc577a3bff775d03cbe80d301b"
ciphertext2 = "zxx1ee6a73b032a526d21fd2ae86ac82c62"
ciphertext  = "zxx6bb1e86a8f6b90f394f853d427849fb47da955ef470f66f464fa261489e4fe2e775d03cbe80d301b"
# Key as a signed byte array, converted to an unsigned byte array
key_signed_byte_array = [61, 22, 11, 57, 110, 89, -20, -1, 0, 99, 111, -120, 55, 4, -9, 10, 11, 45, 71, -89, 21, -99, 54, 51]
key_byte_array = [b & 0xff for b in key_signed_byte_array]
key = bytes(key_byte_array)

# Strip the 'zxx' prefix and decode the ciphertext from hex
des3_ciphertext = ciphertext.lstrip('zxx')
des3_cipherbytes = decode(des3_ciphertext, 'hex')

# Create the cipher object
cipher = DES3.new(key, DES3.MODE_ECB)  # Assuming ECB mode, change if necessary

# Decrypt the data and remove padding
plaintext_padded = cipher.decrypt(des3_cipherbytes)
plaintext = plaintext_padded[:-plaintext_padded[-1]]

# Print the decoded plaintext
print(plaintext.decode('utf-8'))
