from abc import ABCMeta, abstractproperty


class Proxy(metaclass=ABCMeta):

    @abstractproperty
    def proxy_config(self):
        """
        Return the proxy hostname, scheme, and port according to the
        configuration expected by module requests. Example:
            {'http': 'localhost:8080', 'https': 'localhost:8080'}
        :return: dict
        """
        pass
