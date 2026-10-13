import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import urllib.request
import zipfile
import pyautogui

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA (KILL SWITCH)
# ==========================================
# Cole aqui o link "Raw" do arquivo de status no seu GitHub.
# (Exemplo de como o link deve ser explicado logo abaixo no texto)
URL_STATUS_GITHUB = (
    "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/status.txt"
)


def verificar_seguranca_remota():
  """Verifica na nuvem se o aplicativo tem permissão para rodar."""
  try:
    req = urllib.request.Request(
        URL_STATUS_GITHUB, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=4) as resposta:
      conteudo = resposta.read().decode("utf-8").strip().upper()
      if "BLOQUEADO" in conteudo:
        return False
    return True
  except Exception:
    # Por segurança, se a internet cair ou o link falhar, bloqueia o app para evitar uso indevido offline
    return False


# ==========================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ==========================================
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class AutomacaoWinRARApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Impressor Automático de Etiquetas (.lbx)")
    self.root.geometry("500x400")
    self.root.resizable(False, False)

    self.lista_arquivos_carregados = []

    # --- Seção para carregar o arquivo compactado (.zip) ---
    lbl_arquivo = tk.Label(
        root,
        text="Arquivo Compactado de Etiquetas (.ZIP):",
        font=("Arial", 10, "bold"),
    )
    lbl_arquivo.pack(anchor="w", padx=20, pady=(15, 2))

    frame_arq = tk.Frame(root)
    frame_arq.pack(padx=20, pady=5, fill="x")

    self.lbl_status_arq = tk.Label(
        frame_arq,
        text="Nenhum arquivo carregado",
        fg="gray",
        anchor="w",
        font=("Arial", 9),
    )
    self.lbl_status_arq.pack(side="left", fill="x", expand=True)

    btn_procurar = tk.Button(
        frame_arq,
        text="Selecionar Arquivo...",
        command=self.carregar_arquivo_compactado,
        font=("Arial", 9),
    )
    btn_procurar.pack(side="right", padx=(5, 0))

    # --- Select (Combobox) para escolher o item ---
    lbl_item = tk.Label(
        root, text="Selecione o Item da Etiqueta:", font=("Arial", 10, "bold")
    )
    lbl_item.pack(anchor="w", padx=20, pady=(15, 5))

    self.combo_item = ttk.Combobox(
        root, values=[], width=55, state="readonly"
    )
    self.combo_item.pack(padx=20, pady=5)

    # --- Quantidade de impressões ---
    lbl_qtd = tk.Label(
        root,
        text="Quantidade de Impressões (Número Inteiro):",
        font=("Arial", 10, "bold"),
    )
    lbl_qtd.pack(anchor="w", padx=20, pady=(15, 5))

    vcmd = (root.register(self.validar_inteiro), "%P")
    self.entry_qtd = tk.Entry(
        root, validate="key", validatecommand=vcmd, width=20, font=("Arial", 11)
    )
    self.entry_qtd.pack(anchor="w", padx=20, pady=5)
    self.entry_qtd.insert(0, "1")

    # --- Botão de Execução ---
    self.btn_executar = tk.Button(
        root,
        text="Iniciar Impressão Automática",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11, "bold"),
        state="disabled",
        command=self.executar_automacao,
    )
    self.btn_executar.pack(padx=20, pady=20, fill="x")

  def validar_inteiro(self, valor):
    if valor == "" or valor.isdigit():
      return True
    return False

  def carregar_arquivo_compactado(self):
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo ZIP de etiquetas",
        filetypes=[("Arquivos ZIP", "*.zip"), ("Todos os arquivos", "*.*")],
    )

    if not caminho:
      return

    nome_curto = os.path.basename(caminho)
    self.lista_arquivos_carregados = []

    try:
      with zipfile.ZipFile(caminho, "r") as zf:
        for filename in zf.namelist():
          if filename.lower().endswith(".lbx"):
            nome_base = os.path.basename(filename)
            if nome_base:
              self.lista_arquivos_carregados.append(nome_base)

      self.lista_arquivos_carregados = sorted(
          list(set(self.lista_arquivos_carregados))
      )

      if self.lista_arquivos_carregados:
        self.combo_item["values"] = self.lista_arquivos_carregados
        self.combo_item.current(0)
        self.lbl_status_arq.config(
            text=f"Carregado: {nome_curto} ({len(self.lista_arquivos_carregados)}"
            " itens)",
            fg="green",
        )
        self.btn_executar.config(state="normal")
        messagebox.showinfo(
            "Sucesso",
            f"{len(self.lista_arquivos_carregados)} etiquetas carregadas com"
            " sucesso!",
        )
      else:
        messagebox.showwarning(
            "Aviso",
            "Nenhum arquivo .lbx foi encontrado dentro deste arquivo ZIP.",
        )

    except Exception as e:
      messagebox.showerror(
          "Erro", f"Não foi possível ler o arquivo ZIP:\n{str(e)}"
      )

  def executar_automacao(self):
    item_selecionado = self.combo_item.get()
    qtd_str = self.entry_qtd.get()

    if not item_selecionado or not qtd_str.isdigit() or int(qtd_str) <= 0:
      messagebox.showerror(
          "Erro", "Selecione um item e informe uma quantidade inteira válida."
      )
      return

    quantidade = int(qtd_str)

    resposta = messagebox.askokcancel(
        "Atenção",
        "Tudo pronto!\n\n1. Deixe a janela do WinRAR aberta na tela com o"
        " arquivo correto.\n2. O script vai aguardar 3 segundos e começar a"
        f" disparar {quantidade} impressões do item:\n->"
        f" {item_selecionado}\n\nDeseja continuar?",
    )

    if not resposta:
      return

    self.root.withdraw()
    time.sleep(3)  # Tempo para focar na tela do WinRAR

    try:
      for i in range(quantidade):
        # 1. Clique esquerdo para selecionar o item na tela atual
        pyautogui.click()
        time.sleep(0.05)  # 50 milissegundos solicitados

        # 2. Clique direito para abrir as opções de menu
        pyautogui.rightClick()
        time.sleep(0.3)

        # 3. Pressiona a tecla 'i' para acionar a opção "Imprimir"
        pyautogui.press("i")
        time.sleep(1.5)  # Aguarda o comando processar

      messagebox.showinfo(
          "Sucesso",
          f"Processo concluído!\nForam disparadas {quantidade} impressões de"
          f" '{item_selecionado}'.",
      )

    except Exception as e:
      messagebox.showerror("Erro na Automação", f"Ocorreu um erro: {str(e)}")

    self.root.deiconify()


if __name__ == "__main__":
  # Executa a checagem de segurança remota antes de abrir a janela
  if not verificar_seguranca_remota():
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Acesso Negado",
        "Este aplicativo foi desativado remotamente por segurança ou sem"
        " conexão com a internet.",
    )
    root.destroy()
  else:
    root = tk.Tk()
    app = AutomacaoWinRARApp(root)
    root.mainloop()