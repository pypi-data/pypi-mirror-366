import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Cache(Provider):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register event listeners
        #AppEvents.Registered.listen(bootstrap.Cache)

        #self.bind_override('uvicore.cache.cache.Cache', 'uvicore.cache.cache2.Cache2')
        # self.bind('uvicore.cache.cache.Cache', 'uvicore.cache.cache.Cache',
        #     aliases=['cache0', 'cache'],
        #     singleton=False,
        # )

        #self.bind('uvicore.cache.cache.Cache')

        # self.bind('uvicore.cache.cache.Cache', 'uvicore.cache.cache2.Cache2',
        #     aliases=['cacheO'],
        #     singleton=True,
        # )

        # Set uvicore.log global connecting to default store
        uvicore.cache = uvicore.ioc.make('uvicore.cache.manager.Manager').connect()

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        #self.registers(self.package.config.registers)

        # Import cache to fire up Ioc so we can later use as short 'cache' names
        #from uvicore.cache.cache import Cache
        pass
