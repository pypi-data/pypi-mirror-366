{#- Get the `tplroot` from `tpldir` #}
{%- set tplroot = tpldir.split('/')[0] %}
{%- set RpmVrfySetting = '/etc/rpm/macros.verify' %}

{%- from tplroot ~ "/map.jinja" import mapdata as forescout with context %}

ForeScout SecureConnector Dependencies Installed:
  pkg.installed:
    - pkgs:
        - bzip2
        - wget

ForeScout SecureConnector Archive Extracted:
  archive.extracted:
    - name: {{ forescout.package.archive.extract_directory }}
    - source: {{ forescout.package.archive.source }}
    - source_hash: {{ forescout.package.archive.source_hash }}
    - user: root
    - group: root
    - mode: 0700

Relax pkgverify options:
  file.managed:
    - contents: '%_pkgverify_level none'
    - group: 'root'
    - mode: '0600'
    - name: '{{ RpmVrfySetting }}'
    - user: 'root'
    - selinux:
        serange: 's0'
        serole: 'object_r'
        setype: 'etc_t'
        seuser: 'system_u'
    - unless:
      - '[[ {{ grains["osmajorrelease"] }} -lt 8 ]]'

{%- if forescout.package.daemon.get('source') %}
ForeScout SecureConnector Daemon Installed:
  pkg.installed:
    - setopt:
      - tsflags=nocrypto
    - sources:
      - {{ forescout.package.daemon.name }}: {{ forescout.package.daemon.source }}
    - skip_verify: True
    - require:
      - file: Relax pkgverify options
    - require_in:
      - cmd: ForeScout SecureConnector Installed
{%- endif %}

ForeScout SecureConnector Systemd Service File:
  file.managed:
    - name: /etc/systemd/system/SecureConnector.service
    - contents: |
        [Unit]
        Description=ForeScout SecureConnector

        [Service]
        ExecStart={{ forescout.package.install_dir }}/bin/ForeScoutSecureConnector
        [Install]
        WantedBy=multi-user.target
    - user: root
    - group: root
    - mode: 0644

ForeScout SecureConnector Installed:
  cmd.run:
    - name: {{ forescout.package.archive.extract_directory }}/{{ forescout.package.install_cmd }}
    - unless: {{ forescout.package.installed_test }}
    - require:
      - archive: ForeScout SecureConnector Archive Extracted
      - file: ForeScout SecureConnector Systemd Service File
      - pkg: ForeScout SecureConnector Dependencies Installed

Restore pkgverify options:
  file.absent:
    - name: '{{ RpmVrfySetting }}'
    - require:
      - cmd: ForeScout SecureConnector Installed
