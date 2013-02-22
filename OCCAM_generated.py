#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
# Generated: Fri Feb 22 18:12:10 2013
##################################################

from gnuradio import audio
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
		self.samplingRate2 = samplingRate2 = 256000
		self.samplingRate = samplingRate = 32000
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
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr="",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samplingRate2)
		self.uhd_usrp_source_0.set_center_freq(462562500, 0)
		self.uhd_usrp_source_0.set_gain(25, 0)
		self.dbpskDemod = digital.dbpsk_demod(
			samples_per_symbol=samplingRate2/samplingRate,
			excess_bw=0.35,
			freq_bw=6.28/100.0,
			phase_bw=6.28/100.0,
			timing_bw=6.28/100.0,
			gray_coded=True,
			verbose=False,
			log=False
		)
		self.dbpskDec = grc_blks2.packet_demod_f(grc_blks2.packet_decoder(
				access_code="",
				threshold=-1,
				callback=lambda ok, payload: self.dbpskDec.recv_pkt(ok, payload),
			),
		)
		self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((3, ))
		self.audio_sink_0 = audio.sink(samplingRate, "plughw:1,0", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.dbpskDemod, 0), (self.dbpskDec, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
		self.connect((self.blocks_multiply_const_vxx_0, 0), (self.dbpskDemod, 0))
		self.connect((self.dbpskDec, 0), (self.audio_sink_0, 0))
		self.connect((self.dbpskDec, 0), (self.audio_sink_0, 1))


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
		self.uhd_usrp_source_0.set_samp_rate(self.samplingRate2)

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

