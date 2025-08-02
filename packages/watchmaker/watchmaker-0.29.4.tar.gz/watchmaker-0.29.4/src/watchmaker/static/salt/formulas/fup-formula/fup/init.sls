#
# Salt state for downloading and installing a yum repository-
# definition RPM from a specified URL
#
#################################################################
{%- from tpldir ~ '/map.jinja' import join_domain with context %}

{#- Set location for helper-files #}
{%- set files = tpldir ~ '/files' %}

{#- fetch our packages/urls as a dict #}
{%- set package_dict = salt.grains.get(
    'urly-packages:lookup:pkgs',
    salt.pillar.get('urly-packages:lookup:pkgs', {})
) %}

{#- Iterate over the dict #}
{%- for package, pkgUrl in package_dict.items() %}
package-install-{{ package }}:
  pkg.installed:
    - sources:
      - {{ package }}: {{ pkgUrl }}
    - allow_updates: True
    - skip_verify: True
{%- endfor %}
