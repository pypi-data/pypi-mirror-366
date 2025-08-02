{#- Get the `tplroot` from `tpldir` #}
{%- set tplroot = tpldir.split('/')[0] %}
{%- set sls_package_install = tplroot ~ '.package.install' %}

{%- from tplroot ~ "/map.jinja" import mapdata as forescout with context %}

include:
  - {{ sls_package_install }}

ForeScout Service Enabled:
  service.enabled:
    - name: {{ forescout.service.name }}
    - enable: True
    - watch:
      - sls: {{ sls_package_install }}

ForeScout Service Running:
  service.running:
    - name: {{ forescout.service.name }}
    - watch:
      - sls: {{ sls_package_install }}
    - require:
      - service: ForeScout Service Enabled
