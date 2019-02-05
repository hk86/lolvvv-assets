:: Wait for Connection to the Internet established
powershell.exe -noprofile -command "while((Test-Connection -ComputerName '10.8.0.2' -Quiet) -eq $False) {Start-Sleep -s 10}"
git pull