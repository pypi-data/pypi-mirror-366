#
# This salt state installs McAfee Agent dependencies, configures iptables, and
# runs a downloaded copy of ePO server's exported install.sh. The `install.sh`
# file is a pre-configured, self-installing SHell ARchive. The SHAR installs
# the MFEcma and MFErt RPMs, service configuration (XML) files and SSL keys
# necessary to secure communications between the local McAfee agent software
# and the ePO server.
#
#################################################################
{%- from tpldir ~ '/map.jinja' import mcafee with context %}

Install McAfee Agent Dependencies:
  pkg.installed:
    - pkgs:
      - unzip
      - ed

{%- if mcafee.client_in_ports %}
Install firewalld for McAfee:
  pkg.installed:
    - pkgs:
      - firewalld

Ensure firewalld is running for McAfee:
  service.running:
    - name: firewalld
    - enable: True
    - watch:
      - pkg: Install firewalld for McAfee

Configure firewalld service for McAfee:
  firewalld.service:
    - name: mcafee
    - ports:
      {%- for port in mcafee.client_in_ports %}
      - {{ port }}/tcp
      {%- endfor %}
    - require:
      - service: Ensure firewalld is running for McAfee

Configure firewalld zone for McAfee:
  firewalld.present:
    - name: mcafee
    - services:
      - mcafee
    - sources: {{ mcafee.client_in_sources }}
    - require:
      - firewalld: Configure firewalld service for McAfee
{%- endif %}

Stage McAfee Install Archive:
  file.managed:
  - name: /root/install.sh
  - source: {{ mcafee.source }}
  - source_hash: {{ mcafee.source_hash }}
  - user: root
  - group: root
  - mode: 0700
  - show_changes: False
  - require:
    - pkg: Install McAfee Agent Dependencies

Remove Existing Packages:
  pkg.purged:
    - pkgs: {{ mcafee.rpms }}

Install McAfee Agent:
  cmd.run:
    - name: 'sh /root/install.sh {{ mcafee.installer_opts }}'
    - cwd: '/root'
    - require:
      - file: Stage McAfee Install Archive
      - pkg: Remove Existing Packages
