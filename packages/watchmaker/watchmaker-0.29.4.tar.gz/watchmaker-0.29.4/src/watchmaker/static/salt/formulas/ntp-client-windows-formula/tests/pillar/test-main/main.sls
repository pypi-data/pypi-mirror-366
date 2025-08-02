ntp-client-windows:
  # When any NTP server is associated with a flag of '0x1', the value of
  # 'specialpollinterval' determines how often the client attempts to sync
  # with that server
  # If 'specialpollinterval' is not present, it defaults to "'3600'".
  specialpollinterval: '384'

  # Map of NTP servers with which to sync. Each key is the DNS name or IP
  # address of an NTP server. Each value is the flag to use with the DNS
  # server.
  # The flags correspond to NTP modes, and are defined in this article:
  # - https://technet.microsoft.com/en-us/library/Cc773263(v=WS.10).aspx
  # For an explanation of NTP modes, see this article:
  # - http://www.bytefusion.com/products/ntm/pts/3_3modesofoperation.htm
  #
  # If 'ntpservers' is not present or empty, it defaults to:
  # "time.windows.com: '0x9'".
  # For any listed ntpserver, if the 'flag' is not specified, it defaults to:
  # "'0x9'".
  ntpservers:
    pool1.example.com: '0x9'
    pool2.example.com: '0x9'
    pool3.example.com: '0x9'
    pool4.example.com: '0x9'
