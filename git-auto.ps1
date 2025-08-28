param (
    [string]$message = "Atualização"
)

# Adiciona todas as mudanças
git add .

# Faz o commit com a mensagem passada como parâmetro
git commit -m $message

# Descobre o branch atual
$branch = git rev-parse --abbrev-ref HEAD

# Faz push pro branch atual
git push origin $branch

Write-Host "✅ Commit e push concluídos no branch $branch!"
