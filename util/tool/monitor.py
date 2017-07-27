#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import threading
import time

from util.android.adb import ADB

"""
安卓cpu，内存监测
"""


class Monitor(threading.Thread):
    """
    监测当前运行的apk的内存和cpu占用
    """

    def __init__(self, device, screen_shot=False, shot_delay=10, min_mem=200, check_delay=3, mem_incr=20,
                 screenshot_dir=None):
        """初始化

        :param device: ADB device
        :param screen_shot: 是否截图
        :param shot_delay: 每次截图间隔，建议大于10s
        :param min_mem: 最低截图内存
        :param check_delay: 每次监测检测，建议大于5s
        :param mem_incr: 新截图需要当前内存大于之前内存mem_incr mb
        :param screenshot_dir: 截图目录
        :return:
        """
        super(Monitor, self).__init__()
        self._device = device
        self._screen_shot = screen_shot
        self._shot_delay = shot_delay
        self._min_mem = min_mem
        self._check_delay = check_delay
        self._mem_incr = mem_incr
        self._screenshot_dir = screenshot_dir
        self._running = False
        self._mem_date = dict()

    def shut_down(self):
        self._running = False
        print('Shutdown Monitor')
        self.analyse()

    def run(self):
        time.sleep(1)
        if not self._device:
            raise Exception("device is None")

        self._running = True
        print('Running Monitor')

        current_package_name = self._device.current_package_name

        print('APK is {0}'.format(current_package_name))
        last_shot_mem = 0
        last_shot_time = 0
        while True:
            if not self._running:
                break
            mem_now = self._device.get_mem_using(current_package_name)
            cpu_use = self._device.get_cpu_using()
            current_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
            print(current_time)
            print("当前CPU总占用{}%".format(cpu_use))
            print("MEM占用：{0}MB".format(mem_now))

            self._mem_date[current_time] = mem_now  # 收集内存数据

            if self._screen_shot:
                if mem_now - last_shot_mem > self._mem_incr:
                    if (time.time() - last_shot_time) > self._shot_delay:
                        last_shot_mem = mem_now
                        last_shot_time = time.time()

                        self._device.screenshot(self._screenshot_dir, 'shot')
                    else:
                        print("距离上次截图间隔不足{0}秒".format(self._shot_delay))
            time.sleep(self._check_delay)

    def analyse(self):
        print('检测期间最高内存占用是：{0}MB'.format(max(self._mem_date.values())))


if __name__ == '__main__':
    monitor = Monitor(ADB(), False, 10, 200, 5, 20, None)
    monitor.start()
    import time
    time.sleep(20)
    monitor.shut_down()
