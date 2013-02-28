#!/usr/bin/env python

#----------------------------------------------
# Modification logs by Qinqin Chen on 2/15/2010
#----------------------------------------------
# gr.hier_block --> gr.hier_block2
# blksimpl --> blks2impl
# delete fg
# fg.connect --> self.connect
# add gr.io_signature specifications for Input&Output
# delete "gr.hier_block.__init__(self, fg, None, None)"
# fm_deemph (self, self.audio_rate) --> fm_deemph (self.audio_rate)
# from gnuradio import audio_oss as audio --> from gnuradio import audio

from gnuradio import gr, gru, blks2, eng_notation, optfir, dsp
#from gnuradio import audio_oss as audio
from gnuradio import audio
#from gnuradio import usrp
from gnuradio import uhd
from gnuradio.eng_option import eng_option

#from gnuradio_swig_python import single_threaded_scheduler, sts_pyrun

from gnuradio.blks2impl.fm_emph import fm_deemph
# from gnuradio.blks2impl.standard_squelch import standard_squelch

import sys
import math

class AlReceivePath(gr.hier_block2):
    def __init__(self, freq, subdev_spec, which_USRP, gain, audio_output, debug):
        gr.hier_block2.__init__(self, "analog_receive_path",
                                gr.io_signature(0, 0, 0), #input signature
                                gr.io_signature(0, 0, 0)) #output signature
        
        self.DEBUG = debug
        self.freq = freq
        self.rx_gain = gain

        #Formerly From XML
        self.fusb_block_size = 2048
        self.fusb_nblocks = 8
        self.rx_usrp_pga_gain_scaling = 0.5
        self.rx_base_band_bw = 5e3
        self.rx_freq_deviation = 2.5e3


              
        # acquire USRP via USB 2.0
        #self.u = usrp.source_c(fusb_block_size=self.fusb_block_size,
        #                       fusb_nblocks=self.fusb_nblocks,
        #                       which=which_USRP)
	self.u = uhd.single_usrp_source(
			device_addr="",
			io_type=uhd.io_type_t.COMPLEX_FLOAT32,
			num_channels=1,
			)
        self.u.get_device
        # get A/D converter sampling rate 
        #adc_rate = self.u.adc_rate()      # 64 MS/s
        adc_rate = 64e6      # 64 MS/s
        if self.DEBUG:
            print "    Rx Path ADC rate:      %d" %(adc_rate)

        # setting USRP and GNU Radio decimation rate
        self.audio_rate = 16e3
        self.max_gr_decim_rate = 40

        self._usrp_decim = 250
        self.gr_rate1 = adc_rate / self._usrp_decim
        gr_interp = 1
        gr_decim  = 16
        self.gr_rate2 = self.gr_rate1 / gr_decim
            

        if self.DEBUG:
            print "    usrp decim: ", self._usrp_decim
            print "    gr rate 1:  ", self.gr_rate1
            print "    gr decim: ", gr_decim
            print "    gr rate 2: ", self.gr_rate2
            print "    gr interp: ", gr_interp 
            print "    audio rate: ", self.audio_rate

      
        # ================  Set up flowgraph  =================================
              
        # set USRP decimation ratio
        #self.u.set_decim_rate(self._usrp_decim)
	self.u.set_samp_rate(self.gr_rate1)
	self.u.set_antenna("RX2")
        

        # set USRP daughterboard subdevice
        if subdev_spec is None:
           subdev_spec = usrp.pick_rx_subdevice(self.u)	
        #self.u.set_mux(usrp.determine_rx_mux_value(self.u, subdev_spec))
        #self.subdev = usrp.selected_subdev(self.u, subdev_spec)
        #if self.DEBUG:
        #    print "    RX Path use daughterboard:  %s"    % (self.subdev.side_and_name())


        # set USRP RF frequency
        """
        Set the center frequency in Hz.
        Tuning is a two step process.  First we ask the front-end to
        tune as close to the desired frequency as it can.  Then we use
        the result of that operation and our target_frequency to
        determine the value for the digital up converter.
        """
        assert(self.freq != None)
        #r = self.u.tune(0, self.subdev, self.freq)
        r = self.u.set_center_freq(self.freq, 0)
        if self.DEBUG:
            if r:
                print "----Rx RF frequency set to %f Hz" %(self.freq)
            else:
                print "Failed to set Rx frequency to %f Hz" %(self.freq)
                raise ValueError, eng_notation.num_to_str(self.freq)
        


        # set USRP Rx PGA gain   
        #r = self.subdev.gain_range()
        #_rx_usrp_gain_range = r[1] - r[0]          
        #_rx_usrp_gain = r[0]+_rx_usrp_gain_range * self.rx_usrp_pga_gain_scaling
        #self.subdev.set_gain(_rx_usrp_gain)
	#self.u.set_gain(3.25, 0)
        #if self.DEBUG:
        #    print "    USRP Rx PGA Gain Range: min = %g, max = %g, step size = %g" \
        #            %(r[0], r[1], r[2])
        #    print "    USRP Rx PGA gain set to: %g" %(_rx_usrp_gain)        

        # Do NOT Enable USRP Auto Tx/Rx switching for analog flow graph!
        #self.subdev.set_enable(False)     


        # Baseband Channel Filter using FM Carson's Rule
        chan_bw = 2*(self.rx_base_band_bw+self.rx_freq_deviation)     #Carson's Rule
        chan_filt_coeffs_float = optfir.low_pass (1,                        #gain
                                            self.gr_rate1,             #sampling rate
                                            chan_bw,              #passband cutoff
                                            chan_bw*1.35,              #stopband cutoff
                                            0.1,                      #passband ripple
                                            60)                       #stopband attenuation
        chan_filt_coeffs_fixed = (
            0.000457763671875,
            0.000946044921875,                     
            0.00067138671875,                    
            0.001068115234375,
            0.00091552734375,                    
            0.0008544921875,                       
            0.000518798828125,                     
            0.0001220703125,                      
            -0.000396728515625,                     
            -0.0008544921875,                       
            -0.00128173828125,                      
            -0.00146484375,                         
            -0.001434326171875,                     
            -0.0010986328125,                       
            -0.000518798828125,                     
            0.000274658203125,                     
            0.001129150390625,                     
            0.00189208984375,                      
            0.00238037109375,                      
            0.00250244140625,                      
            0.002166748046875,                     
            0.0013427734375,                       
            0.000152587890625,                     
            -0.001220703125,                        
            -0.002532958984375,                     
            -0.0035400390625,                       
            -0.003997802734375,                     
            -0.003753662109375,                     
            -0.002777099609375,                     
            -0.0010986328125,                       
            0.000946044921875,                     
            0.00311279296875,                      
            0.00494384765625,                      
            0.00604248046875,                      
            0.006103515625,                        
            0.005035400390625,                     
            0.00286865234375,                      
            -0.0001220703125,                       
            -0.00347900390625,                      
            -0.006561279296875,                     
            -0.008758544921875,                     
            -0.00958251953125,                     
            -0.008636474609375,                     
            -0.005950927734375,                     
            -0.001739501953125,                     
            0.00335693359375,                      
            0.00848388671875,                      
            0.0126953125,                          
            0.01507568359375,                      
            0.014862060546875,                     
            0.01171875,                            
            0.00579833984375,
            -0.002227783203125,                    
            -0.01123046875,                        
            -0.0196533203125,                       
            -0.02587890625,                         
            -0.028228759765625,                     
            -0.025421142578125,                     
            -0.016754150390625,                     
            -0.002166748046875,                     
            0.017608642578125,                     
            0.041015625,                           
            0.0660400390625,
            0.090240478515625,
            0.111083984375,                        
            0.12640380859375,                      
            0.134490966796875,                     
            0.134490966796875,                     
            0.12640380859375,                     
            0.111083984375,                     
            0.090240478515625,                     
            0.0660400390625,                       
            0.041015625,                           
            0.017608642578125,
            -0.002166748046875,                     
            -0.016754150390625,                     
            -0.025421142578125,                     
            -0.028228759765625,                     
            -0.02587890625,                     
            -0.0196533203125,
            -0.01123046875,                         
            -0.002227783203125,
            0.00579833984375,                      
            0.01171875,                            
            0.014862060546875,
            0.01507568359375,                      
            0.0126953125,                          
            0.00848388671875,                      
            0.00335693359375,                     
            -0.001739501953125,                     
            -0.005950927734375,                    
            -0.008636474609375,                     
            -0.00958251953125,                      
            -0.008758544921875,                     
            -0.006561279296875,                     
            -0.00347900390625,                      
            -0.0001220703125,                       
            0.00286865234375,                      
            0.005035400390625,                     
            0.006103515625,                        
            0.00604248046875,                      
            0.00494384765625,                      
            0.00311279296875,                      
            0.000946044921875,                     
            -0.0010986328125,                       
            -0.002777099609375,                     
            -0.003753662109375,                     
            -0.003997802734375,                     
            -0.0035400390625,                       
            -0.002532958984375,                     
            -0.001220703125,                        
            0.000152587890625,                     
            0.0013427734375,                       
            0.002166748046875,                    
            0.00250244140625,                     
            0.00238037109375,                      
            0.00189208984375,                      
            0.001129150390625,                     
            0.000274658203125,                     
            -0.000518798828125,                     
            -0.0010986328125,                       
            -0.001434326171875,                     
            -0.00146484375,                         
            -0.00128173828125,                      
            -0.0008544921875,                       
            -0.000396728515625,                     
            0.0001220703125,                       
            0.000518798828125,                    
            0.0008544921875,                       
            0.00091552734375,                      
            0.001068115234375,                     
            0.00067138671875,                      
            0.000946044921875,                     
            0.000457763671875)

        #r = gr.enable_realtime_scheduling ()
        self.chan_filt = dsp.fir_ccf_fm_demod_decim (chan_filt_coeffs_fixed, 14, gr_decim, 0, 0, 0, 0)
        print "Tap length of chan FIR: ", len(chan_filt_coeffs_fixed)


        # Set the software LNA gain on the output of the USRP       
        gain= self.rx_gain
        self.rx_gain = max(0.0, min(gain, 1e7))        

        if self.DEBUG:
            print "    Rx Path initial software signal gain: %f (max 1e7)" %(gain)
            print "    Rx Path actual software signal gain : %f (max 1e7)" %(self.rx_gain)        

        #FM Demodulator
        fm_demod_gain = self.audio_rate / (2*math.pi*self.rx_freq_deviation)
        self.fm_demod = gr.quadrature_demod_cf (fm_demod_gain)        


        #Compute FIR filter taps for audio filter
        width_of_transition_band = self.rx_base_band_bw * 0.35
        audio_coeffs = gr.firdes.low_pass (1.0,                  #gain
                                           self.gr_rate2,      #sampling rate
                                           self.rx_base_band_bw,
                                           width_of_transition_band,
                                           gr.firdes.WIN_HAMMING)
        

        self.audio_filter = gr.fir_filter_fff(1, audio_coeffs)
        passband_cutoff = self.rx_base_band_bw        
        stopband_cutoff = passband_cutoff * 1.35
 
        self.deemph = fm_deemph(self.audio_rate)

        if self.DEBUG:
            print "Length Audio FIR ", len(audio_coeffs)
        # Audio sink

        audio_sink = audio.sink(int(self.audio_rate),"default")
        #                         "",     #Audio output pcm device name.  E.g., hw:0,0 or surround51 or /dev/dsp
        #                         False)  # ok_to_block
        
        if self.DEBUG:
            print "Before Connecting Blocks"
        # Wiring Up
        #WITH CHANNEL FILTER
        #self.connect (self.u, self.chan_filt, self.lna, self.fm_demod, self.audio_filter, interpolator, self.deemph, self.volume_control, audio_sink)     

        #self.connect (self.u, self.fm_demod, self.audio_filter, self.deemph, self.volume_control, howto_rx, audio_sink)     
        self.connect (self.u, self.chan_filt, self.audio_filter, self.deemph, audio_sink)     
        
        
        #WITHOUT CHANNEL FILTER
        #self.connect (self.u, self.lna, self.fm_demod, self.audio_filter, self.deemph, self.volume_control, audio_sink)     


    def pick_decim_rate(self):
        for i in range(256, 3, -1):
            for j in range(1, self.max_gr_decim_rate+1):
     	        #print "\nUSRP ", i, "\nGR ", j, "mult ", int(64e6/i/j)
     	        if(int(64e6/i/j) == self.audio_rate): return i, j


    # def set_freq(self, target_freq):
    #     self.freq = target_freq
    #     #r = self.u.tune(0, self.subdev, target_freq)
    #     #if r:
    #     #    return True

    #     return False

    def set_gain(self, gain):
        self.gain = gain
        #self.subdev.set_gain(gain)
	self.u.set_gain(gain)

    def set_enable(self, enable):
        self.enabled = enable

    def rx_throt(self, throt):
        """
        analog receive path standard API function for Rx control
        @param throt = 1 or 0 (integer)
        """           
        #self.lna.set_k(self.options.waveform.Rx.PHY.rf.rx_gain * throt)
        #self.volume_control.set_k(throt * self.options.platform.SINK.volume) 


#if __name__ == '__main__':
#    tb = analog_receive_path()
#    try:
#        #tb.start()
#        tb.run()
#    except KeyboardInterrupt:
#        pass


