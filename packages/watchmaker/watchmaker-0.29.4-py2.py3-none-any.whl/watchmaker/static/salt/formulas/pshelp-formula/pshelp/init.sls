{%- from "pshelp/map.jinja" import pshelp with context %}

Copy pshelp files:
  file.recurse:
    - name: '{{ pshelp.cachedir }}'
    - source: salt://{{ tpldir }}/content
    - makedirs: True

UpdatePSHelp:
  cmd.run:
    - name: 'try
        {
          Update-Help -SourcePath {{ pshelp.cachedir }} -Force -ErrorAction Stop
        }
        catch
        {
          Echo $_.Exception | Format-List -Force;
          $Error.Clear()
        }'
    - shell: powershell
    - require:
        - file: Copy pshelp files
    - onlyif: 'if ($($PSVersiontable.PSVersion.Major) -ge 3) { return 0 } else { throw }'
