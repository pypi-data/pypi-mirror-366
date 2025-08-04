import os
import toml
import pathlib
from dataclasses import dataclass

"""
DATA_HOME structure:
    DATA_HOME
        |- users.db
        |- config.toml
"""
DATA_HOME = pathlib.Path(os.environ.get('PODY_HOME', os.path.expanduser('~/.pody')))
SRC_HOME = pathlib.Path(__file__).parent

@dataclass
class Config:
    @dataclass
    class ImageConfig:
        name: str           # e.g. "ubuntu2204-cuda121:latest"
        ports: list[int]    # e.g. [22, 80, 443]
    
    @dataclass
    class DefaultQuota:
        # ["" for string] and [-1 for integer] means no limit
        max_pods: int
        gpu_count: int
        gpus: str               # "all"="", "0,1", "none"
        memory_limit: str       # "64g"
        storage_size: str       # "100g"
        shm_size: str
        commit_count: int
        commit_size_limit: str  # "20g"

    name_prefix: str
    available_ports: list[int | tuple[int, int]]
    volume_mappings: list[str]
    network: str
    default_quota: DefaultQuota
    images: list[ImageConfig]
    commit_name: str
    commit_image_ports: list[int]

def config():
    # prevent circular import
    from .eng.nparse import check_name_part

    def parse_ports(ports_str: str) -> list[int | tuple[int, int]]:
        ports: list[int | tuple[int, int]] = []
        ports_str_sp = ports_str.split(',')
        for port in ports_str_sp:
            if '-' in port:
                start, end = port.split('-')
                start, end = start.strip(), end.strip()
                assert start.isdigit() and end.isdigit()
                ports.append((int(start), int(end)))
            else:
                port = port.strip()
                assert port.isdigit(), "Port must be an integer"
                ports.append(int(port))
        # validity check
        for port in ports:
            if isinstance(port, tuple):
                assert port[0] < port[1], "Invalid port range"
                assert port[0] >= 0 and port[1] <= 65535, "Port range must be between 0 and 65535"
            else:
                assert port >= 0 and port <= 65535, "Port must be between 0 and 65535"
        return ports
    
    config_path = DATA_HOME / "config.toml"
    def create_default_config():
        nonlocal config_path
        template_config_file = pathlib.Path(__file__).parent / "config.default.toml"
        with template_config_file.open() as f:
            with config_path.open('w') as f2:
                f2.write(f.read())
    
    DATA_HOME.mkdir(exist_ok=True)
    if not config_path.exists():
        create_default_config()
    
    loaded = toml.load(config_path)
    name_prefix = loaded.get('name_prefix', "")
    if name_prefix:
        prefix_valid, reason = check_name_part(loaded['name_prefix'])
        if not prefix_valid:
            raise ValueError(f"Invalid name prefix: {reason}")
    
    return Config(
        name_prefix=name_prefix,
        available_ports=parse_ports(loaded['available_ports']), 
        volume_mappings=loaded['volume_mappings'],
        network=loaded.get('network', ""),
        default_quota=Config.DefaultQuota(**loaded['default_quota']),
        images=[Config.ImageConfig(name=i['name'], ports=i['ports']) for i in loaded['images']], 
        commit_name=loaded.get('commit_name', 'pody-commit'),
        commit_image_ports=loaded.get('commit_image_ports', [22])
        )