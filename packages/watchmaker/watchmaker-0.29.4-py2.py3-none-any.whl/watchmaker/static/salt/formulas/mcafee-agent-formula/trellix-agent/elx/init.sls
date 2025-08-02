#
# This salt state installs Trellix Agent dependencies, configures iptables, and
# runs a downloaded copy of ePO server's exported install.sh. The `install.sh`
# file is a pre-configured, self-installing SHell ARchive. The SHAR installs
# the MFEcma and MFErt RPMs, service configuration (XML) files and SSL keys
# necessary to secure communications between the local Trellix agent software
# and the ePO server.
#
#################################################################
{%- from tpldir ~ '/map.jinja' import trellix with context %}

Install Trellix Agent Dependencies:
  pkg.installed:
    - pkgs:
      - unzip
      - ed

{%- if trellix.client_in_ports %}
Install firewalld for Trellix:
  pkg.installed:
    - pkgs:
      - firewalld

Ensure firewalld is running for Trellix:
  service.running:
    - name: firewalld
    - enable: True
    - watch:
      - pkg: Install firewalld for Trellix

Configure firewalld service for Trellix:
  firewalld.service:
    - name: trellix
    - ports:
      {%- for port in trellix.client_in_ports %}
      - {{ port }}/tcp
      {%- endfor %}
    - require:
      - service: Ensure firewalld is running for Trellix

Configure firewalld zone for Trellix:
  firewalld.present:
    - name: trellix
    - services:
      - trellix
    - sources: {{ trellix.client_in_sources }}
    - require:
      - firewalld: Configure firewalld service for Trellix
{%- endif %}

Stage Trellix Install Archive:
  file.managed:
  - name: /root/install.sh
  - source: {{ trellix.source }}
  - source_hash: {{ trellix.source_hash }}
  - user: root
  - group: root
  - mode: 0700
  - show_changes: False
  - require:
    - pkg: Install Trellix Agent Dependencies

Remove Existing Packages:
  pkg.purged:
    - pkgs: {{ trellix.rpms }}

Install Trellix Agent:
  cmd.run:
    - name: 'sh /root/install.sh {{ trellix.installer_opts }}'
    - cwd: '/root'
    - require:
      - file: Stage Trellix Install Archive
      - pkg: Remove Existing Packages
