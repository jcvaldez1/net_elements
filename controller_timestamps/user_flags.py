from ryu import cfg

CONF = cfg.CONF
CONF.register_cli_opts([ cfg.StrOpt( 'controller_mode', default="cold", help='user original CLI option'),])

