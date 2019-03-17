from Cocoa import *
from Foundation import NSObject


class SimpleXibDemoController(NSWindowController):
    counterTextField = objc.IBOutlet()
 
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
 
        # Start the counter
        self.count = 0
 
    @objc.IBAction
    def increment_(self, sender):
        self.count += 1
        self.updateDisplay()
 
    @objc.IBAction
    def decrement_(self, sender):
        self.count -= 1
        self.updateDisplay()
 
    def updateDisplay(self):
        self.counterTextField.setStringValue_(self.count)
 

class AppDelegate (NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        print("Hello, World!")

    def sayHello_(self, sender):
        print("Hello again, World!")

    def applicationShouldTerminateAfterLastWindowClosed_(self, app):
        return True



if __name__ == "__main__":
    app = NSApplication.sharedApplication()

    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
 
    # # Initiate the contrller with a XIB
    # viewController = SimpleXibDemoController.alloc().initWithWindowNibName_("SimpleXibDemo")
 
    # # Show the window
    # viewController.showWindow_(viewController)
 
    # # Bring app to top
    # NSApp.activateIgnoringOtherApps_(True)
 
    win = NSWindow.alloc()
    frame = ((200.0, 300.0), (250.0, 100.0))
    win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
    win.setTitle_ ('HelloWorld')
    win.setLevel_ (3)                   # floating window

    hel = NSButton.alloc().initWithFrame_ (((10.0, 10.0), (80.0, 80.0)))
    win.contentView().addSubview_ (hel)
    hel.setBezelStyle_( 4 )
    hel.setTitle_( 'Hello!' )
    hel.setTarget_( app.delegate() )
    hel.setAction_( "sayHello:" )

    win.display()
    win.orderFrontRegardless()          ## but this one does

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()
