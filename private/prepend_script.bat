:: Wait for Connection to the Internet established
powershell.exe -noprofile -command "while((Test-Connection -ComputerName 'www.google.de' -Quiet) -eq $False) {Start-Sleep -s 10}"
git pull