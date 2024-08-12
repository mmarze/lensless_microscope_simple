"""
MIT License

Copyright (c) 2024 Marcin J Marzejon
e-mail: marcin.marzejon@pw.edu.pl
Based on :https://www.1stvision.com/cameras/IDS/IDS-manuals/en/program-start-acquisition.html

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

import ids_peak.ids_peak as ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import ids_peak.ids_peak_ipl_extension as ids_ipl_extension
import sys
from datetime import datetime


def open_camera():
    try:
        # Create a DeviceManager object
        device_manager = ids_peak.DeviceManager.Instance()
        # Update the DeviceManager
        device_manager.Update()
            
        # Exit if no device was found
        if device_manager.Devices().empty():
            print("\n\tNo device found. Exiting Program.\n")
            sys.exit(-1)
        else:
            print("Found Devices: " + str(len(device_manager.Devices())))
            # for elem in device_manager.Devices():
            #     print(elem.DisplayName())
        
        # Open the first device
        device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)
        print('\nOpened Device: ' + device.DisplayName() + '\n')
            
        # Get the node_map of the RemoteDevice
        remote_device_node_map = device.RemoteDevice().NodeMaps()[0]
        
        return True, device, remote_device_node_map
    except Exception as e:
        print("\nEXCEPTION: " + str(e))
    

def set_default_parameters(remote_device_node_map):
    # set ReverseX to false
    remote_device_node_map.FindNode("ReverseX").SetValue(False)
    # set ReverseY to false
    remote_device_node_map.FindNode("ReverseY").SetValue(False)
    
    # set BinningVertical to 1 (no binning)
    remote_device_node_map.FindNode("BinningVertical").SetValue(1)
    # set BinningHorizontal to 1 (no binning)
    remote_device_node_map.FindNode("BinningHorizontal").SetValue(1)
    
    # Determine the current entry of PixelFormat - 'Mono10g40IDS' or 'Mono12g24IDS'
    remote_device_node_map.FindNode("PixelFormat").SetCurrentEntry("Mono12g24IDS")
        

def get_exposure_params(remote_device_node_map):
    # exposure time - get settings
    min_exposure_time = -1
    max_exposure_time = -1
    inc_exposure_time = -1

    # Get exposure range. All values in microseconds
    min_exposure_time = remote_device_node_map.FindNode("ExposureTime").Minimum()
    max_exposure_time = remote_device_node_map.FindNode("ExposureTime").Maximum()

    if remote_device_node_map.FindNode("ExposureTime").HasConstantIncrement():
        inc_exposure_time = remote_device_node_map.FindNode("ExposureTime").Increment()
        
    return min_exposure_time, max_exposure_time, inc_exposure_time


def get_exposure_time(remote_device_node_map):
    return remote_device_node_map.FindNode("ExposureTime").Value()


def set_exposure_time(remote_device_node_map, exposure_time):
    remote_device_node_map.FindNode("ExposureTime").SetValue(exposure_time)
    print(f"Exposure time set to {get_exposure_time(remote_device_node_map)}")


def get_gain(remote_device_node_map):
    # Set GainSelector to "AnalogAll" (str)
    remote_device_node_map.FindNode("GainSelector").SetCurrentEntry("AnalogAll")
    return remote_device_node_map.FindNode("Gain").Value()


def set_gain(remote_device_node_map, gain_val):
    # Set GainSelector to "AnalogAll" (str)
    remote_device_node_map.FindNode("GainSelector").SetCurrentEntry("AnalogAll")
    remote_device_node_map.FindNode("Gain").SetValue(gain_val)
    print(f'Gain set to {get_gain(remote_device_node_map)}')
    

def set_adc_gain_correction(remote_device_node_map, value):
    # Set GainSelector to "AnalogAll" (str)
    remote_device_node_map.FindNode("GainSelector").SetCurrentEntry("AnalogAll")
    # Set ADCGainCorrection value (bool)
    remote_device_node_map.FindNode("ADCGainCorrection").SetValue(value)


def get_fps(remote_device_node_map):
    # Determine the current AcquisitionFrameRate (float)
    return remote_device_node_map.FindNode("AcquisitionFrameRate").Value()


def set_fps(remote_device_node_map, fps_value):
    remote_device_node_map.FindNode("AcquisitionFrameRate").SetValue(fps_value)
    print(f'FPS set to {get_fps(remote_device_node_map)}')


def set_trigger_parameters(remote_device_node_map):
    remote_device_node_map.FindNode("TriggerSelector").SetCurrentEntry("ReadOutStart")
    remote_device_node_map.FindNode("TriggerSource").SetCurrentEntry("Software")
    remote_device_node_map.FindNode("TriggerMode").SetCurrentEntry("On")
   

def prepare_acquisition(device):
    try:
        data_streams = device.DataStreams()
        if data_streams.empty():
            print('ERROR! No data streams available!')
            return False, None
        data_stream = device.DataStreams()[0].OpenDataStream()
        return True, data_stream
    except Exception as e:
        print("\nEXCEPTION: " + str(e))
        return False, None


def alloc_and_announce_buffers(data_stream, remote_device_node_map):
    try:
        # Flush queue and prepare all buffers for revoking
        data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
        # Clear all old buffers
        for buffer in data_stream.AnnouncedBuffers():
            data_stream.RevokeBuffer(buffer)

        payload_size = remote_device_node_map.FindNode("PayloadSize").Value()

        # Get number of minimum required buffers
        num_buffers_min_required = data_stream.NumBuffersAnnouncedMinRequired()
                
        # Alloc buffers
        for count in range(num_buffers_min_required):
            buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
            data_stream.QueueBuffer(buffer)
        return True
    except Exception as e:
        print("\nEXCEPTION: " + str(e))
        return False


def start_acquisition(data_stream, remote_device_node_map):
    try:
        data_stream.StartAcquisition()
        # (ids_peak.AcquisitionStartMode_Default, ids_peak.data_stream.INFINITE_NUMBER)
        remote_device_node_map.FindNode("TLParamsLocked").SetValue(1)
        remote_device_node_map.FindNode("AcquisitionStart").Execute()
        remote_device_node_map.FindNode("AcquisitionStart").WaitUntilDone()
        return True
    except Exception as e:
        print("\nEXCEPTION: " + str(e))
        return False


def acquire_and_save(remote_device_node_map, data_stream):
    try:
        remote_device_node_map.FindNode("TriggerSoftware").Execute()
        buffer = data_stream.WaitForFinishedBuffer(2000)
        # convert to Mono image
        raw_image = ids_ipl_extension.BufferToImage(buffer)
        mono_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_Mono12)
        data_stream.QueueBuffer(buffer)
        filename = "C:\\Users\\marcinmarzejon\\" + str(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")) + ".png"
        ids_ipl.ImageWriter.Write(filename, mono_image)
        return True
    except Exception as e:
        print("\nEXCEPTION: " + str(e))
        return False


def main():
    # init library
    ids_peak.Library.Initialize()
    # # Create a DeviceManager object
    # device_manager = ids_peak.DeviceManager.Instance()
    
    try:
        # open camera
        status, my_device, my_remote_device_node_map = open_camera()
        
        # set default parameters - binning, flipping etc
        set_default_parameters(my_remote_device_node_map)
        
        # get exposure time
        print(f'Exposure time: {get_exposure_time(my_remote_device_node_map)}')
        # set exposure time
        # set_exposure_time(my_remote_device_node_map, 6000)
        
        # ADC Gain Correction
        set_adc_gain_correction(my_remote_device_node_map, True)
        # get gain value
        print(f'Gain: {get_gain(my_remote_device_node_map)}')
        # set gain to 1.0
        # set_gain(my_remote_device_node_map, 1.0)
        
        # get fps
        print(f'FPS: {get_fps(my_remote_device_node_map)}')
        # set fps
        # set_fps(my_remote_device_nod_emap, 11.0)
        
        # set Trigger parameters
        set_trigger_parameters(my_remote_device_node_map)
        
        status, my_data_stream = prepare_acquisition(my_device)
        if not status:
            sys.exit(-2)
        
        if not alloc_and_announce_buffers(my_data_stream, my_remote_device_node_map):
            sys.exit(-3)
        
        # start acquisition    
        if not start_acquisition(my_data_stream, my_remote_device_node_map):
            sys.exit(-4)
        
        # # acquire and save an image
        if not acquire_and_save(my_remote_device_node_map, my_data_stream):
            sys.exit(-5)
               
        # close device
        my_device = None
        del my_device

    except Exception as e:
        print("\nEXCEPTION: " + str(e))
        return -2
    finally:
        ids_peak.Library.Close()

        
if __name__ == '__main__':
    main()
