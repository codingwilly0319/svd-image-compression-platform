from __future__ import annotations

from pathlib import Path

from .platform import ImageCompressionPlatform
from .records import RecordNotFoundError
from .users import AuthenticationError, User, UserManager


class PlatformCLI:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.platform = ImageCompressionPlatform(
            project_root / "data" / "records.json",
            project_root / "uploads",
        )
        self.user_manager = UserManager()
        self.user: User | None = None

    def run(self) -> None:
        print("SVD Image Compression Platform")
        self.user = self._login()
        print(f"Logged in as {self.user.username} ({self.user.role})")

        while True:
            self._print_menu()
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    self._compress_image()
                elif choice == "2":
                    self._show_history()
                elif choice == "3":
                    self._show_admin_summary()
                elif choice == "4":
                    self._show_linear_algebra_details()
                elif choice == "0":
                    print("Goodbye.")
                    return
                else:
                    print("Unknown option. Please choose again.")
            except (ValueError, FileNotFoundError, RecordNotFoundError) as exc:
                print(f"Error: {exc}")
            self._pause()

    def _login(self) -> User:
        print("Demo accounts: operator/operator123, admin/admin123")
        while True:
            username = input("Username [operator]: ").strip() or "operator"
            password = input("Password [operator123]: ").strip() or "operator123"
            try:
                return self.user_manager.authenticate(username, password)
            except AuthenticationError as exc:
                print(f"Login failed: {exc}")

    def _print_menu(self) -> None:
        print()
        print("1. Compress image")
        print("2. Show compression history")
        print("3. Admin summary")
        print("4. Show SVD details")
        print("0. Exit")

    def _pause(self) -> None:
        print()
        input("Press Enter to continue...")

    def _compress_image(self) -> None:
        default_path = self.project_root / "sample_images" / "sample-gradient.png"
        raw_path = input(f"Image path [{default_path.name}]: ").strip()
        image_path = Path(raw_path) if raw_path else default_path
        if not image_path.is_absolute():
            image_path = self.project_root / image_path

        record = self.platform.analyze_image(image_path)
        print("Compression saved.")
        self._print_record(record)

    def _show_history(self) -> None:
        records = self.platform.history()
        if not records:
            print("No compression records yet.")
            return

        for record in records:
            self._print_record(record)

    def _show_admin_summary(self) -> None:
        if self.user is None or not self.user.is_admin:
            print("Admin summary requires the admin account.")
            return

        summary = self.platform.admin_summary()
        print()
        print("Admin summary")
        print(f"Total records: {summary['total_records']}")
        print(f"Average quality: {summary['average_quality_score']}")
        print(f"Average compression ratio: {summary['average_compression_ratio']}")
        print(f"Average RMSE: {summary['average_error']}")

    def _show_linear_algebra_details(self) -> None:
        records = self.platform.history()
        if not records:
            print("No compression records yet.")
            return

        record_id = input("Record id [latest]: ").strip()
        record = self.platform.get_record(record_id) if record_id else records[-1]
        features = record.features

        print()
        print(f"Record: {record.id} ({record.image_name})")
        print(f"Formula: {features['formula']}")
        print(f"Processed matrix: {features['processed_height']} x {features['processed_width']}")
        print("Singular values:")
        print(features["singular_values"])
        print("Energy by rank:")
        for item in features["energy_curve"]:
            print(f"- Rank {item['rank']}: {item['retained_energy_percent']}%")

    def _print_record(self, record) -> None:
        print()
        print(f"ID: {record.id}")
        print(f"Image: {record.image_name}")
        print(f"Default: {record.result_label}")
        print(f"Quality: {record.quality_score:.2f}")
        print("Variants:")
        for variant in record.variants:
            print(
                f"- Rank {variant['rank']}: saved {variant['compression_ratio'] * 100:.0f}%, "
                f"RMSE {variant['rmse']}"
            )
