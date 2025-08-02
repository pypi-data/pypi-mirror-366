Fix ForeScout Ownerships:
  file.directory:
    - name: '/usr/lib/forescout'
    - user: 'root'
    - group: 'root'
    - recurse:
      - user
      - group
