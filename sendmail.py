#!/usr/bin/python

"""
Send one cached file in `sendcache` and delete the mentioned file.


This piece of program fetchs the newest result existing in `sendcache` and
send it to mailing lists configured in `config/maillist-address` using SMTP
configurations defined by `config/smtp-server`, `config/smtp-username` and
`config/smtp-password`. Edit these files to input proper parameters.

Notice that parameters read from `config` path are trim'ed.
"""

import os
import subprocess
import sys
import time

from sender import Attachment, Mail, Message




def getConf(name):
    return open(os.path.join('config', name), 'r').read().strip()

smtpFrom = getConf('smtp-from')
smtpServer = getConf('smtp-server')
smtpUsername = getConf('smtp-username')
smtpPassword = getConf('smtp-password')
smtpPort = int(getConf('smtp-port'), 10)

receiversRaw = getConf('maillist-address').split('\n')
receivers = []
for each in receiversRaw:
    each = each.strip()
    if '' != each:
        receivers.append(each)

cacheListRaw = os.listdir('sendcache')
cacheList = []
removeList = []
for each in cacheListRaw:
    fullname = os.path.realpath(os.path.join('sendcache', each))
    if not os.path.isfile(fullname):
        continue
    if fullname.endswith('.7z'):
        cacheList.append(fullname)
    else:
        removeList.append(fullname)
cacheList.sort()
if len(cacheList) < 1:
    sys.exit(0)
targetFile = cacheList[-1]
removeList.append(targetFile)



# checksum of targetFile
checksum = subprocess.check_output(['sha1sum', targetFile])
checksum = checksum.split('\n')[0].strip()[0:40]



# size of targetFile
fileSize = os.path.getsize(targetFile)



# determine subject
timeStr = os.path.basename(targetFile)[:12]
timeStr = timeStr[0:4] + '-' + timeStr[4:6] + '-' + timeStr[6:8] + 'T' +\
    timeStr[8:10] + ':' + timeStr[10:12] + 'Z'
if targetFile.endswith('.ir.7z'):
    channelStr = 'IR'
    subject = "[MTSAT-2 Data Broadcast][IR][%s]" % timeStr 
else:
    channelStr = 'VIS'
    subject = "[MTSAT-2 Data Broadcast][VIS][%s]" % timeStr 



# determine message body
maillistStr = '\n'.join(['    %s' % i for i in receivers])
body = """
**NEVER reply to this mail directly. No human's dealing with your reply!**

This is another update of MTSAT-2 plotted image(s) with:

    Channel: %s
    Retrieved time at: %s

The image(s) is(are) compressed into a 7zip file and attached to this mail.
To verify its integrity, following clues are provided:

    SHA1-checksum: %s
    Size: %d bytes

*NeoAtlantis Laboratory of Applied Science and Occultism*, have generated this
email and sent via following mailing list(s). This may be the reason, that you
have received this email:

%s

All other mailing lists are not maintained by NeoAtlantis.

DISCLAIMER: This email is not digital signed and is therefore subject to threat
being manipulated. NeoAtlantis is not responsible for any consequences, caused
either directly or indirectly, by using this data. We do NOT assure the
accuracy and correctness of this data, although we welcome advices improving or
correcting our mechanism.

CONTACTS:

    NeoAtlantis <contact@chaobai.li>
    
Visit [http://mtsat-2.neoatlantis.org] for online data source.
""" % (channelStr, timeStr, checksum, fileSize, maillistStr)
body = body.strip()
print body
print '---'


# construct mail

msg = Message(subject, fromaddr=('NeoAtlantis MTSAT-2 Data Broadcast', smtpFrom))
msg.body = body
msg.to = receivers[0]
if len(receivers) > 1:
    msg.cc = receivers[1:]
msg.date = time.time()
msg.charset = "UTF-8"

attachment = Attachment(\
    os.path.basename(targetFile),
    'application/x-7z-compressed',
    open(targetFile, 'r').read()
)

msg.attach(attachment)



# do send mail

print "> Send mail with SMTP server [%s:%d]." % (smtpServer, smtpPort)

mailer = Mail(\
    smtpServer,
    port=smtpPort,
    username=smtpUsername,
    password=smtpPassword,
    use_tls=True,
    use_ssl=False,
    debug_level=10000
)



# remove files firstly, so that confict processes will not send the same file
# again.

try:
    for each in removeList:
        print "> Remove files that are no longer useful: %s" % each
        os.remove(each)
except:
    pass



# finally
try:
    mailer.send(msg)
except Exception,e:
    print "> Send mail error: %s" % e
    sys.exit(1)
print "> Mail sent."
sys.exit(0)
