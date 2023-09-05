import os, telebot, subprocess, re, time, socket, asyncio, requests, json, random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
from pytube import YouTube

# Load the configuration from the JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Read configuration values from the loaded JSON
TELEGRAM_BOT_TOKEN = config.get('telegram_bot_token')
ALLOWED_USERS = config.get('allowed_users', '').split(",")
ALLOWED_USERS = [int(user_id) for user_id in ALLOWED_USERS if user_id]

download_paths = config.get('download_paths', {})
PATH_ARIA = download_paths.get('aria')
PATH_GDOWN = download_paths.get('gdown')
PATH_PYTUBE = download_paths.get('pytube')

vnstat_config = config.get('vnstat', {})
VNSTAT_PATH = vnstat_config.get('folder')
VNSTAT_IMG_5M = vnstat_config.get('images', {}).get('5_minute')
VNSTAT_IMG_H = vnstat_config.get('images', {}).get('hours')
VNSTAT_IMG_HG = vnstat_config.get('images', {}).get('hours_graph')
VNSTAT_IMG_D = vnstat_config.get('images', {}).get('days')
VNSTAT_IMG_M = vnstat_config.get('images', {}).get('months')
VNSTAT_IMG_Y = vnstat_config.get('images', {}).get('years')
VNSTAT_IMG_TD = vnstat_config.get('images', {}).get('top_days')

pytube_ask = {}
active_downloads = {}
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def membuat_random_msg():
    json_url = "https://raw.githubusercontent.com/mxvwrt/PyBotOWRT/main/pesan/random.json"

    response = requests.get(json_url)
    if response.status_code == 200:
        json_data = response.text
        data = json.loads(json_data)

        random_msg_key = random.choice(list(data.keys()))
        random_msg = data[random_msg_key]["msg"]

        return random_msg
    else:
        return "Gagal mendapatkan data JSON."

# kirim_random = membuat_random_msg()
# bot.send_message(chat_id, membuat_random_msg())
def create_keyboard(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for row in buttons:
        keyboard.row(*[types.KeyboardButton(button) for button in row])

    return keyboard

start_layout_btn = [
    ["🚀 OpenClash", "⏳ Vnstat", "💠 Download"],
    ["✈️ Speedtest", "👀 Web to IP", "⁉️ Cek IP"],
    ["♻️ Adb", "🌿 Ram", "🔓 Spek"]
]


vnstat_layout_btn = [
    ["Foto / Gambar", "Data / Text"],
    ["Batal"]
]
vnstat_submenu_layout_btn = [
    ["5 Menit", "Jam", "Jam Grafik"],
    ["Harian", "Bulanan", "Tahun"],
    ["Top Harian", "Batal"]
]
adb_layout_btn = [
    ["All Device", "TCPIP 5555", "Reboot Devices"],
    ["Batal"]
]
download_layout_btn = [
    ["Aria2c", "Gdown (Dengan ID)", "Pytube (Youtube)"],
    ["Batal"]
]
path_download_layout_btn = [
    ["Default", "Custom"],
    ["Batal"]
]


oc_layout_btn = [
    ["Mulai", "Stop", "Restart"],
    ["Reload", "Enable Autostart", "Disable Autostart"],
    ["Cek Autostart", "Batal"]
]
keyboard_oc = create_keyboard(oc_layout_btn)
keyboard_start = create_keyboard(start_layout_btn)
keyboard_vnstat = create_keyboard(vnstat_layout_btn)
keyboard_vnstat_submenu = create_keyboard(vnstat_submenu_layout_btn)
keyboard_adb = create_keyboard(adb_layout_btn)
keyboard_download = create_keyboard(download_layout_btn)
keyboard_path= create_keyboard(path_download_layout_btn)



perintah_batal = "Perintah dibatalkan."
main_menu = "Pilihan Opsi Menu :"
invalid_perintah = "Perintah Tidak Ada !"
develop_by = "\n\n───    Dibuat oleh <a href='tg://user?id=1451137464'>MXVWRT </a>    ───" 


@bot.message_handler(commands=['start'])
def send_menu(message):
    bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
@bot.message_handler(func=lambda message: True)
def handle_menu_selection(message):
    if message.from_user.id not in ALLOWED_USERS:
        bot.send_message(message.chat.id, "Anda tidak diizinkan untuk menggunakan perintah BOT ini.")
        return
    selected_command = message.text.lower()
    if selected_command == "🌿 ram":
        chat_id = message.chat.id
        ram_info = get_ram_info()
        bot.send_message(chat_id, f"Informasi RAM:\n\n{ram_info}", parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(message.chat.id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif selected_command == "🚀 openclash":
        bot.reply_to(message, "Opsi Untuk Openclash:\nKeterangan \n"
                            "Mulai = Mulai Openclash\n"
                            "Stop = Stop Openclash\n"
                            "Restart = Restart Openclash\n"
                            "Reload = Reload configuration\n"
                            "Enable Autostart = Enable service autostart\n"
                            "Disable Autostart = Disable service autostart\n"
                            "Cek Autostart = Periksa apakah layanan dimulai saat boot"
                            "Batalkan Perintah\n", reply_markup=keyboard_oc)
        bot.register_next_step_handler(message, process_openclash_option)
    elif selected_command == "⏳ vnstat":
        bot.reply_to(message, "Pilihan Opsi Vnstat :\n", reply_markup=keyboard_vnstat)
        bot.register_next_step_handler(message, handle_vnstat_main_option)
    elif selected_command == "⁉️ cek ip":
        chat_id = message.chat.id
        public_ip = get_ip_info()
        if public_ip:
            bot.send_message(chat_id, public_ip,parse_mode='MarkdownV2')
            random_message = membuat_random_msg()
            bot.send_message(chat_id, random_message, parse_mode='HTML')
            time.sleep(0.5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
        else:
            bot.send_message(chat_id, "Gagal mendapatkan alamat IP publik.")
            random_message = membuat_random_msg()
            bot.send_message(chat_id, random_message, parse_mode='HTML')
            time.sleep(0.5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    elif selected_command == "♻️ adb":
        bot.reply_to(message, "Pilihan Opsi Untuk ADB :\n", reply_markup=keyboard_adb)
        bot.register_next_step_handler(message, process_adb_option)
    elif selected_command == "💠 download":
        bot.reply_to(message, "Pilih Metode Download :\n", reply_markup=keyboard_download)
        bot.register_next_step_handler(message, choose_download_method)
    elif selected_command == "✈️ speedtest":
        chat_id = message.chat.id
        result = execute_speedtest_secure()
        bot.send_message(chat_id, result, parse_mode='HTML')
        time.sleep(0.5)
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif selected_command == "🔓 spek":
        chat_id = message.chat.id
        cleaned_output = get_cleaned_output()
        formatted_text = f"<b>───   SPESIFIKASI   ───</b>\n{cleaned_output}<b>───────────────────</b>"
        bot.send_message(chat_id, formatted_text, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif selected_command == "👀 web to ip":
        bot.reply_to(message, 'Masukkan Domain:')
        bot.register_next_step_handler(message, process_domain_name)
    else:
        bot.send_message(message.chat.id, "Perintah tidak valid. Pilih perintah yang valid dari menu.")
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)

def get_ram_info():
    try:
        output = subprocess.check_output(["/bin/ram"], text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def process_openclash_option(message):
    option = message.text.lower()
    chat_id = message.chat.id
    options = {
        "batal": "cancel",
        "mulai": "start",
        "stop": "stop",
        "restart": "restart",
        "reload": "reload",
        "enable autostart": "enable",
        "disable autostart": "disable",
        "cek autostart": "enabled"
    }
    if option in options:
        command_option = options[option]
        if command_option == "cancel":
            response = perintah_batal
        else:
            result = run_openclash_command(command_option)
            response = f"Option {option}. {command_option}:\n\n{result}"
    else:
        response = "Opsi Tidak Ada Di Menu."
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    bot.send_message(message.chat.id, response, parse_mode='HTML')
    random_message = membuat_random_msg()
    bot.send_message(chat_id, random_message, parse_mode='HTML')
    time.sleep(0.5)
    bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
def run_openclash_command(option):
    try:
        output = subprocess.check_output(["/etc/init.d/openclash", option], text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def handle_vnstat_main_option(message):
    option = message.text.lower()
    if option == "batal":
        bot.send_message(message.chat.id, perintah_batal)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    elif option == "foto / gambar":
        bot.reply_to(message, "Pilihan Opsi Untuk Metode Gambar Dengan Vnstat :\n", reply_markup=keyboard_vnstat_submenu)
        bot.register_next_step_handler(message, process_vnstat_img)
    elif option == "data / text":
        bot.reply_to(message, "Pilihan Opsi Untuk Metode Data Dengan Vnstat :\n", reply_markup=keyboard_vnstat_submenu)
        bot.register_next_step_handler(message, process_vnstat_data)
def process_vnstat_img(message):
    subprocess.run(["/www/vnstati/vnstati.sh"])
    option = message.text.lower()
    if option == "batal":
        bot.send_message(message.chat.id, perintah_batal)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    elif option == "5 menit":
        if VNSTAT_PATH and VNSTAT_IMG_5M:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_5M)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif option == "jam":
        if VNSTAT_PATH and VNSTAT_IMG_H:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_H)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif option == "jam grafik":
        if VNSTAT_PATH and VNSTAT_IMG_HG:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_HG)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    elif option == "harian":
        if VNSTAT_PATH and VNSTAT_IMG_D:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_D)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    elif option == "bulanan":
        if VNSTAT_PATH and VNSTAT_IMG_M:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_M)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    elif option == "tahun":
        if VNSTAT_PATH and VNSTAT_IMG_Y:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_Y)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    elif option == "top harian":
        if VNSTAT_PATH and VNSTAT_IMG_TD:
            chat_id = message.chat.id
            combined_path = os.path.join(VNSTAT_PATH, VNSTAT_IMG_TD)
            if os.path.exists(combined_path):
                with open(combined_path, 'rb') as f:
                    bot.send_photo(chat_id, photo=f)
                random_message = membuat_random_msg()
                bot.send_message(chat_id, random_message, parse_mode='HTML')
            else:
                bot.send_message(chat_id, text=f"File '{os.path.basename(combined_path)}' TIDAK ADA.")
        else:
            bot.send_message(chat_id, text="Variabel Path tidak disetel.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    else:
        bot.send_message(message.chat.id, "Opsi tidak valid. Silahkan pilih 0-7.")
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
def process_vnstat_data(message):
    chat_id = message.chat.id
    option = message.text.strip().lower()
    options = {
        "batal": "cancel",
        "5 menit": "-5",
        "jam": "-h",
        "jam grafik": "-hg",
        "harian": "-d",
        "bulanan": "-m",
        "tahun": "-y",
        "top harian": "-t"
    }
    if option in options:
        command_option = options[option]
        if command_option == "cancel":
            bot.send_message(chat_id, "Perintah dibatalkan.")
            time.sleep(0.5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
        else:
            result = execute_vnstat(command_option)
            bot.send_message(chat_id, result, parse_mode='HTML')
            random_message = membuat_random_msg()
            bot.send_message(chat_id, random_message, parse_mode='HTML')
            time.sleep(5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    else:
        bot.send_message(chat_id, "Opsi tidak valid. Harap pilih opsi yang valid (1 hingga 7).")
def execute_vnstat(command):
    try:
        output = subprocess.check_output(["vnstat", command], text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def get_ip_info():
    url = 'http://ip-api.com/json//?fields=country,countryCode,region,regionName,city,timezone,isp,org,as,asname,query'
    response = requests.get(url).json()
    
    ip_info = (
        "`\n"
        "==== Informasi Detail IP ====\n"
        "Nama Negara   : " + response['country'] + "\n"
        "Kode Negara   : " + response['countryCode'] + "\n"
        "Region        : " + response['region'] + "\n"
        "Nama Region   : " + response['regionName'] + "\n"
        "Kota          : " + response['city'] + "\n"
        "Zona Waktu    : " + response['timezone'] + "\n"
        "ISP           : " + response['isp'] + "\n"
        "Organisasi    : " + response['org'] + "\n"
        "AS            : " + response['as'] + "\n"
        "Nama AS       : " + response['asname'] + "\n"
        "Alamat IP     : " + response['query'] + "\n"
        "===============================\n"
        "`"
        "Dibuat oleh [MXVWRT](tg://user?id=1451137464)\n"
        
    )
    return ip_info

def process_adb_option(message):
    chat_id = message.chat.id
    option = message.text.lower()
    if option == "all device":
        result = execute_adb("devices")
        bot.send_message(chat_id, result, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif option == "tcpip 5555":
        result = execute_adb("tcpip 5555")
        bot.send_message(chat_id, result, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif option == "reboot devices":
        result = execute_adb("reboot")
        bot.send_message(chat_id, result, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    elif option == "batal":
        bot.send_message(chat_id, perintah_batal)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    else:
        bot.send_message(chat_id, "Opsi Tidak Ada Di Menu")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
def execute_adb(command):
    try:
        output = subprocess.check_output(["/usr/bin/adb"] + command.split(), text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def choose_download_method(message):
    download_method = message.text.lower()
    if download_method == "aria2c":
        bot.reply_to(message, "Harap Kirimkan Link Unduhan : ")
        bot.register_next_step_handler(message, aria2_download_with_link)
    elif download_method == "gdown (dengan id)":
        bot.reply_to(message, "Kirimkan ID file Google Drive :")
        bot.register_next_step_handler(message, gdown_download_with_file_id)
    elif download_method == "pytube (youtube)":
        bot.reply_to(message, "Kirimkan URL video YouTube :")
        bot.register_next_step_handler(message, pytube_process_url)
    elif download_method == "batal":
        bot.reply_to(message, perintah_batal)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    else:
        bot.reply_to(message, invalid_perintah)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
def aria2_download_with_link(message):
    download_link = message.text.strip()
    bot.reply_to(message, f"Apakah Anda Ingin Default Path {PATH_ARIA} Atau Custom ?", reply_markup=keyboard_path)
    bot.register_next_step_handler(message, aria2_download_with_path_decision, download_link)
def aria2_download_with_path_decision(message, download_link):
    decision = message.text.strip().lower()
    if decision == "default":
        download_path = PATH_ARIA
        aria2_download_file(message, download_link, download_path)
    elif decision == "custom":
        bot.reply_to(message, "Berikan Custom Pathnya (Tidak Permanen) :")
        bot.register_next_step_handler(message, aria2_download_with_path, download_link)
    elif decision == "batal":
        bot.reply_to(message, perintah_batal)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    else:
        bot.reply_to(message, invalid_perintah)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
def aria2_download_with_path(message, download_link):
    download_path = message.text.strip()
    aria2_download_file(message, download_link, download_path)
def aria2_download_file(message, download_link, download_path):
    if ALLOWED_USERS and message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "Anda tidak diizinkan untuk menggunakan perintah ini.")
        return
    bot.send_message(message.chat.id, "Download dimulai. Harap tunggu...")
    active_downloads[message.chat.id] = True
    aria2c_cmd = ["aria2c", download_link, "-d", download_path]
    subprocess.run(aria2c_cmd)
    aria2_send_completion_message(message, download_path)

def aria2_send_completion_message(message, download_path):
    chat_id = message.chat.id
    bot.reply_to(message, f"Pengunduhan selesai. Berkas disimpan sebagai: {download_path}")
    random_message = membuat_random_msg()
    bot.send_message(chat_id, random_message, parse_mode='HTML')
    time.sleep(0.5)
    bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
def gdown_download_with_file_id(message):
    file_id = message.text.strip()
    bot.reply_to(message, "Silakan masukkan nama file yang diinginkan dengan ekstensi (.zip dan lain lain ) untuk gdown (WAJIB!):")
    bot.register_next_step_handler(message, gdown_download_with_filename, file_id)
def gdown_download_with_filename(message, file_id):
    filename_with_extension = message.text.strip()
    bot.reply_to(message, f"Apakah Anda Ingin Default Path {PATH_GDOWN} Atau Custom ?", reply_markup=keyboard_path)
    bot.register_next_step_handler(message, gdown_download_with_path_decision, file_id, filename_with_extension)
def gdown_download_with_path_decision(message, file_id, filename_with_extension):
    decision = message.text.strip().lower()
    if decision == "default":
        download_path = os.path.join(PATH_GDOWN, filename_with_extension)
        gdown_download_file(message, file_id, download_path)
    elif decision == "custom":
        bot.reply_to(message, "Berikan Custom Pathnya (Tidak Permanen):")
        bot.register_next_step_handler(message, gdown_download_with_path, file_id, filename_with_extension)
    elif decision == "batal":
        bot.reply_to(message, perintah_batal)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)
    else:
        bot.reply_to(message, invalid_perintah)
        time.sleep(0.5)
        bot.send_message(message.chat.id, main_menu, reply_markup=keyboard_start)

def gdown_download_with_path(message, file_id, filename_with_extension):
    download_path = message.text.strip()
    download_path = os.path.join(download_path, filename_with_extension)
    gdown_download_file(message, file_id, download_path)
def gdown_download_file(message, file_id, download_path):
    if ALLOWED_USERS and message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "Anda tidak diizinkan untuk menggunakan perintah ini.")
        return
    bot.send_message(message.chat.id, "Download dimulai. Harap tunggu...")
    active_downloads[message.chat.id] = True
    time.sleep(10)
    download_command = f"gdown --id {file_id} -O {download_path} --no-cookies"
    os.system(download_command)
    gdown_send_completion_message(message, download_path, file_id)
def gdown_send_completion_message(message, download_path, file_id):
    chat_id = message.chat.id
    bot.reply_to(message, f"Pengunduhan selesai. Berkas disimpan sebagai: \n{download_path}{file_id}")
    random_message = membuat_random_msg()
    bot.send_message(chat_id, random_message, parse_mode='HTML')
    time.sleep(0.5)
    bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
def pytube_process_url(message):
    chat_id = message.chat.id
    user_message = message.text
    try:
        if user_message.startswith("https://www.youtube.com/"):
            pytube_ask[chat_id] = {'video_url': user_message}
            msg = bot.send_message(chat_id, f"Apakah Anda Ingin Default Path {PATH_PYTUBE} Atau Custom ?", reply_markup=keyboard_path)
            bot.register_next_step_handler(msg, pytube_ask_custom_path)
        else:
            bot.send_message(chat_id, "Mohon kirimkan URL video YouTube yang valid.")
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "Terjadi kesalahan. Mohon coba lagi.")

def pytube_ask_custom_path(message):
    chat_id = message.chat.id
    user_choice = message.text.lower()

    try:
        if user_choice == 'custom':
            msg = bot.send_message(chat_id, "Masukkan jalur penyimpanan kustom:")
            bot.register_next_step_handler(msg, pytube_save_custom_path)
        elif user_choice == "default":
            custom_save_path = PATH_PYTUBE
            pytube_ask[chat_id]['custom_path'] = custom_save_path
            pytube_ask_resolution_available(message, custom_save_path)
        elif user_choice == "batal":
            bot.reply_to(message, perintah_batal)
            time.sleep(0.5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
        else:
            bot.reply_to(message, invalid_perintah)
            time.sleep(0.5)
            bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "Terjadi kesalahan. Mohon coba lagi.")

def pytube_save_custom_path(message):
    chat_id = message.chat.id
    custom_path = message.text.strip()
    if not custom_path:
        bot.send_message(chat_id, "Custom Path Tidak Ada,Membuat Directory Dengan Path = " + custom_path)
        try:
            # Create the directory using subprocess
            subprocess.run(["mkdir", custom_path], check=True)

            bot.send_message(chat_id, "Directory Sudah Terbuat: " + custom_path)
        except subprocess.CalledProcessError:
            bot.send_message(chat_id, "Gagal membuat direktori. Silakan periksa masukan Anda.")

    try:
        pytube_ask[chat_id]['custom_path'] = custom_path
        pytube_ask_resolution_available(message, custom_path)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "Terjadi kesalahan. Mohon coba lagi.")

def pytube_ask_resolution_available(message, custom_path):
    chat_id = message.chat.id
    video_url = pytube_ask[chat_id]['video_url']

    try:
        yt = YouTube(video_url)
        video_streams = yt.streams.filter(file_extension='mp4', progressive=True)

        resolutions_text = "\n".join([f"{idx + 1}. Resolusi: {stream.resolution}" for idx, stream in enumerate(video_streams)])
        resolutions_text += "\n999. Batalkan"

        msg = bot.send_message(chat_id, f"Pilih resolusi video:\n{resolutions_text}")
        bot.register_next_step_handler(msg, pytube_download_video, video_streams)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "Terjadi kesalahan. Mohon coba lagi.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

def pytube_download_video(message, video_streams):
    chat_id = message.chat.id
    user_input = message.text

    if user_input == '999':
        bot.send_message(chat_id, "Perintah dibatalkan.")
        return

    try:
        selected_index = int(user_input) - 1
        selected_stream = video_streams[selected_index]
        custom_path = pytube_ask[chat_id]['custom_path']

        selected_stream.download(output_path=custom_path)
        title = selected_stream.title
        message = f"Video '{title}' berhasil diunduh!"
        bot.send_message(chat_id, message, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    except (ValueError, IndexError):
        bot.reply_to(message, invalid_perintah)
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)

    # Hapus informasi percakapan setelah selesai
    del pytube_ask[chat_id]


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        print(f"Error executing command: {e}")
        return None

def execute_speedtest_secure():
    try:
        output = subprocess.check_output(["speedtest-cli", "--secure"], text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
def process_domain_name(message):
    chat_id = message.chat.id
    domain_name = message.text.strip()
    ip_addresses = get_ip_addresses(domain_name)
    if ip_addresses:
        response = f"Domain <code>{domain_name}</code> :\n"
        for ip_address in ip_addresses:
            response += f"↳ <code>{ip_address}</code>\n"
        bot.reply_to(message, response, parse_mode='HTML')
        random_message = membuat_random_msg()
        bot.send_message(chat_id, random_message, parse_mode='HTML')
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
    else:
        bot.send_message(chat_id, f"Tidak dapat Mengambil IP untuk '{domain_name}'.")
        time.sleep(0.5)
        bot.send_message(chat_id, main_menu, reply_markup=keyboard_start)
def get_ip_addresses(domain_name):
    try:
        ip_addresses = set()
        addrinfo = socket.getaddrinfo(domain_name, None)
        for family, _, _, _, sockaddr in addrinfo:
            ip_address = sockaddr[0]
            ip_addresses.add(ip_address)
        return list(ip_addresses)
    except socket.gaierror as e:
        print(f"Error: {e}")
        return None
def get_cleaned_output():

    command = ["/usr/bin/pyowrt_util"]
    output = subprocess.check_output(command, universal_newlines=True)

    start_index = output.find("Model :")
    if start_index == -1:
        return ""

    end_index = output.find("LAN   :")
    if end_index == -1:
        end_index = len(output)

    output = output[start_index:end_index]

    cleaned_output = re.sub(r'\x1b\[.*?m', '', output)
    cleaned_output = re.sub(r'^s\s+\*\s+', '', cleaned_output, flags=re.MULTILINE)

    cleaned_output = cleaned_output.replace("─" * 50, "")

    return cleaned_output

async def main():
    print("Bot telah berjalan.")
    await bot.infinity_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

