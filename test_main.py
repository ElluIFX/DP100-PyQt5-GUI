import time

from controller import MDP_P906

if __name__ == "__main__":
    mdp = MDP_P906(
        freq=2521,
        idcode="08375434",
        led_color=(0x66, 0xCC, 0xFF),
        debug=False,
        tx_output_power="4dBm",
    )

    try:
        mdp.connect()
    except Exception:
        print("Connection failed, try to auto match")
        mdp.auto_match()
        mdp.connect()

    mdp.set_voltage(5)
    mdp.set_current(2)
    mdp.set_output(True)
    print(mdp.get_set_voltage_current())
    print(mdp.get_status())
    print(mdp.get_realtime_value())

    t0 = time.perf_counter()
    cnt = 0
    cnt2 = 0

    def rt_cbk(vals):
        global cnt, t0, cnt2
        cnt += 1
        t1 = time.perf_counter() - t0
        print(
            f"{t1/cnt:0.5f}s {cnt/t1:5.1f}fps {t1/cnt2:0.5f}s {cnt2/t1:5.1f}fps {vals}             \r",
            end="",
        )

    # async
    # mdp.register_realtime_value_callback(rt_cbk)
    # while True:
    #     cnt2 += 1
    #     vals = mdp.request_realtime_value()

    # sync
    while True:
        cnt2 += 1
        vals = mdp.get_status()
        # vals = mdp.get_realtime_value()
        rt_cbk(vals)
