import json
from tkinter import EXCEPTION
from .constants import *
from .logging import Log
from .exceptions import *
from .utils import *
import os
from .login import *
from time import sleep
from datetime import datetime, date,timedelta
import logging
from playwright.async_api import async_playwright



class Upload:
    def __init__(
        self,
        root_profile_directory: str="",
        proxy_option: str = "",
        timeout: int = 3,
        watcheveryuploadstep: bool = True,
        debug: bool = True,
        CHANNEL_COOKIES: str = "",
        recordvideo:bool=False

    ) -> None:
        self.timeout = timeout
        self.log = Log(debug)
        self.root_profile_directory=root_profile_directory
        self.proxy_option=proxy_option
        self.watcheveryuploadstep=watcheveryuploadstep
        self._playwright=''
        self.browser=''
        self.context=''
        self.page=''
        self.recordvideo=recordvideo
        # self.setup()


    async def startpage(
        self,
        url
    ) -> Tuple[bool, Optional[str]]:
        """Uploads a video to YouTube.
        Returns if the video was uploaded and the video id.
        """
        self._playwright = await self._start_playwright()
            #     browser = p.chromium.launch()

        # proxy_option = "socks5://127.0.0.1:1080"

        headless=True
        if self.watcheveryuploadstep:
            headless=False
        print('whether run in view mode',headless)
        if self.proxy_option == "":
            print('start web page without proxy')

            browserLaunchOptionDict = {
                "headless": headless,
                # "executable_path": executable_path,
                "timeout": 30000
            }

            if not self.root_profile_directory:
                self.browser = await self._start_browser("firefox", **browserLaunchOptionDict)
            else:
                self.browser = await self._start_persistent_browser(
                    "firefox", user_data_dir=self.root_profile_directory, **browserLaunchOptionDict
                )
            if self.recordvideo:
                self.context = await self.browser.new_context(record_video_dir="test-results")
            else:
                self.context = await self.browser.new_context()
        else:
            print('start web page with proxy')

            browserLaunchOptionDict = {
                "headless": headless,
                "proxy": {
                    "server": self.proxy_option,
                },

                # timeout <float> Maximum time in milliseconds to wait for the browser instance to start. Defaults to 30000 (30 seconds). Pass 0 to disable timeout.#
                "timeout": 30000
            }

            if not self.root_profile_directory:
                self.browser = await self._start_browser("firefox", **browserLaunchOptionDict)
            else:
                self.browser = await self._start_persistent_browser(
                    "firefox", user_data_dir=self.root_profile_directory, **browserLaunchOptionDict
                )
        # Open new page
            if self.recordvideo:
                self.context = await self.browser.new_context(record_video_dir="test-results")
            else:
                self.context = await self.browser.new_context()
        self.log.debug("Firefox is now running")
        page = await self.context.new_page()

        return page
   

    async  def _start_playwright(self):
        #  sync_playwright().start()
        return await  async_playwright().start()
    async def _start_browser(self, browser: str, **kwargs):
        if browser == "chromium":
            return await self._playwright.chromium.launch(**kwargs)

        if browser == "firefox":
            return await self._playwright.firefox.launch(**kwargs)

        if browser == "webkit":
            return await self._playwright.webkit.launch(**kwargs)

        raise RuntimeError(
            "You have to select either 'chromium', 'firefox', or 'webkit' as browser."
        )

    async def _start_persistent_browser(
        self, browser: str, user_data_dir: Optional[Union[str, Path]], **kwargs
    ):
        if browser == "chromium":
            return await self._playwright.chromium.launch_persistent_context(
                user_data_dir, **kwargs
            )
        if browser == "firefox":
            return await self._playwright.firefox.launch_persistent_context(
                user_data_dir, **kwargs
            )
        if browser == "webkit":
            return await self._playwright.webkit.launch_persistent_context(
                user_data_dir, **kwargs
            )

        raise RuntimeError(
            "You have to select either 'chromium', 'firefox' or 'webkit' as browser."
        )
    async def close(self):
        await self.browser.close()
        await self._playwright.stop()