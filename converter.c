/*
 * A fast converter
 * ================
 *
 * This converter converts the Uint16 measure result into Uint8 grayscale
 * value(for actually writing an image), and counts the max/min grayscale
 * values ever plotted, which is useful for generating equalized image and
 * plot scale bars.
 *
 * The extreme values counted are attached at end using 2 bytes, the first
 * represents maximal value, second the minimal.
 */

#include <stdio.h>

#define tableSize 65536

int main(){
    int c;
    unsigned char convertTable[tableSize], conv = 0;
    unsigned char grayScale, maxGray = 0, minGray = 255;
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
            grayScale = convertTable[convIndex & (tableSize - 1)];

            if(grayScale > maxGray) maxGray = grayScale;
            if(grayScale < minGray) minGray = grayScale;

            putchar(grayScale);
        };
    };

    /*putchar(maxGray);
    putchar(minGray);*/

    fflush(stdout);
    return 0;
};
