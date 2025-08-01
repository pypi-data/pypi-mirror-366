---
title: AgentSphere Desktop
description: Discover AgentSphere Desktop, a secure virtual desktop designed for AI agents performing 'Computer Use' tasks. This guide shows you how to programmatically control a complete, isolated desktop environment to launch GUI applications, all via our Python and JavaScript SDKs.   # for seo optimization
keywords: AgentSphere Desktop, Computer Use, virtual desktop, GUI automation, autonomous agents, stream desktop, mouse control, keyboard control, launch applications, screenshot, secure agent runtime, cloud sandbox, AI agent infra, AgentSphere alternative, build autonomous AI agent      # for seo optimization
---

## AgentSphere Desktop - Virtual Computer for Computer Use

AgentSphere Desktop is a secure virtual desktop ready for Computer Use. Each sandbox is isolated from the others and can be customized with any dependencies you need.

![AgentSphere Desktop](/docs/images/agentsphere-desktop.png)


## Get Started

AgentSphere Desktop is built on top of [AgentSphere Sandbox](https://www.agentsphere.run/).

### 1. Get AgentSphere API key

1. Sign up at [AgentSphere](https://www.agentsphere.run) and get your API key.

2. Set environment variable `AGENTSPHERE_API_KEY` with your API key.

### 2. Install SDK

<Tabs>
  <TabPanel label="Python">

```bash
pip install agentsphere-desktop
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```bash
npm install agentsphere-desktop
```

  </TabPanel>
</Tabs>

### 3. Create Your Desktop

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox

# Create a new desktop sandbox
desktop = Sandbox()

# Launch an application
desktop.launch('google-chrome')  # or vscode, firefox, etc.

# Wait 10s for the application to open
desktop.wait(10000)

# Stream the application's window
# Note: There can be only one stream at a time
# You need to stop the current stream before streaming another application
desktop.stream.start(
    window_id=desktop.get_current_window_id(), # if not provided the whole desktop will be streamed
    require_auth=True
)

# Get the stream auth key
auth_key = desktop.stream.get_auth_key()

# Print the stream URL
print('Stream URL:', desktop.stream.get_url(auth_key=auth_key))

# Kill the sandbox after the tasks are finished
# desktop.kill()
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

// Start a new desktop sandbox
const desktop = await Sandbox.create()

// Launch an application
await desktop.launch('google-chrome') // or vscode, firefox, etc.

// Wait 10s for the application to open
await desktop.wait(10000)

// Stream the application's window
// Note: There can be only one stream at a time
// You need to stop the current stream before streaming another application
await desktop.stream.start({
  windowId: await desktop.getCurrentWindowId(), // if not provided the whole desktop will be streamed
  requireAuth: true,
})

// Get the stream auth key
const authKey = desktop.stream.getAuthKey()

// Print the stream URL
console.log('Stream URL:', desktop.stream.getUrl({ authKey }))

// Kill the sandbox after the tasks are finished
// await desktop.kill()
```

  </TabPanel>
</Tabs>


## Work with AgentSphere Desktop

### Stream Desktop Screen

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Start the stream
desktop.stream.start()

# Get stream URL
url = desktop.stream.get_url()
print(url)

# Get stream URL and disable user interaction
url = desktop.stream.get_url(view_only=True)
print(url)

# Stop the stream
desktop.stream.stop()
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Start the stream
await desktop.stream.start()

// Get stream URL
const url = desktop.stream.getUrl()
console.log(url)

// Get stream URL and disable user interaction
const url = desktop.stream.getUrl({ viewOnly: true })
console.log(url)

// Stop the stream
await desktop.stream.stop()
```

  </TabPanel>
</Tabs>


### Stream with Password Protection

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Start the stream
desktop.stream.start(
    require_auth=True  # Require authentication with an auto-generated key
)

# Retrieve the authentication key
auth_key = desktop.stream.get_auth_key()

# Get stream URL
url = desktop.stream.get_url(auth_key=auth_key)
print(url)

# Stop the stream
desktop.stream.stop()
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Start the stream
await desktop.stream.start({
  requireAuth: true, // Require authentication with an auto-generated key
})

// Retrieve the authentication key
const authKey = await desktop.stream.getAuthKey()

// Get stream URL
const url = desktop.stream.getUrl({ authKey })
console.log(url)

// Stop the stream
await desktop.stream.stop()
```

  </TabPanel>
</Tabs>


### Stream Specific Apps

> [!WARNING]
>
> - Will raise an error if the desired application is not open yet
> - The stream will close once the application closes
> - Creating multiple streams at the same time is not supported, you may have to stop the current stream and start a new one for each application

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Get current (active) window ID
window_id = desktop.get_current_window_id()

# Get all windows of the application
window_ids = desktop.get_application_windows("Firefox")

# Start the stream
desktop.stream.start(window_id=window_ids[0])

# Stop the stream
desktop.stream.stop()
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Get current (active) window ID
const windowId = await desktop.getCurrentWindowId()

// Get all windows of the application
const windowIds = await desktop.getApplicationWindows('Firefox')

// Start the stream
await desktop.stream.start({ windowId: windowIds[0] })

// Stop the stream
await desktop.stream.stop()
```

  </TabPanel>
</Tabs>


### Mouse Control

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

desktop.double_click()
desktop.left_click()
desktop.left_click(x=100, y=200)
desktop.right_click()
desktop.right_click(x=100, y=200)
desktop.middle_click()
desktop.middle_click(x=100, y=200)
desktop.scroll(10) # Scroll by the amount. Positive for up, negative for down.
desktop.move_mouse(100, 200) # Move to x, y coordinates
desktop.drag((100, 100), (200, 200)) # Drag using the mouse
desktop.mouse_press("left") # Press the mouse button
desktop.mouse_release("left") # Release the mouse button
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

await desktop.doubleClick()
await desktop.leftClick()
await desktop.leftClick(100, 200)
await desktop.rightClick()
await desktop.rightClick(100, 200)
await desktop.middleClick()
await desktop.middleClick(100, 200)
await desktop.scroll(10) // Scroll by the amount. Positive for up, negative for down.
await desktop.moveMouse(100, 200) // Move to x, y coordinates
await desktop.drag([100, 100], [200, 200]) // Drag using the mouse
await desktop.mousePress('left') // Press the mouse button
await desktop.mouseRelease('left') // Release the mouse button
```

  </TabPanel>
</Tabs>


### Keyboard Control

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Write text at the current cursor position with customizable typing speed
desktop.write("Hello, world!")  # Default: chunk_size=25, delay_in_ms=75
desktop.write("Fast typing!", chunk_size=50, delay_in_ms=25)  # Faster typing

# Press keys
desktop.press("enter")
desktop.press("space")
desktop.press("backspace")
desktop.press(["ctrl", "c"]) # Key combination
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Write text at the current cursor position with customizable typing speed
await desktop.write('Hello, world!')
await desktop.write('Fast typing!', { chunkSize: 50, delayInMs: 25 }) // Faster typing

// Press keys
await desktop.press('enter')
await desktop.press('space')
await desktop.press('backspace')
await desktop.press(['ctrl', 'c']) // Key combination
```

  </TabPanel>
</Tabs>


### Window Control

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Get current (active) window ID
window_id = desktop.get_current_window_id()

# Get all windows of the application
window_ids = desktop.get_application_windows("Firefox")

# Get window title
title = desktop.get_window_title(window_id)
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Get current (active) window ID
const windowId = await desktop.getCurrentWindowId()

// Get all windows of the application
const windowIds = await desktop.getApplicationWindows('Firefox')

// Get window title
const title = await desktop.getWindowTitle(windowId)
```

  </TabPanel>
</Tabs>


### Capture a Screenshot

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Take a screenshot and save it as "screenshot.png" locally
image = desktop.screenshot()
# Save the image to a file
with open("screenshot.png", "wb") as f:
    f.write(image)
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()
const image = await desktop.screenshot()
// Save the image to a file
fs.writeFileSync('screenshot.png', image)
```

  </TabPanel>
</Tabs>


### Open a File

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Open file with default application
desktop.files.write("/home/user/index.js", "console.log('hello')") # First create the file
desktop.open("/home/user/index.js") # Then open it
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Open file with default application
await desktop.files.write('/home/user/index.js', "console.log('hello')") // First create the file
await desktop.open('/home/user/index.js') // Then open it
```

  </TabPanel>
</Tabs>


### Launch Apps

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Launch the application
desktop.launch('google-chrome')
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Launch the application
await desktop.launch('google-chrome')
```

  </TabPanel>
</Tabs>


### Run Bash Commands

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

# Run any bash command
out = desktop.commands.run("ls -la /home/user")
print(out)
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()

// Run any bash command
const out = await desktop.commands.run('ls -la /home/user')
console.log(out)
```

  </TabPanel>
</Tabs>


### Wait

<Tabs>
  <TabPanel label="Python">

```python
from agentsphere_desktop import Sandbox
desktop = Sandbox()

desktop.wait(1000) # Wait for 1 second
```

  </TabPanel>
  <TabPanel label="JavaScript & TypeScript">

```javascript
import { Sandbox } from 'agentsphere-desktop'

const desktop = await Sandbox.create()
await desktop.wait(1000) // Wait for 1 second
```

  </TabPanel>
</Tabs>
