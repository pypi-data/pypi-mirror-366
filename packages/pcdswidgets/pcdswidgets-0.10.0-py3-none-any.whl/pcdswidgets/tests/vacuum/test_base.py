import pytest
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout

from pcdswidgets.icons import RGASymbolIcon
from pcdswidgets.vacuum.base import ContentLocation, PCDSSymbolBase


class BaseSymbol(PCDSSymbolBase):
    """Test Symbol for base class tests"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.icon = RGASymbolIcon(parent=self)


@pytest.fixture(scope='function')
def symbol(qtbot):
    symbol = BaseSymbol()
    qtbot.addWidget(symbol)
    return symbol


def test_show_icon(symbol):
    symbol.showIcon = False
    assert not symbol.icon.isVisible()


def test_symbol_paintEvent_smoke(symbol):
    symbol.show()


def test_no_controls_content(symbol):
    symbol.controlsLocation = ContentLocation.Hidden
    widget_layout = symbol.interlock.layout().itemAt(0).layout().itemAt(0).widget().layout()
    widget = widget_layout.itemAt(1).widget()
    assert widget == symbol.icon


@pytest.mark.parametrize('location,layout,position',
                         [(ContentLocation.Top, QVBoxLayout, 0),
                          (ContentLocation.Bottom, QVBoxLayout, 1),
                          (ContentLocation.Left, QHBoxLayout, 0),
                          (ContentLocation.Right, QHBoxLayout, 1)],
                         ids=['Top', 'Bottom', 'Left', 'Right'])
def test_controls_content_location(symbol, location, layout, position):
    symbol.controlsLocation = location
    assert isinstance(symbol.interlock.layout(), layout)
    widget_layout = symbol.interlock.layout().itemAt(position).layout()
    widget = widget_layout.itemAt(0).widget()
    assert widget == symbol.controls_frame


def test_icon_fixed_size(symbol):
    size = 30
    symbol.iconSize = size
    assert symbol.icon.width() == size
    assert symbol.icon.height() == size


@pytest.mark.parametrize('rotate', (False, True), ids=('Standard', 'Rotated'))
def test_icon_rotation(symbol, rotate):
    symbol.rotateIcon = rotate
    assert symbol.icon.rotation == 90 * int(rotate)


@pytest.mark.parametrize('location,layout,position',
                         [(ContentLocation.Top, QVBoxLayout, 0),
                          (ContentLocation.Bottom, QVBoxLayout, 1),
                          (ContentLocation.Left, QVBoxLayout, 0),
                          (ContentLocation.Right, QVBoxLayout, 1)],
                         ids=['Top', 'Bottom', 'Left', 'Right'])
def test_text_location(symbol, location, layout, position):
    symbol.controlsLocation = ContentLocation.Bottom
    symbol.channelsPrefix = "ca://area:function:device:01"
    symbol.showName = True
    symbol.textLocation = location
    assert isinstance(symbol.interlock.layout(), layout)
    widget_layout = symbol.interlock.layout().itemAt(0).layout().itemAt(0).widget().layout()
    widget = widget_layout.itemAt(position).widget()
    assert widget == symbol.name


@pytest.mark.parametrize('location,layout,position',
                         [(ContentLocation.Left, QHBoxLayout, 0),
                          (ContentLocation.Right, QHBoxLayout, 1)],
                         ids=['Left', 'Right'])
def test_text_and_controls_location(symbol, location, layout, position):
    symbol.controlsLocation = location
    symbol.channelsPrefix = "ca://area:function:device:01"
    symbol.showName = True
    symbol.textLocation = location
    assert isinstance(symbol.interlock.layout(), layout)
    widget_layout = symbol.interlock.layout().itemAt(position).layout().itemAt(0).widget().layout()
    widget = widget_layout.itemAt(0).widget()
    assert widget == symbol.name


def test_name_text(symbol):
    symbol.channelsPrefix = "ca://area:function:device:01"
    symbol.showName = True
    assert symbol.name.text() == "area-function-device-01"
    symbol.overrideName = True
    assert symbol.name.text() == ""
    symbol.setOverrideName = "test-override"
    assert symbol.name.text() == "test-override"
