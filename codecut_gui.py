
import idc
import ida_kernwin

import imp
import snap_cg

import lfa
import maxcut
import module
import cc_base
import modnaming
import basicutils_7x as basicutils

from PyQt5 import QtCore, QtGui, QtWidgets

from IDAMagicStrings import get_source_strings

#-------------------------------------------------------------------------------
def handler(item, column_no):
  if item.ignore:
    return

  ea = item.ea
  if is_mapped(ea):
    jumpto(ea)

#-------------------------------------------------------------------------------
class CBaseTreeViewer(ida_kernwin.PluginForm):
  def populate_tree(self):
    # Clear previous items
    self.tree.clear()

    # Get source file names
    self.dict, _ = get_source_strings()
    module_names = {}
    for key in self.dict:
      for values in self.dict[key]:
        ea, module_name = values[0], values[2]
        module_names[ea] = module_name

    self.modules_cache = {}
    #Do LFA and MaxCut Analysis to find module boundaries
    _, lfa_modlist = lfa.analyze()
    for module_data in lfa_modlist:
      module_name = "Module 0x%08x:0x%08x" % (module_data.start, module_data.end)
      for ea in module_names:
        if ea >= module_data.start and ea <= module_data.end:
          module_name = module_names[ea]
          break

      if module_name in self.modules_cache:
        item = self.modules_cache[module_name]
      else:
        item = QtWidgets.QTreeWidgetItem(self.tree)
        item.setText(0, module_name)
        item.ea = module_data.start
        item.ignore = True
        self.modules_cache[module_name] = item

      for func in Functions(module_data.start, module_data.end):
        node = QtWidgets.QTreeWidgetItem(item)
        node.setText(0, "0x%08x: %s" % (func, idc.get_func_name(func)))
        node.ea = func
        node.ignore = False

    self.tree.itemDoubleClicked.connect(handler)

  def OnCreate(self, form):
    # Get parent widget
    self.parent = ida_kernwin.PluginForm.FormToPyQtWidget(form)

    # Create tree control
    self.tree = QtWidgets.QTreeWidget()
    self.tree.setHeaderLabels(("Names",))
    self.tree.setColumnWidth(0, 100)

    # Create layout
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.tree)
    self.populate_tree()

    # Populate PluginForm
    self.parent.setLayout(layout)

  def Show(self, title):
    return ida_kernwin.PluginForm.Show(self, title, options = ida_kernwin.PluginForm.WOPN_PERSIST)

#-------------------------------------------------------------------------------
def main():
  tree_frm = CBaseTreeViewer()
  tree_frm.Show("Object Files")

if __name__ == "__main__":
  imp.reload(modnaming)
  imp.reload(module)
  imp.reload(cc_base)
  imp.reload(lfa)
  imp.reload(maxcut)
  imp.reload(snap_cg)
  imp.reload(basicutils)
  main()

