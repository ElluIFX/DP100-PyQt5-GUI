import struct
from functools import lru_cache


def calc_checksum(data: bytes):
    r = 0x88
    for c in data:
        r ^= c
    return bytes([r])


def gen_packet(type: int, data: bytes):
    assert len(data) < 29
    packet = struct.pack("B", type) + struct.pack("B", len(data)) + data
    return packet + calc_checksum(packet)


def gen_get_volt_cur():
    """
    Type 4
    """
    packet = gen_packet(4, bytes.fromhex("00"))
    return packet


def parse_type4_response(data: bytes):
    """
    Type 4 response contains SET VALUE of CURRENT and VOLTAGE (not realtime value)
    """
    assert data[0] == 4
    assert data[1] == 5
    current = data[2:4].hex()
    current = float(current[0] + "." + current[1:])
    voltage = data[4:7].hex()
    voltage = float(voltage[0:3] + "." + voltage[3:])
    return (current, voltage)


def gen_call_for_id():
    """
    Type 5
    """
    packet = gen_packet(5, bytes.fromhex("4D"))
    return packet


def parse_type5_response(data: bytes):
    """
    Type 5 response contains IDCODE
    """
    assert data[0] == 5
    assert data[1] == 4
    return data[2:6]


def gen_dispatch_ch_addr(addr: bytes, ch: int):
    """
    Type 6
    """
    packet = gen_packet(6, addr[::-1] + bytes([ch]))
    return packet


def parse_type6_response(data: bytes):
    """
    Type 6 response
    """
    assert data[0] == 6
    assert data[1] == 3  # or FAIL ?
    return data[2:4]


def gen_set_voltage(idcode: bytes, voltage: float, m01_channel: int = 0, blink=True):
    """
    Type 7
    """
    assert 0.0 <= voltage <= 30.0
    v = "{:07.3f}".format(voltage).replace(".", "")
    # subtype 03 len 03
    d = "{}{:02x}{:02x}0303{}".format(idcode.hex(), m01_channel, 1 if blink else 0, v)
    packet = gen_packet(7, bytes.fromhex(d))
    return packet


def gen_set_current(idcode: bytes, current: float, m01_channel: int = 0, blink=True):
    """
    Type 7
    """
    assert 0.0 <= current <= 10.0
    c = "{:07.3f}".format(current).replace(".", "")
    # subtype 02 len 03
    d = "{}{:02x}{:02x}0203{}".format(idcode.hex(), m01_channel, 1 if blink else 0, c)
    packet = gen_packet(7, bytes.fromhex(d))
    return packet


def gen_set_output(idcode: bytes, state: bool, m01_channel: int = 0, blink=True):
    """
    Type 7
    """
    # subtype 0c len 03
    d = "{}{:02x}{:02x}0C00{:02x}".format(
        idcode.hex(), m01_channel, 1 if blink else 0, 1 if state else 0
    )
    packet = gen_packet(7, bytes.fromhex(d))
    return packet


@lru_cache()
def gen_get_type7(idcode: bytes, m01_channel: int = 0, blink=True):
    """
    Type 7
    """
    d = "{}{:02x}{:02x}".format(idcode.hex(), m01_channel, 1 if blink else 0)
    packet = gen_packet(7, bytes.fromhex(d))
    return packet


def parse_type7_response(
    data: bytes, HVzero16: int, HVgain16: int, HCzero04: int, HCgain04: int
):
    """
    Type 7 response contains information of device
    """
    assert data[0] == 7
    if data[1] == 0x1C or data[1] == 0x16:
        errflag = data[2]
        locked = data[3]
        temp = data[4:6].hex()
        temperature = float(temp[0:3] + "." + temp[3])
        state = data[6]
        input_volt = data[7:10].hex()
        input_volt = float(input_volt[0:3] + "." + input_volt[3:])
        input_curr = data[10:12].hex()
        input_curr = float(input_curr[0] + "." + input_curr[1:])
        realtime_adc = []
        for i in range(4):
            sd = data[12 + i * 3 : 12 + i * 3 + 3].hex()
            sv = int(sd[0:3], 16)
            sc = int(sd[3:6], 16)
            v = _volt_adc_correct(sv, HVgain16, HVzero16)
            c = _curr_adc_correct(sc, HCgain04, HCzero04)
            realtime_adc.append((v, c))
        if data[1] == 0x1C:
            voltage = data[24:27].hex()
            voltage = float(voltage[0:3] + "." + voltage[3:])
            current = data[27:30].hex()
            current = float(current[0:3] + "." + current[3:])
        else:
            voltage = current = -1
        return (
            errflag,
            input_volt,
            input_curr,
            voltage,
            current,
            locked,
            state,
            temperature,
            realtime_adc,
        )
    raise RuntimeError(f"parse_type7_response: unknown data[1] {data[1]:02x}")


@lru_cache()
def gen_get_type8(idcode: bytes, m01_channel: int = 0, blink=True):
    """
    Type 8
    """
    d = "{}{:02x}{:02x}".format(idcode.hex(), m01_channel, 1 if blink else 0)
    packet = gen_packet(8, bytes.fromhex(d))
    return packet


def parse_type8_response(
    data: bytes, HVzero16: int, HVgain16: int, HCzero04: int, HCgain04: int
):
    """
    Type 8 response contains realtime adc values
    """
    assert data[0] == 8
    assert data[1] <= 0x1C
    errflag = data[2]
    values = []
    for i in range(0, data[1] - 1, 3):
        sd = data[2 + 1 + i : 2 + 1 + i + 3].hex()
        sv = int(sd[0:3], 16)
        sc = int(sd[3:6], 16)
        v = _volt_adc_correct(sv, HVgain16, HVzero16)
        c = _curr_adc_correct(sc, HCgain04, HCzero04)
        values.append((v, c))
    return (errflag, values)


def _volt_adc_correct(value: int, gain: int, offset: int) -> float:
    """
    Correct voltage adc value to V
    """
    val = round((value * 16 - offset) * gain / 100000.0)
    return val / 1000 if val > 1 else 0.0


def _curr_adc_correct(value: int, gain: int, offset: int) -> float:
    """
    Correct current adc value to A
    """
    val = round((value * 4 - offset) * gain / 100000.0 * 2)
    return val / 1000 if val > 1 else 0.0


def gen_set_led_color(
    idcode: bytes, led_color: int = 0x3168, m01_channel: int = 0, blink=True
):
    """
    Type 9
    """
    d = "{}{:02x}{:02x}{:04x}".format(
        idcode.hex(), m01_channel, 1 if blink else 0, led_color
    )
    packet = gen_packet(9, bytes.fromhex(d))
    return packet


def parse_type9_response(data: bytes):
    """
    Type 9 response have id and ADC calibration vals HVzero16/HVgain16/HCzero04/HCgain04
    """
    assert data[0] == 9
    assert data[1] == 14
    idcode = data[2:6]
    # unk1 = data[6] # ?
    HVzero16 = int(data[7:9].hex(), 16)
    HVgain16 = int(data[9:11].hex(), 16)
    HCzero04 = int(data[11:13].hex(), 16)
    HCgain04 = int(data[13:15].hex(), 16)
    assert data[15] == 2
    return (idcode, HVzero16, HVgain16, HCzero04, HCgain04)
