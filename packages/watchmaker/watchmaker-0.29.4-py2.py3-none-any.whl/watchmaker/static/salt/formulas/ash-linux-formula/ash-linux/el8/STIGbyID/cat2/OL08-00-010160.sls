# Ref Doc:    STIG - Oracle Linux 8 v1r4
# Finding ID: V-248544
# Rule ID:    SV-248544r818611_rule
# STIG ID:    OL08-00-010160
# SRG ID:     SRG-OS-000120-GPOS-00061
#
# Finding Level: medium
#
# Rule Summary:
#       The OL8 operating system "pam_unix.so" module must be configured in
#       the password-auth file to use a FIPS 140-2 approved cryptographic
#       hashing algorithm for system authentication.
#
# References:
#   CCI:
#     - CCI-000803
#   NIST SP 800-53 :: IA-7
#   NIST SP 800-53A :: IA-7.1
#   NIST SP 800-53 Revision 4 :: IA-7
#
###########################################################################
{%- set stig_id = 'OL08-00-010160' %}
{%- set helperLoc = tpldir ~ '/files' %}
{%- set skipIt = salt.pillar.get('ash-linux:lookup:skip-stigs', []) %}
{%- set targFile = '/etc/pam.d/password-auth' %}

{{ stig_id }}-description:
  test.show_notification:
    - text: |
        --------------------------------------
        STIG Finding ID: V-248544
             SHA512 password hashing must be
             enforced through the PAM system's
             /etc/pam.d/password-auth file
        --------------------------------------

{%- if stig_id in skipIt %}
notify_{{ stig_id }}-skipSet:
  test.show_notification:
    - text: |
        Handler for {{ stig_id }} has been selected for skip.
{%- else %}
file_{{ stig_id }}-{{ targFile }}:
  file.replace:
    - name: {{ targFile }}
    - pattern: '(^password\s*)(sufficient\s*)(.*)(pam_unix\.so)(.*)'
    - repl: '\1\2\3\4\5 sha512'
    - onlyif:
      - grep -q ORACLE_SUPPORT_PRODUCT /etc/os-release
      - grep -vP '^password\s*sufficient\s*.*pam_unix\.so.*sha512.*'
        {{ targFile }} | grep sha512

{%- endif %}
