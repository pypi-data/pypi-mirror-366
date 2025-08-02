function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if ((Test-Admin) -eq $false)  {
    if ($elevated) {
        # tried to elevate, did not work, aborting
    } else {
        Start-Process powershell.exe -Verb RunAs -ArgumentList ('-noprofile -noexit -file "{0}" -elevated' -f ($myinvocation.MyCommand.Definition))
    }
    exit
}

$nl = [Environment]::NewLine

# Visual Studio Code
Write-Host "Download VSCode Installer"$nl
Invoke-WebRequest "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user" -OutFile $env:USERPROFILE\Downloads\VSCode.exe
Write-Host "Unblock the script"$nl
Unblock-File $env:USERPROFILE\Downloads\VSCode.exe
Write-Host "CD to User Profile"$nl
Set-Location $env:USERPROFILE\Downloads\
Write-Host "Run VSCode Script"$nl
Start-Process $env:USERPROFILE\Downloads\VSCode.exe

# Notepad++
Write-Host "Download Notepad++ Installer"$nl
# Check the operating system architecture
if ((Get-CimInstance Win32_OperatingSystem).OSArchitecture -eq "64-bit") {
    # Download the 64-bit installer
    Invoke-WebRequest "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.8/npp.8.6.8.Installer.x64.exe" -OutFile "$env:USERPROFILE\Downloads\Notepad++.exe"
} 
else {
    # Download the 32-bit installer
    Invoke-WebRequest "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.8/npp.8.6.8.Installer.exe" -OutFile "$env:USERPROFILE\Downloads\Notepad++.exe"
}
Write-Host "Install Notepad++"$nl
Start-Process $env:USERPROFILE\Downloads\Notepad++.exe

# PuTTY
Write-Host "Download PuTTY Installer"$nl
# Check the operating system architecture
if ((Get-CimInstance Win32_OperatingSystem).OSArchitecture -eq "64-bit") {
    # Download the 64-bit installer
    Invoke-WebRequest "https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.81-installer.msi" -OutFile "$env:USERPROFILE\Downloads\PuTTY.msi"
} 
else {
    # Download the 32-bit installer
    Invoke-WebRequest "https://the.earth.li/~sgtatham/putty/latest/w32/putty-0.81-installer.msi" -OutFile "$env:USERPROFILE\Downloads\PuTTY.msi"
}
Write-Host "Install PuTTY"$nl
Start-Process $env:USERPROFILE\Downloads\PuTTY.msi

# Pageant
Write-Host "Download PuTTY Installer"$nl
# Check the operating system architecture
if ((Get-CimInstance Win32_OperatingSystem).OSArchitecture -eq "64-bit") {
    # Download the 64-bit installer
    Invoke-WebRequest "https://the.earth.li/~sgtatham/putty/latest/w64/pageant.exe" -OutFile "$env:USERPROFILE\Downloads\Pageant.exe"
} 
else {
    # Download the 32-bit installer
    Invoke-WebRequest "https://the.earth.li/~sgtatham/putty/latest/w32/pageant.exe" -OutFile "$env:USERPROFILE\Downloads\Pageant.exe"
}
Write-Host "Install Pageant"$nl
Start-Process $env:USERPROFILE\Downloads\Pageant.exe