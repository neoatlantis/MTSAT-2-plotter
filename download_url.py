#!/usr/bin/env python

def getDownloadURL(timestamp, bandName, bandNumber):
    dm = timestamp[:6]
    return 'ftp://hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20151105/%s/%s/%s.%s.%02d.fld.geoss.bz2' % (
        dm,
        bandName.upper(),
        timestamp,
        bandName.lower(),
        int(bandNumber)
    )

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print "Usage: python download_url.py <YYYYMMDDHHMM> <EXT|VIS|TIR|SIR> <XX>"
        sys.exit(1)

    print getDownloadURL(sys.argv[1], sys.argv[2], sys.argv[3])
