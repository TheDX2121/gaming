from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from database.mongo import get_db
from shared.settings import Settings
from shared.security import get_secret_key
from bot.catalog import GAMES
from bot import services
from shared.time_utils import now_utc


def create_app() -> Flask:
    settings = Settings.load()
    app = Flask(__name__)
    app.secret_key = get_secret_key(settings.secret_key)

    admin_hash = generate_password_hash(settings.admin_password)

    def login_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("admin_logged_in"):
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapper

    @app.route("/", methods=["GET"])
    def login():
        if session.get("admin_logged_in"):
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/login", methods=["POST"])
    def do_login():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == settings.admin_username and check_password_hash(admin_hash, password):
            session["admin_logged_in"] = True
            services.log("security", "admin_login_success", details={"username": username})
            return redirect(url_for("dashboard"))
        services.log("security", "admin_login_failed", details={"username": username})
        flash("Access denied", "error")
        return redirect(url_for("login"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        stats = {
            "users": db.users.count_documents({}),
            "banned": db.users.count_documents({"banned": True}),
            "logs": db.logs.count_documents({}),
            "transactions": db.transactions.count_documents({}),
            "treasury": (db.admin_treasury.find_one({"_id": "main"}) or {}).get("balance", 0),
        }
        top = list(db.users.find({}).sort("coins", -1).limit(5))
        return render_template("dashboard.html", stats=stats, top=top)

    @app.route("/users")
    @login_required
    def users():
        db = get_db()
        q = request.args.get("q", "").strip()
        query = {}
        if q:
            if q.isdigit():
                query = {"user_id": int(q)}
            else:
                query = {"username": {"$regex": q, "$options": "i"}}
        users_list = list(db.users.find(query).sort("created_at", -1).limit(100))
        return render_template("users.html", users=users_list, q=q)

    @app.route("/users/<int:user_id>/ban", methods=["POST"])
    @login_required
    def ban_user(user_id: int):
        get_db().users.update_one({"user_id": user_id}, {"$set": {"banned": True}})
        services.log("admin", "ban_user", user_id=user_id)
        return redirect(url_for("users"))

    @app.route("/users/<int:user_id>/unban", methods=["POST"])
    @login_required
    def unban_user(user_id: int):
        get_db().users.update_one({"user_id": user_id}, {"$set": {"banned": False}})
        services.log("admin", "unban_user", user_id=user_id)
        return redirect(url_for("users"))

    @app.route("/coins", methods=["GET", "POST"])
    @login_required
    def coins():
        if request.method == "POST":
            mode = request.form.get("mode")
            amount = int(request.form.get("amount", "0"))
            reason = request.form.get("reason", "admin_manual")
            db = get_db()
            if mode == "one_add":
                user_id = int(request.form.get("user_id", "0"))
                services.add_coins(user_id, amount, reason=reason)
                services.log("admin", "manual_add_coins", user_id=user_id, details={"amount": amount, "reason": reason})
            elif mode == "one_remove":
                user_id = int(request.form.get("user_id", "0"))
                services.remove_coins(user_id, amount, reason=reason)
                services.log("admin", "manual_remove_coins", user_id=user_id, details={"amount": amount, "reason": reason})
            elif mode == "all_add":
                result = db.users.update_many({}, {"$inc": {"coins": amount}, "$set": {"updated_at": now_utc()}})
                services.log("admin", "add_coins_all", details={"amount": amount, "matched": result.matched_count, "reason": reason})
            return redirect(url_for("coins"))
        return render_template("coins.html")

    @app.route("/treasury")
    @login_required
    def treasury():
        db = get_db()
        treasury_doc = db.admin_treasury.find_one({"_id": "main"}) or {"balance": 0, "total_shop_revenue": 0}
        transactions = list(db.transactions.find({}).sort("created_at", -1).limit(100))
        return render_template("treasury.html", treasury=treasury_doc, transactions=transactions)

    @app.route("/shop", methods=["GET", "POST"])
    @login_required
    def shop():
        db = get_db()
        if request.method == "POST":
            item_id = request.form.get("item_id", "")
            price = int(request.form.get("price", "0"))
            active = request.form.get("active") == "on"
            db.shop_items.update_one({"item_id": item_id}, {"$set": {"price": price, "active": active}})
            services.log("admin", "update_shop_item", details={"item_id": item_id, "price": price, "active": active})
            return redirect(url_for("shop"))
        items = list(db.shop_items.find({}).sort("category", 1))
        return render_template("shop.html", items=items)

    @app.route("/games")
    @login_required
    def games_page():
        return render_template("games.html", games=GAMES)

    @app.route("/tournaments")
    @login_required
    def tournaments():
        db = get_db()
        items = list(db.tournaments.find({}).sort("created_at", -1).limit(50))
        return render_template("tournaments.html", tournaments=items)

    @app.route("/logs")
    @login_required
    def logs():
        db = get_db()
        type_filter = request.args.get("type", "")
        query = {"type": type_filter} if type_filter else {}
        items = list(db.logs.find(query).sort("created_at", -1).limit(200))
        return render_template("logs.html", logs=items, type_filter=type_filter)

    @app.route("/settings")
    @login_required
    def settings_page():
        return render_template("settings.html", settings=settings)

    return app
