from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging

# Configuração do Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Seu ID de chat no Telegram e Token do Bot
MEU_CHAT_ID = '5427353052'
TOKEN = '6918125741:AAHJJmC-clGtfuY27gZm0PgSoHdgrDPLoEE'

# Função para cadastrar usuário
async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = ' '.join(context.args)
    nome_usuario = context.args[0]  # Supondo que o nome do usuário é o primeiro argumento

    # Verificar se o usuário já está cadastrado
    usuario_ja_cadastrado = False
    try:
        with open("assinaturas.txt", "r") as file:
            for line in file:
                if nome_usuario.lower() == line.lower().split()[0]:  # Compara o nome do usuário
                    usuario_ja_cadastrado = True
                    break
    except FileNotFoundError:
        pass  # Arquivo ainda não existe, será criado depois

    # Adicionar usuário se não estiver cadastrado
    if not usuario_ja_cadastrado:
        with open("assinaturas.txt", "a") as file:
            file.write(user_data + "\n")
        await update.message.reply_text("Usuário cadastrado com sucesso!")
    else:
        await update.message.reply_text("Usuário já cadastrado.")

# Função para consultar usuário
async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nome = ' '.join(context.args)
    try:
        with open("assinaturas.txt", "r") as file:
            encontrado = False
            for line in file:
                if nome.lower() in line.lower():
                    await update.message.reply_text(line)
                    encontrado = True
                    break
            if not encontrado:
                await update.message.reply_text("Usuário não encontrado.")
    except FileNotFoundError:
        await update.message.reply_text("Arquivo de assinaturas não encontrado.")

# Função para verificar assinaturas expiradas
async def verificar_expiracoes(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("assinaturas.txt", "r") as file:
            for line in file:
                dados = line.split()
                data_expiracao = datetime.strptime(dados[-1], "%d/%m/%Y")
                if data_expiracao.date() <= datetime.now().date():
                    await context.bot.send_message(chat_id=MEU_CHAT_ID, text=f"A assinatura expirou: {line}")
    except FileNotFoundError:
        logging.info("Arquivo de assinaturas não encontrado.")

# Função principal
def main():
    application = Application.builder().token(TOKEN).build()

    cadastrar_handler = CommandHandler("cadastrar", cadastrar)
    consultar_handler = CommandHandler("consultar", consultar)

    application.add_handler(cadastrar_handler)
    application.add_handler(consultar_handler)

    # Configuração do APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(verificar_expiracoes, 'cron', hour=0, minute=0, args=[application])
    scheduler.start()

    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()
