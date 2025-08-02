# Ref Doc:    STIG - RHEL 8 v1r7
# Finding ID: V-230235
# STIG ID:    RHEL-08-010140
# Rule ID:    SV-230235r743925_rule
# SRG ID(s):  SRG-OS-000080-GPOS-00048
# Finding Level:        high
#
# Rule Summary:
#       RHEL 8 operating systems booted with EFI must
#       require authentication upon booting into
#       single-user and maintenance modes
#
# References:
#   CCI:
#     - CCI-000213
#   NIST SP 800-53 :: AC-3
#   NIST SP 800-53A :: AC-3.1
#   NIST SP 800-53 Revision 4 :: AC-3
#
#################################################################
{%- set stig_id = 'RHEL-08-010140' %}
{%- set helperLoc = tpldir ~ '/files' %}
{%- from tpldir ~ '/grub2_info.jinja' import grubEncryptedPass with context %}
{%- from tpldir ~ '/grub2_info.jinja' import grubUser with context %}
{%- set skipIt = salt.pillar.get('ash-linux:lookup:skip-stigs', []) %}
{%- set mustSet = salt.pillar.get('ash-linux:lookup:grub-passwd', '') %}
{%- set grubUserFile = '/etc/grub.d/01_users' %}
{%- if salt.grains.get('os')|lower == 'centos stream' %}
  {%- set grubPassFile = '/boot/efi/EFI/centos/user.cfg' %}
{%- else %}
  {%- set grubPassFile = '/boot/efi/EFI/redhat/user.cfg' %}
{%- endif %}


{{ stig_id }}-description:
  test.show_notification:
    - text: |
        --------------------------------------
        STIG Finding ID: V-230234
             RHEL 8 must require authenticated
             user in order to access single-
             user and maintenance modes
        --------------------------------------

{%- if stig_id in skipIt %}
notify_{{ stig_id }}-skipSet:
  test.show_notification:
    - text: |
        Handler for {{ stig_id }} has been selected for skip.
{%- else %}
user_cfg_exists-{{ stig_id }}:
  file.touch:
    - name: '{{ grubPassFile }}'
    - makedirs: True
    - onlyif:
      - test -d /sys/firmware/efi/
    - unless: {{ grubPassFile }}

user_cfg_content-{{ stig_id }}:
  file.managed:
    - name: '{{ grubPassFile }}'
    - contents: |-
        GRUB2_PASSWORD={{ grubEncryptedPass }}
    - onchanges:
      - file: user_cfg_exists-{{ stig_id }}
    - onchanges_in:
      - regen_grubCfg-{{ stig_id }}

grubuser_superDef-{{ grubUserFile }}-{{ stig_id }}:
  file.replace:
    - name: '{{ grubUserFile }}'
    - pattern: 'superusers=".*"'
    - repl: 'superusers="{{ grubUser }}"'

grubuser_userSub-{{ grubUserFile }}-{{ stig_id }}:
  file.replace:
    - name: '{{ grubUserFile }}'
    - pattern: 'password_pbkdf2 .* \\'
    - repl: 'password_pbkdf2 {{ grubUser }} \\'

regen_grubCfg-{{ stig_id }}:
  cmd.run:
    - name: '/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg'
    - cwd: /root
    - onchanges:
       - file: grubuser_superDef-{{ grubUserFile }}-{{ stig_id }}
       - file: grubuser_userSub-{{ grubUserFile }}-{{ stig_id }}
    - onchanges_in:
      - file: fix_perms_grubCfg-{{ stig_id }}

fix_perms_grubCfg-{{ stig_id }}:
  file.managed:
    - name: '/boot/grub2/grub.cfg'
    - mode: '0600'
    - owner: 'root'
    - selinux:
        serange: 's0'
        serole: 'object_r'
        setype: 'boot_t'
        seuser: 'unconfined_u'
    - user: 'root'

{%- endif %}
