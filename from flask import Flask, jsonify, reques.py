from flask import Flask, jsonify, request
import requests
import svgwrite
from io import BytesIO
from datetime import datetime
import base64

app = Flask(__name__)

# 天気予報データを取得する関数
def get_weather_data(city_code):
    url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
    response = requests.get(url)
    data = response.json()
    
    weather_data = []
    for forecast in data['forecasts'][:3]:  # 今日、明日、明後日のデータを取得
        weather_data.append({
            "date": forecast['date'],
            "telop": forecast['telop'],
            "image_url": forecast['image']['url'],
            "day": forecast['dateLabel']
        })
    return weather_data

# SVG画像を生成する関数
def create_weather_svg(weather_data):
    dwg = svgwrite.Drawing(size=("900px", "300px"), debug=True)
    for i, data in enumerate(weather_data):
        response = requests.get(data["image_url"])
        image_url = f"image_{i}.svg"
        x_offset = i * 300

        # 画像とテキストをSVGに追加
        dwg.add(dwg.image(href=data["image_url"], insert=(75 + x_offset, 75), size=("150px", "150px")))
        dwg.add(dwg.text(data["date"][5:], insert=(150 + x_offset, 80), fill='black', font_size=40, font_family='Comic Sans MS', text_anchor="middle"))
        dwg.add(dwg.text(data["day"], insert=(150 + x_offset, 110), fill='black', font_size=30, font_family='Comic Sans MS', text_anchor="middle"))
        dwg.add(dwg.text(data["telop"], insert=(150 + x_offset, 230), fill='red', font_size=45, font_family='Comic Sans MS', text_anchor="middle", font_weight="bold"))

    # SVGデータをバイナリとして返す
    svg_io = BytesIO()
    dwg.write(svg_io)
    svg_io.seek(0)
    return svg_io.getvalue()

# Flaskのエンドポイント
@app.route('/generate_weather_image', methods=['GET'])
def generate_weather_image():
    city_code = request.args.get('city_code')
    if not city_code:
        return jsonify({'error': 'City code is required'}), 400

    # 天気データ取得
    weather_data = get_weather_data(city_code)

    # SVG画像生成
    svg_data = create_weather_svg(weather_data)

    # 生成したSVGをbase64でエンコードしてJSONで返す
    encoded_svg = base64.b64encode(svg_data).decode('utf-8')
    return jsonify({'svg_image': encoded_svg})

# Renderでアプリを起動するためのエントリポイント
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)