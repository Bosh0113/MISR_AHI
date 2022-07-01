from ftplib import FTP

ftp = FTP()
ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
# disconnect ftp server
ftp.close()