from ftplib import FTP

if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220218'
    
    ahi_data_time = '201606210950'
    ahi_data_folder1 = '201606'
    ahi_data_folder2 = '20160621'
    ahi_saa_filename = ahi_data_time + '.sun.azm.fld.4km.bin.bz2'
    ahi_saa_path = '/gridded/FD/V20190123/' + ahi_data_folder1 + '/4KM/' + ahi_data_folder2 + '/' + ahi_saa_filename
    ftp_dl_url = 'ftp://hmwr829gr.cr.chiba-u.ac.jp' + ahi_saa_path
    print(ftp_dl_url)

    ftp = FTP()
    ftp.connect('hmwr829gr.cr.chiba-u.ac.jp', 21)
    ftp.login()
    local_file = ws + '/' + ahi_saa_filename
    with open(local_file, 'wb') as f:
        ftp.retrbinary('RETR ' + ahi_saa_path, f.write, 1024*1024)
    ftp.close()
