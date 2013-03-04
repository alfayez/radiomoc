#!/usr/bin/env python

# GNU Radio block names
CLASS_OPTIONS            = "options"
CLASS_VARIABLE           = "variable"
CLASS_SIG_GNU            = "gr_sig_source_x"
CLASS_SINE_GNU           = "gr.GR_COS_WAVE"
CLASS_FIR_GNU            = "gr_fir_filter_xxx"
CLASS_INTERP_FIR_GNU     = "gr_interp_fir_filter_xxx"
CLASS_MULT_CONST_GNU     = "blocks_multiply_const_vxx"
CLASS_DBPSK_TX_GNU       = "digital_dxpsk_mod"
CLASS_DBPSK_RX_GNU       = "digital_dxpsk_demod"
CLASS_NOISE_GNU          = "analog_noise_source_x"
CLASS_ADD_GNU            = "blocks_add_xx"
CLASS_SCOPE_GNU          = "wxgui_scopesink2"
CLASS_GAUSS_GNU          = "analog.GR_GAUSSIAN"
CLASS_DBPSK_ENC_GNU      = "blks2_packet_encoder"
CLASS_DBPSK_DEC_GNU      = "blks2_packet_decoder"
CLASS_USRP_SINK_GNU      = "uhd_usrp_sink"
CLASS_USRP_SRC_GNU       = "uhd_usrp_source"
CLASS_FILE_SINK_GNU      = "gr_file_sink"
CLASS_FILE_SRC_GNU       = "gr_file_source"

# Init Values
XML_HEADER1 = "<?xml version=\"1.0\" standalone=\"no\"?>"
XML_HEADER2 = ""

PARAM_COLOR = [0.0, 0.0, 1.0, 1.0]
PARAM_ORIG  = [1,0]
PARAM_STEP  = 60
PARAM_OFFSET = 25

BLOCK_ORIG  = [0, 200]
BLOCK_STEP  = 230
BLOCK_OFFSET = 25

X_AXIS = 0
Y_AXIS = 1

# Keywords
PARAM_GNU                = "param"
KEY_GNU                  = "key"
VALUE_GNU                = "value"
FLOW_GNU                 = "flow_graph"
BLOCK_GNU                = "block"
TIMESTAMP_GNU            = "timestamp"
NONE                     = "None"
COORDINATE               = "_coordinate"
ROTATION                 = "_rotation"
