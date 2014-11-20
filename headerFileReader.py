#!/usr/bin/python

def extractConvertTable(content):
    lines = content.strip().split('\n')
    begin = False
    recorded = []
    for each in lines:
        if each.startswith('_UNIT:='):
            begin = True
            continue
        elif each == '':
            break
        if begin:
            recorded.append(each)
    return '\n'.join(recorded)

if __name__ == '__main__':
    content = open('testdata/sample.txt', 'r').read()
    print extractConvertTable(content)
