"""
Adds a Juptyer/qtconsole widget to the first top level widget that contains
a QWidgets called 'widgetLogWin'. The new widget will be called 'pythonConsoleWidget'.
"""

# Copyright (c) 2020, ImFusion GmbH
# Distributed under the terms of the Modified BSD License.

from PyQt5 import Qt
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
import textwrap
import sip
import imfusion as imf


class ConsoleWidget(RichJupyterWidget):
    def __init__(self, *args, **kwargs):
        super(ConsoleWidget, self).__init__(*args, **kwargs)

        self.font_size = 12
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel(show_banner=True)
        self.kernel_manager.kernel.gui = 'qt'
        self.kernel_manager.kernel.shell.banner2 = "Type '%imfusion_doc' to show the documentation."
        self.kernel_client = self._kernel_manager.client()
        self.kernel_client.start_channels()
        # select a color mode that is readable with our stylesheet
        self.kernel_client.kernel.do_execute('''%colors linux''',
                                             silent=True, store_history=False)
        # The exit() command crashes with the InProcessKernel.
        # Instead we just close the widget.
        exit_override = textwrap.dedent('''
            def exit():
                from PyQt5 import Qt, QtWidgets
                Qt.qApp.exit()
            ''')
        self.kernel_client.kernel.do_execute(exit_override,
                                             silent=True, store_history=False)
        imfusion_magic = textwrap.dedent('''
            from IPython.core.magic import register_line_magic
            @register_line_magic
            def imfusion_doc(line):
                import webbrowser
                import imfusion
                webbrowser.open(imfusion.pyDocUrl())
            ''')
        self.kernel_client.kernel.do_execute(imfusion_magic,
                                             silent=True, store_history=False)

        self.exit_requested.connect(self.stop)
        self.executed.connect(self.update_display)

    def update_display(self):
        imf.app.updateDisplay()

    def stop(self):
        self.close()


def _add_console_to_layout(layoutPtr, startupCommand):
    layout = sip.wrapinstance(sip.voidptr(layoutPtr).__int__(), Qt.QLayout)

    console = ConsoleWidget()
    console.setObjectName('pythonConsoleWidget')
    console.style_sheet = '''
        .error { color: #fc5053; }
        .in-prompt { color: #29abe2; text-decoration: underline; }
        .in-prompt-number { font-weight: bold; }
        .out-prompt { color: #fd971f; text-decoration: underline; }
        .out-prompt-number { font-weight: bold; }
        .inverted { background-color: #737373; }
    '''
    console.syntax_style = 'monokai'
    if startupCommand:
        console._execute(startupCommand, True)
    layout.addWidget(console)
