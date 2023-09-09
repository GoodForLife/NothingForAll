import requests, subprocess
LOCAL_VERSION = "1.1"
VERSION_URL = "https://raw.githubusercontent.com/mxvwrt/pyowrt/main/version"

bash_script = """
#!/bin/bash
rm -r app.py
wget -o app.py https://raw.githubusercontent.com/GoodForLife/NothingForAll/main/app.py
"""
def version_check():
    try:
        response = requests.get(VERSION_URL)
        remote_version = response.text.strip()
        if remote_version > LOCAL_VERSION:
            return True
        else:
            return False
    except Exception as e:
        print("Error Saat Mengambil Versi Yang Terbaru, Silahkan Cek Koneksi Internet Anda")
        return False
def version_check_upgrade():
    try:
        response = requests.get(VERSION_URL)
        remote_version = response.text.strip()
        return remote_version
    except Exception as e:
        print("Error Saat Mengambil Versi Yang Terbaru, Silahkan Cek Koneksi Internet Anda")
        return None
def update_app():
    remote_version = version_check_upgrade()  # Menyimpan hasil dari version_check() ke dalam variabel remote_version
    if remote_version is not None:
        if remote_version > LOCAL_VERSION:
            print(f"Versi terbaru ({remote_version}) tersedia. Memeriksa dan menghapus file jika diperlukan...")
            # Simpan skrip bash ke dalam file dengan nama my_script.sh
            with open("update.sh", "w") as script_file:
                script_file.write(bash_script)

            # Beri izin eksekusi pada skrip bash
            subprocess.run(["chmod", "+x", "update.sh"])

            # Jalankan skrip bash
            subprocess.run(["./update.sh"])
            subprocess.run(["python app.py"])
            print("Update selesai.")
        else:
            print("Anda sudah menggunakan versi yang terbaru.")
    else:
        print("Tidak dapat mengambil versi online. Update dibatalkan.")
