#!/usr/bin/env python

#----------------------------------------------
# Modification logs by Qinqin Chen on 2/22/2010
#----------------------------------------------
# self.subdev._which-->self.subdev.which()
# gr.hier_block --> gr.hier_block2
# blksimpl --> blks2impl
# delete fg
# fg.connect --> self.connect
# add gr.io_signature specifications for Input&Output
# delete "gr.hier_block.__init__(self, fg, None, None)"
# fm_preemph (self, self.gr_rate, tau)--> fm_preemph (self.gr_rate, tau)
# from gnuradio import audio_oss as audio --> from gnuradio import audio
# src = audio.source(int(32e3)) --> src = audio.source(int(32e3), audio_input)


from gnuradio import gr, blks2, optfir
#from gnuradio import usrp
from gnuradio import uhd
from gnuradio import eng_notation
#from gnuradio import audio_oss as audio
from gnuradio import audio
from gnuradio.blks2impl.fm_emph import fm_preemph
import math
import sys

class AlTransmitPath(gr.top_block): 
    def __init__(self, freq, subdev_spec, which_USRP, audio_input, debug):
        #gr.hier_block2.__init__(self, "analog_transmit_path",
        #                        gr.io_signature(0, 0, 0), #input signature
        #                        gr.io_signature(0, 0, 0)) #output signature
        
        gr.top_block.__init__(self)
        self.DEBUG = debug
        self.freq = freq
        #self.freq = 462562500
        # audio_input="hw:0"

        #Formerly from XML
        self.tx_usrp_pga_gain_scaling = 1.0
        self.tx_power = 1
        self.tx_mod_type = 'fm'
        self.tx_freq_deviation = 2.5e3
        self.tx_base_band_bw = 5e3
           
        ##################  USRP settings  ###################
        r = gr.enable_realtime_scheduling ()
        # acquire USRP via USB 2.0

        #self.u = usrp.sink_c(fusb_block_size=1024,
        #                     fusb_nblocks=4,
        #                     which=which_USRP)
	self.u = uhd.single_usrp_sink(
			device_addr="",
			io_type=uhd.io_type_t.COMPLEX_FLOAT32,
			num_channels=1,
			)
                                             
        # get D/A converter sampling rate
        #self.dac_rate = self.u.dac_rate()          #128 MS/s
        self.dac_rate = 128e6          #128 MS/s
        if self.DEBUG:
            print "    Tx Path DAC rate:      %d" %(self.dac_rate)
 
        #System digital sample rate setting
        self.audio_rate = 16e3
        self._gr_interp = 16
        self.max_gr_interp_rate = 40
        self._usrp_interp = 500
        self.gr_rate = self.dac_rate / self._usrp_interp
        self._gr_decim = 1

        if self.DEBUG:
            print "    usrp interp: ", self._usrp_interp
            print "    gr interp: ", self._gr_interp
            print "    gr rate1:  ", self.gr_rate
            print "    gr decim: ", self._gr_decim
            print "    audio rate: ", self.audio_rate

        # set USRP interplation ratio
        #self.u.set_interp_rate(self._usrp_interp)   
        self.u.set_samp_rate(self.gr_rate)

        # set USRP daughterboard subdevice
        #if subdev_spec is None:
        #    subdev_spec = usrp.pick_tx_subdevice(self.u)
        #self.u.set_mux(usrp.determine_tx_mux_value(self.u, subdev_spec))
        #self.subdev = usrp.selected_subdev(self.u, subdev_spec)
	self.u.set_antenna("TX/RX")

        #if self.DEBUG:
        #    print "    TX Path use daughterboard:  %s"    % (self.subdev.side_and_name())
       
         
        # Set center frequency of USRP
        """
        Set the center frequency we're interested in.
        Tuning is a two step process.  First we ask the front-end to
        tune as close to the desired frequency as it can.  Then we use
        the result of that operation and our target_frequency to
        determine the value for the digital up converter.
        """
        assert(self.freq != None)
        #r = self.u.tune(self.subdev.which(), self.subdev, self.freq)
        r = self.u.set_center_freq(self.freq, 0)

        if self.DEBUG:
            if r:
                print "    Tx Frequency: %s" %(eng_notation.num_to_str(self.freq))
            else:
                print "----Failed to set Tx frequency to %s" % (eng_notation.num_to_str(self.freq),)
                raise ValueError
        
            
        # Set the USRP Tx PGA gain, (Note that on the RFX cards this is a nop.)  
        # subdev.set_gain(subdev.gain_range()[1])    # set max Tx gain      
        #g = self.subdev.gain_range()
        g = self.u.get_gain_range(0)
        #_tx_usrp_gain_range = g[1]-g[0]
        _tx_usrp_gain_range = g
        #_tx_usrp_gain = g[0] + _tx_usrp_gain_range * self.tx_usrp_pga_gain_scaling
        #_tx_usrp_gain = g + _tx_usrp_gain_range * self.tx_usrp_pga_gain_scaling

        #self.subdev.set_gain(_tx_usrp_gain)        
        #self.u.set_gain(_tx_usrp_gain, 0)
        self.u.set_gain(10, 0)

        #if self.DEBUG:
        #    print "    USRP Tx PGA Gain Range: min = %g, max = %g, step size = %g" \
        #                    %(g[0], g[1], g[2])
        #    print "    USRP Tx PGA gain set to: %g" %(_tx_usrp_gain)


        # Set the transmit amplitude sent to the USRP (param: ampl 0 <= ampl < 16384.)
        """
        Convert tx_power(mW) in waveform.xml to amplitude in gnu radio
        """
        ampl= 1638.3*pow(self.tx_power, 0.5) 
        self.tx_amplitude = max(0.0, min(ampl, 16383.0))
        if self.DEBUG:
            print "tx amplitude:", self.tx_amplitude

        #gr digital amplifier
	self.tx_amplitude = 1.0
        self.gr_amp = gr.multiply_const_cc (int(self.tx_amplitude))   # software amplifier (scaler)
        print "GR amp= ", int(self.tx_amplitude)
        if self.DEBUG:
            print "    Tx power acquired from waveform configuration XML file is: %f between (0, 100.0mW)" %(self.tx_power)
            print "    Tx Path initial software signal amplitude to USRP: %f / 16383.0" %(ampl)
            print "    Tx Path actual software signal amplitude to USRP: %f / 16383.0"  %(self.tx_amplitude)
            

        ##################  Choose the corresponding analog modem ################### 
        if self.DEBUG:
            print "----Tx path modulation: %s"  % (self.tx_mod_type)


        chan_filter_coeffs_fixed = (        
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

        #chan_filter = gr.interp_fir_filter_ccf(self._gr_interp, chan_filter_coeffs_fixed)
        #chan_filter_dsp = gr.dsp_fir_ccf (chan_filter_coeffs_fixed, 14, self._gr_interp, 0, 0, 0, 1)
        #r = gr.enable_realtime_scheduling ()
        if self.DEBUG:
            print "interpolation rate = ", self._gr_interp

        # FM modulator
        k = 2 * math.pi * self.tx_freq_deviation / self.gr_rate
        
        modulator = gr.frequency_modulator_fc(k)
 
        # Pre-emphasis for FM modulation	
        """
        tau is preemphasis time constant, inverse proportional to channel bandwidth 
        """
        chan_bw = 2.0*(self.tx_base_band_bw + \
                            self.tx_freq_deviation)# Carson's rule of FM channel bandwidth 
        
        tau = 1/(chan_bw * 0.5)
        if self.DEBUG:
            print "    channel bandwidth: ", chan_bw
            print "    tau: ", tau
        preemph = fm_preemph (self.gr_rate, tau)           
       

#        audio_coeffs = (
# 0.00058729130373770002,
# 0.0016584444738215582,
# 0.0015819269921330031,
# 0.0014607862142637573,
# 0.00020681278261230754,
#-0.0013001097961560814,
#-0.00249802658603143,  
#-0.0024276134129972843,
#-0.00083069749014258953,
# 0.0017562878158492619,
# 0.003963761120687582,  
# 0.0043075911442784871,
# 0.0020710872871114866,
#-0.0020172640629268932,
#-0.005882026963765212,  
#-0.0070692053073845166,
#-0.0041954626649490937,
# 0.0019311082705710714,
# 0.0082980827342646387,
# 0.011045923787287403,  
# 0.0076530405054369872,
#-0.0012102332109476402,
#-0.011372099802214802,  
#-0.016910189774436514,  
#-0.013347352799620162,  
#-0.00068013535845177706,
# 0.015578754320259895,  
# 0.026379517186832846,  
# 0.023618496101893545,  
# 0.0051085800414948012,
#-0.022608534445133374,  
#-0.045529642916534545,  
#-0.047580556152787695,  
#-0.018048092177406189,  
# 0.042354392363985506,  
# 0.11988807809069109,  
# 0.19189052073753335,  
# 0.2351677633079737,    
# 0.2351677633079737,    
# 0.19189052073753335,  
# 0.11988807809069109,  
# 0.042354392363985506,  
#-0.018048092177406189,  
#-0.047580556152787695,  
#-0.045529642916534545,  
#-0.022608534445133374,  
# 0.0051085800414948012,
# 0.023618496101893545,  
# 0.026379517186832846,  
# 0.015578754320259895,  
#-0.00068013535845177706,
#-0.013347352799620162,  
#-0.016910189774436514,  
#-0.011372099802214802,  
#-0.0012102332109476402,
# 0.0076530405054369872,
# 0.011045923787287403,  
# 0.0082980827342646387,
# 0.0019311082705710714,
#-0.0041954626649490937,
#-0.0070692053073845166,
#-0.005882026963765212,  
#-0.0020172640629268932,
# 0.0020710872871114866,
# 0.0043075911442784871,
# 0.003963761120687582,  
# 0.0017562878158492619,
#-0.00083069749014258953,
#-0.0024276134129972843,
#-0.00249802658603143,  
#-0.0013001097961560814,
# 0.00020681278261230754,
# 0.0014607862142637573,
# 0.0015819269921330031,
# 0.0016584444738215582,
# 0.00058729130373770002)
        

        audio_coeffs = (
            -0.021392822265625,
             -0.0194091796875,                      
             0.02972412109375,                      
             -0.018341064453125,                    
             -0.025299072265625,                    
             0.07745361328125,                      
             -0.08251953125,                        
             -0.033905029296875,                    
             0.56634521484375,                      
             0.56634521484375,                      
             -0.033905029296875,                    
             -0.08251953125,                        
             0.07745361328125,                      
             -0.025299072265625,                    
             -0.018341064453125,                    
             0.02972412109375,                      
             -0.0194091796875,                      
             -0.021392822265625) 

        #audio_coeffs = (
        #    -0.21392822265625,
        #     -0.194091796875,                      
        #     0.2972412109375,                      
        #     -0.18341064453125,                    
        #     -0.25299072265625,                    
        #     0.7745361328125,                      
        #     -0.8251953125,                        
        #     -0.33905029296875,                    
        #     5.6634521484375,                      
        #     5.6634521484375,                      
        #     -0.33905029296875,                    
        #     -0.8251953125,                        
        #     0.7745361328125,                      
        #     -0.25299072265625,                    
        #     -0.18341064453125,                    
        #     0.2972412109375,                      
        #     -0.194091796875,                      
        #     -0.21392822265625) 
        self.audio_filter = gr.interp_fir_filter_fff(self._gr_interp, audio_coeffs)
 
        #Source audio Low-pass Filter
        #self.audio_throt = gr.multiply_const_ff(50)
        self.audio_throt = gr.multiply_const_ff(5)

        if self.DEBUG:
            print "audio decim FIR filter tap length:", len(audio_coeffs)
     
        # Setup audio source 
        src = audio.source(int(self.audio_rate), audio_input)
            
        # Wiring up
        #self.connect(src, self.audio_throt, interpolator, preemph, modulator, chan_filter_dsp, self.gr_amp, self.u)
        

        self.connect(src, self.audio_throt, self.audio_filter, modulator, self.gr_amp, self.u)
        #self.connect(src, self.audio_throt, self.audio_filter, modulator, self.gr_amp, self.u)
        

        #self.connect(src, self.audio_throt, self.audio_filter, preemph, modulator, chan_filter_dsp, self.gr_amp, self.u)
        #self.connect(src, self.audio_throt, preemph, howto_tx, modulator, self.gr_amp, self.u)
        
        #self.connect(src, self.audio_throt, interpolator, preemph, modulator, self.gr_amp, self.u)
             

    def pick_interp_rate(self):
        for i in range(412, 3, -1):
            for j in range(1, self.max_gr_interp_rate+1):
     	        #print "\nUSRP ", i, "\nGR ", j, "mult ", int(64e6/i/j)
     	        if(int(self.dac_rate/i/j) == self.audio_rate): return i, j   
   

    # def set_freq(self, target_freq):
    #     self.freq = target_freq
    #     #r = self.u.tune(0, self.subdev, target_freq)
    #     #if r:
    #     #    return True

    #     return False

    def set_enable(self, enable):
        ''' Set H/w TX enable. '''
	print "Legacy Function"
        #self.subdev.set_enable(enable)


    def tx_throt(self, throt):
        """
        analog_tx_path standard API function for Tx control
        @param throt = 1 or 0 (integer)
        """
        #self.audio_throt.set_k(throt)
        #self.gr_amp.set_k(int(throt * self.tx_amplitude)) 
              
            
#if __name__ == '__main__':
 #   fg = analog_transmit_path ()
 #   fg.start()
  #  raw_input ('Press Enter to quit: ')
   # fg.stop()
    #fg.wait()
if __name__ == '__main__':
    tb = AlTransmitPath(462562500, "", "", "plughw:0,0", 0)
    try:
        tb.run()
    except KeyboardInterrupt:
        pass
