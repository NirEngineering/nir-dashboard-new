Dim shell
Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
shell.Run """C:\Users\civil\AppData\Local\Python\bin\python.exe"" run_all.py", 0, False
