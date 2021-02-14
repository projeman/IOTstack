#!/usr/bin/env python3

import signal

def main():
  from blessed import Terminal
  from deps.chars import specialChars, commonTopBorder, commonBottomBorder, commonEmptyLine
  import time
  from deps.host_exec import execInteractive
  global signal

  global renderMode
  global backupRestoreSelectionInProgress
  global mainMenuList
  global currentMenuItemIndex
  global hideHelpText
  
  try: # If not already set, then set it.
    hideHelpText = hideHelpText
  except:
    hideHelpText = False

  term = Terminal()

  def runBackup():
    global needsRender
    print("Execute Backup:")
    print("bash ./scripts/backup.sh")
    execInteractive('bash ./scripts/backup.sh')
    print("")
    print("Backup completed.")
    print("Press [Up] or [Down] arrow key to show the menu if it has scrolled too far.")
    time.sleep(1)
    needsRender = 1
    return True

  def dropboxInstall():
    global needsRender
    print("Install Dropbox:")
    print("git clone https://github.com/andreafabrizi/Dropbox-Uploader.git ~/Dropbox-Uploader")
    execInteractive('git clone https://github.com/andreafabrizi/Dropbox-Uploader.git ~/Dropbox-Uploader')
    print("chmod +x ~/Dropbox-Uploader/dropbox_uploader.sh")
    execInteractive('chmod +x ~/Dropbox-Uploader/dropbox_uploader.sh')
    print("cd ~/Dropbox-Uploader && ./dropbox_uploader.sh")
    execInteractive('cd ~/Dropbox-Uploader && ./dropbox_uploader.sh')
    time.sleep(1) # Give time to see errors
    print("")
    print("Dropbox install finished")
    print("Press [Up] or [Down] arrow key to show the menu if it has scrolled too far.")
    time.sleep(1)
    needsRender = 1
    return True

  def rcloneInstall():
    global needsRender
    print("Install rClone:")
    print("sudo apt install -y rclone")
    execInteractive('sudo apt install -y rclone')
    print("")
    print("rClone install finished")
    print("Please run 'rclone config' to configure the rclone google drive backup")
    print("Press [Up] or [Down] arrow key to show the menu if it has scrolled too far.")
    needsRender = 1
    return True

  def rCloneSetup():
    global needsRender
    print("Setup rclone:")
    print("rclone config")
    execInteractive('rclone config')
    print("")
    print("rclone setup completed. Press [Up] or [Down] arrow key to show the menu if it has scrolled too far.")
    time.sleep(1)
    needsRender = 1
    return True

  def runRestore():
    global needsRender
    print("Execute Restore:")
    print('bash ./scripts/restore.sh')
    execInteractive('bash ./scripts/restore.sh')
    print("")
    print("Restore completed.")
    print("Press [Up] or [Down] arrow key to show the menu if it has scrolled too far.")
    time.sleep(1)
    needsRender = 1
    return True

  def goBack():
    global backupRestoreSelectionInProgress
    global needsRender
    backupRestoreSelectionInProgress = False
    needsRender = 1
    return True

  mainMenuList = [
    ["Run backup", runBackup],
    ["Install Dropbox", dropboxInstall],
    ["Install rclone", rcloneInstall],
    ["Setup rclone (must be installed first)", rCloneSetup],
    ["Restore from backup", runRestore],
    ["Back", goBack]
  ]

  hotzoneLocation = [7, 0] # Top text

  backupRestoreSelectionInProgress = True
  currentMenuItemIndex = 0
  menuNavigateDirection = 0

  # Render Modes:
  #  0 = No render needed
  #  1 = Full render
  #  2 = Hotzone only
  needsRender = 1

  def onResize(sig, action):
    global mainMenuList
    global currentMenuItemIndex
    mainRender(1, mainMenuList, currentMenuItemIndex)

  def renderHotZone(term, menu, selection, hotzoneLocation):
    lineLengthAtTextStart = 71
    print(term.move(hotzoneLocation[0], hotzoneLocation[1]))
    for (index, menuItem) in enumerate(menu):
      toPrint = ""
      if index == selection:
        toPrint += ('{bv} -> {t.blue_on_green} {title} {t.normal} <-'.format(t=term, title=menuItem[0], bv=specialChars[renderMode]["borderVertical"]))
      else:
        toPrint += ('{bv}    {t.normal} {title}    '.format(t=term, title=menuItem[0], bv=specialChars[renderMode]["borderVertical"]))

      for i in range(lineLengthAtTextStart - len(menuItem[0])):
        toPrint += " "

      toPrint += "{bv}".format(bv=specialChars[renderMode]["borderVertical"])

      toPrint = term.center(toPrint)
      
      print(toPrint)

  def mainRender(needsRender, menu, selection):
    term = Terminal()
    
    if needsRender == 1:
      print(term.clear())
      print(term.move_y(6 - hotzoneLocation[0]))
      print(term.black_on_cornsilk4(term.center('IOTstack Backup Commands')))
      print("")
      print(term.center(commonTopBorder(renderMode)))
      print(term.center(commonEmptyLine(renderMode)))
      print(term.center("{bv}      Select backup command to run                                              {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
      print(term.center(commonEmptyLine(renderMode)))
      print(term.center(commonEmptyLine(renderMode)))
      print(term.center(commonEmptyLine(renderMode)))

    if needsRender >= 1:
      renderHotZone(term, menu, selection, hotzoneLocation)

    if needsRender == 1:
      print(term.center(commonEmptyLine(renderMode)))
      if not hideHelpText:
        if term.height < 30:
          print(term.center(commonEmptyLine(renderMode)))
          print(term.center("{bv}      Not enough vertical room to render controls help text                     {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center(commonEmptyLine(renderMode)))
        else: 
          print(term.center(commonEmptyLine(renderMode)))
          print(term.center("{bv}      Controls:                                                                 {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center("{bv}      [Up] and [Down] to move selection cursor                                  {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center("{bv}      [H] Show/hide this text                                                   {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center("{bv}      [Enter] to run command                                                    {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center("{bv}      [Escape] to go back to main menu                                          {bv}".format(bv=specialChars[renderMode]["borderVertical"])))
          print(term.center(commonEmptyLine(renderMode)))
      print(term.center(commonEmptyLine(renderMode)))
      print(term.center(commonBottomBorder(renderMode)))

  def runSelection(selection):
    global needsRender
    mainRender(1, mainMenuList, currentMenuItemIndex)
    import types
    if len(mainMenuList[selection]) > 1 and isinstance(mainMenuList[selection][1], types.FunctionType):
      mainMenuList[selection][1]()
    else:
      print(term.green_reverse('IOTstack Error: No function assigned to menu item: "{}"'.format(mainMenuList[selection][0])))
    needsRender = 1

  def isMenuItemSelectable(menu, index):
    if len(menu) > index:
      if len(menu[index]) > 2:
        if menu[index][2]["skip"] == True:
          return False
    return True

  if __name__ == 'builtins':
    global signal
    term = Terminal()
    signal.signal(signal.SIGWINCH, onResize)
    with term.fullscreen():
      menuNavigateDirection = 0
      mainRender(needsRender, mainMenuList, currentMenuItemIndex)
      backupRestoreSelectionInProgress = True
      with term.cbreak():
        while backupRestoreSelectionInProgress:
          menuNavigateDirection = 0

          if not needsRender == 0: # Only rerender when changed to prevent flickering
            mainRender(needsRender, mainMenuList, currentMenuItemIndex)
            needsRender = 0

          key = term.inkey(esc_delay=0.05)
          if key.is_sequence:
            if key.name == 'KEY_TAB':
              menuNavigateDirection += 1
            if key.name == 'KEY_DOWN':
              menuNavigateDirection += 1
            if key.name == 'KEY_UP':
              menuNavigateDirection -= 1
            if key.name == 'KEY_ENTER':
              runSelection(currentMenuItemIndex)
              if backupRestoreSelectionInProgress == False:
                return True
            if key.name == 'KEY_ESCAPE':
              backupRestoreSelectionInProgress = False
              return True
          elif key:
            if key == 'h': # H pressed
              if hideHelpText:
                hideHelpText = False
              else:
                hideHelpText = True
              mainRender(1, mainMenuList, currentMenuItemIndex)

          if menuNavigateDirection != 0: # If a direction was pressed, find next selectable item
            currentMenuItemIndex += menuNavigateDirection
            currentMenuItemIndex = currentMenuItemIndex % len(mainMenuList)
            needsRender = 2

            while not isMenuItemSelectable(mainMenuList, currentMenuItemIndex):
              currentMenuItemIndex += menuNavigateDirection
              currentMenuItemIndex = currentMenuItemIndex % len(mainMenuList)
    return True

  return True

originalSignalHandler = signal.getsignal(signal.SIGINT)
main()
signal.signal(signal.SIGWINCH, originalSignalHandler)