splunkforwarder:

  lookup:

    ##############################################################
    # WINDOWS: Required parameters for the splunkforwarder-formula
    # Uncomment and set the required parameters, or the formula
    # will fail.
    ##############################################################

    # deploymentclient.conf contains the information necessary for connecting
    # to the splunk server.
    # deploymentclient:client_name is an identifier for the client environment
    # deploymentclient:target_uri is is the fqdn:port of the splunk collector
    deploymentclient:
      client_name: splunk-uf-windows-srv
      target_uri: 'hostname.domainname:9098'

    ##############################################################
    # WINDOWS: Optional parameters for the splunkforwarder-formula
    ##############################################################

    # log-local.cfg contains information on what logs will be forwarded to the
    # splunk server.
    #log_local:
      #contents: |
          #category.StatusMgr=WARN
          #category.TcpOutputProc=WARN
          #category.FilesystemChangeWatcher=ERROR

    # `package` is the name of the winrepo package containing the
    # splunkforwarder
    #package: splunkforwarder

    # `service` is the name of the splunkforwarder service
    #service: SplunkForwarder
