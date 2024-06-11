import logging
import asyncio
import os

import pymem
import win32gui
import win32process

logging.basicConfig(filename="application.log", level=logging.INFO)
logging.getLogger('pymem').setLevel(logging.INFO)

DATA = {
    "ENABLE_AUTOPLAY": False,
    
    "PROCESS_ID": None,
    "ADDRESS": {
        'is_playing': None,
        'autoplay': None,
        'time': None
    }
}

signal = None

async def load_addresses(redo_scan = False):
    handle = pymem.Pymem()
    handle.open_process_from_id(DATA['PROCESS_ID'])
    module = pymem.process.module_from_name(handle.process_handle, 'beatbanger.exe')

    if redo_scan:
        signal.changeText("Preparing script")
        await asyncio.sleep(0.1)
    
        pattern = {
            'is_playing': b'.\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00.....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00....\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x1C\\x00\\x00\\x00....',
            'autoplay': b'.\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00.....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x1C\\x00\\x00\\x00..........\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x00\\x00....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x00\\x00....',
            'time': b'........\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x03\\x00\\x00\\x00............\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x00\\x00....\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x00\\x00......\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x03\\x00\\x00\\x00....'
        }

        signal.changeText(f"Searching addresses.. [0/{len(pattern)}]")
        await asyncio.sleep(0.1)
        
        for index, key in enumerate(DATA['ADDRESS'], 1):
            try:
                DATA['ADDRESS'][key] = pymem.pattern.pattern_scan_all(handle.process_handle, pattern[key], return_multiple=False)
                signal.changeText(f"Searching addresses.. [{index}/{len(pattern)}]")
                await asyncio.sleep(0.1)
            except Exception as e:
                DATA['ADDRESS'][key] = None
                logging.info("Address not found - `{}`".format(key))
                
        if any(value is None for value in DATA['ADDRESS'].values()):
            logging.info("is_playing : {:X} | autoplay : {:X} | time : {:X}".format(DATA['ADDRESS'].values()))
            return signal.changeText("Error! Check application.log")

    await asyncio.sleep(0.1)
    signal.changeText("Script loaded and booted!")

    if DATA['ENABLE_AUTOPLAY']: await autoplay(handle)
        
async def autoplay(handle):
    try:
        while DATA['ENABLE_AUTOPLAY']:
            if handle.read_int(DATA['ADDRESS']['is_playing']) == 1:
                if handle.read_double(DATA['ADDRESS']['time']) > 0.0:
                    handle.write_int(DATA['ADDRESS']['autoplay'], 1)
                else:
                    handle.write_int(DATA['ADDRESS']['autoplay'], 0)
            else:
                handle.write_int(DATA['ADDRESS']['autoplay'], 0)
            await asyncio.sleep(0.1)
        handle.write_int(DATA['ADDRESS']['autoplay'], 0)
    except:
        return signal.disableScript()

async def connect():
    for process_name in ["Beat Banger (DEBUG)", "Beat Banger"]:
        window_handle = win32gui.FindWindow(None, process_name)
        if window_handle: break
    if not window_handle:
        signal.disableScript("Game is not launched!")
    
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    redo_scan = True if DATA["PROCESS_ID"] != pid else False
    DATA["PROCESS_ID"] = pid
    
    if any(value is None for value in DATA['ADDRESS'].values()): redo_scan = True
    await load_addresses(redo_scan)

if __name__ == "__main__":
    asyncio.run(connect())