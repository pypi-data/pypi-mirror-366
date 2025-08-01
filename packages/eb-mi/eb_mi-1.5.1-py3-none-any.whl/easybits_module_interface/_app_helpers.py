import asyncio
import logging
import sentry_sdk
import os
from aio_pika import connect_robust


async def bootstrap_module_class(module_implementation, **config) -> None:
    """
    Main entry point for module implementations, aka application loop.

    :param module_implementation: ModuleInterface implementation (as class)
    :param config: Configuration dictionary
    :return: None

    ================  =============  =============
    Key               Type           Description
    ================  =============  =============
    logger            dict           Logger configuration
    logger.level      str            Logger level
    logger.path       str            Path to logger configuration file
    logger.name       str            Name of logger
    ================= =============  =============
    broker            dict           Broker configuration
    broker.uri        str            Broker uri
    """
    logger_config = config.get('logger', None)
    broker_config = config.get('broker', None)

    assert 'uri' in broker_config, 'broker uri required!'

    logger_name = None
    if logger_config is not None:
        logging.basicConfig()
        if 'level' in logger_config:
            logging.getLogger().setLevel(logger_config['level'])

        if 'path' in logger_config:
            # set up logger from file
            logging.config.fileConfig(logger_config['path'])

        # create logger
        logger_name = logger_config.get('name', 'module_interface')
        _ = logging.getLogger(name=logger_name)

    connection = await connect_robust(broker_config['uri'])
    module = module_implementation(connection)
    module.init_logger(logger_name)
    return module


async def main(module_implementation, **config) -> None:
    """
    Main entry point for module implementations, aka application loop.

    :param module_implementation: ModuleInterface implementation (as class)
    :param config: Configuration dictionary
    :return: None

    ================  =============  =============
    Key               Type           Description
    ================  =============  =============
    logger            dict           Logger configuration
    logger.level      str            Logger level
    logger.path       str            Path to logger configuration file
    logger.name       str            Name of logger
    ================= =============  =============
    broker            dict           Broker configuration
    broker.uri        str            Broker uri
    """
    module = await bootstrap_module_class(module_implementation, **config)
    try:
        await module.run()
    except Exception as e:
        module.logger.error(e)
    finally:
        module.logger.info("MAIN Shutting down")
        await module.shutdown()


async def multitask_main(loop, module_cls, logger_name, logger_config_path, tasks):  # pragma: no cover
    """
    Main entry point for module implementations that requires multiple threads.

    This method starts all tasks and shuts down the application gracefully.

    :param loop: Your current asyncio loop
    :param module_implementation: ModuleInterface implementation (as class)
    :param logger_name: The name of your logger/application
    :param tasks: A list of strings containing method names of the `module_implementation`
                that will be executed in parallel
    """
    module = await bootstrap_module_class(
        module_cls,
        logger={
            "path": logger_config_path,
            "level": logging.DEBUG,
            "name": logger_name
        },
        broker={'uri': os.environ.get('RMQ_REMOTE_URL')}
    )

    task_map = []
    for t in tasks:
        task = loop.create_task(getattr(module, t)())
        task.add_done_callback(lambda x: module.logger.debug(f'Future: {x}'))
        task_map.append(task)

    try:
        await asyncio.gather(*task_map)
    except asyncio.CancelledError:
        module.logger.error("Main loop cancelled")
        await module.shutdown()


def setup_application():  # pragma: no cover
    VERSION = '0000000'
    if os.path.exists(os.path.join(os.path.dirname(__file__), '../version.txt')):
        with open(os.path.join(os.path.dirname(__file__), '../version.txt'), 'r') as f:
            VERSION = f.read().strip()

    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN', None),
        environment=os.environ.get('SENTRY_ENVIRONMENT', None),
        release=VERSION,
    )

