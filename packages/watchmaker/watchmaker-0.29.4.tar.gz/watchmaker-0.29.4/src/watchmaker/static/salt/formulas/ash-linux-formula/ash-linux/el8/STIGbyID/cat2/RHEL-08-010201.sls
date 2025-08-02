# Ref Doc:    STIG - RHEL 8 v1r11
# Finding ID: V-244525
# Rule ID:    SV-244525r917886_rule
# STIG ID:    RHEL-08-010201
# SRG ID:     SRG-OS-000163-GPOS-00072
#             SRG-OS-000126-GPOS-00066
#             SRG-OS-000279-GPOS-00109
#
# Finding Level: medium
#
# Rule Summary:
#       RHEL 8 be configured so that all network connections associated with SSH
#       traffic are terminated after 10 minutes of becoming unresponsive.
#
# References:
#   CCI:
#     - CCI-001133
#   NIST SP 800-53 :: SC-10
#   NIST SP 800-53A :: SC-10.1 (ii)
#   NIST SP 800-53 Revision 4 :: SC-10
#
###########################################################################
{%- set stig_id = 'RHEL-08-010201' %}
{%- set helperLoc = tpldir ~ '/files' %}
{%- set skipIt = salt.pillar.get('ash-linux:lookup:skip-stigs', []) %}
{%- set svcName = 'sshd' %}
{%- set cfgFile = '/etc/ssh/sshd_config' %}
{%- set cfgParm = 'ClientAliveInterval' %}
{%- set cfgValue = '600' %}

{{ stig_id }}-description:
  test.show_notification:
    - text: |
        --------------------------------------
        STIG Finding ID: V-244525
             The OS must terminate all SSH
             sessions ater 10 minutes of
             becoming unresponsive
        --------------------------------------

{%- if stig_id in skipIt %}
notify_{{ stig_id }}-skipSet:
  test.show_notification:
    - text: |
        Handler for {{ stig_id }} has been selected for skip.
{%- else %}
Fix/set sshd {{ cfgParm }} value:
  file.replace:
    - name: '{{ cfgFile }}'
    - append_if_not_found: True
    - not_found_content: |-

        # Inserted per STIG {{ stig_id }}
        {{ cfgParm }} {{ cfgValue }}
    - pattern: '^(|#)\s*{{ cfgParm }}.*'
    - repl: '{{ cfgParm }} {{ cfgValue }}'

service_sshd:
  service.running:
    - name: '{{ svcName }}'
    - watch:
      - file: 'Fix/set sshd {{ cfgParm }} value'
{%- endif %}
