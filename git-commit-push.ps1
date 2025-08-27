param(
    [string]$msg
)

if (-not $msg) {
    Write-Host "Você precisa fornecer uma mensagem de commit."
    exit
}

git add .
git commit -m "$msg"
git push
Write-Host "Atualizado com sucesso!"
