:: Wait for Connection to the Internet established
powershell.exe -noprofile -command "while((Test-Connection -ComputerName '88.99.138.8' -Quiet) -eq $False) {Start-Sleep -s 10}"
git pull