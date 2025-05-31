import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

let fastApiProcess: ChildProcess | null = null

async function waitForBackend(url: string, timeout = 10000): Promise<boolean> {
  const start = Date.now()
  while (Date.now() - start < timeout) {
    try {
      const res = await fetch(url)
      if (res.ok) return true
    } catch (_) {
      // Do nothing, wait
    }
    await new Promise((resolve) => setTimeout(resolve, 500))
  }
  return false
}


function startFastApiServer(): void {
  // Determine the correct binary name based on platform
  let binaryName = 'fastapi-server'
  if (process.platform === 'win32') {
    binaryName = 'fastapi-server.exe'
  } else if (process.platform === 'darwin') {
    binaryName = 'fastapi-server-mac'
  }

  const serverPath = is.dev 
    ? join(__dirname, `../../bin/${binaryName}`) // Development path
    : join(process.resourcesPath, `bin/${binaryName}`) // Production path

  console.log('Starting FastAPI server at:', serverPath)
  
  try {
    fastApiProcess = spawn(serverPath, [], {
      stdio: ['pipe', 'pipe', 'pipe'], // Capture stdout, stderr
      detached: false
    })

    fastApiProcess.stdout?.on('data', (data) => {
      console.log(`FastAPI stdout: ${data}`)
    })

    fastApiProcess.stderr?.on('data', (data) => {
      console.error(`FastAPI stderr: ${data}`)
    })

    fastApiProcess.on('close', (code) => {
      console.log(`FastAPI server exited with code ${code}`)
      fastApiProcess = null
    })

    fastApiProcess.on('error', (error) => {
      console.error('Failed to start FastAPI server:', error)
      fastApiProcess = null
    })

  } catch (error) {
    console.error('Error spawning FastAPI server:', error)
  }
}

function stopFastApiServer(): void {
  if (fastApiProcess) {
    console.log('Stopping FastAPI server...')
    fastApiProcess.kill('SIGTERM')
    fastApiProcess = null
  }
}

async function createWindow(): Promise<void> {
  startFastApiServer() // Start FastAPI before showing the window

  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  const backendReady = await waitForBackend('http://localhost:8000/', 10000)

  if (backendReady) {
    mainWindow.show()
  } else {
    console.error('FastAPI server did not become ready in time.')
    mainWindow.loadURL('data:text/html,<h1>Backend failed to start</h1>')
    mainWindow.show()
    return
  }

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  stopFastApiServer() // Stop the server before quitting
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// Handle app termination
app.on('before-quit', () => {
  stopFastApiServer()
})

// Handle unexpected exits
process.on('exit', () => {
  stopFastApiServer()
})

process.on('SIGINT', () => {
  stopFastApiServer()
  app.quit()
})

process.on('SIGTERM', () => {
  stopFastApiServer()
  app.quit()
})