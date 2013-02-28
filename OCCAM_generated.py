#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
# Generated: Thu Feb 28 18:44:59 2013
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
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
		self.samplingRate2 = samplingRate2 = 2000000
		self.samplingRate = samplingRate = 320000
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
		self.uhd_usrp_sink_0 = uhd.usrp_sink(
			device_addr="",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_sink_0.set_subdev_spec("A:0", 0)
		self.uhd_usrp_sink_0.set_samp_rate(samplingRate2)
		self.uhd_usrp_sink_0.set_center_freq(462562500, 0)
		self.uhd_usrp_sink_0.set_gain(0, 0)
		self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
		self.rfScale_0 = blocks.multiply_const_vff((10, ))
		self.rfScale = blocks.multiply_const_vcc((0.3, ))
		self.gr_file_source_0 = gr.file_source(gr.sizeof_float*1, "/home/alfayez/workspace/occam-research/music-tx.dat", True)
		self.dbpskMod = digital.dbpsk_mod(
			samples_per_symbol=samplingRate2/samplingRate,
			excess_bw=0.35,
			gray_coded=True,
			verbose=False,
			log=False)
			
		self.dbpskEnc = grc_blks2.packet_mod_f(grc_blks2.packet_encoder(
				samples_per_symbol=10,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=True,
			),
			payload_length=0,
		)

		##################################################
		# Connections
		##################################################
		self.connect((self.dbpskEnc, 0), (self.dbpskMod, 0))
		self.connect((self.rfScale, 0), (self.uhd_usrp_sink_0, 0))
		self.connect((self.dbpskMod, 0), (self.rfScale, 0))
		self.connect((self.rfScale_0, 0), (self.dbpskEnc, 0))
		self.connect((self.gr_file_source_0, 0), (self.rfScale_0, 0))


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

