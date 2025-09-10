import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Lista de departamentos (carpetas principales)
DEPARTAMENTOS = [
    "Francisco Morazán", "Comayagua", "La Paz", "Intibucá",
    "Lempira", "Olancho", "El Paraíso", "Choluteca", "Valle"
]

# Diccionario para mantener el estado del usuario
user_data = {}

# Crear carpetas base al iniciar el bot
def crear_carpetas_base():
    for depto in DEPARTAMENTOS:
        os.makedirs(f"BACKUP MP 2025/{depto}", exist_ok=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[d] for d in DEPARTAMENTOS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "📂 HOLA!!! Bienvenido al bot 🤖 de backup." \
         "Por favor selecciona el departamento:",
        reply_markup=reply_markup
    )

# Manejo de texto: elegir departamento o escribir nombre del sitio
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Paso 1: Selección de departamento
    if text in DEPARTAMENTOS:
        user_data[user_id] = {"departamento": text}
        await update.message.reply_text(
            f"Departamento seleccionado: {text}.\nAhora escribe el 📝 NOMBRE DEL SITIO donde te encuentras:"
        )
        return

    # Paso 2: Nombre del sitio
    if user_id in user_data and "departamento" in user_data[user_id] and "sitio" not in user_data[user_id]:
        user_data[user_id]["sitio"] = text

        depto = user_data[user_id]["departamento"]
        sitio = user_data[user_id]["sitio"]
        path = f"BACKUP MP 2025/{depto}/{sitio}"
        os.makedirs(path, exist_ok=True)

        await update.message.reply_text(
            f"Sitio registrado: {sitio}.\nYa puedes subir BACKUP se guardara en:\n{depto}/{sitio}"
        )
        return

    # Mensaje de error si el flujo no está claro
    await update.message.reply_text(
        "Usa /start para comenzar nuevamente y seleccionar un departamento."
    )

# Manejo de documentos
async def recibir_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data or "departamento" not in user_data[user_id] or "sitio" not in user_data[user_id]:
        await update.message.reply_text("Primero selecciona un departamento y un sitio usando /start.")
        return

    depto = user_data[user_id]["departamento"]
    sitio = user_data[user_id]["sitio"]
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    save_path = f"BACKUP MP 2025/{depto}/{sitio}/{file_name}"

    await file.download_to_drive(save_path)
    await update.message.reply_text(f"✅ BACKUP guardado en: {depto}/{sitio}")
    await update.message.reply_text(f"▶️ PRESIONA /start nuevamente para guardar nuevo BACKUP")

# Programa principal
def main():
    crear_carpetas_base()
    TOKEN = "8432653727:AAGIyqPf9nC_IdvG24Crnk5pbA6ZVweyIvY"  # ← Reemplaza con el token de tu bot

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, recibir_documento))

    print("🤖 Bot en ejecución...")
    app.run_polling()

if __name__ == '__main__':
    main()
