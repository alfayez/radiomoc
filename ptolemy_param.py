#!/usr/bin/env python

# Ptolemy Names
NAME_ICON     = "_icon"
NAME_COLOR    = "_color"
NAME_LOCATION = "_location"
NAME_SDF      = "SDF Director"
NAME_MULTDIV  = "MultiplyDivide"
NAME_DELAY    = "SampleDelay"
NAME_LOWPASS  = "Low Pass"
NAME_CHOP     = "Chop"
NAME_COMP     = "Comparator"
NAME_ATTR     = "attributeName"
NAME_TAPS       = "taps"
NAME_SHOW_NAME = "_showName"
NAME_DISP_WIDTH = "displayWidth"
NAME_WIN_PROP = "_windowProperties"
NAME_PLOT_SIZE = "_plotSize"
NAME_VERG_SIZE = "_vergilSize"
NAME_VERG_ZOOM = "_vergilZoomFactor"
NAME_VERG_CENTER = "_vergilCenter"

# Ptolemy Classes
CLASS_COMP_ACT  = "ptolemy.actor.TypedCompositeActor"
CLASS_PARAMETER = "ptolemy.data.expr.Parameter"
CLASS_EXP_PARAM = "ptolemy.data.expr.ExpertParameter"
CLASS_ICON      = "ptolemy.vergil.icon.ValueIcon"
CLASS_BICON     = "ptolemy.vergil.icon.BoxedValueIcon"
CLASS_ATTR_ICON = "ptolemy.vergil.icon.AttributeValueIcon"
CLASS_COLOR     = "ptolemy.actor.gui.ColorAttribute"
CLASS_LOCATION  = "ptolemy.kernel.util.Location"
CLASS_SDF       = "ptolemy.domains.sdf.kernel.SDFDirector"
CLASS_MULTDIV   = "ptolemy.actor.lib.MultiplyDivide"
CLASS_DELAY     = "ptolemy.domains.sdf.lib.SampleDelay"
CLASS_FIR       = "ptolemy.domains.sdf.lib.FIR"
CLASS_CHOP      = "ptolemy.domains.sdf.lib.Chop"
CLASS_COMP      = "ptolemy.actor.lib.logic.Comparator"
CLASS_STR_ATTR  = "ptolemy.kernel.util.StringAttribute"
CLASS_CHOICE_STYLE = "ptolemy.actor.gui.style.ChoiceStyle"
CLASS_NAMED_IO_PORT = "ptolemy.actor.TypedIOPort"
CLASS_NAMED_IO_RELATION = "ptolemy.actor.TypedIORelation"
CLASS_SING_PARAM = "ptolemy.data.expr.SingletonParameter"
CLASS_CONST = "ptolemy.actor.lib.Const"
CLASS_SEQ_PLOT = "ptolemy.actor.lib.gui.SequencePlotter"
CLASS_WIN_PROP = "ptolemy.actor.gui.WindowPropertiesAttribute"
CLASS_SIZE_ATTR = "ptolemy.actor.gui.SizeAttribute"

# USER Defined Composite Blocks
CLASS_DBPSK_RX = "CLASS_DSBPSK_RX"

# Ptolemy Parameters
VAL_COLOR_PARAMETER = "{0.0, 0.0, 1.0, 1.0}"
VAL_WIN_PROP = "{bounds={175, 249, 808, 527}, maximized=true}"
VAL_VERG_SIZE_ATTR = "[600, 400]"
VAL_VERG_ZOOM = "1.0"
VAL_VERG_CENTER = "{300.0, 200.0}"

PROP = "property"
ENT  = "entity"
NONE = "None"
RELATION = "relation"
LINK = "link"
VERTEX= "vertex"
PORT = "port"