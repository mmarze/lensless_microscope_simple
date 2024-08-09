"""
MIT License

Copyright (c) 2024 Marcin J Marzejon
e-mail: marcin.marzejon@pw.edu.pl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from kdc101_kinesis_thorlabs import *
from cam_IDS_U338JxXLEM import *
import time


if __name__ == '__main__':

    # STEPPER MOTOR - positions
    step = 0.8/1000
    N = 31
    SM_init_pos = 0.0

    try:
        # DEVICES INIT
        # # camera
        # MyCamId, MyCamAllMode = parse_args()
        # print(get_frame_rate_(MyCamId))

        # stepper motor
        MyStage = kdc101_create_dev('27601295')
        kdc101_init(MyStage, '27601295', homing=True, settings_name='MTS25/M-Z8')
        kdc101_move_to_abs_pos(MyStage, SM_init_pos, True)
        kdc101_get_curr_pos(MyStage, True)
        time.sleep(1)

        # FOR LOOP - EXPERIMENT
        for i in range(N):
            kdc101_move_to_rel_pos(MyStage, step, True)
            kdc101_get_curr_pos(MyStage, True)
            time.sleep(1)
            # save_frame_(MyCamId)
                # CODE HERE!!!!

        # CLOSE DEVICES -----------------------------
        kdc101_close(MyStage)

    except Exception as ex:
        print(f"An error occurred!!: {ex}")
    finally:
        kdc101_close(MyStage)
