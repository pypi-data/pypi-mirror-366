{#- Get the `tplroot` from `tpldir` #}
{%- set tplroot = tpldir.split('/')[0] %}
{%- set sls_service_clean = tplroot ~ '.service.clean' %}

{%- from tplroot ~ "/map.jinja" import mapdata as forescout with context %}

ForeScout SecureConnector Removed:
  cmd.run:
    - name: {{ forescout.package.uninstall_cmd }}
    - onlyif: {{ forescout.package.uninstall_test }}
    - require:
      - sls: {{ sls_service_clean }}

{%- if forescout.package.daemon.get('source') %}
ForeScout SecureConnector Daemon Removed:
  pkg.removed:
    - name: {{ forescout.package.daemon.name }}
    - require:
      - cmd: ForeScout SecureConnector Removed
    - require_in:
      - file: ForeScout SecureConnector Dir Removed
{%- endif %}

ForeScout SecureConnector Dir Removed:
  file.absent:
    - name: {{ forescout.package.install_dir }}
    - require:
      - cmd: ForeScout SecureConnector Removed

ForeScout SecureConnector Systemd Service File Removed:
  file.absent:
    - name: /etc/systemd/system/SecureConnector.service
    - require:
      - cmd: ForeScout SecureConnector Removed

ForeScout SecureConnector Archive Removed:
  file.absent:
    - name: {{ forescout.package.archive.extract_directory }}
