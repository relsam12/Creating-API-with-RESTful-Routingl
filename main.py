from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)
SECRET_KEY = "A3f#k9Pz"


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def read_cafe_record():
    # When someone makes a GET request to the /random route, our Flask server should
    # fetch a random cafe from our database.
    result = db.session.execute(db.Select(Cafe))
    all_cafe = result.scalars().all()
    random_cafe = random.choice(all_cafe)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "can_take_calls": random_cafe.can_take_calls,
        "seats": random_cafe.seats,
        "coffee_price": random_cafe.coffee_price
    })


@app.route("/all")
def all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafe = result.scalars().all()
    # to_dict() adalah function manual yang dibuat untuk bisa konversi semua database ke dictionary.
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafe])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Note, this may get more than one cafe per location
    all_cafes2 = result.scalars().all()
    if all_cafes2:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes2])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new Cafe"})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(cafe={"success": f"Successfully Update the Coffee Price of {cafe.name}"})
    else:
        return jsonify(error={"error": "Sorry the Cafe is not found."})


# HTTP DELETE - Delete Record
@app.route("/report-close/<int:cafe_id>", methods=["DELETE"])
def report_close(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == SECRET_KEY:
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": f"{cafe.name} Have Success for being Delete."})
        else:
            return jsonify(response={"error": "Failed, the cafe is not found."})
    else:
        return jsonify(response={"rejected": "sorry access denied, your API KEY is fault."})


if __name__ == '__main__':
    app.run(debug=True)
