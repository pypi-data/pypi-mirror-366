{#- Get the `tplroot` from `tpldir` #}
{%- set tplroot = tpldir.split('/')[0] %}

{%- from tplroot ~ "/map.jinja" import mapdata as forescout with context %}

ForeScout SecureConnector Service Dead:
  service.dead:
    - name: {{ forescout.service.name }}
    - enable: False
