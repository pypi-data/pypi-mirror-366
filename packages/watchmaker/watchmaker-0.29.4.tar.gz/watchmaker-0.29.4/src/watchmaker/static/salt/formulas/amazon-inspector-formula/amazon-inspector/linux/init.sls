# -*- coding: utf-8 -*-
{%- from tpldir ~ '/map.jinja' import data with context %}

disable_local_gpg_check:
  cmd.run:
    - name: yum-config-manager --setopt=localpkg_gpgcheck=0 --save
    - onlyif:
      - 'grep "^localpkg_gpgcheck = 1" /etc/yum.conf'
    - prereq:
      - cmd: install_amazon_inspector

enable_local_gpg_check:
  cmd.run:
    - name: yum-config-manager --setopt=localpkg_gpgcheck=1 --save
    - onchanges:
      - cmd: disable_local_gpg_check
    - require:
      - cmd: install_amazon_inspector

install_amazon_inspector:
  cmd.script:
    - name: amazon-inspector-agent-install.sh
    - source: {{ data.install_url }}
    - cwd: /root
    - shell:  /bin/bash
    - unless: /etc/init.d/awsagent status

start_amazon_inspector:
  cmd.run:
    - name: /etc/init.d/awsagent restart
    - require:
      - cmd: enable_local_gpg_check
    - onchanges:
      - cmd: install_amazon_inspector

ensure_amazon_inspector_is_running:
  cmd.run:
    - name: /etc/init.d/awsagent status
    - require:
      - cmd: start_amazon_inspector
