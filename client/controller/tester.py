"""
This Python file allows to send commands to nirone and inspect the output.
"""
from dataclasses import dataclass
from nir_driver import CMDS, write_command, read_response, serialFlush, sensorMeasureWavelengths, measureGet, connectNIR
from time import sleep

@dataclass
class OPTIO:
    description: str
    cmd: str

def cmdAction() -> None:
    
    return None

def getOptions() -> list[OPTIO]:
    Options: list[OPTIO] = []
    for CMD_Description in CMDS:
        Option = OPTIO(CMD_Description, CMDS[CMD_Description])
        Options.append(Option)
    return Options

def showOptions(Options: list[OPTIO]) -> None:
    print("Options:")
    for i, Option in enumerate(Options):
        print(f"{i + 1}) {Option.description}")
    print("0) Exit")
    return None

def askChoice() -> int:
    Choice = int(-1)
    Feed = input("Your choice: ")
    try:
        Choice = int(Feed)
    except Exception:
        pass
    return Choice

def main() -> None:
    ser = connectNIR()
    Options: list[OPTIO] = getOptions()
    RunMenu = True
    while RunMenu:
        Quit = input("Continue (q to quit | enter continue): ")
        if "q" == Quit:
            RunMenu = False
            print("")
            continue
        showOptions(Options)
        Choice = askChoice()
        if Choice > 0:
            ChoiceIndex = Choice - 1
            print(f"Do: {Options[ChoiceIndex].description}")
            print(f"Send command: {Options[ChoiceIndex].cmd}")
            write_command(ser, f"{Options[ChoiceIndex].cmd}")
            sleep(1)
            print(f"Receive response...")
            print(read_response(ser, False, False))
        elif Choice == 0:
            RunMenu = False
        else:
            print("Unknown option, try again!")
        print("")
    Options.clear()
    return None

main()
