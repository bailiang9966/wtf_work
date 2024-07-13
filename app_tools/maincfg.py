import yaml

MARKET_SPOT = 'SPOT'
MARKET_UF = 'UF'
USDT = 'USDT'

def read_yaml(yaml_file = 'config/cfg.yaml'):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        yaml_cfg = yaml.safe_load(file)
    return yaml_cfg

MAINCFG = read_yaml()
