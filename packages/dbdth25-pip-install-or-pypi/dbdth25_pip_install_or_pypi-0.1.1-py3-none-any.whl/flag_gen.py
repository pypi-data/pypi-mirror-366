import base64
import zlib
import pickle
from itertools import cycle

TEST_FLAG="Aks7Azw3Ag4XAxQNAiwiAxZSAldIA1w6AiMmAy4+AjQhAwIhAjwTAycEAhJEAy0MAkY6AwATAjQxAxQDAkQNAxMEAjFEAxNQAiFDAygTAhYoAxAwAjIWA0YBAhJFAzUAAgQNAwASAjAFAyYkAkMuAwRZAjUKAyc5AjAQAxc5AgABAwktAjUEAzU8AgYmAxUbAgwJAzJTAioWA0haAj9HAwgTAkQxAycgAhUBAysCAhcEA0VTAiwlAzYgAg8CAykyAi8yAyshAkdEAysQAg43AyIgAi83AwYOAikPAygEAggTAyYM"

def decode_flag(flag):
    step1 = base64.b64decode(flag).decode()
    step2 = ''.join([chr((ord(c) - 97 + 13) % 26 + 97) if 'a' <= c <= 'z' 
                     else chr((ord(c) - 65 + 13) % 26 + 65) if 'A' <= c <= 'Z' 
                     else c for c in step1])
    key = b"secret"
    step3 = bytes([a ^ b for a, b in zip(step2.encode(), cycle(key))]).decode()
    reversed_str = step3[::-1]
    step4 = ''.join([chr((ord(c) - ord('a') + 7) % 26 + ord('a')) if 'a' <= c <= 'z'
                     else chr((ord(c) - ord('A') + 7) % 26 + ord('A')) if 'A' <= c <= 'Z'
                     else c for c in reversed_str])
    filtered = ''.join([step4[i] for i in range(len(step4)) if (i + 1) % 3 != 0])
    step5 = filtered
    compressed_data = base64.b64decode(step5.encode())
    step6 = zlib.decompress(compressed_data).decode()
    pickled_data = base64.b64decode(step6.encode())
    nested_dict = pickle.loads(pickled_data)
    final_flag = nested_dict['level1']['level2']['flag']
    return final_flag

if __name__ == "__main__":
    print("Look at that! Someone has been trying to decode the flag!")
    decoded_flag = decode_flag(test_flag) # noop
    print("Here you go!", decoded_flag) # Frenzy Flag!