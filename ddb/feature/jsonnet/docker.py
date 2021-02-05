from collections import defaultdict

from ddb.feature.docker.lib.compose.config.types import ServicePort


def apply_resolve_ports_conflicts(compose):
    """
    Resolve ports conflicts in docker compose configuration.
    """
    published = defaultdict(set)

    if 'services' in compose:  # pylint:disable=too-many-nested-blocks
        for service in compose['services'].values():
            if 'ports' in service:
                service_ports = service['ports']
                for index, port in enumerate(tuple(service_ports)):
                    parsed_ports = ServicePort.parse(port)
                    if len(parsed_ports) == 1:
                        parsed_port = parsed_ports[0]
                        new_published = parsed_port.published
                        while new_published in published[parsed_port.protocol]:
                            new_published = new_published + 1
                        published[parsed_port.protocol].add(new_published)
                        if parsed_port.published != new_published:
                            if isinstance(port, str):
                                service_port_data = dict(parsed_port._asdict())
                                service_port_data['published'] = new_published
                                new_port = ServicePort(**service_port_data)
                                port = new_port.legacy_repr()
                                if not new_port.protocol and port.endswith('/tcp'):
                                    port = port[:-4]
                            else:
                                port['published'] = str(new_published)
                            service_ports[index] = port

    return compose
