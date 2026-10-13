import os
import subprocess

# 1. Cria uma pasta temporária para colocar os arquivos de etiqueta falsos
pasta_temp = "etiquetas_temp"
os.makedirs(pasta_temp, exist_ok=True)

lista_fakes = [
    "BASE LIQUIDA CREME.lbx",
    "BASE LIQUIDA MORANGO.lbx",
    "BASE LIQUIDA MORANGO MATE.lbx",
    "MOLHO DE ALHO (ABERTO).lbx",
    "MOLHO AO SUGO.lbx",
    "QUEIJO PRATO FATIADO.lbx",
    "PRESUNTO COZIDO.lbx",
    "TOMATE PICADO.lbx",
    "RYAN ROBERT"
]

# Cria arquivos vazios .lbx dentro da pasta temporária
for lbx in lista_fakes:
  caminho_arquivo = os.path.join(pasta_temp, lbx)
  with open(caminho_arquivo, "w") as f:
    f.write("conteudo simulado de etiqueta")

nome_rar = "etiquetas_teste.rar"
# Remove o .rar antigo se já existir
if os.path.exists(nome_rar):
  os.remove(nome_rar)

# 2. Caminho padrão onde o WinRAR costuma ficar instalado no Windows
caminho_winrar = r"C:\Program Files\WinRAR\Rar.exe"

try:
  # Executa o comando do WinRAR para compactar a pasta em .rar
  # Comando: Rar.exe a -ep1 etiquetas_teste.rar etiquetas_temp\
  comando = [caminho_winrar, "a", "-ep1", nome_rar, pasta_temp + "\\"]
  resultado = subprocess.run(
      comando, capture_output=True, text=True, check=True
  )

  print(
      f"Sucesso! Arquivo '{nome_rar}' gerado no formato .rar usando o WinRAR"
      " do seu PC."
  )

except Exception as e:
  print(
      "Não foi possível chamar o WinRAR automaticamente. Certifique-se de que"
      f" ele está instalado em C:\\Program Files\\WinRAR\\.\nErro: {e}"
  )

# Limpa os arquivos soltos da pasta temporária
for lbx in lista_fakes:
  caminho_arquivo = os.path.join(pasta_temp, lbx)
  if os.path.exists(caminho_arquivo):
    os.remove(caminho_arquivo)
if os.path.exists(pasta_temp):
  os.rmdir(pasta_temp)