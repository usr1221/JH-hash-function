import JHhash

def read_test_vectors(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    test_vectors = []
    i = 0
    while i < len(lines):
        original_message = lines[i].strip().split(": ")[1]
        test_vectors.append({
            "message": original_message,
            "hashes": {
                224: lines[i+1].strip().split(": ")[1],
                256: lines[i+2].strip().split(": ")[1],
                384: lines[i+3].strip().split(": ")[1],
                512: lines[i+4].strip().split(": ")[1]
            }
        })
        i += 5
    return test_vectors
def check_hashes(test_vectors):
    for vector in test_vectors:
        message = bytes.fromhex(vector["message"])
        for hashbitlen, expected_hash in vector["hashes"].items():
            computed_hash = bytearray()
            JHhash.Hash(hashbitlen, message, len(message) * 4, computed_hash)
            if computed_hash.hex() != expected_hash:
                print(f"Test failed for message {vector['message']} with hash length {hashbitlen}.")
                print(f"Expected: {expected_hash}")
                print(f"Got:      {computed_hash.hex()}")
            else:
                print(f"Test passed for message {vector['message']} with hash length {hashbitlen}.")

if __name__ == "__main__":
    test_vectors = read_test_vectors('output.txt')
    check_hashes(test_vectors)
