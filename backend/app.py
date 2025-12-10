from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register_user():
    """
    Kullanıcı kayıt işlemi için endpoint.
    Chatbot bu endpoint'e JSON POST isteği atacak.
    Beklenen alanlar: ad, soyad, okul_no, tc_no
    """

    data = request.get_json()

    if not data:
        return jsonify({"error": "Lütfen geçerli bir JSON gönderin"}), 400
    
    ad = data.get("ad")
    soyad = data.get("soyad")
    okul_no = data.get("okul_no")
    tc_no = data.get("tc_no")

    if not ad or not soyad or not okul_no or not tc_no:
        return jsonify({"error": "Tüm alanlar zorunludur"}), 400
    
    if len(tc_no) != 11:
        return jsonify({"error": "TC numarası 11 haneli olmalıdır"}), 400
    
    if not okul_no.isdigit():
        return jsonify({"error": "Okul numarası sadece rakamlardan oluşmalıdır"}), 400
    
    return jsonify({"message": "Kayıt başarılı"}), 200



if __name__ == "__main__":
    app.run(debug=True, port=5001)