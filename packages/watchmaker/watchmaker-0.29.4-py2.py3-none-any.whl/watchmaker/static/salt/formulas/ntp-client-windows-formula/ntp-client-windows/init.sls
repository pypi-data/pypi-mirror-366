{%- from "ntp-client-windows/map.jinja" import time with context %}

w32tm_specialpollinterval:
  reg.present:
    - name: 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient'
    - vname: SpecialPollInterval
    - vdata: {{ time.specialpollinterval }}
    - vtype: REG_DWORD
    - watch_in:
      - service: w32tm_service

w32tm_ntpserver:
  reg.present:
    - name: 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Parameters'
    - vname: NtpServer
    - vdata: {{ time.servers }}
    - vtype: REG_SZ
    - watch_in:
      - service: w32tm_service

w32tm_type:
  reg.present:
    - name: 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Parameters'
    - vname: Type
    - vdata: NTP
    - vtype: REG_SZ
    - watch_in:
      - service: w32tm_service

w32tm_service:
  service.running:
    - name: W32Time
    - onchanges_in:
      - cmd: w32tm_resync

w32tm_resync:
  cmd.run:
    - name: w32tm /config /update
