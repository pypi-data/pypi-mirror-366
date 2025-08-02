import functools
import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

import punq  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    # These imports are only for type checking and will not cause circular imports at runtime
    from castlecraft_engineer.abstractions.command_bus import CommandBus
    from castlecraft_engineer.abstractions.event_bus import EventBus
    from castlecraft_engineer.abstractions.query_bus import QueryBus

logger = logging.getLogger(__name__)


class ContainerBuilder:
    """
    Builds the DI container progressively.
    """

    def __init__(self) -> None:
        self._logger = logger
        self._container = punq.Container()
        self._registered_sync_db_names: set[str] = set()
        self._registered_async_db_names: set[str] = set()
        self._cache_registered = False
        self._async_cache_registered = False
        self._authentication_registered = False
        self._command_bus_registered = False
        self._query_bus_registered = False
        self._event_bus_registered = False
        self._authorization_registered = False
        self.command_bus: Optional["CommandBus"] = None
        self.query_bus: Optional["QueryBus"] = None
        self.event_bus: Optional["EventBus"] = None
        self._container.register(punq.Container, instance=self._container)
        self._logger.info("Initialized ContainerBuilder.")

    def with_database(
        self, name: str = "default", db_config: Optional[Dict[str, Any]] = None
    ) -> "ContainerBuilder":
        """
        Registers synchronous database components for a named connection.

        Args:
            name: A unique name for this database connection (e.g., "default", "read_replica").
            db_config: Optional dictionary to override database connection settings.
                       Keys can include 'connection_string', 'enable_sql_log',
                       and other keyword arguments for SQLAlchemy's `create_engine`.
        """
        if name in self._registered_sync_db_names:
            self._logger.warning(
                f"Synchronous database components for '{name}' already registered. Skipping.",
            )
            return self

        self._logger.info(
            f"Registering synchronous database components for '{name}'..."
        )

        try:
            from sqlalchemy import Engine
            from sqlalchemy.orm import Session, sessionmaker

            from castlecraft_engineer.database.connection import get_engine

            config = db_config or {}
            sync_engine = get_engine(db_config=config)
            self._container.register(
                Engine,
                instance=sync_engine,
                name=f"db_sync_engine_{name}",
            )

            sync_session_factory = sessionmaker(
                bind=sync_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=Session,
            )
            self._container.register(
                sessionmaker[Session],
                instance=sync_session_factory,
                name=f"db_sync_session_factory_{name}",
            )

            self._container.register(
                Session,
                factory=lambda **_: sync_session_factory(),
                name=f"db_sync_session_{name}",
            )

            # For backward compatibility, register the default session without a name
            if name == "default":
                self._container.register(
                    Session,
                    factory=lambda **_: sync_session_factory(),
                )

            self._registered_sync_db_names.add(name)
            self._logger.info(
                f"Synchronous database components for '{name}' registered."
            )
        except Exception as e:
            self._logger.error(
                f"Failed to register synchronous database components: {e}",
                exc_info=True,
            )

        return self

    def with_async_database(
        self, name: str = "default", db_config: Optional[Dict[str, Any]] = None
    ) -> "ContainerBuilder":
        """
        Registers asynchronous database components for a named connection.

        Args:
            name: A unique name for this database connection (e.g., "default", "read_replica").
            db_config: Optional dictionary to override database connection settings.
                       Keys can include 'async_connection_string', 'enable_sql_log',
                       and other keyword arguments for SQLAlchemy's `create_async_engine`.
        """
        if name in self._registered_async_db_names:
            self._logger.warning(
                f"Asynchronous database components for '{name}' already registered. Skipping.",
            )
            return self

        self._logger.info(
            f"Registering asynchronous database components for '{name}'..."
        )

        try:
            from sqlalchemy.ext.asyncio import (
                AsyncEngine,
                AsyncSession,
                async_sessionmaker,
            )

            from castlecraft_engineer.database.connection import get_async_engine

            config = db_config or {}
            async_engine = get_async_engine(db_config=config)
            self._container.register(
                AsyncEngine, instance=async_engine, name=f"db_async_engine_{name}"
            )

            async_session_factory = async_sessionmaker(
                bind=async_engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            self._container.register(
                async_sessionmaker[AsyncSession],
                instance=async_session_factory,
                name=f"db_async_session_factory_{name}",
            )

            self._container.register(
                AsyncSession,
                factory=lambda **_: async_session_factory(),
                name=f"db_async_session_{name}",
            )

            # For backward compatibility, register the default session without a name
            if name == "default":
                self._container.register(
                    AsyncSession,
                    factory=lambda **_: async_session_factory(),
                )

            self._registered_async_db_names.add(name)
            self._logger.info(
                f"Asynchronous database components for '{name}' registered."
            )
        except Exception as e:
            self._logger.error(
                f"Failed to register asynchronous database components: {e}",
                exc_info=True,
            )

        return self

    def with_cache(
        self,
        is_async: bool = False,
        cache_config: Optional[Dict[str, Any]] = None,
    ) -> "ContainerBuilder":
        """
        Registers Cache connection and components.

        Args:
            is_async: If True, registers the asynchronous Redis client.
                      If False (default), registers the synchronous client.
            cache_config: Optional dictionary of parameters to override environment
                          variables for cache connection.
        """
        if is_async and self._async_cache_registered:
            self._logger.warning(
                "Asynchronous cache components already registered. Skipping.",
            )
            return self
        if not is_async and self._cache_registered:
            self._logger.warning(
                "Synchronous cache components already registered. Skipping.",
            )
            return self

        config = cache_config or {}

        if is_async:
            self._logger.info(
                "Registering asynchronous cache components...",
            )

            try:
                import redis.asyncio as aredis

                from castlecraft_engineer.caching.cache import (
                    get_redis_cache_async_connection,
                )

                # Safer: Register a factory
                self._container.register(
                    aredis.Redis,
                    factory=lambda **_: get_redis_cache_async_connection(**config),
                    scope=punq.Scope.singleton,
                    name="cache_async",
                )
                self._async_cache_registered = True
                self._logger.info(
                    "Asynchronous cache components registered (factory).",
                )
            except Exception as e:
                self._logger.error(
                    f"Failed to register asynchronous cache components: {e}",
                    exc_info=True,
                )
        else:
            self._logger.info("Registering synchronous cache components...")
            try:
                import redis

                from castlecraft_engineer.caching.cache import (
                    get_redis_cache_connection,
                )

                sync_cache_client = get_redis_cache_connection(**config)
                self._container.register(
                    redis.Redis, instance=sync_cache_client, name="cache_sync"
                )
                self._cache_registered = True
                self._logger.info("Synchronous cache components registered.")
            except Exception as e:
                self._logger.error(
                    f"Failed to register synchronous cache components: {e}",
                    exc_info=True,
                )

        return self

    def with_authentication(
        self, auth_config: Optional[Dict[str, Any]] = None
    ) -> "ContainerBuilder":
        """
        Registers Authentication components.

        Args:
            auth_config: Optional dictionary of parameters to override
                         environment variables for AuthenticationService
                         configuration.
        """
        if self._authentication_registered:
            self._logger.warning(
                "Authentication components already registered. Skipping.",
            )
            return self

        self._logger.info(
            "Registering Authentication components (AuthenticationService)...",
        )

        try:
            from castlecraft_engineer.application.auth import AuthenticationService

            config = auth_config or {}

            # Prefer async if registered, otherwise use sync if registered
            def auth_service_factory(
                container=self._container,
            ):
                sync_cache = None
                async_cache = None
                if self._async_cache_registered:
                    try:
                        import redis.asyncio as aredis

                        # Resolve the async client (trigger factory)
                        async_cache = container.resolve(
                            aredis.Redis,
                            name="cache_async",
                        )
                        self._logger.info(
                            "AuthenticationService will use asynchronous cache.",
                        )
                    except ImportError:
                        self._logger.info(
                            "aredis library not found for auth_service_factory. Async cache will not be used."  # noqa: E501
                        )
                    except Exception as e:
                        self._logger.error(
                            f"Failed to resolve async cache for AuthenticationService: {e}"
                        )
                if not async_cache and self._cache_registered:
                    try:
                        import redis

                        sync_cache = container.resolve(
                            redis.Redis,
                            name="cache_sync",
                        )
                        self._logger.info(
                            "AuthenticationService will use synchronous cache.",
                        )
                    except ImportError:
                        self._logger.info(
                            "redis library not found for auth_service_factory. Sync cache will not be used."  # noqa: E501
                        )
                    except Exception as e:
                        self._logger.error(
                            f"Failed to resolve sync cache for AuthenticationService: {e}"
                        )

                return AuthenticationService(
                    cache_client=sync_cache,
                    async_cache_client=async_cache,
                    config=config,
                )

            self._container.register(
                AuthenticationService,
                factory=auth_service_factory,
                scope=punq.Scope.singleton,
            )
            self._authentication_registered = True
            self._logger.info("Authentication components registered.")
        except Exception as e:
            self._logger.error(
                f"Failed to register Authentication components: {e}",
                exc_info=True,
            )

        return self

    def with_command_bus(self) -> "ContainerBuilder":
        """Registers the CommandBus as a singleton."""
        if self._command_bus_registered:
            self._logger.warning("CommandBus already registered. Skipping.")
            return self

        self._logger.info("Registering CommandBus...")
        try:
            from castlecraft_engineer.abstractions.command_bus import CommandBus

            self._container.register(
                CommandBus,
                factory=lambda c=self._container: CommandBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._command_bus_registered = True
            self.command_bus = self._container.resolve(CommandBus)
            self._logger.info("CommandBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register CommandBus: {e}", exc_info=True)
        return self

    def with_query_bus(self) -> "ContainerBuilder":
        """Registers the QueryBus as a singleton."""
        if self._query_bus_registered:
            self._logger.warning("QueryBus already registered. Skipping.")
            return self

        self._logger.info("Registering QueryBus...")
        try:
            from castlecraft_engineer.abstractions.query_bus import QueryBus

            self._container.register(
                QueryBus,
                factory=lambda c=self._container: QueryBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._query_bus_registered = True
            self.query_bus = self._container.resolve(QueryBus)
            self._logger.info("QueryBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register QueryBus: {e}", exc_info=True)
        return self

    def with_event_bus(self) -> "ContainerBuilder":
        """
        Registers the EventBus as a singleton.
        Note: Event handlers are typically registered directly with the
        EventBus instance after it's resolved, not via the DI container
        for the handlers themselves unless the EventBus is modified to
        resolve handlers.
        """
        if self._event_bus_registered:
            self._logger.warning("EventBus already registered. Skipping.")
            return self

        self._logger.info("Registering EventBus...")
        try:
            from castlecraft_engineer.abstractions.event_bus import EventBus

            self._container.register(
                EventBus,
                factory=lambda c=self._container: EventBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._event_bus_registered = True
            self.event_bus = self._container.resolve(EventBus)
            self._logger.info("EventBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register EventBus: {e}", exc_info=True)
        return self

    def with_authorization(
        self, engine_name: Optional[str] = None
    ) -> "ContainerBuilder":
        """
        Registers Authorization connection and components.

        Args:
            engine_name: Optionally specify the authorization engine name,
                         overriding the environment variable setting.
        """

        if not self._authentication_registered:
            self._logger.error(
                "Authentication components need to be registered. Skipping.",
            )
            return self

        if self._authorization_registered:
            self._logger.warning(
                "Authorization components already registered. Skipping.",
            )
            return self

        self._logger.info(
            "Setting up and registering Authorization components...",
        )

        try:
            from castlecraft_engineer.authorization.setup import setup_authorization

            setup_authorization(self._container, auth_engine_name=engine_name)
            self._authorization_registered = True
            self._logger.info(
                "Authorization components set up and registered.",
            )
        except Exception as e:
            self._logger.error(
                f"Failed to set up authorization components: {e}",
                exc_info=True,
            )

        return self

    def register(
        self,
        type_or_name: Any,
        **kwargs,
    ) -> "ContainerBuilder":
        """Directly register a component."""
        self._container.register(type_or_name, **kwargs)
        return self

    def build(self) -> punq.Container:
        """Returns the configured container."""
        self._logger.info("DI container build complete.")
        return self._container


def create_injector(container: punq.Container):
    def inject(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)

            # Identify names of arguments explicitly passed by the caller
            explicitly_passed_names = sig.bind_partial(*args, **kwargs).arguments.keys()

            kwargs_to_inject = {}
            for name, param in sig.parameters.items():
                # Attempt to inject if:
                # 1. The parameter was NOT explicitly passed by the caller.
                # 2. The parameter has a type annotation.
                if (
                    name not in explicitly_passed_names
                    and param.annotation != inspect.Parameter.empty
                ):
                    try:
                        resolved_dependency = container.resolve(
                            param.annotation,
                        )
                        kwargs_to_inject[name] = resolved_dependency
                    except punq.MissingDependencyError:
                        logger.error(
                            f"Missing dependency: {param.annotation}",
                        )
            final_kwargs = {**kwargs_to_inject, **kwargs}
            return func(*args, **final_kwargs)

        return wrapper

    return inject
