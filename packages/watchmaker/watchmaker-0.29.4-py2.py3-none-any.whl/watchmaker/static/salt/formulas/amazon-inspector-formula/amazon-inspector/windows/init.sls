# -*- coding: utf-8 -*-
{%- from tpldir ~ '/map.jinja' import data with context %}

install_amazon_inspector:
  cmd.script:
    - name: AWSAgentInstall.exe
    - source: {{ data.install_url }}
    - args: ' /passive /install'
