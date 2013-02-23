#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
<<<<<<< HEAD
# Generated: Fri Feb 22 19:40:57 2013
=======
# Generated: Fri Feb 22 19:47:27 2013
>>>>>>> fbf9684b95c9db76c1f65b625fa8d8a89c533473
##################################################

from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import scopesink2
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class OCCAM_generated(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Occam Generated")
		_icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Variables
		##################################################
		self.symbolTime = symbolTime = 2
		self.stdValG = stdValG = 0.40
		self.seedValG = seedValG = 0L
		self.samplingRate2 = samplingRate2 = 256000
		self.samplingRate = samplingRate = 48000
		self.rfGain2 = rfGain2 = 1.0
		self.rfGain = rfGain = 30.0
		self.recvThresh = recvThresh = 0.3
		self.rcFiltCoeff = rcFiltCoeff = 1.0
		self.meanValG = meanValG = 0.0
		self.gaussGain = gaussGain = 0.3
		self.carrierPhase = carrierPhase = 0.0
		self.carrierGain = carrierGain = 1.0
		self.carrierFreq = carrierFreq = 4.0

		##################################################
		# Blocks
		##################################################
		self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
			self.GetWin(),
			title="Scope Plot",
			sample_rate=samplingRate,
			v_scale=0,
			v_offset=0,
			t_scale=0,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.Add(self.wxgui_scopesink2_0.win)
		self.uhd_usrp_sink_0 = uhd.usrp_sink(
			device_addr="",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_sink_0.set_samp_rate(samplingRate2)
		self.uhd_usrp_sink_0.set_center_freq(462562500, 0)
		self.uhd_usrp_sink_0.set_gain(3, 0)
		self.rfScale_0 = blocks.multiply_const_vff((500, ))
		self.rfScale = blocks.multiply_const_vcc((0.2, ))
		self.dbpskMod = digital.dbpsk_mod(
			samples_per_symbol=samplingRate2/samplingRate,
			excess_bw=0.35,
			gray_coded=True,
			verbose=False,
			log=False)
			
		self.dbpskEnc = grc_blks2.packet_mod_f(grc_blks2.packet_encoder(
				samples_per_symbol=1,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=True,
			),
			payload_length=0,
		)
<<<<<<< HEAD
		self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((1, ))
		self.audio_sink_0 = audio.sink(samplingRate, "", True)
=======
		self.audio_source_0 = audio.source(samplingRate, "", True)
>>>>>>> fbf9684b95c9db76c1f65b625fa8d8a89c533473

		##################################################
		# Connections
		##################################################
<<<<<<< HEAD
		self.connect((self.dbpskDemod, 0), (self.dbpskDec, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
		self.connect((self.blocks_multiply_const_vxx_0, 0), (self.dbpskDemod, 0))
		self.connect((self.dbpskDec, 0), (self.audio_sink_0, 0))
=======
		self.connect((self.dbpskEnc, 0), (self.dbpskMod, 0))
		self.connect((self.rfScale, 0), (self.uhd_usrp_sink_0, 0))
		self.connect((self.dbpskMod, 0), (self.rfScale, 0))
		self.connect((self.rfScale_0, 0), (self.dbpskEnc, 0))
		self.connect((self.audio_source_0, 0), (self.rfScale_0, 0))
		self.connect((self.rfScale_0, 0), (self.wxgui_scopesink2_0, 0))
>>>>>>> fbf9684b95c9db76c1f65b625fa8d8a89c533473


	def get_symbolTime(self):
		return self.symbolTime

	def set_symbolTime(self, symbolTime):
		self.symbolTime = symbolTime

	def get_stdValG(self):
		return self.stdValG

	def set_stdValG(self, stdValG):
		self.stdValG = stdValG

	def get_seedValG(self):
		return self.seedValG

	def set_seedValG(self, seedValG):
		self.seedValG = seedValG

	def get_samplingRate2(self):
		return self.samplingRate2

	def set_samplingRate2(self, samplingRate2):
		self.samplingRate2 = samplingRate2
		self.uhd_usrp_sink_0.set_samp_rate(self.samplingRate2)

	def get_samplingRate(self):
		return self.samplingRate

	def set_samplingRate(self, samplingRate):
		self.samplingRate = samplingRate
		self.wxgui_scopesink2_0.set_sample_rate(self.samplingRate)

	def get_rfGain2(self):
		return self.rfGain2

	def set_rfGain2(self, rfGain2):
		self.rfGain2 = rfGain2

	def get_rfGain(self):
		return self.rfGain

	def set_rfGain(self, rfGain):
		self.rfGain = rfGain

	def get_recvThresh(self):
		return self.recvThresh

	def set_recvThresh(self, recvThresh):
		self.recvThresh = recvThresh

	def get_rcFiltCoeff(self):
		return self.rcFiltCoeff

	def set_rcFiltCoeff(self, rcFiltCoeff):
		self.rcFiltCoeff = rcFiltCoeff

	def get_meanValG(self):
		return self.meanValG

	def set_meanValG(self, meanValG):
		self.meanValG = meanValG

	def get_gaussGain(self):
		return self.gaussGain

	def set_gaussGain(self, gaussGain):
		self.gaussGain = gaussGain

	def get_carrierPhase(self):
		return self.carrierPhase

	def set_carrierPhase(self, carrierPhase):
		self.carrierPhase = carrierPhase

	def get_carrierGain(self):
		return self.carrierGain

	def set_carrierGain(self, carrierGain):
		self.carrierGain = carrierGain

	def get_carrierFreq(self):
		return self.carrierFreq

	def set_carrierFreq(self, carrierFreq):
		self.carrierFreq = carrierFreq

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = OCCAM_generated()
	tb.Run(True)

