import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    email = request.form["email"]

    # Vérifiez si l'email est vide
    if not email:
        flash("Veuillez entrer un email.")
        return redirect(url_for("index"))

    # Cherchez le club correspondant à l'email
    club = [club for club in clubs if club["email"] == email]

    if not club:  # Si l'email n'est pas trouvé
        flash("Email incorrect, veuillez réessayer.")
        return redirect(url_for("index"))  # Redirige vers la page d'accueil

    club = club[0]  # Récupérez le premier club si l'email est correct
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = next((c for c in clubs if c["name"] == club), None)

    if foundClub:
        for comp in competitions:
            if comp["name"] == competition:
                # Convertir la date de la compétition en objet datetime
                competition_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")

                # Vérifier si la date de la compétition est passée
                if competition_date < datetime.now():
                    flash(
                        f"La compétition {comp['name']} est terminée, vous ne pouvez pas réserver."
                    )
                    return render_template(
                        "welcome.html", club=foundClub, competitions=competitions
                    )

                foundCompetition = comp
                return render_template(
                    "booking.html", club=foundClub, competition=foundCompetition
                )

    flash("Quelque chose s'est mal passé - veuillez réessayer")
    return render_template("welcome.html", club=foundClub, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition_name = request.form.get("competition")
    club_name = request.form.get("club")
    places = request.form.get("places")

    if not places or not places.isdigit():
        flash("Veuillez entrer un nombre valide de places.")
        return redirect(url_for("book", competition=competition_name, club=club_name))
    try:
        placesRequired = int(places)
    except (ValueError, TypeError):
        flash("Veuillez entrer un nombre valide.")
        return redirect(url_for("book", competition=competition_name, club=club_name))

    # Bloquer les nombres inférieurs à 0 ou supérieurs à 12
    if placesRequired < 0:
        flash(
            "Le nombre de places ne peut pas être inférieur à 0. Veuillez entrer un nombre valide."
        )
        return redirect(url_for("book", competition=competition_name, club=club_name))

    placesRequired = int(places)

    competition = next((c for c in competitions if c["name"] == competition_name), None)
    club = next((c for c in clubs if c["name"] == club_name), None)

    if competition and club:

        available_places = int(competition["numberOfPlaces"])
        club_points = int(club["points"])

        if placesRequired > 12:
            flash("Pas assez de point vous pouvez que réserver 12 places")
        if club_points < placesRequired:
            flash("Vous n'avez pas assez de points pour réserver ce nombre de places.")
            return render_template("welcome.html", club=club, competitions=competitions)

        else:
            competition["numberOfPlaces"] = available_places - placesRequired
            club["points"] = club_points - placesRequired
            flash("Great-booking complete!")

    return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
