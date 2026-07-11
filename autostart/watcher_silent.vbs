Dim shell
Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\Users\civil\OneDrive\Desktop\Nir Engineering\Nir Engineering ScanSystem\nir_engineering_system\אפליקציית דשבורד למעקב מסמכים\nir_final"
shell.Run "pythonw.exe run_all.py", 0, False
