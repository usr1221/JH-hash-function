#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jh_ref.h"

#define MAX_LINE_LENGTH 8192 // Increased buffer size

void printHashToFile(FILE *outputFile, const BitSequence* hashval, int hashbitlen) {
    for (int i = 0; i < hashbitlen / 8; i++) {
        fprintf(outputFile, "%02x", hashval[i]);
    }
    fprintf(outputFile, "\n");
}

void printHexToFile(FILE *outputFile, const BitSequence* data, size_t datalen) {
    for (size_t i = 0; i < datalen; i++) {
        fprintf(outputFile, "%02x", data[i]);
    }
    fprintf(outputFile, "\n");
}

int hexCharToByte(char hex) {
    if ('0' <= hex && hex <= '9') return hex - '0';
    if ('A' <= hex && hex <= 'F') return hex - 'A' + 10;
    if ('a' <= hex && hex <= 'f') return hex - 'a' + 10;
    return -1;
}

void hexStringToBytes(const char* hexstr, BitSequence* bytes, size_t* byteLen) {
    size_t len = strlen(hexstr);
    if (len % 2 != 0) {
        fprintf(stderr, "Invalid hex string length: %zu\n", len);
        exit(EXIT_FAILURE);
    }
    *byteLen = len / 2;
    for (size_t i = 0; i < *byteLen; i++) {
        int high = hexCharToByte(hexstr[2 * i]);
        int low = hexCharToByte(hexstr[2 * i + 1]);
        if (high == -1 || low == -1) {
            fprintf(stderr, "Invalid hex character: %c%c\n", hexstr[2 * i], hexstr[2 * i + 1]);
            exit(EXIT_FAILURE);
        }
        bytes[i] = (high << 4) | low;
    }
}

int main() {
    int hashbitlens[] = {224, 256, 384, 512}; // Valid hash lengths
    BitSequence data[MAX_LINE_LENGTH / 2]; // Increased size to handle larger inputs
    BitSequence hashval[64];
    DataLength databitlen;

    // Open the input file containing strings to hash
    FILE *inputFile = fopen("input.txt", "r");
    if (inputFile == NULL) {
        perror("Error opening input file");
        return EXIT_FAILURE;
    }

    // Open the output file to save the hashes
    FILE *outputFile = fopen("output.txt", "w");
    if (outputFile == NULL) {
        perror("Error opening output file");
        fclose(inputFile);
        return EXIT_FAILURE;
    }

    char line[MAX_LINE_LENGTH];
    while (fgets(line, sizeof(line), inputFile)) {
        // Remove newline character if present
        line[strcspn(line, "\n")] = 0;

        size_t byteLen = 0;
        memset(data, 0, sizeof(data));
        hexStringToBytes(line, data, &byteLen);
        databitlen = byteLen * 4; // Length in bits

        // Save the original message in hexadecimal format to the output file
        fprintf(outputFile, "Original message in hex: ");
        printHexToFile(outputFile, data, byteLen);

        // Test all valid hash lengths
        for (int i = 0; i < sizeof(hashbitlens) / sizeof(hashbitlens[0]); i++) {
            int hashbitlen = hashbitlens[i];

            // Call the hashing function
            HashReturn result = Hash(hashbitlen, data, databitlen, hashval);

            if (result == SUCCESS) {
                fprintf(outputFile, "Hash length %d: ", hashbitlen);
                printHashToFile(outputFile, hashval, hashbitlen);
            } else if (result == BAD_HASHLEN) {
                fprintf(stderr, "Invalid hash length %d\n", hashbitlen);
            } else {
                fprintf(stderr, "Hashing failed for hash length %d\n", hashbitlen);
            }
        }
    }

    fclose(inputFile);
    fclose(outputFile);

    return EXIT_SUCCESS;
}
