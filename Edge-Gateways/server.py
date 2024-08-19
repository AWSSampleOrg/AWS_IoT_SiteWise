import asyncio
import logging
import sys
import time

import asyncua
import asyncua.ua
import psutil

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

async def set_cpu(ua_var):
    cpu = psutil.cpu_percent()
    await ua_var.write_value(cpu)
    logger.info(f"CPU Usage: {cpu}%")

async def set_memory(ua_var: asyncua.Node):
    scale = 1024**2
    mem = psutil.virtual_memory().used / scale
    await ua_var.write_value(mem)
    logger.info(f'Memory Used: {mem}MB')

async def main():

    server = asyncua.Server()
    await server.init()
    server.set_endpoint('opc.tcp://localhost:4840/freeopcua/server')

    uri = 'http://python-opcua.example.com'
    idx = await server.register_namespace(uri)

    objects = server.get_objects_node()

    obj_sample = await objects.add_object(idx, 'SampleObject')
    var_cpu = await obj_sample.add_variable(idx, 'CPU', 0.0, asyncua.ua.VariantType.Double)
    var_mem = await obj_sample.add_variable(idx, 'Memory', 0.0, asyncua.ua.VariantType.Double)

    await server.start()

    logger.info('Starting OPC UA Server ...')

    try:
        start = time.time()
        while True:
            await asyncio.sleep(1)
            elasped_time = time.time() - start

            await asyncio.gather(
                set_cpu(var_cpu),
                set_memory(var_mem))

            logger.info(f'Elasped Time: {elasped_time}sec')

    finally:
        await server.stop()

        logger.info('Stopping OPC UA Server ...')

if __name__ == '__main__':
    asyncio.run(main())
