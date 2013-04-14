#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
# Generated: Sun Apr 14 14:50:35 2013
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
		self.stdValG = stdValG = 0.40
		self.seedValG = seedValG = 0L
		self.samplingRate2 = samplingRate2 = 640000
		self.samplingRate = samplingRate = 320000
		self.rfGain2 = rfGain2 = 25.0
		self.rfGain = rfGain = 0.2
		self.recvThresh = recvThresh = 0.3
		self.rcFiltCoeff = rcFiltCoeff = 1.0
		self.meanValG = meanValG = 0.0
		self.gaussGain = gaussGain = 0.3
		self.excessBw = excessBw = 0.35
		self.dataName = dataName = 1.0
		self.dataGain = dataGain = 10.0
		self.carrierFreq = carrierFreq = 462562500.0
		self.bbGain2 = bbGain2 = 1.0
		self.bbGain = bbGain = 0.5

		##################################################
		# Blocks
		##################################################
		self.rfOut = uhd.usrp_sink(
			device_addr="",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.rfOut.set_subdev_spec("A:0", 0)
		self.rfOut.set_samp_rate(samplingRate2)
		self.rfOut.set_center_freq(carrierFreq, 0)
		self.rfOut.set_gain(rfGain, 0)
		self.rfOut.set_antenna("TX/RX", 0)
		self.dbpskMod = digital.dbpsk_mod(
			samples_per_symbol=samplingRate2/samplingRate,
			excess_bw=0.35,
			gray_coded=True,
			verbose=False,
			log=False)
			
		self.dbpskEnc = grc_blks2.packet_mod_f(grc_blks2.packet_encoder(
				samples_per_symbol=samplingRate2/samplingRate,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=False,
			),
			payload_length=0,
		)
		self.dataSrc = gr.file_source(gr.sizeof_float*1, "music-tx1.0.dat", False)
		self.channelFilter = blocks.multiply_const_vcc((1.0, ))
		self.basebandScale = blocks.multiply_const_vcc((bbGain, ))

		##################################################
		# Connections
		##################################################
		self.connect((self.dbpskMod, 0), (self.channelFilter, 0))
		self.connect((self.basebandScale, 0), (self.rfOut, 0))
		self.connect((self.dataSrc, 0), (self.dbpskEnc, 0))
		self.connect((self.dbpskEnc, 0), (self.dbpskMod, 0))
		self.connect((self.channelFilter, 0), (self.basebandScale, 0))


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
		self.rfOut.set_samp_rate(self.samplingRate2)

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
		self.rfOut.set_gain(self.rfGain, 0)

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

	def get_excessBw(self):
		return self.excessBw

	def set_excessBw(self, excessBw):
		self.excessBw = excessBw

	def get_dataName(self):
		return self.dataName

	def set_dataName(self, dataName):
		self.dataName = dataName

	def get_dataGain(self):
		return self.dataGain

	def set_dataGain(self, dataGain):
		self.dataGain = dataGain

	def get_carrierFreq(self):
		return self.carrierFreq

	def set_carrierFreq(self, carrierFreq):
		self.carrierFreq = carrierFreq
		self.rfOut.set_center_freq(self.carrierFreq, 0)

	def get_bbGain2(self):
		return self.bbGain2

	def set_bbGain2(self, bbGain2):
		self.bbGain2 = bbGain2

	def get_bbGain(self):
		return self.bbGain

	def set_bbGain(self, bbGain):
		self.bbGain = bbGain
		self.basebandScale.set_k((self.bbGain, ))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = OCCAM_generated()
	tb.Run(True)

