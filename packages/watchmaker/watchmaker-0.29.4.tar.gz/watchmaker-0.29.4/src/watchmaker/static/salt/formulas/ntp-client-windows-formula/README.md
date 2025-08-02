[![license](https://img.shields.io/github/license/plus3it/ntp-client-windows-formula.svg)](./LICENSE)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/ntp-client-windows-formula?branch=master&svg=true)](https://ci.appveyor.com/project/plus3it/ntp-client-windows-formula)

# ntp-client-windows-formula
Salt formula to configure the Windows Time Service to sync with one or more
NTP servers.


## Available States

- [ntp-client-windows](#ntp-client-windows)


### ntp-client-windows

Configure the registry entries required for a Windows system to sync time from
one or more NTP servers. Microsoft describes the relevant registry entries in
a [Technet article]
(https://technet.microsoft.com/en-us/library/Cc773263(v=WS.10).aspx).


## Configuration

This formula uses pillar to configure all the relevant registry entries. If no
pillar settings are configured, then the formula will default to the values
specified below.


### ntp-client-windows:specialpollinterval

This setting controls how frequently the Windows Time Service polls the NTP
server. This setting is only used if the `flag` for the corresponding NTP
server is `'0x1'`. See [ntpservers](#ntp-client-windows:ntpservers) for more
on the `flag` parameter.

>*Default*: `'3600'`

**Example**:

```
ntp-client-windows:
  specialpollinterval: '384'
```


### ntp-client-windows:ntpservers

This is a map of key:value pairs. Each key is the DNS name or IP address of an
NTP server, and each value is the `flag` to use with that NTP server. The
`flag` is a hex value in the form `'0xN'`:

- '0x1' : SpecialInterval - Use the SpecialPollInterval setting to determine
how frequently to sync
- '0x2' : UseAsFallBackOnly - Only sync with this server if all other servers fail
- '0x4' : SymmetricActive - A link describing this NTP mode is [here]
(http://www.bytefusion.com/products/ntm/pts/3_3modesofoperation.htm)
- '0x8' : Client - Receive time from this peer, but to do serve time to it

As these are hex values, they may be bitwise OR'd to combine possible
configurations. Only '0x8' and '0x4' are mutually exclusive. i.e. '0x9' means
the service will use the '0x1' and '0x8' flags.

For more information, see the Technet article linked at the top of the Readme.

>*Default*: `time.windows.com: '0x9'`

**Example**:

```
ntp-client-windows:
  ntpservers:
    time.windows.com: '0x8'
    time.nist.gov: '0x8'
```
