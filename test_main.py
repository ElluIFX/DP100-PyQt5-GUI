import time

from mdp_controller import MDP_P906

if __name__ == "__main__":
    mdp = MDP_P906(
        freq=2521, idcode=b"\x08\x37\x54\x34", led_color=(0x66, 0xCC, 0xFF), debug=False
    )
    # mdp.auto_match()
    mdp.connect()
    print(mdp.get_set_value())
    print(mdp.get_realtime_value())
    t0 = time.perf_counter()
    cnt = 0
    cnt2 = 0

    mdp.set_voltage(5)
    mdp.set_current(2)
    mdp.set_output(True)

    def rt_cbk(vals):
        global cnt, t0, cnt2
        cnt += 1
        t1 = time.perf_counter() - t0
        print(
            f"\r{t1/cnt:0.5f}s {cnt/t1:5.1f}ps {t1/cnt2:0.5f}s {cnt2/t1:5.1f}ps {vals}              ",
            end="",
        )

    # mdp.register_realtime_value_callback(rt_cbk)

    # while True:
    #     cnt2 += 1
    #     vals = mdp.request_realtime_value()

    while True:
        cnt2 += 1
        vals = mdp.get_realtime_value()
        rt_cbk(vals)
