import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import os
from PIL import Image, ImageTk
import pyperclip

class UserManagementApp:
    def __init__(self, root):
        self.root = root
        root.title('Sistema de Gerenciamento de Usuários 1.0')

        self.setup_widgets()
        self.users_file = 'bd.txt'
        self.load_users()
        self.check_for_expiring_users()

    def setup_widgets(self):
        # Carregar e exibir a logo
        self.logo_image = Image.open("logo.png")  # Substitua pelo caminho correto
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.root, image=self.logo_photo)
        self.logo_label.pack()

        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        ttk.Label(frame, text='Nome:').grid(row=0, column=0, sticky='w')
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky='ew')

        ttk.Label(frame, text='Informações:').grid(row=1, column=0, sticky='w')
        self.info_entry = ttk.Entry(frame)
        self.info_entry.grid(row=1, column=1, sticky='ew')

        ttk.Label(frame, text='Tipo de Plano:').grid(row=2, column=0, sticky='w')
        self.plan_var = tk.StringVar()
        self.plan_combobox = ttk.Combobox(frame, textvariable=self.plan_var)
        self.plan_combobox['values'] = ('Básico - 32,90', 'Intermediário - 42,90', 'Avançado - 59,90')
        self.plan_combobox.grid(row=2, column=1, sticky='ew')

        ttk.Label(frame, text='Data de Expiração (dd/mm/aaaa):').grid(row=3, column=0, sticky='w')
        self.expiry_date_entry = ttk.Entry(frame)
        self.expiry_date_entry.grid(row=3, column=1, sticky='ew')

        self.btn_register = ttk.Button(frame, text="✅ Efetuar Cadastro", command=self.register_user)
        self.btn_register.grid(row=4, column=0, columnspan=2)
        self.btn_search_user = ttk.Button(frame, text="🔍 Pesquisar Usuário", command=self.search_user)
        self.btn_search_user.grid(row=6, column=0, columnspan=2)
        self.btn_toggle_status = ttk.Button(frame, text="✅ Ativar/Desativar", command=self.toggle_user_status)
        self.btn_toggle_status.grid(row=7, column=0, columnspan=2)
        self.btn_show_users = ttk.Button(frame, text="👤 Exibir Usuários", command=self.show_users)
        self.btn_show_users.grid(row=5, column=0, columnspan=2)

        self.btn_show_disabled = ttk.Button(frame, text="❌ Exibir Desativados", command=self.show_disabled_users)
        self.btn_show_disabled.grid(row=8, column=0, columnspan=2)
        self.btn_count_users = ttk.Button(frame, text="🔄 Total de Usuários", command=self.count_users)
        self.btn_count_users.grid(row=11, column=0, columnspan=2)  # Ajuste a posição conforme necessário
        self.btn_copy_message = ttk.Button(frame, text="📤 Mensagem Cobrança", command=self.copy_message)
        self.btn_copy_message.grid(row=9, column=0, columnspan=2)
        

        self.users_text = tk.Text(self.root, height=10)
        self.users_text.pack(padx=10)

        self.total_label = ttk.Label(self.root, text='Total em Caixa: R$ 0.00')
        self.total_label.pack()

        # Footer com direitos autorais
        self.footer_label = ttk.Label(self.root, text='© 2023 LisboaCodes - Todos os direitos reservados')
        self.footer_label.pack(side='bottom')

    def register_user(self):
        name = self.name_entry.get()
        info = self.info_entry.get()
        plan = self.plan_combobox.get()
        expiry_date = self.expiry_date_entry.get()
         # Verifica se todos os campos estão preenchidos
        if not (name and info and plan and expiry_date):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        with open(self.users_file, 'a') as file:
            file.write(f'{name}|{info}|{plan}|{expiry_date}|1\n')

        self.load_users()
        self.clear_input_fields()
        messagebox.showinfo("Cadastro", "Usuário cadastrado com sucesso!")

    def clear_input_fields(self):
        self.name_entry.delete(0, tk.END)
        self.info_entry.delete(0, tk.END)
        self.plan_combobox.set('')
        self.expiry_date_entry.delete(0, tk.END)

    def load_users(self):
        if not os.path.exists(self.users_file):
            open(self.users_file, 'w').close()

        with open(self.users_file, 'r') as file:
            users = file.readlines()

        user_data = []
        for user in users:
            parts = user.strip().split('|')
            if len(parts) == 4:
                name, info, plan, expiry_date_str = parts
                status = '1'
            elif len(parts) == 5:
                name, info, plan, expiry_date_str, status = parts
            else:
                continue

            try:
                expiry_date = datetime.datetime.strptime(expiry_date_str, "%d/%m/%Y")
                user_data.append((name, info, plan, expiry_date, status, expiry_date_str))
            except ValueError:
                continue

        user_data.sort(key=lambda x: x[3])

        self.users_text.delete('1.0', tk.END)
        total_value = 0
        for name, _, plan, _, status, expiry_date_str in user_data:
            if status == '1':
                if 'Básico' in plan:
                    total_value += 32.90
                elif 'Intermediário' in plan:
                    total_value += 42.90
                elif 'Avançado' in plan:
                    total_value += 59.90

                self.users_text.insert(tk.END, f'Nome: {name}, Plano: {plan}, Expira em: {expiry_date_str}\n')

        self.total_label.config(text=f'Total em Caixa: R$ {total_value:.2f}')

    def show_users(self):
        self.load_users()
        
    def count_users(self):
        with open(self.users_file, 'r') as file:
            users = file.readlines()

        total_users = len(users)
        disabled_users = sum(user.strip().split('|')[-1] == '0' for user in users)

        messagebox.showinfo("Contagem de Usuários", f"Total de Usuários: {total_users}\nUsuários Desativados: {disabled_users}")    

    def search_user(self):
        search_name = simpledialog.askstring("Pesquisar Usuário", "Digite o nome do usuário:")
        if search_name:
            found = False
            with open(self.users_file, 'r') as file:
                for user in file:
                    name, info, plan, expiry_date, status = user.strip().split('|')
                    if search_name.lower() in name.lower() and status == '1':
                        found = True
                        self.users_text.delete('1.0', tk.END)
                        self.users_text.insert(tk.END, f'Nome: {name}, Informações: {info}, Plano: {plan}, Expira em: {expiry_date}\n')
                        break

            if not found:
                messagebox.showinfo("Pesquisa", "Usuário não encontrado.")

    def toggle_user_status(self):
        username = simpledialog.askstring("Ativar/Desativar Usuário", "Digite o nome do usuário:")
        if username:
            self.toggle_status(username)
            self.load_users()

    def toggle_status(self, username):
        updated_users = []
        with open(self.users_file, 'r') as file:
            for user in file:
                name, info, plan, expiry_date, status = user.strip().split('|')
                if name == username:
                    status = '0' if status == '1' else '1'
                updated_users.append('|'.join([name, info, plan, expiry_date, status]) + '\n')

        with open(self.users_file, 'w') as file:
            file.writelines(updated_users)

    def show_disabled_users(self):
        with open(self.users_file, 'r') as file:
            disabled_users = [user for user in file if user.strip().split('|')[-1] == '0']

        self.users_text.delete('1.0', tk.END)
        for user in disabled_users:
            name, info, plan, expiry_date, _ = user.strip().split('|')
            self.users_text.insert(tk.END, f'Nome: {name}, Plano: {plan}, Expira em: {expiry_date}\n')

    def check_for_expiring_users(self):
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        expiring_users = []
        with open(self.users_file, 'r') as file:
            for user in file:
                parts = user.strip().split('|')
                if len(parts) == 5:
                    name, _, _, expiry_date, status = parts
                elif len(parts) == 4:
                    name, _, _, expiry_date = parts
                    status = '1'
                else:
                    continue

                if expiry_date == today and status == '1':
                    expiring_users.append(name)

        if expiring_users:
            expiring_msg = "Usuários expirando hoje: " + ", ".join(expiring_users)
            messagebox.showinfo("Usuários Expirando", expiring_msg)

    def copy_message(self):
        message = (
        "🌟 Aviso de Renovação FileHub - Plano XXX 🌟\n\n"
        "Olá! Sua assinatura do Plano XXX na FileHub expirou.\n\n"
        "Para continuar desfrutando de nossos serviços:\n"
        "1. Renove aqui: [Link de Renovação]\n"
        "2. Pagamento via PIX: [Chave PIX]\n\n"
        "Após o pagamento, seu acesso será imediatamente liberado.\n\n"
        "🕒 Horário de Suporte:\n"
        "- Segunda a Sexta: 09h às 12h e 14h às 18h\n"
        "- Sábado: 09h às 12h\n\n"
        "Para qualquer dúvida, estamos à disposição!"
    )
        pyperclip.copy(message)
        messagebox.showinfo("Mensagem Copiada", "A mensagem padrão foi copiada para a área de transferência.")

# Criação da janela principal
root = tk.Tk()
app = UserManagementApp(root)
root.mainloop()
