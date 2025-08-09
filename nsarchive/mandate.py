import math
import time

EPOCH = 1577833200 # 1er Janvier 2020
PATIENTAGE_DATE = 1725141600 # 1er Septembre 2024
OPEN_DATE = 1756677600 # 1er Septembre 2025

MANDATE_DURATION = 2419200 # 28 jours

def get_cycle(ts: int = round(time.time())):
    if EPOCH <= ts < PATIENTAGE_DATE:
        return 0
    elif PATIENTAGE_DATE <= ts < OPEN_DATE:
        return 1
    elif OPEN_DATE <= ts:
        return math.floor((ts - OPEN_DATE) / MANDATE_DURATION) + 2
    else:
        raise ValueError(f"Timestamp {ts} is out of range (must be greater than or equal to {EPOCH}).")

def get_day(ts: int = round(time.time())) -> int:
    cycle = get_cycle(ts)

    if cycle == 0:
        return math.floor((ts - EPOCH) / 86400)
    elif cycle == 1:
        return math.floor((ts - PATIENTAGE_DATE) / 86400)
    else:
        return math.floor(((ts - OPEN_DATE) % MANDATE_DURATION) / 86400)

def get_phase(ts: int = round(time.time())) -> str:
    cycle = get_cycle(ts)

    if cycle < 2: # Les deux premiers cycles durent (beaucoup) plus longtemps qu'un cycle normal.
        return 'undefined'

    day = get_day(ts)

    if day == 0:
        return 'investiture' # Investiture du PR
    elif 1 <= day < 24:
        return 'paix' # Rien du tout
    elif 24 <= day < 28:
        return 'partials' # Élections législatives
    elif 28 <= day < 52:
        return 'paix' # Toujours rien
    elif 52 <= day < 56:
        return 'elections' # Élections législatives et présidentielles

    else:
        raise ValueError(f"Idk what happened but it seems that {day} is greater than 55...")


def next_election(type: str = 'partial') -> int:
    if get_cycle() == 1:
        return PATIENTAGE_DATE
    elif get_cycle() == 2:
        return OPEN_DATE
    else:
        if type == 'partial':
            ts = OPEN_DATE + get_cycle() * MANDATE_DURATION
        elif type == 'full':
            ts = OPEN_DATE + get_cycle() * MANDATE_DURATION

            if get_cycle() % 2 == 1:
                ts += 28 * 86400

        ts = round(ts / 86400) * 86400

        return ts