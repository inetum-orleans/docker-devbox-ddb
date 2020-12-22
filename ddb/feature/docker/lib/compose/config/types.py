from collections import namedtuple

from .errors import ConfigurationError
from docker.utils.ports import build_port_bindings


class ServicePort(namedtuple('_ServicePort', 'target published protocol mode external_ip')):
    def __new__(cls, target, published, *args, **kwargs):
        try:
            if target:
                target = int(target)
        except ValueError:
            raise ConfigurationError('Invalid target port: {}'.format(target))

        if published:
            if isinstance(published, str) and '-' in published:  # "x-y:z" format
                a, b = published.split('-', 1)
                if not a.isdigit() or not b.isdigit():
                    raise ConfigurationError('Invalid published port: {}'.format(published))
            else:
                try:
                    published = int(published)
                except ValueError:
                    raise ConfigurationError('Invalid published port: {}'.format(published))

        return super().__new__(
            cls, target, published, *args, **kwargs
        )

    @classmethod
    def parse(cls, spec):
        if isinstance(spec, cls):
            # When extending a service with ports, the port definitions have already been parsed
            return [spec]

        if not isinstance(spec, dict):
            result = []
            try:
                for k, v in build_port_bindings([spec]).items():
                    if '/' in k:
                        target, proto = k.split('/', 1)
                    else:
                        target, proto = (k, None)
                    for pub in v:
                        if pub is None:
                            result.append(
                                cls(target, None, proto, None, None)
                            )
                        elif isinstance(pub, tuple):
                            result.append(
                                cls(target, pub[1], proto, None, pub[0])
                            )
                        else:
                            result.append(
                                cls(target, pub, proto, None, None)
                            )
            except ValueError as e:
                raise ConfigurationError(str(e))

            return result

        return [cls(
            spec.get('target'),
            spec.get('published'),
            spec.get('protocol'),
            spec.get('mode'),
            None
        )]

    @property
    def merge_field(self):
        return (self.target, self.published, self.external_ip, self.protocol)

    def repr(self):
        return {
            k: v for k, v in zip(self._fields, self) if v is not None
        }

    def legacy_repr(self):
        return normalize_port_dict(self.repr())


def normalize_port_dict(port):
    return '{external_ip}{has_ext_ip}{published}{is_pub}{target}/{protocol}'.format(
        published=port.get('published', ''),
        is_pub=(':' if port.get('published') is not None or port.get('external_ip') else ''),
        target=port.get('target'),
        protocol=port.get('protocol', 'tcp'),
        external_ip=port.get('external_ip', ''),
        has_ext_ip=(':' if port.get('external_ip') else ''),
    )
