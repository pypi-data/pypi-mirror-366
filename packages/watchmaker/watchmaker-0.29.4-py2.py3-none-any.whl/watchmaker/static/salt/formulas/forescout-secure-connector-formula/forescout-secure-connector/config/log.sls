ForeScout OS Log-Dir Setup:
  file.directory:
    - group: 'root'
    - mode: '0755'
    - name: '/var/log/forescout'
    - selinux:
        serange: 's0'
        serole: 'object_r'
        setype: 'lib_t'
        seuser: 'system_u'

ForeScout Symlink to OS Log-Dir:
  file.symlink:
    - group: 'root'
    - makedirs: True
    - mode: '0755'
    - name: '/usr/lib/forescout/bin/log'
    - require:
      - file: Forescout Zap Default Log-Dir
    - target: '/var/log/forescout'
    - user: 'root'

Forescout Zap Default Log-Dir:
  file.absent:
    - name: '/usr/lib/forescout/bin/log'
    - onlyif:
      - '[[ -d /usr/lib/forescout/bin/log ]]'
    - require:
      - file: ForeScout OS Log-Dir Setup
