#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Occam Generated
# Author: Almohanad Fayez
# Generated: Mon Feb 18 14:49:53 2013
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
		self.samplingRate2 = samplingRate2 = 256000
		self.samplingRate = samplingRate = 16000
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
			device_addr="4bd1d69b",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_sink_0.set_clock_source("internal", 0)
		self.uhd_usrp_sink_0.set_samp_rate(samplingRate2)
		self.uhd_usrp_sink_0.set_center_freq(462562500, 0)
		self.uhd_usrp_sink_0.set_gain(20, 0)
		self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
		self.rfScale = blocks.multiply_const_vcc((rfGain, ))
		self.dbpskMod = digital.dbpsk_mod(
			samples_per_symbol=2,
			excess_bw=0.35,
			gray_coded=True,
			verbose=False,
			log=False)
			
		self.dbpskEnc = grc_blks2.packet_mod_f(grc_blks2.packet_encoder(
				samples_per_symbol=2,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=True,
			),
			payload_length=0,
		)
		self.dataSrc = gr.sig_source_f(samplingRate, gr.GR_COS_WAVE, 500.0, carrierGain, 0)
		self.channelFilter = gr.interp_fir_filter_ccf(samplingRate2/samplingRate, (0.00009979730726535182734615592181626198, -0.000100505550765651511082102165239859914, 0.000086241122844543649777343530260509397,-0.000067496456868908080934180149235146473, 0.000038055707197024689618803511281797114, 0.000002308927879570821060380798536715297, -0.000038934888020601433064951657492258619,  0.0000797949012601345720888459944752924, -0.000119271397627435403248838396983444454, 0.000141588780926367869801921206551753585, -0.000159486503090906062791651254251235059, 0.00016278021662664320166717668580957934, -0.000139825098689991776917257437773400852, 0.000111501293582660625388312813921487532, -0.00006400835217915140261044082414798595, -0.000005006490874363215331176689415482173, 0.000065759885101799990005100315926256371, -0.000137653864730918386056340851908430523, 0.000210797987857793675319992288130777069, -0.000250749579031937233023624722605404713, 0.000288557249057667930796505784130090433, -0.000301317569520909763619576082760431746, 0.000259377812119693034690476318715468551, -0.000213724006086556784318394863753098889, 0.000126678781682289232340260509701579394, 0.000013949015769916376684955938713983414, -0.000131217348685418172668168401706623172, 0.00028579933421299808914833873174643486, -0.00045836693707892686060548226301136765, 0.000547710656233076857019037575469155854, -0.000657871130322525859458748787034210181, 0.000719950102798743059306918468109870446, -0.000622716978035946547818946239516435526, 0.000550853545184937579137773866477800766, -0.000350683627360438463730490932235284163, -0.000065340665929834707524592740668367696, 0.000370412330330842950835978921730884394, -0.000891495468632764933442080845793498156, 0.001614087658203858547875664264381612156, -0.001956070124727197177827431318064554944, 0.002664658433291339310194922873620271275, -0.003382225612193875442790247376478873775, 0.002970158926546061749218718972542774281, -0.003425616950978864483357000381147372536, 0.002932504612944049088990583484815033444, 0.001817811091226404591678078581651334389, -0.00323201843756877084390399801350213238, 0.016027413383035659516506754584952432197, -0.096710592066912529074507176574115874246, 0.240354903905041800138420171606412623078, 0.681971863420548829459733042313018813729, 0.240354903905041800138420171606412623078, -0.096710592066912529074507176574115874246, 0.016027413383035659516506754584952432197, -0.00323201843756877084390399801350213238, 0.001817811091226404591678078581651334389, 0.002932504612944049088990583484815033444, -0.003425616950978864483357000381147372536, 0.002970158926546061749218718972542774281, -0.003382225612193875442790247376478873775, 0.002664658433291339310194922873620271275, -0.001956070124727197177827431318064554944, 0.001614087658203858547875664264381612156, -0.000891495468632764933442080845793498156, 0.000370412330330842950835978921730884394, -0.000065340665929834707524592740668367696, -0.000350683627360438463730490932235284163, 0.000550853545184937579137773866477800766, -0.000622716978035946547818946239516435526, 0.000719950102798743059306918468109870446, -0.000657871130322525859458748787034210181, 0.000547710656233076857019037575469155854, -0.00045836693707892686060548226301136765, 0.00028579933421299808914833873174643486, -0.000131217348685418172668168401706623172, 0.000013949015769916376684955938713983414, 0.000126678781682289232340260509701579394, -0.000213724006086556784318394863753098889, 0.000259377812119693034690476318715468551, -0.000301317569520909763619576082760431746, 0.000288557249057667930796505784130090433, -0.000250749579031937233023624722605404713, 0.000210797987857793675319992288130777069, -0.000137653864730918386056340851908430523, 0.000065759885101799990005100315926256371, -0.000005006490874363215331176689415482173, -0.00006400835217915140261044082414798595, 0.000111501293582660625388312813921487532, -0.000139825098689991776917257437773400852, 0.00016278021662664320166717668580957934, -0.000159486503090906062791651254251235059, 0.000141588780926367869801921206551753585,-0.000119271397627435403248838396983444454, 0.0000797949012601345720888459944752924, -0.000038934888020601433064951657492258619, 0.000002308927879570821060380798536715297, 0.000038055707197024689618803511281797114, -0.000067496456868908080934180149235146473, 0.000086241122844543649777343530260509397, -0.000100505550765651511082102165239859914, 0.00009979730726535182734615592181626198))

		##################################################
		# Connections
		##################################################
		self.connect((self.dataSrc, 0), (self.dbpskEnc, 0))
		self.connect((self.dbpskMod, 0), (self.channelFilter, 0))
		self.connect((self.channelFilter, 0), (self.rfScale, 0))
		self.connect((self.dbpskEnc, 0), (self.dbpskMod, 0))
		self.connect((self.rfScale, 0), (self.uhd_usrp_sink_0, 0))


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
		self.dataSrc.set_sampling_freq(self.samplingRate)

	def get_rfGain2(self):
		return self.rfGain2

	def set_rfGain2(self, rfGain2):
		self.rfGain2 = rfGain2

	def get_rfGain(self):
		return self.rfGain

	def set_rfGain(self, rfGain):
		self.rfGain = rfGain
		self.rfScale.set_k((self.rfGain, ))

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
		self.dataSrc.set_amplitude(self.carrierGain)

	def get_carrierFreq(self):
		return self.carrierFreq

	def set_carrierFreq(self, carrierFreq):
		self.carrierFreq = carrierFreq

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = OCCAM_generated()
	tb.Run(True)

