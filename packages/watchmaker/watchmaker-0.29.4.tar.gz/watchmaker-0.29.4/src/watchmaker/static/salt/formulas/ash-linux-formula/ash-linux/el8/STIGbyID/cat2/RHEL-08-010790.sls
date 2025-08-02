# Ref Doc:    STIG - RHEL 8 v1r7
# Finding ID: V-230327
# STIG ID:    RHEL-08-010790
# Rule ID:    SV-230327r627750_rule
# SRG ID:     SRG-OS-000480-GPOS-00227
#
# Finding Level: medium
#
# Rule Summary:
#	All local files and directories must have a valid group owner.
#
# CCI-002165
#  - CCI-000366
#
# NIST SP 800-53 :: CM-6 b
# NIST SP 800-53A :: CM-6.1 (iv)
# NIST SP 800-53 Revision 4 :: CM-6 b#
#
#################################################################
{%- set stig_id = 'RHEL-08-010790' %}
{%- set helperLoc = tpldir ~ '/files' %}
{%- set skipIt = salt.pillar.get('ash-linux:lookup:skip-stigs', []) %}
{%- set nogroupFiles = [] %}
{%- set localFstypes = [
  'ext2',
  'ext3',
  'ext4',
  'xfs',
  'jfs',
  'btrfs'
] %}
{%- set mountData = salt.mount.fstab() %}
{%- set mounts = mountData.keys() %}

{{ stig_id }}-description:
  test.show_notification:
    - text: |
        --------------------------------------
        STIG Finding ID: V-230327
             All local files and directories
             must have a valid group owner
        --------------------------------------

{%- if stig_id in skipIt %}
notify_{{ stig_id }}-skipSet:
  test.show_notification:
    - text: |
        Handler for {{ stig_id }} has been selected for skip.
{%- else %}
# Find files with no valid owner..
  {%- for mount in mounts %}
    {%- set mountType = mountData[mount]['fstype'] %}
    {%- if mountData[mount]['fstype'] in localFstypes %}
      {%- set foundString = salt.cmd.shell('find ' + mount + ' -xdev -nogroup') %}
      {%- set foundList = foundString.split('\n') %}
      {%- do nogroupFiles.extend(foundList) %}
    {%- endif %}
  {%- endfor %}

# Take ownership of files
  {%- if nogroupFiles %}
    {%- for file in nogroupFiles %}
      {%- if file %}
file_{{ stig_id }}-{{ file }}:
  file.managed:
    - name: '{{ file }}'
    - group: 'root'
      {%- endif %}
    {%- endfor %}
  {%- endif %}
{%- endif %}
