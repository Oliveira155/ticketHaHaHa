param (
    [string]$message = "Atualização"
)

# Adiciona todas as mudanças
git add .

# Faz o commit com a mensagem passada como parâmetro
git commit -m $message

# Faz push pro branch atual
git push origin oliveira

Write-Host "---- Atualização feita!"
