[![license](https://img.shields.io/github/license/plus3it/windows-update-agent-formula.svg)](./LICENSE)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/windows-update-agent-formula?branch=master&svg=true)](https://ci.appveyor.com/project/plus3it/windows-update-agent-formula)

# windows-update-agent-formula
Salt formula to manage the configuration of the Windows Update Agent


## Available States

-   [windows-update-agent](#windows-update-agent)


### windows-update-agent

Configure the registry entries associated with the Windows Update Agent.
Microsoft describes the relevant registry entries in a [Technet article]
(https://technet.microsoft.com/en-us/library/Dd939844(v=WS.10).aspx).


## Configuration

This formula uses pillar to configure all the relevant registry entries. If no
pillar settings are configured, then the formula by default will do nothing.


### windows-update-agent:lookup:remove-undefined-keys

If this setting is set to `True`, then the formula will remove any registry
entry that is either not present in pillar or that is undefined (`''`). This
causes Windows to resume the default behavior for the corresponding registry
key(s).

>*Default*: `False`

**Example**:

```
windows-update-agent:
  lookup:
    remove-undefined-keys: True
```


### windows-update-agent:lookup:registry

This is a dictionary of all the registry keys and subkeys that can be
configured by this formula. Detailed descriptions of the registry entries can
be found in the [linked Microsoft Technet article]
(https://technet.microsoft.com/en-us/library/Dd939844(v=WS.10).aspx). If none
of the pillar settings have a value, by default the formula will do nothing.
To remove undefined keys, see the configuration setting [remove-undefined-keys]
(#windows-update-agent:remove-undefined-keys).

**Example -- Utilize an internal WSUS server for updates**:
>Note the three settings below that have defined values...

```
windows-update-agent:
  lookup:
    registry:
      'HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate':
        AcceptTrustedPublisherCerts: ''
        DisableWindowsUpdateAccess: ''
        ElevateNonAdmins: ''
        TargetGroup: ''
        TargetGroupEnabled: ''
        WUServer: 'https://wsus.example.com'
        WUStatusServer: 'https://wsus.example.com'
      'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer':
        DisableWindowsUpdateAccess: ''
      'HKEY_LOCAL_MACHINE\SYSTEM\Internet Communication Management\Internet Communication':
        NoWindowsUpdate: ''
      'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\WindowsUpdate':
        DisableWindowsUpdateAccess: ''
      'HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU':
        AlwaysAutoRebootAtScheduledTime: ''
        AlwaysAutoRebootAtScheduledTimeMinutes: ''
        AUOptions: ''
        AutoInstallMinorUpdates: ''
        DetectionFrequency: ''
        DetectionFrequencyEnabled: ''
        NoAutoRebootWithLoggedOnUsers: ''
        NoAutoUpdate: ''
        RebootRelaunchTimeout: ''
        RebootRelaunchTimeoutEnabled: ''
        RebootWarningTimeout: ''
        RebootWarningTimeoutEnabled: ''
        RescheduleWaitTime: ''
        RescheduleWaitTimeEnabled: ''
        ScheduledInstallDay: ''
        ScheduledInstallTime: ''
        UseWUServer: '1'
```
