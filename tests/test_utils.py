
def test_rescale():
    from pyjoystick.utils import rescale

    # Int32
    assert rescale(-32768, curr_min=-32768, curr_max=32767, new_min=-1, new_max=1) == -1
    assert round(rescale(0, curr_min=-32768, curr_max=32767, new_min=-1, new_max=1), 4) == 0  # Not exact
    assert rescale(32767, curr_min=-32768, curr_max=32767, new_min=-1, new_max=1) == 1

    # Degrees
    assert rescale(-180, curr_min=-180, curr_max=180, new_min=0, new_max=360) == 0
    assert rescale(0, curr_min=-180, curr_max=180, new_min=0, new_max=360) == 180
    assert rescale(180, curr_min=-180, curr_max=180, new_min=0, new_max=360) == 360


def test_periodic_thread():
    import time
    from pyjoystick.utils import PeriodicThread

    li = []

    def run():
        li.append(time.time())

    test_interval = 0.1
    precision = 1
    attempts = 10

    tmr = PeriodicThread(test_interval, run)
    tmr.start()

    while len(li) <= attempts:
        time.sleep(test_interval/2)

    tmr.join()

    diff = [t - li[i] for i, t in enumerate(li[1:])]  # i is already offset by 1
    # print(diff)
    assert len(diff) == attempts, 'Wrong found attempts {} != {}'.format(len(diff), attempts)
    assert all(round(t, precision) == test_interval for t in diff), diff


if __name__ == '__main__':
    test_rescale()
    test_periodic_thread()

    print('All tests finished successfully!')
