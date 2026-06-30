from __future__ import annotations

from functools import wraps
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from .platform import ImageCompressionPlatform
from .records import CompressionRecord, RecordNotFoundError
from .users import AuthenticationError, UserManager


ALLOWED_EXTENSIONS = {".ppm", ".png", ".jpg", ".jpeg"}
PREVIEW_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def create_app(project_root: str | Path | None = None) -> Flask:
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )
    app.config["SECRET_KEY"] = "dev-secret-change-before-deploy"
    app.config["UPLOAD_FOLDER"] = root / "uploads"
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
    app.config["PROJECT_ROOT"] = root

    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    platform = ImageCompressionPlatform(root / "data" / "records.json", upload_folder)
    users = UserManager()

    def current_user() -> dict[str, str] | None:
        username = session.get("username")
        role = session.get("role")
        if not username or not role:
            return None
        return {"username": str(username), "role": str(role)}

    def image_url_for_record(record: CompressionRecord) -> str | None:
        if record.image_name == "sample-gradient.png":
            return url_for("static", filename="sample-preview.png")
        extension = Path(record.image_name).suffix.casefold()
        candidate = upload_folder / record.image_name
        if extension in PREVIEW_EXTENSIONS and candidate.exists():
            return url_for("uploaded_file", filename=record.image_name)
        return None

    def login_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if current_user() is None:
                flash("請先登入", "error")
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped_view

    def admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("請先登入", "error")
                return redirect(url_for("login"))
            if user["role"] != "admin":
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    @app.context_processor
    def inject_user() -> dict[str, object]:
        return {"current_user": current_user()}

    @app.get("/")
    def index():
        if current_user() is None:
            return redirect(url_for("login"))
        return redirect(url_for("dashboard"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip() or "operator"
            password = request.form.get("password", "")
            try:
                user = users.authenticate(username, password)
            except AuthenticationError as exc:
                flash(str(exc), "error")
            else:
                session["username"] = user.username
                session["role"] = user.role
                flash("登入成功", "success")
                return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.post("/logout")
    def logout():
        session.clear()
        flash("已登出", "success")
        return redirect(url_for("login"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        records = list(reversed(platform.history()))
        return render_template(
            "dashboard.html",
            records=records[:6],
            summary=platform.admin_summary(),
            image_url_for_record=image_url_for_record,
        )

    @app.route("/analyze", methods=["GET", "POST"])
    @login_required
    def analyze():
        if request.method == "POST":
            if request.form.get("use_sample") == "1":
                sample_path = root / "sample_images" / "sample-gradient.png"
                record = platform.analyze_image(sample_path)
                flash("範例圖片已完成 SVD 壓縮", "success")
                return redirect(url_for("record_detail", record_id=record.id))

            uploaded_file = request.files.get("image")
            if uploaded_file is None or uploaded_file.filename == "":
                flash("請選擇圖片檔案", "error")
                return redirect(url_for("analyze"))

            original_name = secure_filename(uploaded_file.filename)
            extension = Path(original_name).suffix.casefold()
            if extension not in ALLOWED_EXTENSIONS:
                flash("支援格式：PPM、PNG、JPG", "error")
                return redirect(url_for("analyze"))

            stored_name = f"{uuid4().hex[:8]}-{original_name}"
            stored_path = upload_folder / stored_name
            uploaded_file.save(stored_path)

            try:
                record = platform.analyze_image(stored_path)
            except Exception as exc:
                stored_path.unlink(missing_ok=True)
                flash(f"圖像壓縮失敗：{exc}", "error")
                return redirect(url_for("analyze"))

            flash("圖片已完成 SVD 壓縮", "success")
            return redirect(url_for("record_detail", record_id=record.id))

        return render_template("analyze.html")

    @app.get("/records")
    @login_required
    def records():
        records = list(reversed(platform.history()))
        return render_template(
            "records.html",
            records=records,
            image_url_for_record=image_url_for_record,
        )

    @app.get("/records/<record_id>")
    @login_required
    def record_detail(record_id: str):
        try:
            record = platform.get_record(record_id)
        except RecordNotFoundError:
            abort(404)
        return render_template(
            "record_detail.html",
            record=record,
            image_url=image_url_for_record(record),
        )

    @app.get("/records/<record_id>/math")
    @login_required
    def math_detail(record_id: str):
        try:
            record = platform.get_record(record_id)
        except RecordNotFoundError:
            abort(404)
        return render_template("math_detail.html", record=record)

    @app.get("/admin")
    @admin_required
    def admin():
        return render_template("admin.html", summary=platform.admin_summary())

    @app.get("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename: str):
        return send_from_directory(upload_folder, filename)

    return app
