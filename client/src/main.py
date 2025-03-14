# src/main.py
import asyncio
from hardware_class import ButtonControl
from event_manager import EventManager
from bt.bt_uart import uart_main

class Main:
    def __init__(self) -> None:
        self.event_manager = EventManager()
        self.buttons = ButtonControl(self.event_manager)

    async def buttons_task(self):
        await self.buttons.monitor_for_press()

    async def device_task(self):
        await self.event_manager.wait_for_events()
    
    async def run_uart_in_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def thread_wrapper():
            await uart_main(self.event_manager)
        task = loop.create_task(thread_wrapper())
        await asyncio.to_thread(loop.run_until_complete, task)
    
    async def main_loop(self):
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.buttons_task())
        loop.create_task(self.device_task())
        loop.create_task(uart_main(self.event_manager))
        loop.run_forever()
        """
        tasks = [self.buttons_task(), self.device_task(), self.run_uart_in_thread()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    app = Main()
    asyncio.run(app.main_loop())

