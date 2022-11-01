import asyncio
import json
import sys
from asyncio import AbstractEventLoop, Task
from json import JSONDecodeError
from typing import *
import logging

from csgo.FSM import FSM, State, DynamicFSM

from lightServer import *

sys.path.append('../')


class CSGOLights(DynamicFSM):
    def __init__(self):
        super().__init__()
        self.flashTask: Optional[Task] = None

        self.blinkState: bool = False
        self.gameState: Optional[Dict] = None

        loop: AbstractEventLoop = asyncio.get_event_loop()
        asyncio.ensure_future(self.__mainLoop())
        loop.run_forever()

    async def __mainLoop(self):
    # TODO: Redo this whole thing becuase this is shit
        while True:
            with open('csgo.json', 'r') as file:
                try:
                    gameState: Dict = json.loads(file.read())
                    self.gameState = gameState

                    if self.gameState.get('player', {}).get('activity', None) == 'menu':
                        self.setState('MainMenu')
                    else:
                        if self.gameState.get('player', {}).get('state', {}).get('flashed', False):
                            self.setState('Flashbang')
                        elif self.gameState.get('round', {}).get('bomb', None) == 'planted':
                            self.setState('BombPlantedSlow')
                        else:
                            if self.gameState.get('player', {}).get('team', None) == 'T':
                                self.setState('LiveT')
                            else:
                                self.setState('LiveCT')
                except JSONDecodeError:
                    continue

            await asyncio.sleep(1. / 30.)

    def enterMainMenu(self):
        setLight(
                on = True,
                saturation = 254,
                brightness = 60,
                hue = 34952)

    def enterLiveT(self):
        setLight(
                on = True,
                saturation = 254,
                brightness = 60,
                hue = 6200)

    def enterLiveCT(self):
        setLight(
                on = True,
                saturation = 254,
                brightness = 60,
                hue = 34952)

    def enterBombPlantedSlow(self):
        self.flashTask = asyncio.create_task(self.blinkLightSlow())

    def exitBombPlantedSlow(self):
        self.flashTask.cancel()

    def enterBombPlantedFast(self):
        self.flashTask = asyncio.create_task(self.blinkLightFast())

    def exitBombPlantedFast(self):
        self.flashTask.cancel()

    def enterFlashbang(self):
        setLight(
                on = True,
                saturation = 0,
                brightness = 250,
                transitionTime = 2,
                hue = 0)

    async def blinkLightSlow(self):
        while True:
            setLight(on = True,
                     saturation = 254,
                     brightness = 250,
                     hue = 0)
            await asyncio.sleep(1)
            setLight(on = False)
            await asyncio.sleep(1)

    async def blinkLightFast(self):
        while True:
            setLight(on = True,
                     saturation = 254,
                     brightness = 250,
                     hue = 0)
            await asyncio.sleep(.5)
            setLight(on = False)
            await asyncio.sleep(.5)


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG, format = "::%(levelname)s:: %(asctime)s: %(message)s")
    CSGOLights()
