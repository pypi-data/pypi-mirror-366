#
# This salt state attempts to download and install the correct Splunk
# client-agent for the host's architecture. Further, the state will attempt
# to locate and install appropriate client configuration files. Th salt state
# will also add the requisite iptables exceptions to the OUTPUT filter to
# allow communications between the local Splunk agent and the remote Splunk
# Enterprise collector.
#
#################################################################

{%- from tpldir ~ '/map.jinja' import splunkforwarder with context %}

{%- set comment = "Connectivity for splunkforwarder" %}

{%- for port in splunkforwarder.client_out_ports %}
Allow Splunk Mgmt Outbound Port {{ port }}:
  cmd.run:
    - name: |
        firewall-cmd --direct --add-rule ipv4 filter OUTPUT_direct 50 -p tcp -m tcp --dport={{ port }} -m comment --comment "{{ comment }}" -j ACCEPT
        firewall-cmd --permanent --direct --add-rule ipv4 filter OUTPUT_direct 50 -p tcp -m tcp --dport={{ port }} -m comment --comment "{{ comment }}" -j ACCEPT
{%- endfor %}

Install Splunk Package:
  pkg.installed:
    - sources:
      - {{ splunkforwarder.package }}: {{ splunkforwarder.package_url }}
    - skip_verify: True

Install Client Log Config File:
  file.managed:
    - name: {{ splunkforwarder.log_local.conf }}
    - user: {{ splunkforwarder.user.name }}
    - group: {{ splunkforwarder.user.name }}
    - mode: 0600
    - contents: |
        {{ splunkforwarder.log_local.contents | indent(8) }}
    - require:
      - pkg: Install Splunk Package
      - user: Manage Splunk User

Install Client Agent Config File:
  file.managed:
    - name: {{ splunkforwarder.deploymentclient.conf }}
    - user: {{ splunkforwarder.user.name }}
    - group: {{ splunkforwarder.user.name }}
    - mode: 0600
    - contents: |
        [deployment-client]
        disabled = false
        clientName = {{ splunkforwarder.deploymentclient.client_name }}

        [target-broker:deploymentServer]
        targetUri = {{ splunkforwarder.deploymentclient.target_uri }}
    - require:
      - pkg: Install Splunk Package
      - user: Manage Splunk User

{%- if splunkforwarder.inputs.get('sections') %}
Create Inputs Conf:
  file.managed:
    - name: {{ splunkforwarder.inputs.conf }}
    - user: {{ splunkforwarder.user.name }}
    - group: {{ splunkforwarder.user.name }}
    - mode: 0600
    - makedirs: True
    - replace: False
    - require_in:
      - ini: Configure Local Log Sources

Configure Local Log Sources:
  ini.options_present:
    - name: {{ splunkforwarder.inputs.conf }}
    - sections: {{ splunkforwarder.inputs.sections | yaml }}
    - require_in:
      - cmd: Start Splunk Service
    - watch_in:
      - service: Ensure Splunk Service is Running
{%- endif %}

Configure Splunk Agent Boot-scripts:
  cmd.run:
    - name: {{ splunkforwarder.bin_file }} enable boot-start {{ splunkforwarder.service_opts }}
    - require:
      - file: Install Client Log Config File
      - file: Install Client Agent Config File
    - unless: test -f {{ splunkforwarder.service_file }}

Start Splunk Service:
  cmd.run:
    - name: {{ splunkforwarder.bin_file }} start
    - require:
      - cmd: Configure Splunk Agent Boot-scripts
    - unless: test -f {{ splunkforwarder.cert_file }}

Enable Splunk Service:
  service.enabled:
    - name: {{ splunkforwarder.service }}
    - require:
      - cmd: Start Splunk Service

Ensure Splunk Service is Running:
  service.running:
    - name: {{ splunkforwarder.service }}
    - require:
      - service: Enable Splunk Service
    - watch:
      - file: Install Client Log Config File
      - file: Install Client Agent Config File

Pre-Create Splunk Log Directory:
  file.directory:
    - name: /var/log/splunk
    - user: {{ splunkforwarder.user.name }}
    - group: {{ splunkforwarder.user.name }}
    - dir_mode: 0700
    - recurse:
      - user
      - group
      - mode
    - makedirs: True
    - require_in:
      - file: Create Sym-link To Splunk Log Dir

Create Sym-link To Splunk Log Dir:
  file.symlink:
    - name: /opt/splunkforwarder/var/log/splunk
    - target: /var/log/splunk
    - user: {{ splunkforwarder.user.name }}
    - group: {{ splunkforwarder.user.name }}
    - mode: 0700
    - makedirs: True
    - require_in:
      - pkg: Install Splunk Package

Manage Splunk User:
  user.present:
    - name: {{ splunkforwarder.user.name }}
    - fullname: {{ splunkforwarder.user.fullname }}
    - home: {{ splunkforwarder.user.home }}
    - usergroup: True
    - require_in:
      - file: Pre-Create Splunk Log Directory
