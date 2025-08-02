# -*- coding: utf-8 -*-
{%- set os_family = salt['grains.get']('os_family') %}

{%- if os_family == 'Windows' %}

include:
  - .windows

{%- else %}

include:
  - .linux

{%- endif %}
