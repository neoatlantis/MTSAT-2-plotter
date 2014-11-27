#include <stdio.h>

#define tableSize 65536

int main(){
    int c;
    unsigned char convertTable[tableSize], conv = 0;
    unsigned long i, convIndex;

    for(i=0; i<tableSize; i++)
        convertTable[i] = getchar();

    while(EOF != (c = getchar())){
        if(0 == conv){
            convIndex = c & 0xFF;
            conv = 1;
        } else {
            convIndex <<= 8;
            convIndex += c & 0xFF;
            conv = 0;
            putchar(convertTable[convIndex & (tableSize - 1)]);
        };
    };

    fflush(stdout);
    return 0;
};
