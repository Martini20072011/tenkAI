import google.generativeai as gemini
import json
import pandas as pd
import os
import sys
import openpyxl
import requests # Novo import necessário para a verificação de atualização
from openpyxl.styles import Font, Alignment
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk

# Versão atual do aplicativo
VERSION = "1.0.1"

# --- FUNÇÃO PARA ENCONTRAR ARQUIVOS EMPACOTADOS ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Encontra o caminho da pasta onde o script está sendo executado
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
excel_path = os.path.join(script_dir, 'pedidos.xlsx')

# COLOQUE SUA CHAVE DE API AQUI!
# RECOMENDAÇÃO DE SEGURANÇA: NÃO DEIXE SUA CHAVE EXPOSTA NO CÓDIGO
gemini.configure(api_key="SUA_CHAVE_AQUI")

def rodar_robo():
    conteudo = text_area.get('1.0', tk.END).strip()
    
    if not conteudo:
        messagebox.showerror("Erro", "O campo de texto está vazio.\nPor favor, cole o texto do pedido antes de rodar o robô.")
        return

    try:
        model = gemini.GenerativeModel('gemini-1.5-flash-latest')

        prompt = """
        Você é um analista de pedidos para um distribuidor. Sua função é receber textos de pedidos e extrair os produtos, suas quantidades e seus respectivos preços.

        Instruções:
        1. Analise o texto de entrada para identificar produtos, suas quantidades e preços.
        2. Retorne a resposta APENAS no formato JSON, sem nenhum texto adicional antes ou depois.
        3. O formato do JSON deve ser uma lista de objetos, onde cada objeto tem três chaves: 'produto', 'quantidade' e 'preco'.
        4. O texto pode ter siglas como 'DZ' (dúzia) ou 'CX' (caixa). Coloque a sigla na coluna 'quantidade'. Se não houver quantidade explícita, use "1". Se houver uma quantidade como 'cx c/8kg', 'kg' ou 'CX plástica', inclua isso na coluna 'quantidade'.
        5. O preço pode estar precedido por símbolos como '*' ou '$', e pode ter vírgula. Extraia apenas o valor numérico e o formate para o padrão 'R$ 0,00'.
        6. Se o preço estiver faltando ou for indicado com símbolos como '$$$', retorne o valor da chave 'preco' como "Não informado".
        7. Ignore emojis e qualquer texto de introdução ou conclusão.
        
        Texto para análise:
        """ + conteudo

        response = model.generate_content(prompt)
        resposta_ia = response.text.strip()

        if resposta_ia.startswith("```json"):
            resposta_ia = resposta_ia[7:].strip()
        if resposta_ia.endswith("```"):
            resposta_ia = resposta_ia[:-3].strip()

        json_response = json.loads(resposta_ia)
        df = pd.DataFrame(json_response)

        df = df[['produto', 'quantidade', 'preco']]
        
        with pd.ExcelWriter(excel_path, engine='openyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Pedidos')

            worksheet = writer.sheets['Pedidos']
            
            header_font = Font(name='Calibri', size=15, bold=True)
            header_alignment = Alignment(horizontal='center')

            for cell in worksheet["1:1"]:
                cell.font = header_font
                cell.alignment = header_alignment

            body_font = Font(name='Calibri', size=15)
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.font = body_font

            for column in worksheet.columns:
                max_length = 0
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 10)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            worksheet.freeze_panes = 'A2'

        os.startfile(excel_path)
        messagebox.showinfo("Sucesso", "Tabela de pedidos criada e salva com sucesso!")

    except json.JSONDecodeError:
        messagebox.showerror("Erro", "A IA não retornou um JSON válido. Tente novamente com outro texto.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# --- FUNÇÃO PARA VERIFICAÇÃO DE ATUALIZAÇÃO ---
def check_for_updates():
    try:
        # URL do arquivo de versão no seu site
        version_url = "https://martini20072011.github.io/tenkAI-updates/version.txt"
        
        # Faz a requisição para o arquivo de versão
        response = requests.get(version_url)
        response.raise_for_status() # Lança um erro para status de HTTP ruins
        
        latest_version = response.text.strip()
        
        # Compara a versão online com a versão local
        if latest_version > VERSION:
            messagebox.showinfo(
                "Atualização Disponível", 
                f"Uma nova versão ({latest_version}) do tenkAI está disponível! Por favor, baixe a nova versão do nosso site."
            )
        else:
            print("O aplicativo está atualizado.")
    except requests.exceptions.RequestException as e:
        # Mostra um erro se não conseguir se conectar à internet
        print(f"Erro ao verificar atualizações. Verifique sua conexão com a internet. Detalhes: {e}")
    except Exception as e:
        # Captura outros erros
        print(f"Erro inesperado ao verificar atualizações: {e}")

# --- FUNÇÕES PARA OS BOTÕES ---
def alpha_button_click():
    button_frame.place_forget()
    analysis_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

def beta_button_click():
    messagebox.showinfo("Beta", "Função Beta em desenvolvimento.")

def cortana_button_click():
    messagebox.showinfo("Cortana", "Função Cortana em desenvolvimento.")
    
def voltar_tela_inicial():
    analysis_frame.place_forget()
    button_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

def exit_fullscreen(event):
    root.attributes('-fullscreen', False)

# --- CONFIGURAÇÕES DA JANELA PRINCIPAL ---
root = tk.Tk()
root.title("tenkAI")
root.attributes('-fullscreen', True)
root.bind('<Escape>', exit_fullscreen)

# Chame a função de verificação de atualização aqui
check_for_updates()

# --- CARREGAR E PREPARAR AS IMAGENS ---
try:
    caminho_fundo = resource_path('assets/novo_fundo.jpg')
    caminho_logo_empresa = resource_path('assets/logo_martini_transparente.png')
    caminho_logo_oficial = resource_path('assets/logo ofc.png')

    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    
    fundo_pil = Image.open(caminho_fundo)
    fundo_pil = fundo_pil.resize((largura_tela, altura_tela), Image.LANCZOS)

    logo_empresa_pil = Image.open(caminho_logo_empresa)
    logo_empresa_pil = logo_empresa_pil.resize((200, 200), Image.LANCZOS)
    
    fundo_pil.paste(logo_empresa_pil, (20, 20), logo_empresa_pil)
    
    logo_oficial_pil = Image.open(caminho_logo_oficial)
    logo_oficial_pil = logo_oficial_pil.resize((600, 600), Image.LANCZOS)

    fundo_img = ImageTk.PhotoImage(fundo_pil)
    logo_oficial_img = ImageTk.PhotoImage(logo_oficial_pil)
    
    fundo_label = tk.Label(root, image=fundo_img)
    fundo_label.place(x=0, y=0, relwidth=1, relheight=1)

    logo_oficial_label = tk.Label(root, image=logo_oficial_img, bg="white")
    logo_oficial_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

except FileNotFoundError as e:
    root.configure(bg="white")
    messagebox.showwarning("Aviso", f"Arquivo não encontrado: {e.filename}")

# --- FRAME PARA OS BOTÕES DE SELEÇÃO ---
button_frame = tk.Frame(root)
button_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# Botão Alpha
alpha_button = tk.Button(button_frame, text="Alpha", command=alpha_button_click, font=("Helvetica", 16), width=18, bg="white", bd=1, relief="solid")
alpha_button.pack(side=tk.LEFT, padx=15, pady=10)

# Botão Cortana (em destaque)
cortana_button = tk.Button(button_frame, text="Botão Cortana")