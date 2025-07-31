#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##############################################################
#  program ecpet
#
#  a wrapper to run eddy-covariance processing by ec-pack/ec-frame
#
#  (C) 2017 Clemens Druee, Umweltmeteorologie, Universitaet Trier
#
# ##############################################################

import logging
from . import eclogger

# improved logging # ------------------------------------------------------
eclogger.setup_custom_logging()

logging.basicConfig(
    level=logging.NORMAL,
    format="%(levelname)7s: %(module)8s: %(message)s",
#    datefmt="%Y-%m-%d %H:%M:%S"
)

import argparse
import os
import re
import sys
from time import sleep

import numpy as np
from numpy import version as ver_np
from pandas import __version__ as ver_pd
from pandas import to_datetime as pd_to_datetime
from scipy import __version__ as ver_scipy

#
# import modules using improved logging # ---------------------------------
#
from . import _version as version
from . import ecconfig
from . import ecdb
from . import ecengine
from . import ecfile
from . import ecutils as ec
#
#  optional : GUI framework
#
try:
    import wx
    import wx.adv
    from wx.lib.masked import TimeCtrl
    import wx.lib.agw.pygauge
    import wx.lib.mixins.listctrl as listmix

    have_wx = True
    global imagepath
except ImportError:
    have_wx = False
    wx = TimeCtrl = listmix = None
#
#  optional : inter-thread communication
#
try:
    # from wx.lib.pubsub import pub
    from pubsub import pub
    from pubsub import __version__ as ver_pub
    from threading import Thread, Event

    have_com = True
except ImportError:
    pub = ver_pub = Thread = Event = None
    have_com = False
#
#  optional : maps
#
try:
    import matplotlib as mpl

    mpl.use('WXAgg')
    from matplotlib.backends.backend_wxagg import \
        FigureCanvasWxAgg as FigureCanvas
    from matplotlib.pyplot import Figure
    from matplotlib import __version__ as ver_mpl
    import requests
    from io import BytesIO
    from PIL import Image

    have_mpl = True
except ImportError:
    mpl = FigureCanvas = Figure = requests = BytesIO = Image = None
    ver_mpl = None
    have_mpl = False
# Try to import basemap for fallback
try:
    from mpl_toolkits.basemap import Basemap

    HAVE_BASEMAP = True
except ImportError:
    Basemap = None
    HAVE_BASEMAP = False
#
# setup logger
#
logger = logging.getLogger(__name__)
# suppress annoying findfont debug messages
# https://stackoverflow.com/a/58393562
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

ApCodes = ['Not present',
           'CSATSonic', 'TCouple', 'CampKrypton', 'Pt100', 'Psychro',
           'Son3Dcal', 'MierijLyma', 'LiCor7500', 'KaijoTR90',
           'KaijoTR61', 'GillSolent', 'GenericSonic']
ApType = {'Not present': 'Select',
          'CSATSonic': 'Sonic',
          'TCouple': 'Thermo',
          'CampKrypton': 'Hygro',
          'Pt100': 'Thermo',
          'Psychro': 'Hygro',
          'Son3Dcal': 'Sonic',
          'MierijLyma': 'Hygro',
          'LiCor7500': 'Hygro',
          'KaijoTR90': 'Sonic',
          'KaijoTR61': 'Sonic',
          'GillSolent': 'Sonic',
          'GenericSonic': 'Sonic'
          }
ApCompany = {'Not present': '',
             'CSATSonic': 'Campbell Scientific',
             'TCouple': 'generic',
             'CampKrypton': 'Campbell Scientific Inc',
             'Pt100': 'generic',
             'Psychro': 'generic',
             'Son3Dcal': 'various',
             'MierijLyma': 'Mierij Meteo BV',
             'LiCor7500': 'LiCor Inc',
             'KaijoTR90': 'Sonic Corporation (ex Kaijo Denki)',
             'KaijoTR61': 'Sonic Corporation (ex Kaijo Denki)',
             'GillSolent': 'Gill Instruments', 'GenericSonic': ''
             }
ApMake = {'Not present': '',
          'CSATSonic': 'CSAT3',
          'TCouple': 'Thermocouple',
          'CampKrypton': 'KH20',
          'Pt100': 'Pt100',
          'Psychro': 'Psychrometer',
          'Son3Dcal': 'KNMI-calibrated',
          'MierijLyma': 'Lyman-alpha hygrometer',
          'LiCor7500': 'Li-7500',
          'KaijoTR90': 'TR90-AH probe',
          'KaijoTR61': 'TR-61 probe',
          'GillSolent': 'Gill Solent',
          'GenericSonic': '3-D Sonic Anemometer'
          }
ApPath = {'Not present': 0,
          'CSATSonic': 0.10,
          'TCouple': None,
          'CampKrypton': 0,
          'Pt100': None,
          'Psychro': None,
          'Son3Dcal': 0,
          'MierijLyma': 0,
          'LiCor7500': 0.10,
          'KaijoTR90': 0.05,
          'KaijoTR61': 0,
          'GillSolent': 0,
          'GenericSonic': -1
          }
#
# stages descriptions
#
r_labels = {'start': 'start over  ',
            'pre':  'preprocessor',
            'plan': 'planar fit  ',
            'flux': 'flux calc.  ',
            'post': 'postprocesor',
            'out':  'write output'}
#
#
# List of variables that are set by the GUI
#
gui_set = [
    'ConfName',
    'AvgInterval',
    'PlfitInterval',
    'RawDir', 'DatDir', 'OutDir',
    'RawFastData', 'RawSlowData',
    'fastfmt.U_col',
    'fastfmt.V_col',
    'fastfmt.W_col',
    'fastfmt.Tsonic_col',
    'fastfmt.Tcouple_col',
    'fastfmt.Humidity_col',
    'fastfmt.CO2_col',
    'fastfmt.Press_col',
    'fastfmt.diag_col',
    'fastfmt.agc_col',
    'slowfmt.Tref_col',
    'slowfmt.RelHum_col',
    'slowfmt.Pref_col',
    'fastfmt.U_nam',
    'fastfmt.V_nam',
    'fastfmt.W_nam',
    'fastfmt.Tsonic_nam',
    'fastfmt.Tcouple_nam',
    'fastfmt.Humidity_nam',
    'fastfmt.CO2_nam',
    'fastfmt.Press_nam',
    'fastfmt.diag_nam',
    'fastfmt.agc_nam',
    'slowfmt.Tref_nam',
    'slowfmt.RelHum_nam',
    'slowfmt.Pref_nam',
    'DateBegin', 'DateEnd',
    'Par.FREQ',
    'InstLatLon',
    'SourceArea',
    'SonCal.QQType',
    'SonCal.QQX',
    'SonCal.QQY',
    'SonCal.QQZ',
    'SonCal.QQYaw',
    'SonCal.QQPath',
    'CoupCal.QQType',
    'CoupCal.QQX',
    'CoupCal.QQY',
    'CoupCal.QQZ',
    'HygCal.QQType',
    'HygCal.QQX',
    'HygCal.QQY',
    'HygCal.QQZ',
    'HygCal.QQPath',
    'Co2Cal.QQType',
    'Co2Cal.QQX',
    'Co2Cal.QQY',
    'Co2Cal.QQZ',
    'Co2Cal.QQPath',
]
gui_image = None
defaults = ecconfig.Config()

# ----------------------------------------------------------------
#
# graphical interface  using wxpython
#
if have_wx:
    #
    # ----------------------------------------------------------------
    def ErrorBox(parent, message, caption='Error!'):
        dlg = wx.MessageDialog(parent, message, caption,
                               wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
        return

    def WarningBox(parent, message, caption='Warning!'):
        dlg = wx.MessageDialog(parent, message, caption,
                               wx.OK | wx.ICON_WARNING)
        result = dlg.ShowModal()
        dlg.Destroy()
        return result == wx.ID_OK

    def Font_Title():
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(18)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        return font

    def Font_Welcome():
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(round(wx.SystemSettings.GetFont(
            wx.SYS_SYSTEM_FONT).GetPointSize()*1.25))
        return font

    def Font_bf():
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        return font

    def Font_em():
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetStyle(wx.FONTSTYLE_SLANT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        return font

    # ----------------------------------------------------------------
    class Page_Welcome(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            """Constructor"""
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.title = wx.StaticText(self, wx.ID_ANY, 'Weclome to EC-PeT')
            self.title.SetFont(Font_Title())
            self.title.Size = wx.Size(-1, int(Font_Title().GetPointSize()*1.2))

            self.info = wx.StaticText(self, wx.ID_ANY, 'This wizard will guide you ' +
                                      'creating or editing a configuration.\n' +
                                      'Please press "Next".')
            self.info.SetFont(Font_Welcome())

            # assemble the page
            self.SetSizer(self.right_sizer)
            self.right_sizer.Add(self.title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            self.right_sizer.AddSpacer(20)
            self.right_sizer.Add(self.info, 0, wx.EXPAND | wx.ALL, 5)
            self.right_sizer.AddSpacer(20)

            # event bindings

        def Leave(self, event):
            pass

    # ----------------------------------------------------------------------
    class Page_Dirs(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)

            self.title = wx.StaticText(self, wx.ID_ANY, 'Step1: Select directories',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))
            self.title.SetFont(Font_Title())

            self.curdir_box = wx.StaticBox(
                self, wx.ID_ANY, label="Working Directory")
            self.curdir_bsz = wx.StaticBoxSizer(self.curdir_box, wx.VERTICAL)
            self.curdir_desc = wx.StaticText(self, wx.ID_ANY,
                                             'All paths below are relative to this directory.')
            self.curdir_txt = wx.StaticText(self, wx.ID_ANY, os.getcwd())
            self.curdir_txt.SetFont(Font_em())

            self.rawdir_box = wx.StaticBox(self, wx.ID_ANY, label="RawDir")
            self.rawdir_bsz = wx.StaticBoxSizer(self.rawdir_box, wx.VERTICAL)
            self.rawdir_desc = wx.StaticText(self, wx.ID_ANY,
                                             'Select directory, where the raw data are located:')
            self.rawdir_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.rawdir_txt = wx.TextCtrl(self, wx.ID_ANY, size=(480, -1),
                                          style=wx.TE_RIGHT)
            self.rawdir_btn = wx.Button(self, wx.ID_ANY, 'Browse')

            self.datdir_box = wx.StaticBox(self, wx.ID_ANY, label="DatDir")
            self.datdir_bsz = wx.StaticBoxSizer(self.datdir_box, wx.VERTICAL)
            self.datdir_desc = wx.StaticText(self, wx.ID_ANY,
                                             'Select directory, where intermediate data will be stored:')
            self.datdir_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.datir_txt = wx.TextCtrl(self, wx.ID_ANY, size=(480, -1),
                                         style=wx.TE_RIGHT)
            self.datir_btn = wx.Button(self, wx.ID_ANY, 'Browse')

            self.outdir_box = wx.StaticBox(self, wx.ID_ANY, label="OutDir")
            self.outdir_bsz = wx.StaticBoxSizer(self.outdir_box, wx.VERTICAL)
            self.outdir_desc = wx.StaticText(self, wx.ID_ANY,
                                             'Select directory, where the result files will be stored):')
            self.outdir_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.outdir_txt = wx.TextCtrl(self, wx.ID_ANY, size=(480, -1),
                                          style=wx.TE_RIGHT)
            self.outdir_btn = wx.Button(self, wx.ID_ANY, 'Browse')

            # assemble the page
            self.SetSizer(self.right_sizer)
            self.right_sizer.Add(self.title, 0, wx.EXPAND | wx.ALL, 5)
            self.right_sizer.Add(self.curdir_bsz, 0, wx.EXPAND | wx.ALL, 5)
            self.curdir_bsz.Add(self.curdir_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.curdir_bsz.Add(self.curdir_desc, 0, wx.EXPAND | wx.ALL, 5)

            self.right_sizer.Add(self.rawdir_bsz, 0, wx.EXPAND | wx.ALL, 5)
            self.rawdir_bsz.Add(self.rawdir_desc, 0, wx.EXPAND | wx.ALL, 5)
            self.rawdir_bsz.Add(self.rawdir_sizer, 0, wx.EXPAND | wx.ALL, 5)
            #
            self.rawdir_sizer.Add(self.rawdir_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.rawdir_sizer.Add(self.rawdir_btn, 0, wx.ALL, 5)

            self.right_sizer.Add(self.datdir_bsz, 0, wx.EXPAND | wx.ALL, 5)
            self.datdir_bsz.Add(self.datdir_desc, 0, wx.EXPAND | wx.ALL, 5)
            self.datdir_bsz.Add(self.datdir_sizer, 0, wx.EXPAND | wx.ALL, 5)
            #
            self.datdir_sizer.Add(self.datir_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.datdir_sizer.Add(self.datir_btn, 0, wx.ALL, 5)

            self.right_sizer.Add(self.outdir_bsz, 0, wx.EXPAND | wx.ALL, 5)
            self.outdir_bsz.Add(self.outdir_desc, 0, wx.EXPAND | wx.ALL, 5)
            self.outdir_bsz.Add(self.outdir_sizer, 0, wx.EXPAND | wx.ALL, 5)
            #
            self.outdir_sizer.Add(self.outdir_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.outdir_sizer.Add(self.outdir_btn, 0, wx.ALL, 5)
            self.right_sizer.Add(wx.StaticLine(self, -1),
                                 0, wx.EXPAND | wx.ALL, 5)

            # set design

            # event bindings
            self.Bind(wx.EVT_BUTTON, self.rawdir_browse, self.rawdir_btn)
            self.Bind(wx.EVT_BUTTON, self.datir_browse, self.datir_btn)
            self.Bind(wx.EVT_BUTTON, self.outdir_browse, self.outdir_btn)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)

        def rawdir_browse(self, event):
            dlg = wx.DirDialog(self, message="Choose a directory",
                               defaultPath=os.path.join(os.getcwd(), self.wizard.guilist.get('RawDir')))
            if dlg.ShowModal() == wx.ID_OK:
                self.wizard.guilist.put(
                    'RawDir', os.path.relpath(dlg.GetPath(), os.getcwd()))
            dlg.Destroy()  # best to do this sooner than later
            self.Update()

        def datir_browse(self, event):
            dlg = wx.DirDialog(self, message="Choose a directory",
                               defaultPath=os.path.join(os.getcwd(), self.wizard.guilist.get('DatDir')))
            if dlg.ShowModal() == wx.ID_OK:
                self.wizard.guilist.put(
                    'DatDir', os.path.relpath(dlg.GetPath(), os.getcwd()))
            dlg.Destroy()  # best to do this sooner than later
            self.Update()

        def outdir_browse(self, event):
            dlg = wx.DirDialog(self, message="Choose a directory",
                               defaultPath=os.path.join(os.getcwd(), self.wizard.guilist.get('OutDir')))
            if dlg.ShowModal() == wx.ID_OK:
                self.wizard.guilist.put(
                    'OutDir', os.path.relpath(dlg.GetPath(), os.getcwd()))
            dlg.Destroy()  # best to do this sooner than later
            self.Update()

        def Enter(self, event=0):
            logger.debug('actual working directory:'+str(os.getcwd()))
            self.curdir_txt.SetLabel(os.getcwd())
            self.Update()

        def Update(self, event=0):
            self.rawdir_txt.ChangeValue(self.wizard.guilist.get('RawDir'))
            self.datir_txt.ChangeValue(self.wizard.guilist.get('DatDir'))
            self.outdir_txt.ChangeValue(self.wizard.guilist.get('OutDir'))

    # ----------------------------------------------------------------------
    class Page_Files(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)

            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step2: Select raw data files',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))
            self.patfast_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.patfast_lbl = wx.StaticText(self, wx.ID_ANY, 'Filter:')
            self.patfast_txt = wx.TextCtrl(self, wx.ID_ANY, size=(300, -1))
            self.patfast_btn = wx.Button(self, wx.ID_ANY, 'Apply')
            self.rawfast_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.rawfast_list = wx.ListCtrl(self, wx.ID_ANY, size=(360, 180),
                                            style=wx.LC_REPORT)
            self.rawfast_list.InsertColumn(0, 'Fast raw data files', width=360)
            self.files_slow_chk = wx.CheckBox(self, wx.ID_ANY, size=(
                120, -1), label='Use individual\nfile names')

            self.patslow_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.patslow_lbl = wx.StaticText(self, wx.ID_ANY, 'Filter:')
            self.patslow_txt = wx.TextCtrl(self, wx.ID_ANY, size=(300, -1))
            self.patslow_btn = wx.Button(self, wx.ID_ANY, 'Apply')
            self.rawslow_chk = wx.CheckBox(self, wx.ID_ANY, size=(
                120, -1), label='Use different\nfiles for slow\n(refercence)\ndata:')
            self.rawslow_chk.SetValue(True)
            self.rawslow_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.rawslow_list = wx.ListCtrl(self, wx.ID_ANY, size=(360, 180),
                                            style=wx.LC_REPORT)
            self.rawslow_list.InsertColumn(0, 'Slow raw data files', width=360)
            self.files_fast_chk = wx.CheckBox(self, wx.ID_ANY, size=(
                120, -1), label='Use individual\nfile names')

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(self.title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            self.right_sizer.Add(self.patfast_sizer)
            self.patfast_sizer.AddSpacer(120)
            self.patfast_sizer.Add(self.patfast_lbl, 0, wx.ALL, 5)
            self.patfast_sizer.Add(self.patfast_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.patfast_sizer.Add(self.patfast_btn, 0, wx.ALL, 5)
            self.right_sizer.Add(self.rawfast_sizer)
            self.rawfast_sizer.AddSpacer(120)
            self.rawfast_sizer.Add(self.rawfast_list, 0, wx.EXPAND | wx.ALL, 5)
            self.rawfast_sizer.Add(self.files_fast_chk)

            self.right_sizer.Add(self.patslow_sizer)
            self.patslow_sizer.AddSpacer(120)
            self.patslow_sizer.Add(self.patslow_lbl, 0, wx.ALL, 5)
            self.patslow_sizer.Add(self.patslow_txt, 0, wx.EXPAND | wx.ALL, 5)
            self.patslow_sizer.Add(self.patslow_btn, 0, wx.ALL, 5)
            self.right_sizer.Add(self.rawslow_sizer)
            self.rawslow_sizer.Add(self.rawslow_chk)
            self.rawslow_sizer.Add(self.rawslow_list, 0, wx.EXPAND | wx.ALL, 5)
            self.rawslow_sizer.Add(self.files_slow_chk)
            self.right_sizer.Add(wx.StaticLine(self, -1),
                                 0, wx.EXPAND | wx.ALL, 5)

            # set design
            self.title.SetFont(Font_Title())

            # event bindings
            self.Bind(wx.EVT_BUTTON, self.patfast_apply, self.patfast_btn)
            self.Bind(wx.EVT_BUTTON, self.patslow_apply, self.patslow_btn)
            self.Bind(wx.EVT_CHECKBOX, self.check_toggle)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)

            # fill in initially
            self.filter_fast = ''
            self.files_fast = []
            self.filter_slow = ''
            self.files_slow = []

        def rawfast_find(self, pattern):
            logger.debug('Page_Files:rawfast_find')
            sandclock = wx.BusyCursor()
            self.files_fast = ecfile.find(
                self.wizard.guilist.get('RawDir'), pattern.split(' '))
            del sandclock

        def rawslow_find(self, pattern):
            logger.debug('Page_Files:rawslow_find')
            sandclock = wx.BusyCursor()
            self.files_slow = ecfile.find(
                self.wizard.guilist.get('RawDir'), pattern.split(' '))
            del sandclock

        def store_files(self):
            logger.debug('Page_Files:store_files')

            # store fast file list
            if self.files_fast_chk.IsChecked():
                # selected to store individual files
                nf = self.rawfast_list.GetSelectedItemCount()
                logger.debug('fast files selcted: '+str(nf))
                files = []
                for i in range(self.rawfast_list.GetItemCount()):
                    if self.rawfast_list.IsSelected(i):
                        files.append(self.rawfast_list.GetItemText(i))
                self.wizard.guilist.put('RawFastData', ' '.join(files))
                self.wizard.storage['SampleFileFast'] = files[0]
            else:
                # selected to store pattern
                self.wizard.guilist.put('RawFastData', self.filter_fast)
                self.wizard.storage['SampleFileFast'] = self.files_fast[0]

            # store fast file list
            if self.files_slow_chk.IsChecked():
                # selected to store individual files
                ns = self.rawslow_list.GetSelectedItemCount()
                logger.debug('slow files selcted: '+str(ns))
                files = []
                for i in range(self.rawslow_list.GetItemCount()):
                    if self.rawslow_list.IsSelected(i):
                        files.append(self.rawslow_list.GetItemText(i))
                self.wizard.guilist.put('RawSlowData', ' '.join(files))
                self.wizard.storage['SampleFileSlow'] = files[0]
            else:
                # selected to store pattern
                self.wizard.guilist.put('RawSlowData', self.filter_slow)
                self.wizard.storage['SampleFileSlow'] = self.files_slow[0]

        def check_toggle(self, event):
            logger.debug('Page_Files:check_toggle')
            # empty list if one of the files_*_chk was unchecked
            origin = event.GetEventObject()
            if origin == self.files_fast_chk and event.IsChecked() is False:
                self.rawfast_find(self.filter_fast)
            if origin == self.files_slow_chk and event.IsChecked() is False:
                self.rawslow_find(self.filter_slow)
            # show new state
            self.Update()

        def patfast_apply(self, event):
            logger.debug('Page_Files:patfast_apply')
            self.filter_fast = self.patfast_txt.GetValue()
            self.rawfast_find(self.filter_fast)
            self.Update()

        def patslow_apply(self, event):
            logger.debug('Page_Files:patslow_apply')
            self.filter_slow = self.patslow_txt.GetValue()
            self.rawslow_find(self.filter_slow)
            self.Update()

        def Enter(self, event):
            logger.debug('Page_Files:Enter')

            # fill the controls for fast files
            if ec.isglob(self.wizard.guilist.get('RawFastData')):
                self.files_fast_chk.SetValue(False)
                self.filter_fast = self.wizard.guilist.get('RawFastData')
                self.rawfast_find(self.filter_fast)
            elif self.wizard.guilist.get('RawFastData') == '':
                self.files_fast_chk.SetValue(False)
                self.filter_fast = '*'
                self.rawfast_find(self.filter_fast)
            else:
                self.files_fast_chk.SetValue(True)
                self.filter_fast = ''
                self.rawfast_find(self.wizard.guilist.get('RawFastData'))

            # disable separate list if file list/pattern are identical
            if self.wizard.guilist.get('RawSlowData') == self.wizard.guilist.get('RawFastData'):
                self.rawslow_chk.SetValue(False)
                self.patslow_txt.ChangeValue('')
                self.files_slow = []

            # fill the controls for (separate) slow files
            else:
                if ec.isglob(self.wizard.guilist.get('RawSlowData')):
                    self.files_slow_chk.SetValue(False)
                    self.filter_slow = self.wizard.guilist.get('RawSlowData')
                    self.rawslow_find(self.filter_slow)
                elif self.wizard.guilist.get('RawSlowData') == '':
                    self.files_slow_chk.SetValue(False)
                    self.filter_slow = '*'
                    self.rawslow_find(self.filter_slow)
                else:
                    self.files_slow_chk.SetValue(True)
                    self.patslow_txt.ChangeValue('')
                    self.rawslow_find(self.wizard.guilist.get('RawSlowData'))

            # display everything
            self.Update()

        def Update(self, event=0):
            logger.debug('Page_Files:Update')
            logger.debug('RawDir'+str(self.wizard.guilist.get('RawDir')))
            logger.debug('rawslow_chk.IsChecked' +
                          str(self.rawslow_chk.IsChecked()))

            if self.rawslow_chk.IsChecked():
                # slow files separately controlled
                self.patslow_txt.Enabled = True
                self.patslow_btn.Enabled = True
                self.files_slow_chk.Enabled = True
            else:
                # slow files identical to fast files
                self.rawslow_list.Enabled = False
                self.patslow_txt.Enabled = False
                self.patslow_btn.Enabled = False
                self.files_slow_chk.Enabled = False
                self.filter_slow = ''
                self.files_slow = self.files_fast

            # fill files lists
            self.rawslow_list.DeleteAllItems()
            for i in range(len(self.files_slow)):
                logger.debug('rawslow_list:'+sorted(self.files_slow)[i])
                self.rawslow_list.InsertItem(0, sorted(self.files_slow)[i])
            self.rawslow_list.Refresh()
            #
            self.rawfast_list.DeleteAllItems()
            for i in range(len(self.files_fast)):
                logger.debug('rawfast_list:'+sorted(self.files_fast)[i])
                self.rawfast_list.InsertItem(0, sorted(self.files_fast)[i])
            self.rawfast_list.Refresh()

            # select display mode
            if self.files_fast_chk.IsChecked():
                # individual files selected
                self.rawfast_list.Enabled = True
                for i in range(len(self.files_fast)):
                    self.rawfast_list.Select(i, True)
                self.filter_fast = ''
            else:
                # pattern selected
                self.rawfast_list.Enabled = False
            #
            if self.rawslow_chk.IsChecked():
                # slow files separately controlled
                if self.files_slow_chk.IsChecked():
                    # individual files selected
                    self.rawslow_list.Enabled = True
                    for i in range(len(self.files_fast)):
                        self.rawslow_list.Select(i, True)
                        self.filter_slow = ''
                else:
                    # pattern selected
                    self.rawslow_list.Enabled = False

            # display filter  values
            self.patfast_txt.ChangeValue(self.filter_fast)
            self.patslow_txt.ChangeValue(self.filter_slow)

            # make list text grey if list is disabled
            if self.rawfast_list.IsEnabled():
                self.rawfast_list.SetTextColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            else:
                self.rawfast_list.SetTextColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            #
            if self.rawslow_list.IsEnabled():
                self.rawslow_list.SetTextColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            else:
                self.rawslow_list.SetTextColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))

        def Leave(self, event):
            logger.debug('Page_Files:Leave')

            # do nothing if we're going backward
            if not event.GetDirection():
                return

            # check if selection contains files
            if self.files_fast_chk.IsChecked():
                # count files selected if files are selected
                nf = self.rawfast_list.GetSelectedItemCount()
            else:
                # count files found if pattern are selected
                nf = len(self.files_fast)
            if self.files_slow_chk.IsChecked():
                # count files selected if files are selected
                ns = self.rawfast_list.GetSelectedItemCount()
            else:
                # count files found if pattern selected
                ns = len(self.files_slow)

            # contact user if no files are in selection
            if nf == 0 or ns == 0:
                dlg = wx.MessageDialog(self, 'No file(s) selected',
                                       style=wx.OK)
                # why does ShowModal raise an exception here,
                # although it works fine ???
                try:
                    dlg.ShowModal()
                except:
                    pass
                dlg.Destroy()
                event.Veto()
                logger.debug('wizard page next blocked')
                return

            # store selection
            logger.debug(
                'files selected: {:d} fast, {:d} slow'.format(nf, ns))
            self.store_files()

    # ----------------------------------------------------------------------
    class Page_Columns(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # definitions

            self.vars = ['U', 'V', 'W', 'Tsonic', 'Tcouple', 'Humidity', 'CO2', 'Press',
                         'diag', 'agc',
                         'Tref', 'RelHum', 'Pref']
            self.var_type = ['fast', 'fast', 'fast', 'fast', 'fast', 'fast', 'fast', 'fast',
                             'fast', 'fast',
                             'slow', 'slow', 'slow']
            self.var_desc = ['eastward wind component',
                             'northward wind component',
                             'upward wind component',
                             'Sonic temperature',
                             'Fast Thermometer temperature',
                             'Water vapor density',
                             'CO2 density',
                             'Barometric pressure',
                             'CSAT diagnostic word',
                             'Li-7xxx diagnostic word',
                             'reference air temperature',
                             'reference relative himidity',
                             'reference barometric pressure']
            self.ivars = range(len(self.vars))
            self.var_para = [self.var_type[i]+'fmt.'+self.vars[i]+'_nam'
                             for i in self.ivars]
            self.col_para = [self.var_type[i]+'fmt.'+self.vars[i]+'_col'
                             for i in self.ivars]
            self.not_present = '(not present)'
            self.fastcols = []
            self.slowcols = []

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step3: Select data columns',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))
            self.grid = wx.FlexGridSizer(
                rows=len(self.vars)+1, cols=4, hgap=5, vgap=5)
            self.tit_var = wx.StaticText(self, wx.ID_ANY, 'Symbol:')
            self.tit_typ = wx.StaticText(self, wx.ID_ANY, 'Type:')
            self.tit_dsc = wx.StaticText(self, wx.ID_ANY, 'Description:')
            self.tit_nam = wx.StaticText(self, wx.ID_ANY, 'Select column:')
            self.txt_var = []
            self.txt_typ = []
            self.txt_dsc = []
            self.box_nam = []
            for i in self.ivars:
                self.txt_var.append(wx.StaticText(
                    self, wx.ID_ANY, self.vars[i]))
                self.txt_typ.append(wx.StaticText(
                    self, wx.ID_ANY, self.var_type[i]))
                self.txt_dsc.append(wx.StaticText(
                    self, wx.ID_ANY, self.var_desc[i]))
                self.box_nam.append(wx.ComboBox(self,   wx.ID_ANY,
                                                choices=[],
                                                style=wx.CB_DROPDOWN | wx.CB_READONLY))

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(self.title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            self.right_sizer.Add(self.grid, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            self.grid.Add(self.tit_var, 0, wx.ALIGN_LEFT | wx.ALL, 0)
            self.grid.Add(self.tit_typ, 0, wx.ALIGN_LEFT | wx.ALL, 0)
            self.grid.Add(self.tit_dsc, 0, wx.ALIGN_LEFT | wx.ALL, 0)
            self.grid.Add(self.tit_nam, 0, wx.ALIGN_LEFT | wx.ALL, 0)
            for i in self.ivars:
                self.grid.Add(self.txt_var[i], 0, wx.ALIGN_LEFT | wx.ALL, 0)
                self.grid.Add(self.txt_typ[i], 0, wx.ALIGN_LEFT | wx.ALL, 0)
                self.grid.Add(self.txt_dsc[i], 0, wx.ALIGN_LEFT | wx.ALL, 0)
                self.grid.Add(self.box_nam[i], 0, wx.ALIGN_LEFT | wx.ALL, 0)
            self.right_sizer.Add(wx.StaticLine(self, -1),
                                 0, wx.EXPAND | wx.ALL, 5)

            # set design
            self.title.SetFont(Font_Title())
            self.tit_var.SetFont(Font_bf())
            self.tit_typ.SetFont(Font_bf())
            self.tit_dsc.SetFont(Font_bf())
            self.tit_nam.SetFont(Font_bf())

            # event bindings
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            for i in self.ivars:
                self.Bind(wx.EVT_COMBOBOX, self.Update, self.box_nam[i])
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)

        def get_column_info(self):
            cols = {}
            # get header of fast sample file
            file = self.wizard.storage['SampleFileFast']
            header = ecfile.toa5_get_header(os.path.join(
                self.wizard.guilist.get('RawDir'), str(file)))
            cols['namefast'] = header['column_names']
            cols['unitfast'] = header['column_units']
            cols['smplfast'] = header['column_sampling']
            cols['num_fast'] = header['column_count']

            # get header  of slow sample file
            file = self.wizard.storage['SampleFileSlow']
            header = ecfile.toa5_get_header(os.path.join(
                self.wizard.guilist.get('RawDir'), str(file)))
            cols['nameslow'] = header['column_names']
            cols['unitslow'] = header['column_units']
            cols['smplslow'] = header['column_sampling']
            cols['num_slow'] = header['column_count']

            # extract columns from fast sample file header
            self.fastcols = []
            self.fastcols.append(self.not_present)
            for c in range(cols['num_fast']):
                self.fastcols.append('{:s}:{:s}:{:s}'.format(
                    cols['namefast'][c], cols['unitfast'][c], cols['smplfast'][c]))
#      self.fastcols = self.fastcols + cols['namefast']

            # extract columns from slow sample file header
            self.slowcols = []
            self.slowcols.append(self.not_present)
            for c in range(cols['num_slow']):
                self.slowcols.append('{:s}:{:s}:{:s}'.format(
                    cols['nameslow'][c], cols['unitslow'][c], cols['smplslow'][c]))
#      self.slowcols = self.slowcols + cols['nameslow']

        def get_settings(self):
            # convert column numbers to column names
            text = []
            # loop variables
            for i in self.ivars:
                # get config value
                # ... get column name setting
                setting = self.wizard.guilist.get(self.var_para[i])
                # ... if name not set, try converting column number
                if len(setting) == 0:
                    # column number in config is 1-based, 0 = undefined
                    col_num = self.wizard.guilist.get(
                        self.col_para[i], kind='int', na=0)
                    if (self.var_type[i] == 'fast' and
                            col_num in range(len(self.fastcols))):
                        # number set and in range of existing columns
                        setting = str(self.fastcols[col_num])
                    elif (self.var_type[i] == 'slow' and
                          col_num in range(len(self.slowcols))):
                        # number set and in range of existing columns
                        setting = str(self.slowcols[col_num])
                    else:
                        # number not set or not in range of existing columns
                        setting = ''
                    logger.debug(
                        f'{i}: convert col {col_num} -> nam {setting}')
                if self.var_type[i] == 'fast':
                    if setting in self.fastcols:
                        text.append(setting)
                    else:
                        text.append(self.fastcols[0])  # not present
                elif self.var_type[i] == 'slow':
                    if setting in self.slowcols:
                        text.append(setting)
                    else:
                        text.append(self.slowcols[0])  # not present
                else:
                    raise TypeError

            return text

        def store_settings(self):
            # loop variables
            for i in self.ivars:
                # get config value
                if self.var_type[i] == 'fast':
                    text = self.box_nam[i].GetValue()
                    if text == self.fastcols[0]:
                        setting = ''
                        set_num = 0
                    else:
                        setting = text
                        set_num = self.fastcols.index(text)
                elif self.var_type[i] == 'slow':
                    text = self.box_nam[i].GetValue()
                    if text == self.slowcols[0]:
                        setting = ''
                        set_num = 0
                    else:
                        setting = text
                        set_num = self.slowcols.index(text)
                else:
                    raise TypeError
                # store column names
                self.wizard.guilist.put(self.var_para[i], setting)
                logger.debug(
                    ' '.join(['stored', self.var_para[i], str(setting)]))
                # column number in config is 1-based : '' -> 0 = undefined
                self.wizard.guilist.put(self.col_para[i], set_num)
                logger.debug(
                    ' '.join(['stored', self.col_para[i], str(set_num)]))

        def check_double(self, event=0):
            double = False
            for t in ['fast', 'slow']:
                selected = []
                for i in self.ivars:
                    if self.var_type[i] == t:
                        b = self.box_nam[i]
                        selected.append(b.GetValue())
                    else:
                        selected.append(None)
                for i in self.ivars:
                    if selected[i] is None:
                        # nothing selected
                        pass
                    elif selected.count(selected[i]) > 1 and selected[i] != self.not_present:
                        # same item selected in other column
                        self.box_nam[i].SetBackgroundColour(wx.RED)
                        double = True
                        logger.debug(
                            'column selection not unique '+selected[i])
                    else:
                        self.box_nam[i].SetBackgroundColour(
                            wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            return double

        def Enter(self, event):
            # get values to choose from
            self.get_column_info()
            # pot them into each combobox
            for i in self.ivars:
                self.box_nam[i].Clear()
                if self.var_type[i] == 'fast':
                    for c in self.fastcols:
                        self.box_nam[i].Append(c)
                elif self.var_type[i] == 'slow':
                    for c in self.slowcols:
                        self.box_nam[i].Append(c)
                else:
                    raise TypeError
            # get previous values
            text = self.get_settings()
            for i in self.ivars:
                self.box_nam[i].SetValue(text[i])
            self.Update()

        def Update(self, event=0):
            self.check_double(event)

        def Leave(self, event):
            if event.GetDirection():
                # only brag around if were going forward
                if self.check_double():
                    dlg = wx.MessageDialog(self, 'Warning: duplicate selections',
                                           style=wx.OK | wx.CANCEL)
                    result = dlg.ShowModal()
                    dlg.Destroy()
                    ok = (result == wx.ID_OK)
                else:
                    ok = True
                if ok:
                    self.store_settings()
                else:
                    event.Veto()
                    logger.debug('wizard page next blocked')
            else:
                pass

    # ----------------------------------------------------------------
    # convert datetime.datetime to wx.DateTime
    #

    def dt2wx(tt):
        fmt = "%Y-%m-%d %H:%M:%S"
        string = tt.strftime("%Y-%m-%d %H:%M:%S")
        wxt = wx.DateTime()
        wx.DateTime.ParseFormat(wxt, string, fmt)
        return wxt
    # ----------------------------------------------------------------------

    class Page_Time(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # definitions

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step4: Select time to process',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))
            self.radio_auto = wx.RadioBox(self, label='Processing begin/end times',
                                          choices=['automatic',
                                                   'set manually'],
                                          majorDimension=1,
                                          style=wx.RA_SPECIFY_ROWS)
            self.box_time = wx.StaticBox(
                self, wx.ID_ANY, label="Manual selection")
            self.bsz_time = wx.StaticBoxSizer(self.box_time, wx.VERTICAL)
            self.grd_time = wx.FlexGridSizer(rows=3, cols=2, hgap=25, vgap=10)
            self.txtstart = wx.StaticText(
                self, wx.ID_ANY, 'Processing begin date')
            self.calstart = wx.adv.CalendarCtrl(self, wx.ID_ANY,
                                                date=wx.DateTime.Now(),
                                                style=wx.adv.CAL_MONDAY_FIRST | wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION)
            self.time_sizer_start = wx.BoxSizer(wx.HORIZONTAL)
            self.tx2start = wx.StaticText(self, wx.ID_ANY, 'begin time: ')
            self.spbstart = wx.SpinButton(
                self, wx.ID_ANY, style=wx.SP_VERTICAL)
            self.timstart = TimeCtrl(self, wx.ID_ANY,
                                     value='00:00',
                                     style=wx.TE_PROCESS_TAB,
                                     format='24HHMM',
                                     fmt24hr=True,
                                     displaySeconds=False,
                                     spinButton=self.spbstart)
            self.txtstop = wx.StaticText(
                self, wx.ID_ANY, 'Processing end date')
            self.calstop = wx.adv.CalendarCtrl(self, wx.ID_ANY,
                                               date=wx.DateTime.Now(),
                                               style=wx.adv.CAL_MONDAY_FIRST | wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION)
            self.time_sizer_stop = wx.BoxSizer(wx.HORIZONTAL)
            self.tx2stop = wx.StaticText(self, wx.ID_ANY, 'end time: ')
            self.spbstop = wx.SpinButton(self, wx.ID_ANY, style=wx.SP_VERTICAL)
            self.timstop = TimeCtrl(self, wx.ID_ANY,
                                    value='00:00',
                                    style=wx.TE_PROCESS_TAB,
                                    format='24HHMM',
                                    fmt24hr=True,
                                    displaySeconds=False,
                                    spinButton=self.spbstop)
            self.low_time = wx.BoxSizer(wx.VERTICAL)
            self.btn_time_guess = wx.Button(self, wx.ID_ANY,
                                            label='Guess from fast raw-data files')
            self.box_freq = wx.StaticBox(
                self, wx.ID_ANY, label="Measurement Rate")
            self.bsz_freq = wx.StaticBoxSizer(self.box_freq, wx.HORIZONTAL)
            self.lbl_freq = wx.StaticText(self, wx.ID_ANY, 'Frequency (Hz):')
            self.txt_freq = wx.TextCtrl(self, value='0', size=(120, -1))
            self.btn_freq_guess = wx.Button(self, wx.ID_ANY,
                                            label='Guess from fast raw-data files')

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(
                self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            self.right_sizer.Add(self.radio_auto, flag=wx.EXPAND)
            self.right_sizer.AddSpacer(15)
            self.right_sizer.Add(self.bsz_time, flag=wx.EXPAND)
            self.bsz_time.Add(self.grd_time, 0, wx.EXPAND | wx.ALL, 5)
            self.grd_time.Add(self.txtstart)
            self.grd_time.Add(self.txtstop)
            self.grd_time.Add(self.calstart, 0, wx.EXPAND | wx.ALL, 5)
            self.grd_time.Add(self.calstop, 0, wx.EXPAND | wx.ALL, 5)
            self.grd_time.Add(self.time_sizer_start, 0, wx.EXPAND | wx.ALL, 5)
            self.time_sizer_start.Add(self.tx2start)
            self.time_sizer_start.Add(self.timstart)
            self.time_sizer_start.Add(self.spbstart)
            self.grd_time.Add(self.time_sizer_stop, 0, wx.EXPAND | wx.ALL, 5)
            self.time_sizer_stop.Add(self.tx2stop)
            self.time_sizer_stop.Add(self.timstop)
            self.time_sizer_stop.Add(self.spbstop)
            self.bsz_time.Add(self.low_time, flag=wx.EXPAND)
            self.low_time.Add(self.btn_time_guess,
                              flag=wx.ALIGN_CENTRE | wx.ALL)

            self.right_sizer.AddSpacer(15)
            self.right_sizer.Add(self.bsz_freq, flag=wx.EXPAND)
            self.bsz_freq.Add(self.lbl_freq, flag=wx.EXPAND |
                              wx.ALL, border=15)
            self.bsz_freq.Add(self.txt_freq, flag=wx.EXPAND |
                              wx.ALL, border=15)
            self.bsz_freq.Add(self.btn_freq_guess,
                              flag=wx.EXPAND | wx.ALL, border=15)

            # set design
            self.title.SetFont(Font_Title())

            # event bindings
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)
            self.Bind(wx.EVT_RADIOBOX, self.onRadioBox, self.radio_auto)
            self.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED,
                      self.time_check, self.calstart)
            self.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED,
                      self.time_check, self.calstop)
            self.Bind(wx.lib.masked.EVT_TIMEUPDATE,
                      self.time_check, self.timstart)
            self.Bind(wx.lib.masked.EVT_TIMEUPDATE,
                      self.time_check, self.timstop)
            self.Bind(wx.EVT_BUTTON, self.time_guess, self.btn_time_guess)
            self.Bind(wx.EVT_TEXT, self.freq_check, self.txt_freq)
            self.Bind(wx.EVT_BUTTON, self.freq_guess, self.btn_freq_guess)

        def time_check(self, event=0):
            ok = None
            DateTimestart = self.calstart.GetDate()
            DateTimestop = self.calstop.GetDate()
            DateTimestart += self.timstart.GetValue(as_wxTimeSpan=True)
            DateTimestop += self.timstop.GetValue(as_wxTimeSpan=True)
            if DateTimestart >= DateTimestop:
                logger.debug('begin datetime after end datetime')
                ok = False
                color = wx.RED
            else:
                ok = True
                color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            self.calstart.SetBackgroundColour(color)
            self.calstop.SetBackgroundColour(color)
            self.timstart.SetBackgroundColour(color)
            self.timstop.SetBackgroundColour(color)
            return ok

        def freq_check(self, event=0):
            ok = None
            try:
                f = float(self.txt_freq.GetValue())
            except:
                self.txt_freq.SetBackgroundColour(wx.RED)
                logger.debug('non-numeric value entered for frequency')
                ok = False
            else:
                if f < 1 or f > 50:
                    self.txt_freq.SetBackgroundColour(wx.RED)
                    logger.debug('frequency out of range 0.1..50 Hz')
                    ok = False
                else:
                    self.txt_freq.SetBackgroundColour(
                        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
                    ok = True
            return ok

        def store_settings(self):
            if self.radio_auto.GetSelection() == 1:
                DateTimestart = self.calstart.GetDate()
                DateTimestop = self.calstop.GetDate()
                DateTimestart += self.timstart.GetValue(as_wxTimeSpan=True)
                DateTimestop += self.timstop.GetValue(as_wxTimeSpan=True)
                self.wizard.guilist.put(
                    'DateBegin', DateTimestart.Format('%Y-%m-%d %H:%M:%S'))
                self.wizard.guilist.put(
                    'DateEnd', DateTimestop.Format('%Y-%m-%d %H:%M:%S'))
            else:
                self.wizard.guilist.put('DateBegin', '')
                self.wizard.guilist.put('DateEnd', '')
            self.wizard.guilist.put('Par.FREQ', self.txt_freq.GetValue())

            logger.debug('stored DateBegin: %s' %
                          self.wizard.guilist.get('DateBegin'))
            logger.debug('stored DateEnd  : %s' %
                          self.wizard.guilist.get('DateEnd'))
            logger.debug('stored Par.FREQ : %s' %
                          self.wizard.guilist.get('Par.FREQ'))

        def Enter(self, event):
            nix = wx.DateTime()
            nix.ParseDateTime('1970-01-01 00:00:00')

            db = wx.DateTime()
            if db.ParseDateTime(self.wizard.guilist.get('DateBegin')) != -1:
                pass
            elif db.ParseDate(self.wizard.guilist.get('DateBegin')) != -1:
                pass
            else:
                db = nix
                self.wizard.guilist.put('DateBegin', '')

            de = wx.DateTime()
#            try:
            if de.ParseDateTime(self.wizard.guilist.get('DateEnd')) != -1:
                pass
            elif de.ParseDate(self.wizard.guilist.get('DateEnd')) != -1:
                pass
            else:
                de = nix
                self.wizard.guilist.put('DateEnd', '')

            logger.debug('found DateBegin: %s' % str(db))
            logger.debug('found DateEnd  : %s' % str(de))

            # no times specified in config:
            if db == nix and de == nix:
                logger.debug('switched to auto')
                self.radio_auto.SetSelection(0)
            # start AND end time specified in config:
            elif db != nix and de != nix:
                logger.debug('switched manual (both)')
                self.radio_auto.SetSelection(1)
                self.timstart.SetValue(db)
                self.calstart.SetDate(db)
            # only one date specified
            else:
                logger.debug('switched manual (one)')
                self.time_guess()
                if db != nix:
                    self.calstart.SetDate(db)
                    self.timstart.SetValue(db)
                if de != nix:
                    self.calstop.SetDate(de)
                    self.timstop.SetValue(de)

            self.txt_freq.ChangeValue(self.wizard.guilist.get('Par.FREQ'))
            self.onRadioBox(0)

        def onRadioBox(self, event):
            if self.radio_auto.GetSelection() == 0:
                self.box_time.Disable()
                self.calstart.Disable()
                self.calstop.Disable()
                self.timstart.Disable()
                self.timstop.Disable()
                self.spbstart.Disable()
                self.spbstop.Disable()
                self.btn_time_guess.Disable()
            else:
                self.box_time.Enable()
                self.calstart.Enable()
                self.calstop.Enable()
                self.timstart.Enable()
                self.timstop.Enable()
                self.spbstart.Enable()
                self.spbstop.Enable()
                self.btn_time_guess.Enable()

        def time_guess(self, event=0):
            sandclock = wx.BusyCursor
            tr = ecfile.get_time_range(self.wizard.guilist.get('RawDir'),
                                       self.wizard.guilist.get('RawFastData'))
            DateTimestart = dt2wx(tr[0])
            DateTimestop = dt2wx(tr[1])
            self.calstart.SetDate(DateTimestart)
            self.calstop.SetDate(DateTimestop)
            self.timstart.SetValue(DateTimestart)
            self.timstop.SetValue(DateTimestop)
            del sandclock

        def freq_guess(self, event):
            sandclock = wx.BusyCursor
            files = [os.path.join(self.wizard.guilist.get('RawDir'), x)
                     for x in self.wizard.guilist.get('RawFastData')]
            fs = ecfile.toa5_get_times(str(files[0]), count=True)
#            time_first = dateutil.parser.parse(fs[0][0:16]+':00 UTC')
#            time_last = dateutil.parser.parse(fs[1][0:16]+':00 UTC')
            time_first = pd_to_datetime(fs[0][0:16], utc=True)
            time_last = pd_to_datetime(fs[1][0:16], utc=True)
            f_raw = (fs[2]-1)/(time_last-time_first).total_seconds()
            logger.debug('raw frequeny estimate %f' % f_raw)
            f = round(f_raw)
            self.txt_freq.SetValue('%3i' % f)
            del sandclock

        def Leave(self, event):
            if self.radio_auto.GetSelection() == 1 and not self.time_check():
                ErrorBox(self, 'beginning date/time is not earlier than end date/time')
                ok = False
            else:
                ok = True
            if ok and not self.freq_check():
                ok = WarningBox(self, 'Warning: frequency out of range 0.1..50 Hz')
            else:
                ok = True
            if ok:
                self.store_settings()
            else:
                event.Veto()
    # ----------------------------------------------------------------------


    class IPLocationDetector:
        """Detects user location based on IP address"""

        def __init__(self, fallback_lat=49.74811, fallback_lon=6.67557):
            self.fallback_lat = fallback_lat
            self.fallback_lon = fallback_lon

        def get_location(self):
            """Get location from IP address with fallback"""
            # Try multiple IP location services
            services = [
                'http://ip-api.com/json/',
                'https://ipapi.co/json/',
                'https://freegeoip.app/json/'
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=3)
                    if response.status_code == 200:
                        data = response.json()

                        # Different services use different field names
                        lat = data.get('lat') or data.get('latitude')
                        lon = data.get('lon') or data.get('longitude')

                        if lat is not None and lon is not None:
                            logger.info(
                                f"Location detected from IP: {lat}, {lon}")
                            return float(lat), float(lon)

                except Exception as e:
                    logger.debug(
                        f"IP location service {service} failed: {e}")
                    continue

            # All services failed, use fallback
            logger.info(
                f"Using fallback location: {self.fallback_lat}, {self.fallback_lon}")
            return self.fallback_lat, self.fallback_lon
    # ----------------------------------------------------------------------


    class MapTileDownloader:
        """Handles downloading map tiles from various providers"""

        def __init__(self):
            self.providers = {
                'osm': {
                    'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    'attribution': '© OpenStreetMap contributors'
                },
                'satellite': {
                    'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    'attribution': '© Esri, DigitalGlobe, GeoEye, Earthstar Geographics'
                },
                'terrain': {
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
                'attribution': '© Esri, HERE, Garmin, Intermap, increment P Corp.'
                }
            }

        def deg2tile(self, lat, lon, zoom):
            """Convert lat/lon to tile coordinates"""
            lat_rad = np.radians(lat)
            n = 2.0 ** zoom
            x = int((lon + 180.0) / 360.0 * n)
            y = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
            return x, y

        def tile2deg(self, x, y, zoom):
            """Convert tile coordinates to lat/lon"""
            n = 2.0 ** zoom
            lon = x / n * 360.0 - 180.0
            lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * y / n)))
            lat = np.degrees(lat_rad)
            return lat, lon

        def download_tile(self, provider, zoom, x, y, timeout=5):
            """Download a single tile"""
            try:
                url = self.providers[provider]['url'].format(z=zoom, x=x,
                                                             y=y)
                headers = {'User-Agent': 'LocationPicker/1.0'}
                response = requests.get(url, timeout=timeout,
                                        headers=headers)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))
            except Exception as e:
                logger.debug(f"Failed to download tile {x},{y}: {e}")
                return None

        def get_map_tiles(self, lat, lon, zoom, width_tiles=3,
                          height_tiles=3, provider='osm'):
            """Download multiple tiles to create a map"""
            center_x, center_y = self.deg2tile(lat, lon, zoom)

            # Calculate tile range
            start_x = center_x - width_tiles // 2
            end_x = start_x + width_tiles
            start_y = center_y - height_tiles // 2
            end_y = start_y + height_tiles

            tiles = {}
            for x in range(start_x, end_x):
                for y in range(start_y, end_y):
                    tile = self.download_tile(provider, zoom, x, y)
                    if tile:
                        tiles[(x, y)] = tile

            return tiles, (start_x, start_y, end_x, end_y)
    # ----------------------------------------------------------------------


    class Page_Location(wx.adv.WizardPageSimple):
        lat = None
        lon = None

        def __init__(self, parent, have_mpl=True):
            wx.adv.WizardPageSimple.__init__(self, parent)

            self.have_mpl = have_mpl
            self.map = None
            self.wizard = parent
            self.tile_downloader = MapTileDownloader()
            self.ip_detector = IPLocationDetector()
            self.current_provider = 'osm'
            self.zoom_level = 10
            self.is_dragging = False
            self.drag_start = None
            self.map_cache = {}

            self.init_ui()
            self.bind_events()

        def init_ui(self):
            """Initialize the user interface"""
            # Main sizer
            self.main_sizer = wx.BoxSizer(wx.VERTICAL)

            # Title
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step 5: Specify sensor locations',
                                       style=wx.ALIGN_CENTRE)

            # Map section
            self.map_box = wx.StaticBox(self, wx.ID_ANY,
                                        label="Interactive Map")
            self.map_sizer = wx.StaticBoxSizer(self.map_box, wx.VERTICAL)

            if self.have_mpl:
                # Map controls
                self.controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

                # Provider selection
                self.provider_label = wx.StaticText(self, wx.ID_ANY,
                                                    "Map Type:")
                self.provider_choice = wx.Choice(self, wx.ID_ANY,
                                                 choices=['OpenStreetMap',
                                                          'Satellite',
                                                          'Terrain'])
                self.provider_choice.SetSelection(0)

                # Zoom controls with buttons
                self.zoom_label = wx.StaticText(self, wx.ID_ANY, "Zoom:")
                self.zoom_out_btn = wx.Button(self, wx.ID_ANY, "−",
                                              size=(30, 30))
                self.zoom_slider = wx.Slider(self, wx.ID_ANY, value=10,
                                             minValue=1, maxValue=18,
                                             style=wx.SL_HORIZONTAL | wx.SL_LABELS)
                self.zoom_in_btn = wx.Button(self, wx.ID_ANY, "+",
                                             size=(30, 30))

                # Refresh button
                self.refresh_btn = wx.Button(self, wx.ID_ANY,
                                             "Refresh Map")

                # Add controls to sizer
                self.controls_sizer.Add(self.provider_label, 0,
                                        wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                                        5)
                self.controls_sizer.Add(self.provider_choice, 0, wx.ALL, 5)
                self.controls_sizer.Add(self.zoom_label, 0,
                                        wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                                        5)
                self.controls_sizer.Add(self.zoom_out_btn, 0, wx.ALL, 2)
                self.controls_sizer.Add(self.zoom_slider, 1,
                                        wx.EXPAND | wx.ALL, 5)
                self.controls_sizer.Add(self.zoom_in_btn, 0, wx.ALL, 2)
                self.controls_sizer.Add(self.refresh_btn, 0, wx.ALL, 5)

                # Create matplotlib figure
                self.fig = Figure(figsize=(8, 6), dpi=100)
                self.ax = self.fig.add_subplot(111)
                self.fig.subplots_adjust(left=0.02, right=0.98, top=0.98,
                                         bottom=0.02)

                # Create canvas
                self.canvas = FigureCanvas(self, -1, self.fig)
                self.canvas.SetMinSize(wx.Size(600, 400))

                # Add to map sizer
                self.map_sizer.Add(self.controls_sizer, 0,
                                   wx.EXPAND | wx.ALL, 5)
                self.map_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)

                # Status bar
                self.status_text = wx.StaticText(self, wx.ID_ANY,
                                                 "Click on map to center location")
                self.map_sizer.Add(self.status_text, 0, wx.EXPAND | wx.ALL,
                                   5)

            # Coordinate input section
            self.coord_box = wx.StaticBox(self, wx.ID_ANY,
                                          label="Coordinates")
            self.coord_sizer = wx.StaticBoxSizer(self.coord_box,
                                                 wx.VERTICAL)

            # Decimal degrees
            self.decimal_sizer = wx.FlexGridSizer(2, 4, 5, 10)
            self.decimal_label = wx.StaticText(self, wx.ID_ANY,
                                               "Decimal Degrees:")
            self.lat_label = wx.StaticText(self, wx.ID_ANY, "Latitude:")
            self.lat_text = wx.TextCtrl(self, wx.ID_ANY, "0.00000",
                                        style=wx.TE_PROCESS_ENTER)
            self.lon_label = wx.StaticText(self, wx.ID_ANY, "Longitude:")
            self.lon_text = wx.TextCtrl(self, wx.ID_ANY, "0.00000",
                                        style=wx.TE_PROCESS_ENTER)

            self.decimal_sizer.Add(self.decimal_label, 0,
                                   wx.ALIGN_CENTER_VERTICAL)
            self.decimal_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.decimal_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.decimal_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.decimal_sizer.Add(self.lat_label, 0,
                                   wx.ALIGN_CENTER_VERTICAL)
            self.decimal_sizer.Add(self.lat_text, 1, wx.EXPAND)
            self.decimal_sizer.Add(self.lon_label, 0,
                                   wx.ALIGN_CENTER_VERTICAL)
            self.decimal_sizer.Add(self.lon_text, 1, wx.EXPAND)

            # DMS format
            self.dms_sizer = wx.FlexGridSizer(2, 4, 5, 10)
            self.dms_label = wx.StaticText(self, wx.ID_ANY,
                                           "Degrees, Minutes, Seconds:")
            self.lat_dms_label = wx.StaticText(self, wx.ID_ANY,
                                               "Latitude:")
            self.lat_dms_text = wx.TextCtrl(self, wx.ID_ANY, "0°00'00\"",
                                            style=wx.TE_PROCESS_ENTER)
            self.lon_dms_label = wx.StaticText(self, wx.ID_ANY,
                                               "Longitude:")
            self.lon_dms_text = wx.TextCtrl(self, wx.ID_ANY, "0°00'00\"",
                                            style=wx.TE_PROCESS_ENTER)

            self.dms_sizer.Add(self.dms_label, 0, wx.ALIGN_CENTER_VERTICAL)
            self.dms_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.dms_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.dms_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""), 0)
            self.dms_sizer.Add(self.lat_dms_label, 0,
                               wx.ALIGN_CENTER_VERTICAL)
            self.dms_sizer.Add(self.lat_dms_text, 1, wx.EXPAND)
            self.dms_sizer.Add(self.lon_dms_label, 0,
                               wx.ALIGN_CENTER_VERTICAL)
            self.dms_sizer.Add(self.lon_dms_text, 1, wx.EXPAND)

            # Configure sizers
            self.decimal_sizer.AddGrowableCol(1)
            self.decimal_sizer.AddGrowableCol(3)
            self.dms_sizer.AddGrowableCol(1)
            self.dms_sizer.AddGrowableCol(3)

            # Add to coordinate sizer
            self.coord_sizer.Add(self.decimal_sizer, 0, wx.EXPAND | wx.ALL,
                                 5)
            self.coord_sizer.Add(self.dms_sizer, 0, wx.EXPAND | wx.ALL, 5)

            # Assemble main layout
            self.main_sizer.Add(self.title, 0, wx.ALIGN_CENTER | wx.ALL,
                                10)
            if self.have_mpl:
                self.main_sizer.Add(self.map_sizer, 1, wx.EXPAND | wx.ALL,
                                    5)
            self.main_sizer.Add(self.coord_sizer, 0, wx.EXPAND | wx.ALL, 5)

            self.SetSizer(self.main_sizer)

        def bind_events(self):
            """Bind all events"""
            # Page events
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.on_enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.on_leave)

            # Text events
            self.Bind(wx.EVT_TEXT_ENTER, self.on_coord_change,
                      self.lat_text)
            self.Bind(wx.EVT_TEXT_ENTER, self.on_coord_change,
                      self.lon_text)
            self.Bind(wx.EVT_TEXT_ENTER, self.on_dms_change,
                      self.lat_dms_text)
            self.Bind(wx.EVT_TEXT_ENTER, self.on_dms_change,
                      self.lon_dms_text)

            if self.have_mpl:
                # Map control events
                self.Bind(wx.EVT_CHOICE, self.on_provider_change,
                          self.provider_choice)
                self.Bind(wx.EVT_SLIDER, self.on_zoom_change,
                          self.zoom_slider)
                self.Bind(wx.EVT_BUTTON, self.on_zoom_in, self.zoom_in_btn)
                self.Bind(wx.EVT_BUTTON, self.on_zoom_out,
                          self.zoom_out_btn)
                self.Bind(wx.EVT_BUTTON, self.on_refresh, self.refresh_btn)

                # Canvas events - only click to center, no dragging
                self.canvas.mpl_connect('button_press_event',
                                        self.on_mouse_click)

        def on_enter(self, event):
            """Called when entering the page"""

            # Get coordinates from wizard if available
            try:
                coords = getattr(self.wizard, 'guilist', {}).get(
                    'InstLatLon', ['0.', '0.'])
                logger.debug(f'Location found in old config: {coords}')
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    latlon = [float(x) for x in coords]
                else:
                    latlon = None
            except (AttributeError, ValueError, TypeError):
                latlon = None

            if latlon is None:
                # Initialize coordinates with IP detection
                self.lat, self.lon = self.ip_detector.get_location()

            self.update_display()
            if self.have_mpl:
                self.refresh_map()

        def on_leave(self, event):
            """Called when leaving the page"""
            # Store coordinates back to wizard
            try:
                coords = [float(self.lat_text.GetValue()),
                          float(self.lon_text.GetValue())]
                if hasattr(self.wizard, 'guilist'):
                    self.wizard.guilist.put('InstLatLon', coords)
                logger.debug(f'Stored InstLatLon: {coords}')
            except (ValueError, AttributeError):
                logger.warning('Failed to store coordinates')

        def on_coord_change(self, event):
            """Handle coordinate text changes"""
            try:
                self.lat = float(self.lat_text.GetValue())
                self.lon = float(self.lon_text.GetValue())
                self.update_display()
                if self.have_mpl:
                    self.refresh_map()
            except ValueError:
                # Invalid input - could add visual feedback here
                pass

        def on_dms_change(self, event):
            """Handle DMS format changes"""
            try:
                # Parse DMS format (simple implementation)
                lat_dms = self.lat_dms_text.GetValue()
                lon_dms = self.lon_dms_text.GetValue()

                # Convert DMS to decimal
                self.lat = self.dms2deg(lat_dms)
                self.lon = self.dms2deg(lon_dms)

                self.update_display()
                if self.have_mpl:
                    self.refresh_map()
            except ValueError:
                pass

        def on_provider_change(self, event):
            """Handle map provider changes"""
            providers = ['osm', 'satellite', 'terrain']
            self.current_provider = providers[
                self.provider_choice.GetSelection()]
            self.refresh_map()

        def on_zoom_change(self, event):
            """Handle zoom changes"""
            self.zoom_level = self.zoom_slider.GetValue()
            self.refresh_map()

        def on_refresh(self, event):
            """Handle refresh button"""
            self.refresh_map()

        def on_zoom_in(self, event):
            """Handle zoom in button"""
            self.zoom_level = min(18, self.zoom_level + 1)
            self.zoom_slider.SetValue(self.zoom_level)
            self.refresh_map()

        def on_zoom_out(self, event):
            """Handle zoom out button"""
            self.zoom_level = max(1, self.zoom_level - 1)
            self.zoom_slider.SetValue(self.zoom_level)
            self.refresh_map()

        def on_mouse_click(self, event):
            """Handle mouse click on map - center map at clicked position"""
            if event.inaxes != self.ax or not event.xdata or not event.ydata:
                return

            # Convert click coordinates to lat/lon and center map there
            clicked_lon = event.xdata
            clicked_lat = event.ydata

            # Update center coordinates
            self.lat = clicked_lat
            self.lon = clicked_lon

            # Update display and refresh map
            self.update_display()
            self.refresh_map()

            # Update status
            self.status_text.SetLabel(
                f"Centered at: {self.lat:.5f}°, {self.lon:.5f}°")

        def refresh_map(self):
            """Refresh the map display"""
            if not self.have_mpl:
                return

            # show that we are busy
            sandclock = wx.BusyCursor()

            # Clear the axes
            self.ax.clear()

            # Try to get online tiles first
            try:
                tiles, bounds = self.tile_downloader.get_map_tiles(
                    self.lat, self.lon, self.zoom_level,
                    provider=self.current_provider
                )

                if tiles:
                    self.draw_tile_map(tiles, bounds)
                else:
                    raise Exception("No tiles downloaded")

                self.status_text.SetLabel(
                    f"Online map loaded - {self.current_provider} (Click to center)")

            except Exception as e:
                logger.debug(f"Online map failed: {e}")
                # Fall back to basemap if available
                if HAVE_BASEMAP:
                    self.draw_basemap()
                    self.status_text.SetLabel(
                        "Using offline basemap (Click to center)")
                else:
                    self.draw_simple_map()
                    self.status_text.SetLabel(
                        "Simple map view (Click to center)")

            # Draw location marker
            self.ax.plot(self.lon, self.lat, 'ro', markersize=10,
                         markeredgecolor='white', markeredgewidth=2)

            # Set title and labels
            self.ax.set_title(
                f'Location: {self.lat:.5f}°, {self.lon:.5f}°')
            self.ax.set_xlabel('Longitude')
            self.ax.set_ylabel('Latitude')

            # Refresh canvas
            self.canvas.draw()

            del sandclock

        def draw_tile_map(self, tiles, bounds):
            """Draw map using downloaded tiles"""
            start_x, start_y, end_x, end_y = bounds

            # Calculate the geographic bounds
            lat_min, lon_min = self.tile_downloader.tile2deg(start_x,
                                                             end_y,
                                                             self.zoom_level)
            lat_max, lon_max = self.tile_downloader.tile2deg(end_x,
                                                             start_y,
                                                             self.zoom_level)

            # Create a composite image
            tile_size = 256
            width = (end_x - start_x) * tile_size
            height = (end_y - start_y) * tile_size

            if width > 0 and height > 0:
                composite = Image.new('RGB', (width, height))

                for (x, y), tile in tiles.items():
                    px = (x - start_x) * tile_size
                    py = (y - start_y) * tile_size
                    composite.paste(tile, (px, py))

                # Display the composite image
                self.ax.imshow(np.array(composite),
                               extent=[lon_min, lon_max, lat_min, lat_max],
                               aspect='auto')
                self.ax.set_xlim(lon_min, lon_max)
                self.ax.set_ylim(lat_min, lat_max)

        def draw_basemap(self):
            """Draw map using basemap (fallback)"""
            try:
                # Calculate bounds based on zoom level
                delta = 180 / (2 ** (self.zoom_level - 1))

                # Create basemap
                m = Basemap(
                    projection='merc',
                    llcrnrlat=self.lat - delta,
                    urcrnrlat=self.lat + delta,
                    llcrnrlon=self.lon - delta,
                    urcrnrlon=self.lon + delta,
                    resolution='i',
                    ax=self.ax
                )

                # Draw map features
                m.drawcoastlines(linewidth=0.5)
                m.drawcountries(linewidth=0.5)
                m.fillcontinents(color='lightgray', lake_color='lightblue')
                m.drawmapboundary(fill_color='lightblue')

                # Convert lat/lon to map coordinates for marker
                x, y = m(self.lon, self.lat)

            except Exception as e:
                logger.debug(f"Basemap failed: {e}")
                self.draw_simple_map()

        def draw_simple_map(self):
            """Draw a simple coordinate grid (last resort)"""
            # Calculate bounds
            delta = 180 / (2 ** (self.zoom_level - 1))

            self.ax.set_xlim(self.lon - delta, self.lon + delta)
            self.ax.set_ylim(self.lat - delta, self.lat + delta)

            # Draw grid
            self.ax.grid(True, alpha=0.3)
            self.ax.set_facecolor('lightblue')

            # Add some geographic context
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3,
                            label='Equator')
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3,
                            label='Prime Meridian')

        def update_display(self):
            """Update the coordinate display"""
            # Update decimal degrees
            self.lat_text.ChangeValue(f"{self.lat:.5f}")
            self.lon_text.ChangeValue(f"{self.lon:.5f}")

            # Update DMS format
            lat_dms = self.deg2dms(self.lat)
            lon_dms = self.deg2dms(self.lon)
            self.lat_dms_text.ChangeValue(lat_dms)
            self.lon_dms_text.ChangeValue(lon_dms)

            # Reset background colors
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            self.lat_text.SetBackgroundColour(color)
            self.lon_text.SetBackgroundColour(color)
            self.lat_dms_text.SetBackgroundColour(color)
            self.lon_dms_text.SetBackgroundColour(color)

        def deg2dms(self, deg):
            """Convert decimal degrees to DMS format"""
            d = int(deg)
            m = int((deg - d) * 60)
            s = ((deg - d) * 60 - m) * 60
            return f"{d}°{abs(m):02d}'{abs(s):05.2f}\""

        def dms2deg(self, dms_str):
            """Convert DMS string to decimal degrees"""
            # Simple implementation - you might want to make this more robust
            parts = re.split('[°\'"]+', dms_str.strip())
            if len(parts) >= 3:
                d = float(parts[0])
                m = float(parts[1])
                s = float(parts[2])
                return d + m / 60 + s / 3600
            return 0.0


    # ----------------------------------------------------------------------
    class Page_Apparatus(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.code_thermo = None #self.cho_thermo.GetStringSelection()
            self.code_sonic = None #self.cho_sonic.GetStringSelection()
            self.pos_hygro = [0, 0, 0]
            self.pos_thermo = [0, 0, 0]
            self.pos_sonic = [0, 0, 0]
            self.yaw_sonic = None
            self.code_hygro = None
            self.code_thermo = None
            self.code_sonic = None
            self.wizard = parent

            # definitions
            lbl = ['X:', 'Y:', 'Z:']
            ApImage = {'Not present': 'not-present.png',
                       'CSATSonic': 'CSATSonic.png',
                       'TCouple': 'TCouple.png',
                       'CampKrypton': 'CampKrypton.png',
                       'Pt100': 'Open-Wire.png',
                       'Psychro': 'missing.png',
                       'Son3Dcal': 'MetekUSA1.png',
                       'MierijLyma': 'missing.png',
                       'LiCor7500': 'LiCor7500.png',
                       'KaijoTR90': 'KaijoTR90.png',
                       'KaijoTR61': 'KaijoTR61.png',
                       'GillSolent': 'GillSolent.png',
                       'GenericSonic': 'MetekUSA1.png'
                       }
            self.aparatus_bmp = {x: wx.Bitmap(os.path.join(
                imagepath, ApImage[x]), wx.BITMAP_TYPE_PNG) for x in ApCodes}

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.select_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step6: Select devices',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))
            self.box_sonic = wx.StaticBox(self, wx.ID_ANY, label="Anemometer")
            self.bsz_sonic = wx.StaticBoxSizer(self.box_sonic, wx.VERTICAL)
            lst_sonic = ['Not present'] + \
                [x for x in ApCodes if ApType[x] == 'Sonic']
            self.cho_sonic = wx.Choice(self, wx.ID_ANY, choices=lst_sonic)
            self.bmp_sonic = wx.StaticBitmap(
                self, wx.ID_ANY, self.aparatus_bmp['Not present'],)
            self.txt_sonic_manu = wx.StaticText(
                self, wx.ID_ANY, 'Manufacturer:')
            self.txt_sonic_make = wx.StaticText(self, wx.ID_ANY, 'Model:')
            self.txt_sonic_path = wx.StaticText(
                self, wx.ID_ANY, 'Path length (m):')
            self.txc_sonic_manu = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_sonic_make = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_sonic_path = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txt_sonic_pos = wx.StaticText(
                self, wx.ID_ANY, 'Position (m):')
            self.szr_sonic_pos = [wx.BoxSizer(wx.HORIZONTAL) for i in range(3)]
            self.lbl_sonic_pos = [wx.StaticText(
                self, wx.ID_ANY, lbl[i]) for i in range(3)]
            self.txc_sonic_pos = [wx.TextCtrl(
                self, wx.ID_ANY, '') for i in range(3)]

            self.box_thermo = wx.StaticBox(
                self, wx.ID_ANY, label="Thermometer")
            self.bsz_thermo = wx.StaticBoxSizer(self.box_thermo, wx.VERTICAL)
            lst_thermo = ['Not present'] + \
                [x for x in ApCodes if ApType[x] == 'Thermo']
            self.cho_thermo = wx.Choice(self, wx.ID_ANY, choices=lst_thermo)
            self.bmp_thermo = wx.StaticBitmap(
                self, wx.ID_ANY, self.aparatus_bmp['Not present'])
            self.txt_thermo_manu = wx.StaticText(
                self, wx.ID_ANY, 'Manufacturer:')
            self.txt_thermo_make = wx.StaticText(self, wx.ID_ANY, 'Model:')
            self.txt_thermo_path = wx.StaticText(self, wx.ID_ANY, '')
            self.txc_thermo_manu = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_thermo_make = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_thermo_path = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txt_thermo_pos = wx.StaticText(
                self, wx.ID_ANY, 'Position (m):')
            self.szr_thermo_pos = [wx.BoxSizer(
                wx.HORIZONTAL) for i in range(3)]
            self.lbl_thermo_pos = [wx.StaticText(
                self, wx.ID_ANY, lbl[i]) for i in range(3)]
            self.txc_thermo_pos = [wx.TextCtrl(
                self, wx.ID_ANY, '') for i in range(3)]

            self.box_hygro = wx.StaticBox(
                self, wx.ID_ANY, label="Gas analyzer")
            self.bsz_hygro = wx.StaticBoxSizer(self.box_hygro, wx.VERTICAL)
            lst_hygro = ['Not present'] + \
                [x for x in ApCodes if ApType[x] == 'Hygro']
            self.cho_hygro = wx.Choice(self, wx.ID_ANY, choices=lst_hygro)
            self.bmp_hygro = wx.StaticBitmap(
                self, wx.ID_ANY, self.aparatus_bmp['Not present'])
            self.txt_hygro_manu = wx.StaticText(
                self, wx.ID_ANY, 'Manufacturer:')
            self.txt_hygro_make = wx.StaticText(self, wx.ID_ANY, 'Model:')
            self.txt_hygro_path = wx.StaticText(
                self, wx.ID_ANY, 'Path length (m):')
            self.txc_hygro_manu = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_hygro_make = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txc_hygro_path = wx.TextCtrl(self, wx.ID_ANY, '')
            self.txt_hygro_pos = wx.StaticText(
                self, wx.ID_ANY, 'Position (m):')
            self.szr_hygro_pos = [wx.BoxSizer(wx.HORIZONTAL) for i in range(3)]
            self.lbl_hygro_pos = [wx.StaticText(
                self, wx.ID_ANY, lbl[i]) for i in range(3)]
            self.txc_hygro_pos = [wx.TextCtrl(
                self, wx.ID_ANY, '') for i in range(3)]

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(
                self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            self.right_sizer.Add(self.select_sizer, flag=wx.EXPAND)

            self.select_sizer.AddSpacer(15)
            self.select_sizer.Add(self.bsz_sonic, flag=wx.EXPAND)
            self.bsz_sonic.Add(self.cho_sonic, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_sonic.Add(self.bmp_sonic, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_sonic.Add(self.txt_sonic_manu, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txc_sonic_manu, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txt_sonic_make, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txc_sonic_make, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txt_sonic_path, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txc_sonic_path, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_sonic.Add(self.txt_sonic_pos, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            for i in range(3):
                self.bsz_sonic.Add(
                    self.szr_sonic_pos[i], 0, wx.EXPAND | wx.ALL, 5)
                self.szr_sonic_pos[i].Add(self.lbl_sonic_pos[i])
                self.szr_sonic_pos[i].Add(
                    self.txc_sonic_pos[i], flag=wx.EXPAND)

            self.select_sizer.AddSpacer(15)
            self.select_sizer.Add(self.bsz_thermo, flag=wx.EXPAND)
            self.bsz_thermo.Add(self.cho_thermo, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_thermo.Add(self.bmp_thermo, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_thermo.Add(self.txt_thermo_manu, 0,
                                wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txc_thermo_manu, 0,
                                wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txt_thermo_make, 0,
                                wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txc_thermo_make, 0,
                                wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txt_thermo_path, 0,
                                wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txc_thermo_path, 0,
                                wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_thermo.Add(self.txt_thermo_pos, 0,
                                wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            for i in range(3):
                self.bsz_thermo.Add(
                    self.szr_thermo_pos[i], 0, wx.EXPAND | wx.ALL, 5)
                self.szr_thermo_pos[i].Add(self.lbl_thermo_pos[i])
                self.szr_thermo_pos[i].Add(
                    self.txc_thermo_pos[i], flag=wx.EXPAND)

            self.select_sizer.AddSpacer(15)
            self.select_sizer.Add(self.bsz_hygro, flag=wx.EXPAND)
            self.bsz_hygro.Add(self.cho_hygro, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_hygro.Add(self.bmp_hygro, 0, wx.EXPAND | wx.ALL, 5)
            self.bsz_hygro.Add(self.txt_hygro_manu, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txc_hygro_manu, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txt_hygro_make, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txc_hygro_make, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txt_hygro_path, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txc_hygro_path, 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
            self.bsz_hygro.Add(self.txt_hygro_pos, 0,
                               wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
            for i in range(3):
                self.bsz_hygro.Add(
                    self.szr_hygro_pos[i], 0, wx.EXPAND | wx.ALL, 5)
                self.szr_hygro_pos[i].Add(self.lbl_hygro_pos[i])
                self.szr_hygro_pos[i].Add(
                    self.txc_hygro_pos[i], flag=wx.EXPAND)

            # set design
            self.title.SetFont(Font_Title())

            # event bindings
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)
            self.Bind(wx.EVT_CHOICE, self.OnSelection, self.cho_sonic)
            self.Bind(wx.EVT_CHOICE, self.OnSelection, self.cho_thermo)
            self.Bind(wx.EVT_CHOICE, self.OnSelection, self.cho_hygro)
            for i in range(3):
                self.Bind(wx.EVT_TEXT, self.OnEdit, self.txc_sonic_pos[i])
                self.Bind(wx.EVT_TEXT, self.OnEdit, self.txc_thermo_pos[i])
                self.Bind(wx.EVT_TEXT, self.OnEdit, self.txc_hygro_pos[i])

        def get_settings(self):
            try:
                i = self.wizard.guilist.get('SonCal.QQType', kind='int')
            except:
                i = 0
            self.code_sonic = ApCodes[i]
            logger.debug('SonCal.QQType = %i -> code_sonic = %s' %
                          (i, self.code_sonic))
            try:
                i = self.wizard.guilist.get('CoupCal.QQType', kind='int')
            except:
                i = 0
            self.code_thermo = ApCodes[i]
            logger.debug('CoupCal.QQType = %i -> code_thermo = %s' %
                          (i, self.code_thermo))
            try:
                i = self.wizard.guilist.get('HygCal.QQType', kind='int')
            except:
                i = 0
            self.code_hygro = ApCodes[i]
            logger.debug('HygCal.QQType = %i -> code_hygro = %s' %
                          (i, self.code_hygro))
            # Co2Cal.QQType ignored since all known devices are dual-use
            try:
                v = self.wizard.guilist.get('SonCal.QQYaw', kind='int')
            except:
                v = 0.
            self.yaw_sonic = v
            logger.debug('SonCal.QQYaw = %f -> code_hygro = %f' %
                          (v, self.yaw_sonic))
            axname = ['QQX', 'QQY', 'QQZ']
            for i in range(3):
                key = 'SonCal.'+axname[i]
                try:
                    v = self.wizard.guilist.get(key, kind='float')
                except:
                    v = 0.
                self.pos_sonic[i] = str(v)
                logger.debug('%s -> pos_sonic[%i] = %f' % (key, i, v))
            for i in range(3):
                key = 'CoupCal.'+axname[i]
                try:
                    v = self.wizard.guilist.get(key, kind='float')
                except:
                    v = 0.
                self.pos_thermo[i] = str(v)
                logger.debug('%s -> pos_thermo[%i] = %f' % (key, i, v))
            for i in range(3):
                key = 'HygCal.'+axname[i]
                try:
                    v = self.wizard.guilist.get(key, kind='float')
                except:
                    v = 0.
                self.pos_hygro[i] = str(v)
                logger.debug('%s -> pos_hygro[%i] = %f' % (key, i, v))

        def store_settings(self):
            axname = ['QQX', 'QQY', 'QQZ']
            self.wizard.guilist.put('SonCal.QQType', str(
                ApCodes.index(self.code_sonic)))
            self.wizard.guilist.put('CoupCal.QQType', str(
                ApCodes.index(self.code_thermo)))
            self.wizard.guilist.put('HygCal.QQType', str(
                ApCodes.index(self.code_hygro)))
            self.wizard.guilist.put('Co2Cal.QQType', str(
                ApCodes.index(self.code_hygro)))
            for k in ['Son', 'Coup', 'Hyg', 'Co2']:
                logger.debug('stored '+k+'Cal.QQType %s' %
                              self.wizard.guilist.get(k+'Cal.QQType'))

            # only used if fixed angles are selected
            self.wizard.guilist.put('SonCal.QQPitch', str(0.0))
            # only used if fixed angles are selected
            self.wizard.guilist.put('SonCal.QQRoll', str(0.0))
            self.wizard.guilist.put('SonCal.QQYaw', str(self.yaw_sonic))
            for k in ['Pitch', 'Roll', 'Yaw']:
                logger.debug('stored SonCal.QQ'+k+' %s' %
                              self.wizard.guilist.get('SonCal.QQ'+k))

            self.wizard.guilist.put(
                'SonCal.QQPath', str(ApPath[self.code_sonic]))
            # Coup.QQPath is not used
            self.wizard.guilist.put(
                'HygCal.QQPath', str(ApPath[self.code_hygro]))
            self.wizard.guilist.put(
                'Co2Cal.QQPath', str(ApPath[self.code_hygro]))
            for k in ['Son', 'Hyg', 'Co2']:
                logger.debug('stored '+k+'Cal.QQPath %s' %
                              self.wizard.guilist.get(k+'Cal.QQPath'))

            for i in range(3):
                self.wizard.guilist.put(
                    'SonCal.'+axname[i], str(float(self.pos_sonic[i])))
                self.wizard.guilist.put(
                    'CoupCal.'+axname[i], str(float(self.pos_thermo[i])))
                self.wizard.guilist.put(
                    'HygCal.'+axname[i], str(float(self.pos_hygro[i])))
                self.wizard.guilist.put(
                    'Co2Cal.'+axname[i], str(float(self.pos_hygro[i])))
                for k in ['Son', 'Coup', 'Hyg', 'Co2']:
                    logger.debug(
                        'stored '+k+'Cal.'+axname[i]+' %s' % self.wizard.guilist.get(k+'Cal.'+axname[i]))

        def Update(self):
            self.cho_sonic.SetStringSelection(self.code_sonic)
            self.cho_thermo.SetStringSelection(self.code_thermo)
            self.cho_hygro.SetStringSelection(self.code_hygro)

            self.bmp_sonic.SetBitmap(self.aparatus_bmp[self.code_sonic])
            self.bmp_thermo.SetBitmap(self.aparatus_bmp[self.code_thermo])
            self.bmp_hygro.SetBitmap(self.aparatus_bmp[self.code_hygro])

            self.txc_sonic_manu.SetValue(ApCompany[self.code_sonic])
            self.txc_thermo_manu.SetValue(ApCompany[self.code_thermo])
            self.txc_hygro_manu.SetValue(ApCompany[self.code_hygro])

            self.txc_sonic_make.SetValue(ApMake[self.code_sonic])
            self.txc_thermo_make.SetValue(ApMake[self.code_thermo])
            self.txc_hygro_make.SetValue(ApMake[self.code_hygro])

            self.txc_sonic_path.SetValue(str(ApPath[self.code_sonic]))
            if self.code_sonic in ['Son3Dcal', 'GenericSonic']:
                self.txc_sonic_path.SetEditable(True)
            else:
                self.txc_sonic_path.SetEditable(False)
            self.txc_hygro_path.SetValue(str(ApPath[self.code_hygro]))
            if self.code_hygro in ['MierijLyma']:
                self.txc_hygro_path.SetEditable(True)
            else:
                self.txc_hygro_path.SetEditable(False)

            for i in range(3):
                self.txc_sonic_pos[i].ChangeValue(self.pos_sonic[i])
                self.txc_thermo_pos[i].ChangeValue(self.pos_thermo[i])
                self.txc_hygro_pos[i].ChangeValue(self.pos_hygro[i])

        def Enter(self, event):
            self.get_settings()
            self.Update()

        def OnSelection(self, event):
            self.code_sonic = self.cho_sonic.GetStringSelection()
            self.code_thermo = self.cho_thermo.GetStringSelection()
            self.code_hygro = self.cho_hygro.GetStringSelection()
            logger.debug('selection changed')
            self.Update()

        def OnEdit(self, event):
            for i in range(3):
                logger.debug(self.txc_sonic_pos[i].GetValue())
                self.pos_sonic[i] = self.txc_sonic_pos[i].GetValue()
                try:
                    _ = float(self.pos_sonic[i])
                except:
                    self.txc_sonic_pos[i].SetBackgroundColour(wx.RED)
                else:
                    self.txc_sonic_pos[i].SetBackgroundColour(
                        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
                self.pos_thermo[i] = self.txc_thermo_pos[i].GetValue()
                try:
                    _ = float(self.pos_thermo[i])
                except:
                    self.txc_thermo_pos[i].SetBackgroundColour(wx.RED)
                else:
                    self.txc_thermo_pos[i].SetBackgroundColour(
                        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
                self.pos_hygro[i] = self.txc_hygro_pos[i].GetValue()
                try:
                    _ = float(self.pos_hygro[i])
                except:
                    self.txc_hygro_pos[i].SetBackgroundColour(wx.RED)
                else:
                    self.txc_hygro_pos[i].SetBackgroundColour(
                        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        def Leave(self, event):
            self.store_settings()

    # ----------------------------------------------------------------------
    class Page_Intervals(wx.adv.WizardPageSimple):

        interval_avg = None
        interval_plfit = None
        unit_avg = None
        unit_plfit = None

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step7: Select intervals',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))

            self.box_averaging = wx.StaticBox(
                self, wx.ID_ANY, label="Averaging interval")
            self.bsz_averaging = wx.StaticBoxSizer(
                self.box_averaging, wx.HORIZONTAL)
            self.txt_averaging = wx.StaticText(self, wx.ID_ANY, 'Duration:')
            self.txc_averaging = wx.TextCtrl(self, wx.ID_ANY, '',
                                             size=(100, -1),
                                             style=wx.TE_PROCESS_ENTER)
            self.cbx_averaging = wx.ComboBox(self, wx.ID_ANY,
                                             choices=['s', 'm', 'h', 'd', 'w'],
                                             style=wx.CB_DROPDOWN | wx.CB_READONLY)

            self.box_planarfit = wx.StaticBox(
                self, wx.ID_ANY, label="Planar-fit interval")
            self.bsz_planarfit = wx.StaticBoxSizer(
                self.box_planarfit, wx.HORIZONTAL)
            self.txt_planarfit = wx.StaticText(self, wx.ID_ANY, 'Duration:')
            self.txc_planarfit = wx.TextCtrl(self, wx.ID_ANY, '',
                                             size=(100, -1),
                                             style=wx.TE_PROCESS_ENTER)
            self.cbx_planarfit = wx.ComboBox(self, wx.ID_ANY,
                                             choices=['s', 'm', 'h', 'd', 'w'],
                                             style=wx.CB_DROPDOWN | wx.CB_READONLY)

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(
                self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=10)

            self.right_sizer.Add(self.bsz_averaging,
                                 flag=wx.EXPAND | wx.ALL, border=5)
            self.bsz_averaging.Add(
                self.txt_averaging, flag=wx.EXPAND | wx.ALL, border=10)
            self.bsz_averaging.AddSpacer(10)
            self.bsz_averaging.Add(
                self.txc_averaging, flag=wx.EXPAND | wx.ALL, border=10)
            self.bsz_averaging.Add(self.cbx_averaging,
                                   flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, border=10)

            self.right_sizer.Add(self.bsz_planarfit,
                                 flag=wx.EXPAND | wx.ALL, border=5)
            self.bsz_planarfit.Add(
                self.txt_planarfit, flag=wx.EXPAND | wx.ALL, border=10)
            self.bsz_planarfit.AddSpacer(10)
            self.bsz_planarfit.Add(
                self.txc_planarfit, flag=wx.EXPAND | wx.ALL, border=10)
            self.bsz_planarfit.Add(self.cbx_planarfit,
                                   flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, border=10)

            # set design
            self.title.SetFont(Font_Title())

            # event bindings
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)
            self.Bind(wx.EVT_TEXT, self.OnEdit, self.txc_averaging)
            self.Bind(wx.EVT_TEXT, self.OnEdit, self.txc_planarfit)
            self.Bind(wx.EVT_COMBOBOX, self.OnUnit, self.cbx_averaging)
            self.Bind(wx.EVT_COMBOBOX, self.OnUnit, self.cbx_planarfit)

        def get_settings(self):
            # get value
            try:
                i = self.wizard.guilist.get('AvgInterval', kind='int')
            except:
                i = 0
            self.interval_avg = i
            logger.debug('AvgInterval = %i s' % self.interval_avg)
            # convert longer intervals to longer units
            if self.interval_avg % 3600 == 0:
                self.unit_avg = 'h'
                self.interval_avg = self.interval_avg/3600
            elif self.interval_avg % 60 == 0:
                self.unit_avg = 'm'
                self.interval_avg = self.interval_avg/60
            else:
                self.unit_avg = 's'

            try:
                i = self.wizard.guilist.get('PlfitInterval', kind='int')
            except:
                i = 0
            # convert days to seconds
            self.interval_plfit = i*86400
            logger.debug('PlfitInterval = %i s' % self.interval_plfit)
            # convert longer intervals to longer units
            if self.interval_plfit % (7*86400) == 0:
                self.unit_plfit = 'w'
                self.interval_plfit = self.interval_plfit/(7*86400)
            elif self.interval_plfit % 86400 == 0:
                self.unit_plfit = 'd'
                self.interval_plfit = self.interval_plfit/86400
            elif self.interval_plfit % 3600 == 0:
                self.unit_plfit = 'h'
                self.interval_plfit = self.interval_plfit/3600
            elif self.interval_plfit % 60 == 0:
                self.unit_plfit = 'm'
                self.interval_plfit = self.interval_plfit/60
            else:
                self.unit_plfit = 's'

        def store_settings(self):
            self.cbx_averaging.SetValue('s')
            self.cbx_planarfit.SetValue('d')
            self.OnUnit(0)

            self.wizard.guilist.put('AvgInterval', str(
                int(float(self.txc_averaging.GetValue()))))
            logger.debug('stored AvgInterval %s s' %
                          self.wizard.guilist.get('AvgInterval'))

            self.wizard.guilist.put('PlfitInterval', str(
                float(self.txc_planarfit.GetValue())))
            logger.debug('stored PlfitInterval %s d' %
                          self.wizard.guilist.get('PlfitInterval'))

        def Update(self):
            self.txc_averaging.ChangeValue(str(self.interval_avg))
            self.cbx_averaging.SetValue(self.unit_avg)
            self.txc_planarfit.ChangeValue(str(self.interval_plfit))
            self.cbx_planarfit.SetValue(self.unit_plfit)

        def Enter(self, event):
            self.get_settings()
            self.Update()

        def OnEdit(self, event):
            try:
                self.interval_avg = int(self.txc_averaging.GetValue())
                if self.interval_avg <= 0:
                    raise ValueError
            except:
                self.txc_averaging.SetBackgroundColour(wx.RED)
            else:
                self.txc_averaging.SetBackgroundColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            self.unit_avg = self.cbx_averaging.GetValue()

            try:
                self.interval_plfit = float(self.txc_planarfit.GetValue())
                if self.interval_plfit <= 0:
                    raise ValueError
            except:
                self.txc_planarfit.SetBackgroundColour(wx.RED)
            else:
                self.txc_planarfit.SetBackgroundColour(
                    wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            self.unit_plfit = self.cbx_planarfit.GetValue()

        def OnUnit(self, event):
            mult = {'s': 1,
                    'm': 60,
                    'h': 3600,
                    'd': 86400,
                    'w': 604800}

            # averaging
            mult_avg_old = mult[self.unit_avg]
            unit_avg_new = self.cbx_averaging.GetValue()
            mult_avg_new = mult[unit_avg_new]
            interval_avg_new = self.interval_avg*mult_avg_old/mult_avg_new
            if interval_avg_new > 0.1:
                self.interval_avg = interval_avg_new
                self.unit_avg = unit_avg_new

            # planar fit
            mult_plfit_old = mult[self.unit_plfit]
            unit_plfit_new = self.cbx_planarfit.GetValue()
            mult_plfit_new = mult[unit_plfit_new]
            interval_plfit_new = self.interval_plfit*mult_plfit_old/mult_plfit_new
            if interval_plfit_new > 0.1:
                self.interval_plfit = interval_plfit_new
                self.unit_plfit = unit_plfit_new
            #
            self.Update()

        def Leave(self, event):
            ok = True
            if ok:
                self.store_settings()
            else:
                event.Veto()

    # ----------------------------------------------------------------------
    class Page_Confirm(wx.adv.WizardPageSimple):

        # ----------------------------------------------------------------------
        def __init__(self, parent):
            # call generic constructor
            wx.adv.WizardPageSimple.__init__(self, parent)
            self.wizard = parent

            # define the elements
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)
            self.title = wx.StaticText(self, wx.ID_ANY,
                                       'Step8: Confirm',
                                       style=wx.ALIGN_CENTRE,
                                       size=(-1, Font_Title().GetPointSize()*2))

            self.box_ready = wx.StaticBox(self, wx.ID_ANY, label="Ready to go")
            self.bsz_ready = wx.StaticBoxSizer(self.box_ready, wx.HORIZONTAL)
            self.txt_ready = wx.StaticText(self, wx.ID_ANY, '''
      Select which action you want to take now.\n
      If you wish to refine configuration setting before running
      the actual processing, you should\n
      1) just save the created settings and return to the main window\n
      2) store settings and start processing\n
      Clicking "Finish" will immediately start the processing.
      ''')
            self.rbx_defs = wx.RadioBox(self, wx.ID_ANY, label='Select action',
                                        choices=['just store configuration',
                                                 'start processing now'],
                                        style=wx.RA_VERTICAL)

            # assemble the page
            self.SetSizer(self.right_sizer)

            self.right_sizer.Add(
                self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=10)

            self.right_sizer.Add(
                self.bsz_ready, flag=wx.EXPAND | wx.ALL, border=5)
            self.bsz_ready.Add(
                self.txt_ready, flag=wx.EXPAND | wx.ALL, border=10)

            self.right_sizer.AddSpacer(10)
            self.right_sizer.Add(self.rbx_defs, 0, wx.EXPAND | wx.ALL, 5)
            self.right_sizer.AddSpacer(10)

            # set design
            self.title.SetFont(Font_Title())

            # event bindings
            self.Bind(wx.EVT_RADIOBOX, self.Update, self.rbx_defs)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.Enter)
            self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.Leave)

            # fill in initially

        def Enter(self, event):
            self.rbx_defs.SetSelection(0)

        def Update(self, event=0):
            n = self.rbx_defs.GetSelection()
            actions = ['save', 'execute']
            if n in range(len(actions)):
                self.wizard.action = actions[n]
            else:
                raise ValueError('internal error (unknown action)')

        def Leave(self, event):
            self.Update()

    # ----------------------------------------------------------------------

    class Wizard(wx.adv.Wizard):
        action = None

        def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                     bitmap=wx.NullBitmap, pos=wx.DefaultPosition,
                     style=wx.DEFAULT_DIALOG_STYLE, pars=None):
            # original constructor
            wx.adv.Wizard.__init__(self, parent, id, title, bitmap, pos, style)
            # custom additions
            if pars is None:
                pars = {}
            self.guilist = pars
            self.storage = dict()
            for k, v in self.guilist.items():
                logger.insane('old value: {} = {}'.format(k, v))
            # catch the events
            self.Bind(wx.adv.EVT_WIZARD_CANCEL, self.on_cancel)

        def on_cancel(self, evt):
            # Cancel button has been pressed
            logger.info('cancelled by user')
            self.Destroy()

    def setup_wizard(guilist):
        wizard = Wizard(None, -1, "EC-PeT Setup Wizard",
                        bitmap=wx.Bitmap(os.path.join(imagepath, 'gui-image_text.png'),
                                         wx.BITMAP_TYPE_PNG), pars=guilist)
        page1 = Page_Welcome(wizard)
        page2 = Page_Dirs(wizard)
        page3 = Page_Files(wizard)
        page4 = Page_Columns(wizard)
        page5 = Page_Time(wizard)
        page6 = Page_Location(wizard)
        page7 = Page_Apparatus(wizard)
        page8 = Page_Intervals(wizard)
        page9 = Page_Confirm(wizard)

        wx.adv.WizardPageSimple.Chain(page1, page2)
        wx.adv.WizardPageSimple.Chain(page2, page3)
        wx.adv.WizardPageSimple.Chain(page3, page4)
        wx.adv.WizardPageSimple.Chain(page4, page5)
        wx.adv.WizardPageSimple.Chain(page5, page6)
        wx.adv.WizardPageSimple.Chain(page6, page7)
        wx.adv.WizardPageSimple.Chain(page7, page8)
        wx.adv.WizardPageSimple.Chain(page8, page9)
        wizard.FitToPage(page1)

        wizard.RunWizard(page1)

        guilist = wizard.guilist
        action = wizard.action
        logger.debug('setup_wizard: action = %s' % action)
        wizard.Destroy()
        return guilist, action

    class Project(object):
        def __init__(self, name=None):
            self.conf = ecconfig.Config()
            self.stage = None
            self.changed = bool()
            self.file = None
            if name is not None:
                self.load(name)

        def load(self, name):
            ecdb.dbfile = name
            self.conf = ecdb.conf_from_db()
            logger.insane('loaded config: %s' % str(self.conf._dict))
            self.changed = False
            tables = ecdb.list_tables()
            logger.insane(tables)
            if 'out:files' in tables:
                self.stage = 'out'
            elif 'post:intervals' in tables:
                self.stage = 'post'
            elif 'flux:intervals' in tables:
                self.stage = 'flux'
            elif 'plan:intervals' in tables:
                self.stage = 'plan'
            elif 'pre:intervals' in tables:
                self.stage = 'pre'
            else:
                self.stage = 'start'
            logger.insane(self.stage)
            self.file = os.path.abspath(name)

        def store(self):
            ecdb.conf_to_db(self.conf.to_dict())
            self.changed = False

    class ProgressBox(wx.Dialog):

        def __init__(self):
            wx.Dialog.__init__(self, None, title="Progress")

            self.info = wx.StaticText(self, wx.ID_ANY,
                                      label="Running stage:        ",
                                      style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
            self.stage = wx.Gauge(self, range=len(ec.stages))
            self.number = wx.StaticText(self, wx.ID_ANY,
                                        label="completed:       ",
                                        style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
            self.progress = wx.Gauge(self, range=100)
            self.percent = 0.
            self.progress.SetValue(int(self.percent))

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddStretchSpacer()
            sizer.Add(self.info, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            sizer.Add(self.stage, 0, wx.EXPAND)
            sizer.AddSpacer(20)
            sizer.Add(self.number, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            sizer.Add(self.progress, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            self.SetSizer(sizer)
            sizer.Layout()

            # create a pubsub receiver
            pub.subscribe(self.noProgress,  "pulse")
            pub.subscribe(self.setProgress, "progress")
            pub.subscribe(self.incProgress, "increment")
            pub.subscribe(self.setStage,    "stage")
            pub.subscribe(self.Done,        "done")

        def noProgress(self):
            logger.insane('ProgressBox.Pulse')
            self.progress.Pulse()
            wx.YieldIfNeeded()

        def setProgress(self, msg):
            logger.insane('ProgressBox.SetProgress')
            try:
                self.percent = float(msg)
            except:
                self.percent = 0.
            if self.percent > 100.:
                self.percent = 100.
            if self.percent < 0.:
                self.percent = 0.
            self.number.SetLabel("completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def incProgress(self, msg):
            logger.insane('ProgressBox.incProgress')
            try:
                inc = float(msg)
            except:
                inc = 0
            self.percent += inc
            logger.insane(str(self))
            logger.debug(
                'percent: {:5.2f}% ( + {:.2f}% )'.format(self.percent, inc))
            if self.percent > 100.:
                self.percent = 100.
            if self.percent < 0.:
                self.percent = 0.
            self.number.SetLabel("completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def setStage(self, msg):
            logger.insane('ProgressBox.SetStage')
            if msg in ec.stages:
                sn = r_labels[msg]
                st = ec.stages.index(msg)
                per = 0.
            elif msg in range(len(ec.stages)):
                sn = r_labels[ec.stages[msg]]
                st = msg
                per = 0.
            else:
                sn = ''
                st = 0
                per = 0.
            self.info.SetLabel("Running stage: {:s}".format(sn))
            self.stage.SetValue(st)
            self.percent = per
            self.number.SetLabel("completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def Done(self):
            logger.insane('ProgressBox.Done')
            self.Destroy()


# ----------------------------------------------------------------------


    class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin, listmix.ColumnSorterMixin):
        '''
        TextEditMixin allows any column to be edited.
        '''

        def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                     size=wx.DefaultSize, style=0):
            """Constructor"""

            wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
            listmix.TextEditMixin.__init__(self)
            self.curCol = None
            self.curRow = None
            self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)

        def OpenEditor(self, col, row):
            """allow only editing of column #2 (Values)"""
            logger.insane('CLICK column {:d}, row {:d}'.format(col, row))
            if col != 3:
                logger.insane(
                    'column {:d}, row {:d} not editable'.format(col, row))
                return

            # original code follows here

            # give the derived class a chance to Allow/Veto this edit.
            evt = wx.ListEvent(
                wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetId())
            evt.Index = row
            evt.Column = col
            item = self.GetItem(row, col)
            evt.Item.SetId(item.GetId())
            evt.Item.SetColumn(item.GetColumn())
            evt.Item.SetData(item.GetData())
            evt.Item.SetText(item.GetText())
            ret = self.GetEventHandler().ProcessEvent(evt)
            if ret and not evt.IsAllowed():
                return   # user code doesn't allow the edit.

            if self.GetColumn(col).Align != self.col_style:
                self.make_editor(self.GetColumn(col).Align)

            editor = self.editor
            # original code  causes GTK warning and no editor is shown
            # this is the hack:
            rect = wx.Rect()
            self.GetSubItemRect(row, col, rect)
            editor.SetSize(rect)
            # end hack

            editor.SetValue(self.GetItem(row, col).GetText())
            editor.Show()
            editor.Raise()
            editor.SetSelection(-1, -1)
            editor.SetFocus()

            self.curRow = row
            self.curCol = col

        def OnScroll(self, event):
            ''' lock scrolling during editing. '''
            if hasattr(self, 'editor') and self.editor.Shown is True:
                pass
            else:
                event.Skip()


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


    class Run_Window(wx.Frame):
        ''' EC-PeT main mindow. '''
        #
        #

        def __init__(self, parent, id=-1, title=wx.EmptyString,
                     pos=wx.DefaultPosition, size=(640, 480),
                     style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr,
                     opts=None):
            wx.Frame.__init__(self, None, id, title, pos, size, style, name)
            # - - - - - - - - - - -
            # define window elements
            #
            # Menu bar
            #
            if opts is None:
                opts = {}
            self.menuBar = wx.MenuBar()
            self.m_file = wx.Menu()
            self.m_new = self.m_file.Append(
                wx.ID_ANY, "&New Project", "Create new project.")
            self.Bind(wx.EVT_MENU, self.OnNew, self.m_new)
            self.m_open = self.m_file.Append(
                wx.ID_ANY, "&Open Project", "Open existing project.")
            self.Bind(wx.EVT_MENU, self.OnOpen, self.m_open)
            self.m_close = self.m_file.Append(
                wx.ID_ANY, "&Close Project", "Close current project.")
            self.Bind(wx.EVT_MENU, self.OnClose, self.m_close)
            self.m_exit = self.m_file.Append(
                wx.ID_ANY, "E&xit\tAlt-X", "Close window and exit program.")
            self.Bind(wx.EVT_MENU, self.OnExit, self.m_exit)
            self.menuBar.Append(self.m_file, "&File")
            self.m_conf = wx.Menu()
            self.m_import = self.m_conf.Append(
                wx.ID_ANY, "&Import", "Import a configuration file.")
            self.Bind(wx.EVT_MENU, self.OnImport, self.m_import)
            self.m_modify = self.m_conf.Append(
                wx.ID_ANY, "&Modify", "Modify current configuration.")
            self.Bind(wx.EVT_MENU, self.OnModify, self.m_modify)
            self.m_create = self.m_conf.Append(
                wx.ID_ANY, "&Create", "Create new configuration.")
            self.Bind(wx.EVT_MENU, self.OnCreate, self.m_create)
#            self.m_store = self.m_conf.Append(
#                wx.ID_ANY, "&Store", "Store configuration in project.")
#            self.Bind(wx.EVT_MENU, self.OnStore, self.m_store)
            self.m_export_mini = self.m_conf.Append(
                wx.ID_ANY, "&Export minimal", "Export minimal configuration to file.")
            self.Bind(wx.EVT_MENU, self.OnExportMini, self.m_export_mini)
            self.m_export_full = self.m_conf.Append(
                wx.ID_ANY, "&Export full", "Export full configuration to file.")
            self.Bind(wx.EVT_MENU, self.OnExportFull, self.m_export_full)
            self.menuBar.Append(self.m_conf, "&Config")
            self.m_about = wx.Menu()
            self.m_status = self.m_about.Append(
                wx.ID_ANY, "&Status", "Program status and environment.")
            self.Bind(wx.EVT_MENU, self.OnStatus, self.m_status)
            self.menuBar.Append(self.m_about, "&About")
            self.SetMenuBar(self.menuBar)
            #
            # status bar
            #
            self.statusbar = self.CreateStatusBar(2)
            #
            # main content
            #
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            box = wx.BoxSizer(wx.VERTICAL)

            logo = wx.Bitmap(os.path.join(imagepath, 'gui-image_text.png'),
                             wx.BITMAP_TYPE_PNG)
            self.pic = wx.StaticBitmap(self, wx.ID_ANY, logo)

            sizer.Add(self.pic, 0, wx.ALL, 5)

            self.conlist = EditableListCtrl(self, wx.ID_ANY,
                                            style=wx.LC_REPORT,
                                            size=(640, 400))
            self.conlist.InsertColumn(0, 'Group')
            self.conlist.InsertColumn(1, 'Token')
            self.conlist.InsertColumn(2, '*')
            self.conlist.InsertColumn(3, 'Value')
            self.conlist.SetColumnWidth(0, 80)
            self.conlist.SetColumnWidth(1, 80)
            self.conlist.SetColumnWidth(2, 15)
            self.conlist.SetColumnWidth(3, 465)
            self.conlist.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit)
            self.conlist.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

            box.Add(self.conlist, 0, wx.EXPAND | wx.ALL, 5)

            self.progress = wx.Gauge(self, wx.ID_ANY,
                                     size=(640, 20),
                                     style=wx.GA_HORIZONTAL,
                                     range=100)
            box.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)

            szr_buttons = wx.BoxSizer(wx.HORIZONTAL)

            self.radio = wx.RadioBox(self, wx.ID_ANY, choices=[
                                     r_labels[x] for x in ec.stages])
            szr_buttons.Add(self.radio, flag=wx.ALIGN_CENTRE_VERTICAL)

            szr_buttons.AddStretchSpacer()
            self.btn_start = wx.Button(self, wx.ID_ANY, label="START")
            self.Bind(wx.EVT_BUTTON, self.OnRun, self.btn_start)
            szr_buttons.Add(self.btn_start, flag=wx.ALIGN_CENTRE_VERTICAL)

            box.Add(szr_buttons, 0, wx.EXPAND | wx.ALL, 5)

            sizer.Add(box, 0, wx.ALL, 5)
            self.SetAutoLayout(True)
            self.SetSizer(sizer)
            self.Fit()

            self.Layout()

            # startup
            self.options = opts
            if 'project' in self.options and self.options['project'] is not None:
                self.project = Project(self.options['project'])
            else:
                self.project = None

            self.sortby = [2, 1]

            self.Update()

        # ---------------
        # object methods
        #
        def Update(self):
            logger.debug('current dir: {:s}'.format(os.getcwd()))
            if self.project is None:
                #
                # disable controls
                self.m_close.Enabled = False
                self.m_import.Enabled = False
                self.m_create.Enabled = False
#                self.m_store.Enabled = False
                self.m_modify.Enabled = False
                self.m_export_mini.Enabled = False
                self.m_export_full.Enabled = False
                #
                # empty status bar
                self.statusbar.SetStatusText('no project', 1)
                #
                # empty process completeness
                self.progress.SetValue(0)
                #
                # empty config display
                self.conlist.DeleteAllItems()
                self.sortby = [2, 1]
                #
                # disable start options
                for i in range(len(ec.stages)):
                    self.radio.EnableItem(i, False)
                self.radio.Enabled = False
                self.btn_start.Enabled = False
            else:
                #
                # enable controls
                self.m_close.Enabled = True
                self.m_import.Enabled = True
                self.m_create.Enabled = True
                self.m_modify.Enabled = True
#                self.m_store.Enabled = True
                self.m_export_mini.Enabled = True
                self.m_export_full.Enabled = True
                #
                # show name in status bar
                self.statusbar.SetStatusText(
                    os.path.basename(self.project.file), 1)
                #
                # display config
                self.DisplayConfig()
                #
                # show process completeness
                perc = int(self.progress.GetRange()*(float(ec.stages.index(self.project.stage))
                                                     / float(len(ec.stages)-1)))
                logger.insane('percentage: {:d} ({:d}/{:d})'.format(
                    perc, ec.stages.index(self.project.stage), len(ec.stages)-1))
                self.progress.SetValue(perc)
                #
                # enable start options
                self.radio.Enabled = True
                for i in range(len(ec.stages)):
                    if ec.stages.index(self.project.stage) >= i-1:
                        self.radio.EnableItem(i, True)
                    else:
                        self.radio.EnableItem(i, False)
                self.btn_start.Enabled = True
            wx.YieldIfNeeded()

        def modifyConfig(self, reset=False):
            # make reduced config containing only the keys in gui_set
            if reset:
                # do not reset project config until wizard finishes,
                # the user will his config if he aborts the wizard.
                oldconf = ecconfig.Config()
            else:
                oldconf = self.project.conf
            guilist = ecconfig.Config({k: oldconf._dict[k] for k in gui_set},
                                      reduced=True)
            # call setup_wizard that modifies guilist
            guilist, action = setup_wizard(guilist)
            #
            # now we can reset the project config
            if reset:
                self.project.conf = ecconfig.Config()
            # put new values into project config
            for k in guilist.keys():
                if k not in self.project.conf.keys():
                    logger.error(f'unknown key {k} returned by Wizard')
                    raise ValueError
                v = guilist.get(k)
                if self.project.conf.get(k) != v:
                    # value was changes  by wizard
                    self.project.changed = True
                    self.project.conf.put(k, v)
                    logger.debug('new value: {} = {}'.format(k, v))
            try:
                self.project.conf = ecconfig.check_basic(self.project.conf,
                                                         correct=True)
            except ecconfig.ConfigError as e:
                wx.MessageBox(str(e), 'Configuration Error',
                              wx.ICON_ERROR | wx.OK, self)
            self.Update()

        def ImSure(self):
            if self.project is not None and self.project.changed:
                if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                                 wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                    return False
                else:
                    return True
            else:
                return True

        def DisplayConfig(self):
            row = 0
            sortarray = []
            for k in self.project.conf.keys():
                v = self.project.conf.get(k)
                if '.' in k:
                    group, token = k.split('.', 1)  # get characters before '.'
                else:
                    group = ''              # sort blank at one end
                    token = k
                if self.project.conf.is_default(k):
                    isdefault = 1
                else:
                    isdefault = 0
                sortarray.append((group, token, isdefault, v))
            for by in self.sortby:
                # by is 1-based, negative means reversed sort
                sortarray = sorted(
                    sortarray, key=lambda x: x[abs(by)-1], reverse=(by < 0))
            # (re) fill listctrl
            self.conlist.DeleteAllItems()
            for k in sortarray:
                g, t, d, v = k
                if d == 1:
                    self.conlist.Append((g, t, '', v))
                    self.conlist.SetItemTextColour(
                        row, wx.TheColourDatabase.Find('GREY'))
                else:
                    self.conlist.Append((g, t, '*', v))
                    self.conlist.SetItemTextColour(
                        row, wx.TheColourDatabase.Find('BLACK'))
                row += 1

        def OnColClick(self, event):
            # Get the column clicked (values in array are 1-based to have a meaningful sign)
            col = event.GetColumn() + 1
            # reverse sort order if column is clicked again
            if abs(col) == abs(self.sortby[-1]):
                self.sortby[-1] = -self.sortby[-1]
            else:
                self.sortby.append(col)
            # limit length of array
            if len(self.sortby) > 4:
                self.sortby = self.sortby[-4:]
            self.Update()

        def OnEndEdit(self, event):
            row_id = event.GetIndex()  # Get the current row
#      col_id = event.GetColumn () #Get the current column
            new_data = event.GetLabel()  # Get the changed data

            # construct key of changed value
            g = self.conlist.GetItem(row_id, 0).GetText()
            t = self.conlist.GetItem(row_id, 1).GetText()
            if g != '':
                key = '.'.join((g, t))
            else:
                key = t
            old_data = self.project.conf.get(key)
            self.project.conf.put(key, new_data)
            logger.debug('config value "%s" changed from "%s" to "%s"' % (
                key, old_data, new_data))
            self.project.store()
            self.Update()

        def OnExit(self, event):
            if self.ImSure():
                self.Destroy()

        def OnStatus(self, event):
            self.statusbar.PushStatusText('Status')
            ver = {}
            ver['python'] = sys.version.split()[0]
            ver['numpy'] = ver_np.version
            ver['pandas'] = ver_pd
            ver['scipy'] = ver_scipy
            ver['wxPython'] = wx.__version__
            if have_com:
                ver['pubsub'] = ver_pub
            else:
                ver['pubsub'] = 'not available'
            if have_mpl:
                ver['matplotlib'] = ver_mpl
            else:
                ver['matplotlib'] = 'not vailable'

            message = ('EC-PeT -- ' +
                       'elaboratio concursuum perturbationum Treverensis *)\n' +
                       'Release: '+version.__release__+'\n' +
                       '(C) 2017-2021 Clemens Drüe, Universität Trier\n' +
                       '\n' +
                       'Versions:\n'
                       )
            for k, v in ver.items():
                message += f'{k}: {v}\n'
            msg = wx.MessageDialog(self,
                                   message,
                                   style=wx.OK | wx.ICON_INFORMATION | wx.CENTRE
                                   )
            msg.ShowModal()
            self.statusbar.PopStatusText()

        def OnNew(self, event):
            self.statusbar.PushStatusText('OnNew')
            if self.ImSure():
                # ask the user what new file to open
                wildcard = 'EC-PeT project (.ecp)|*.ecp|SQLite3 files (.sqlite)|*.sqlite'
                with wx.FileDialog(self, "Open project file",
                                   wildcard=wildcard,
                                   style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # file chosen by the user
                    pathname = fileDialog.GetPath()

                    # every second element from wildcard string is an extension
                    ext = wildcard.replace('*', '').split('|')[1::2]
                    # get the extension chosen by user
                    iext = fileDialog.GetFilterIndex()
                    # make sure pathname ends with a proper extension:
                    if not pathname.endswith(ext[iext]):
                        pathname = pathname+ext[iext]

                os.chdir(os.path.dirname(pathname))
                self.project = Project()
                ecdb.dbfile = pathname
                self.project.file = pathname
                self.project.conf = ecconfig.Config()
                logger.insane(
                    'new project filename: {:s}'.format(self.project.file))
                self.project.changed = False
                self.project.stage = 'start'
                self.Update()
            self.statusbar.PopStatusText()

        def OnOpen(self, event):
            self.statusbar.PushStatusText('OnOpen')
            if self.ImSure():
                # ask the user what new file to open
                wildcard = 'EC-PeT project (.ecp)|*.ecp|SQLite3 files (.sqlite)|*.sqlite|All files|*'
                with wx.FileDialog(self, "Open project file", wildcard=wildcard,
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # if project is loaded, unload it first
                    self.project = None
                    self.Update()

                    # Proceed loading the file chosen by the user
                    pathname = fileDialog.GetPath()
                    try:
                        self.project = Project(pathname)
                    except IOError:
                        wx.LogError("Cannot open file '%s'." % pathname)
                    else:
                        os.chdir(os.path.dirname(pathname))
                        self.Update()
            self.statusbar.PopStatusText()

        def OnClose(self, event):
            self.statusbar.PushStatusText('OnClose')
            if self.ImSure():
                if self.project is not None:
                    self.project = None
                self.Update()
            self.statusbar.PopStatusText()

        def OnImport(self, event):
            self.statusbar.PushStatusText('OnImport')
            if self.ImSure():
                # ask the user what new file to open
                with wx.FileDialog(self, "Open config file", wildcard="config files (*.conf)|*.conf|All files|*",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # Proceed loading the file chosen by the user
                    pathname = fileDialog.GetPath()
                    try:
                        arglist = ecconfig.read_file(pathname)
                    except IOError:
                        wx.LogError("Cannot open file '%s'." % pathname)
                    else:
                        self.project.conf = ecconfig.complete(arglist)
                        self.project.store()
                self.Update()
            self.statusbar.PopStatusText()

        def OnCreate(self, event):
            self.statusbar.PushStatusText('OnCreate')
            if self.ImSure():
                #                # make full new config constraint the defaults
                #                self.project.conf = ecconfig.Config()
                # modify it by wizard:
                self.modifyConfig(reset=True)
                # store it
                self.project.store()
            self.statusbar.PopStatusText()

        def OnModify(self, event):
            self.statusbar.PushStatusText('OnModify')
            if self.ImSure():
                # modify it by wizard:
                self.modifyConfig(reset=False)
                # store it
                self.project.store()
            self.statusbar.PopStatusText()

        def Export(self, event, full):
            # ask the user what new file to open
            with wx.FileDialog(self, "Save config file", wildcard="config files (*.conf)|*.conf",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     # the user changed their mind

                # Proceed loading the file chosen by the user
                pathname = fileDialog.GetPath()
                if not pathname.endswith('.conf'):
                    pathname = pathname + '.conf'
                if full:
                    reduced = self.project.conf
                else:
                    reduced = ecconfig.reduce(self.project.conf)
                try:
                    ecconfig.write_file(pathname, reduced)
                except IOError:
                    wx.LogError("Cannot write file '%s'." % pathname)
            self.Update()

        def OnExportMini(self, event):
            self.statusbar.PushStatusText('OnExportMini')
            self.Export(event, full=False)
            self.statusbar.PopStatusText()

        def OnExportFull(self, event):
            self.statusbar.PushStatusText('OnExportFull')
            self.Export(event, full=True)
            self.statusbar.PopStatusText()

        def OnRun(self, stage):
            startat = self.radio.GetSelection()
            logger.debug('running stage'+ec.stages[startat])
            with wx.MessageDialog(self, '(Re)Starting processing at stage: ' +
                                  ' {:s} '.format(
                                      r_labels[ec.stages[startat]]),
                                  style=wx.ICON_QUESTION | wx.OK | wx.CANCEL) as dlg:
                yesno = dlg.ShowModal() == wx.ID_OK
#      dlg.Destroy()
            wx.YieldIfNeeded()
            if yesno:
                if have_com:
                    thread = Thread(target=ecengine.process, kwargs=dict(
                        conf=self.project.conf, startat=startat))
                    dlg = ProgressBox()
                    thread.start()
                    dlg.ShowModal()
                    wx.YieldIfNeeded()
                else:
                    ecengine.process(self.project.conf, startat)
            self.Update()

# end "if have_wx" -------------------------------------------

# ----------------------------------------------------------------
#


def graphical_interface(options):

    global imagepath
    imagepath = ecconfig.find_imagepath()
    global gui_image
    gui_image = os.path.join(imagepath, 'gui-image_text.png')

    app = wx.App(False)
    top = Run_Window(None, title='EC-PeT - Main window', opts=options)
    top.Show()
    app.MainLoop()
    app.Destroy()
    return

# ----------------------------------------------------------------
#
# switch user interface
#


def commandline_interface():

    #  all_values=['AvgInterval','ConfName','DateBegin','DateEnd',
    #            'RawDir','RawFastData','RawSlowData',
    #            'OutDir','PlfitInterval']
    options = {'command': None,
               'project': None,
               'config': None
               }

    # read command line
    parser = argparse.ArgumentParser(description='EC-PeT ' +
                                     '-- elaboratio concursuum perturbationum Treverensis *)\n' +
                                     'Release: '+version.__release__+'\n' +
                                     '(C) 2017-2021 Clemens Drüe, Universität Trier',
                                     epilog='*)= eddy-covariance software from Trier')
    subparsers = parser.add_subparsers(dest='run_command')
    parser_g = subparsers.add_parser('gui',
                                     help='start graphic user interface (GUI)')
    parser_r = subparsers.add_parser('run',
                                     help='use existing configuration, create new project and run it')
    parser_u = subparsers.add_parser('update',
                                     help='use existing configuration, alter it ' +
                                     'according to the command-line options, ' +
                                     'create new project and run it')
    parser_m = subparsers.add_parser('make',
                                     help='generate a new default configuration file ' +
                                     '(including the command-line options)')

    for i in [parser_r]:
        i.add_argument('-r', '--restart',
                       dest='stage', metavar='STAGE',
                       choices=ec.stages, nargs=1, default='start',
                       help='restart at processing stage ["start"]')
        what_r = i.add_mutually_exclusive_group()

    for i in [parser_u, parser_m, what_r]:
        i.add_argument('-c', '--config',
                       dest='config', nargs=1,
                            help='name of the configuration file ' +
                       '[%s]' % defaults.get('ConfName'),
                            metavar='FILE')

    for i in [parser_g, parser_u, what_r]:
        i.add_argument('-p', '--project', default=None, nargs=1,
                       help='name of the project (file) ',
                       metavar='PROJECT')

    for i in [parser_u, parser_m]:
        i.add_argument('-a', '--AvgInterval',
                       dest='avgstring', nargs=1,
                            help='duration for the averaging interval in seconds' +
                       '[%s]' % defaults.get('AvgInterval'),
                            metavar='SECONDS')
        i.add_argument('-b', '--DateBegin',
                       dest='DateBegin', nargs=1,
                       help='start time of fist averaging interval',
                       metavar='TIMESTAMNP')
        i.add_argument('-e', '--DateEnd',
                       dest='DateEnd', nargs=1,
                       help='end time of fist averaging interval',
                       metavar='TIMESTAMNP')
        i.add_argument('-d', '--RawDir',
                       dest='RawDir', nargs=1,
                            help='directory containing the data to process. ' +
                            'all names specified under -f or -s are relative ' +
                            'to this directory ' +
                            '[%s]' % defaults.get('RawDir'),
                            metavar='DIR')
        i.add_argument('-f', '--RawFastData', dest='RawFastData', nargs='+',
                       help='fast (high frequency) data files: given as' +
                       'one or more filenames, wildcard pattern, or ' +
                            'a sub-directory of RawDir (for all files within)' +
                            '[%s]' % defaults.get('RawFastData'),
                            metavar='FILE')
        i.add_argument('-s', '--RawSlowData', dest='RawSlowData', nargs="+",
                       help='fast (high frequency) data files: given as' +
                       'one or more filenames, wildcard pattern, or ' +
                            'a sub-directory of RawDir (for all files within)' +
                            '[%s]' % defaults.get('RawSlowData'),
                            metavar='FILE')
        i.add_argument('-o', '--OutDir', dest='OutDir', nargs=1,
                       help='directory where to store the output ' +
                       '[%s]' % defaults.get('OutDir'),
                       metavar='DIR')
        i.add_argument('-i', '--PlfitInterval',
                       dest='plfitstring', nargs=1,
                            help='duration for the averaging interval in days' +
                       '[%s]' % defaults.get('PlfitInterval'),
                            metavar='DAYS')

    varg = parser.add_mutually_exclusive_group()
    varg.add_argument('-v', '--verbose',
                      dest='verbose', 
                      action='store_const',
                      const=logging.INFO,
                      default=logging.NORMAL,
                      help='increase output verbosity')
    varg.add_argument('--debug',
                      dest='verbose', 
                      action='store_const',
                      const=logging.DEBUG,
                      help='decrease output verbosity')
    varg.add_argument('--debug-insane',
                      dest='verbose', 
                      action='store_const',
                      const=logging.INSANE,
                      help='decrease output verbosity')
    varg.add_argument('-q', '--quiet',
                      dest='verbose',
                      action='store_const',
                      const=logging.ERROR,
                      help='decrease output verbosity')

    # parse
    arglist = vars(parser.parse_args())

    # convert length1-1 lists into strings
    for a in arglist:
        if isinstance(arglist[a], list):
            if len(arglist[a]) == 1:
                arglist[a] = arglist[a][0]

    # collect the conf values among the arguments
    values = {k: v for k, v in arglist.items() if k in ecconfig.defaults.keys()}

    if arglist['verbose'] in [logging.CRITICAL, logging.ERROR,
                              logging.WARNING, logging.NORMAL,
                              logging.INFO, logging.DEBUG, logging.INSANE]:
        logging.root.setLevel(arglist['verbose'])
    logger.normal('logging level: {:s}'.format(
        logging.getLevelName(logging.root.getEffectiveLevel())))

    # set command
    if arglist['run_command'] is not None:
        options['command'] = arglist['run_command']
    else:
        options['command'] = 'gui'
    # set project file
    if 'project' in arglist and arglist['project'] is not None:
        options['project'] = arglist['project']
    # set config file
    if 'config' in arglist and arglist['config'] is not None:
        options['config'] = arglist['config']
    # set starting stage
    if 'stage' in arglist and arglist['stage'] is not None:
        options['stage'] = arglist['stage']

    # convert averaging string into seconds
    if 'avgstring' in values and values['avgstring'] is not None:
        logger.debug('got averaging string "%s"' % values['avgstring'])
        values['AvgInterval'] = ec.string_to_interval(values['avgstring'])
        logger.debug('converted to AvgInterval=%is' % values['AvgInterval'])
        del(values['avgstring'])
    else:
        values['AvgInterval'] = None

    # convert planarfit interval string into seconds
    if 'plfitstring' in values and values['plfitstring'] is not None:
        logger.debug('got planar-fit interval string "%s"' %
                      values['plfitstring'])
        values['PlfitInterval'] = ec.string_to_interval(values['plfitstring'])
        logger.debug('converted to PlfitInterval=%is' %
                      values['PlfitInterval'])
        del(values['plfitstring'])
    else:
        values['PlfitInterval'] = None

    # make sure only set values are there
    for k, v in list(values.items()):
        if v is None:
            del values[k]
            logger.insane('values: %s deleted' % k)
        else:
            logger.debug('values: %s = %s' % (k, v))

    return values, options

# ----------------------------------------------------------------
#
# run in text mode
#

def processing_console(values, options):
    logger.debug('values: %s' % values)
    logger.debug('options: %s' % options)
    if options['command'] == 'make':
        conf = ecconfig.Config(values)
        ecconfig.write(defaults, conf, full=True)
    elif options['command'] == 'update':
        if options['project'] is not None:
            ecdb.dbfile = options['project']
        oldconf = ecconfig.complete(
            ecconfig.read_file(options['ConfName']))
        conf = ecconfig.apply(oldconf, values)
        ecconfig.write(defaults, conf, full=True)
        startat = None
    elif options['command'] == 'run':
        if options['config'] is not None and options['project'] is not None:
            if not os.path.exists(options['ConfName']):
                logger.fatal('config file %s not found!' %
                              options['ConfName'])
                sys.exit(2)
            if os.path.exists(options['project']):
                logger.error('project file %s already exists. ' +
                              'please rename or remove %s' % options['project'])
                sys.exit(1)
            conf = ecconfig.complete(ecconfig.read_file(options['config']))
            ecdb.dbfile = options['project']
        elif options['config'] is not None and options['project'] is None:
            if not os.path.exists(options['config']):
                logger.fatal('config file %s not found!' % options['config'])
                sys.exit(2)
            conf = ecconfig.complete(ecconfig.read_file(options['config']))
            base = os.path.splitext(os.path.basename(options['config']))[0]
            ecdb.dbfile = base + '.ecp'
        elif options['config'] is None and options['project'] is not None:
            if not os.path.exists(options['project']):
                logger.fatal('project file %s not found!' %
                              options['project'])
                sys.exit(2)
            ecdb.dbfile = options['project']
            conf = ecdb.conf_from_db()
        else:
            logger.critical('either a config file (-c) or a project (-p) ' +
                             'must be specified!')
            sys.exit(2)
        #
        if options['stage'] is not None:
            startat = ec.stages.index(options['stage'])
        else:
            startat = 0

        ecdb.conf_to_db(conf)

        if have_com and sys.stdout.isatty():
            logger.debug('initiaslizing progress indicator')

            def getstage(msg):
                global stage_progress, stage_name
                stage_progress = 0
                stage_name = msg

            def getprogress(msg):
                global stage_progress
                stage_progress = msg

            def getincrement(msg):
                global stage_progress
                stage_progress += msg

            pub.subscribe(getprogress, "progress")
            pub.subscribe(getincrement, "increment")
            pub.subscribe(getstage, "stage")

            logger.debug('progress indicator started')

            def task(event):
                global stage_progress, stage_name
                stage_progress = 0
                stage_name = ""
                # execute a task in a loop
                while True:
                    # block for a moment
                    sleep(2)
                    # check for stop
                    if event.is_set():
                        break
                    # refresh progress bar
                    logger.normal('============ STAGE: %5s '
                                   % stage_name
                                   + ' PROGRESS: %5.1f%% ============)'
                                   % stage_progress)

            # create the event
            event = Event()
            # create and configure a new thread
            thread = Thread(target=task, args=(event,))
            # start the new thread
            logger.debug('progress thread starting')
            thread.start()

            indicator = True
        else:
            indicator = False

        ecengine.process(conf, startat)

        if indicator:
            logger.debug('progress thread stopping')
            event.set()
            thread.join()

    else:
        raise ValueError('unknown command "%s"' % options['command'])

# ----------------------------------------------------------------
#
# switch user interface
#


def user_interface():

    # check number of command line arguments (  1 = only command given )
    if len(sys.argv) > 1:
        # if command line arguments are present, get them
        values, options = commandline_interface()
    else:
        values = {}
        options = {}
        if not have_wx:
            # quit if no graphic environment is available
            logger.critical('only command-line interface availabe.')
            logger.critical('Run '+__file__+' -h for help')
            sys.exit(1)
        else:
            options = {'command': 'gui',
                       'project': None,
                       'stage': None}

    logger.debug(f"selected command: {options['command']}")
    # create a complete config with all the user settings
    if options['command'] == 'gui':
        if 'project' in values.keys():
            options['project'] = values['project']
        graphical_interface(options)
    else:
        processing_console(values, options)
    logger.normal('finished successfully')


# ----------------------------------------------------------------
#
# main call
#
if __name__ == "__main__":
    user_interface()
