#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
# Generated: Mon Apr  1 20:02:54 2013
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
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
		self.rfGain = rfGain = 1.0
		self.recvThresh = recvThresh = 0.3
		self.rcFiltCoeff = rcFiltCoeff = 1.0
		self.meanValG = meanValG = 0.0
		self.gaussGain = gaussGain = 0.3
		self.excessBw = excessBw = 0.35
		self.dataName = dataName = 1.0
		self.dataGain = dataGain = 10.0
		self.carrierFreq = carrierFreq = 462562500.0
		self.bbGain2 = bbGain2 = 1.0
		self.bbGain = bbGain = 1.3

		##################################################
		# Blocks
		##################################################
		self.throttle = gr.throttle(gr.sizeof_float*1, samplingRate)
		self.gaussScale = blocks.multiply_const_vcc((gaussGain, ))
		self.gauss = analog.noise_source_c(analog.GR_GAUSSIAN, 0.3, 0)
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
				pad_for_usrp=True,
			),
			payload_length=0,
		)
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
		self.dataSrc = gr.file_source(gr.sizeof_float*1, "music-tx1.0.dat", False)
		self.dataOut = gr.file_sink(gr.sizeof_float*1, "music-rx1.0.dat")
		self.dataOut.set_unbuffered(False)
		self.channelFilter2 = blocks.multiply_const_vcc((1.0, ))
		self.channelFilter = blocks.multiply_const_vcc((1.0, ))
		self.basebandScale2 = blocks.multiply_const_vcc((bbGain2, ))
		self.basebandScale = blocks.multiply_const_vcc((bbGain, ))
		self.add = blocks.add_vcc(1)

		##################################################
		# Connections
		##################################################
		self.connect((self.dataSrc, 0), (self.throttle, 0))
		self.connect((self.throttle, 0), (self.dbpskEnc, 0))
		self.connect((self.dbpskMod, 0), (self.channelFilter, 0))
		self.connect((self.dbpskDemod, 0), (self.dbpskDec, 0))
		self.connect((self.basebandScale, 0), (self.add, 0))
		self.connect((self.gauss, 0), (self.gaussScale, 0))
		self.connect((self.basebandScale2, 0), (self.channelFilter2, 0))
		self.connect((self.add, 0), (self.basebandScale2, 0))
		self.connect((self.dbpskDec, 0), (self.dataOut, 0))
		self.connect((self.dbpskEnc, 0), (self.dbpskMod, 0))
		self.connect((self.gaussScale, 0), (self.add, 1))
		self.connect((self.channelFilter, 0), (self.basebandScale, 0))
		self.connect((self.channelFilter2, 0), (self.dbpskDemod, 0))


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

	def get_samplingRate(self):
		return self.samplingRate

	def set_samplingRate(self, samplingRate):
		self.samplingRate = samplingRate
		self.throttle.set_sample_rate(self.samplingRate)

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
		self.gaussScale.set_k((self.gaussGain, ))

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

	def get_bbGain2(self):
		return self.bbGain2

	def set_bbGain2(self, bbGain2):
		self.bbGain2 = bbGain2
		self.basebandScale2.set_k((self.bbGain2, ))

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

