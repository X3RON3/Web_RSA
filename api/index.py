from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Fungsi utilitas
def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            return False
    return True

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

def split_ascii(ascii_value):
    return ascii_value // 10, ascii_value % 10

def combine_ascii(part1, part2):
    return part1 * 10 + part2

def encrypt(message, e, n):
    try:
        encrypted_message = []
        for char in message:
            ascii_value = ord(char)
            part1, part2 = split_ascii(ascii_value)
            encrypted_message.append(f"{mod_exp(part1, e, n)}-{mod_exp(part2, e, n)}")
        return ", ".join(encrypted_message)
    except Exception as ex:
        print(f"Error saat enkripsi: {ex}")
        raise

def decrypt(encrypted_message, d, n):
    try:
        decrypted_message = ""
        pairs = encrypted_message.split(", ")
        for pair in pairs:
            part1, part2 = map(int, pair.split("-"))
            ascii_value = combine_ascii(mod_exp(part1, d, n), mod_exp(part2, d, n))
            decrypted_message += chr(ascii_value)
        return decrypted_message
    except Exception as ex:
        print(f"Error saat deskripsi: {ex}")
        raise

@app.route('/')
def index():
    return render_template('rsa.html')

# Endpoint untuk menghitung nilai e dan n
@app.route('/calculate', methods=['POST'])
def calculate():
    p = int(request.form.get('p'))
    q = int(request.form.get('q'))

    if not (is_prime(p) and is_prime(q)):
        return jsonify({"error": "p dan q harus bilangan prima."}), 400
    if p == q:
        return jsonify({"error": "p dan q tidak boleh sama."}), 400

    n = p * q
    m = (p - 1) * (q - 1)

    possible_e = []
    for e in range(2, m):
        if gcd(e, m) == 1 and is_prime(e):
            possible_e.append(e)

    possible_e.sort()

    return jsonify({"e": possible_e, "n": n, "m": m})

# Endpoint untuk menghitung nilai d berdasarkan e, p, dan q
@app.route('/calculate_d', methods=['POST'])
def calculate_d():
    e = int(request.form.get('e'))
    p = int(request.form.get('p'))
    q = int(request.form.get('q'))

    n = p * q
    m = (p - 1) * (q - 1)

    if gcd(e, m) != 1:
        return jsonify({"error": "e harus coprime dengan m (p-1)*(q-1)."}), 400

    try:
        d = mod_inverse(e, m)
        return jsonify({"d": d})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

# Endpoint untuk enkripsi dan dekripsi pesan
@app.route('/encrypt_decrypt', methods=['POST'])
def encrypt_decrypt():
    try:
        message = request.form.get('message', '').strip()
        e = request.form.get('e', '').strip()
        d = request.form.get('d', '').strip()
        n = request.form.get('n', '').strip()

        if not message or not e or not d or not n:
            return jsonify({"error": "Semua input (message, e, d, n) harus diisi."}), 400

        e = int(e)
        d = int(d)
        n = int(n)

        encrypted_message = encrypt(message, e, n)
        decrypted_message = decrypt(encrypted_message, d, n)

        return jsonify({
            "e": e,
            "n": n,
            "d": d,
            "encrypted": encrypted_message,
            "decrypted": decrypted_message
        })

    except ValueError as ex:
        return jsonify({"error": f"Input tidak valid: {ex}"}), 400
    except Exception as ex:
        return jsonify({"error": f"Terjadi kesalahan: {str(ex)}"}), 500

# Endpoint untuk dekripsi pesan
@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    try:
        encrypted_message = request.form.get('encryptedMessage', '').strip()
        d = int(request.form.get('dDecrypt', '').strip())
        n = int(request.form.get('nDecrypt', '').strip())

        if not encrypted_message or not d or not n:
            return jsonify({"error": "Semua input (encryptedMessage, d, n) harus diisi."}), 400

        decrypted_message = decrypt(encrypted_message, d, n)

        return jsonify({
            "encryptedMessage": encrypted_message,
            "decryptedMessage": decrypted_message
        })

    except ValueError as ex:
        return jsonify({"error": f"Input tidak valid: {ex}"}), 400
    except Exception as ex:
        return jsonify({"error": f"Terjadi kesalahan: {str(ex)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)