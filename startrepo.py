import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, *, capture=False):
    result = subprocess.run(
        command,
        capture_output=capture,
        text=True
    )

    if capture:
        return result

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="")

    return result


def run_git(*args, capture=False):
    return run_command(
        ["git", *args],
        capture=capture
    )


def run_gh(*args, capture=False):
    return run_command(
        ["gh", *args],
        capture=capture
    )


def check_command(command, name):
    if shutil.which(command) is None:
        print(f"❌ {name} bulunamadı.")
        print(f"Önce {command} kurulu olduğundan emin ol.")
        sys.exit(1)


def get_git_config(key):
    result = run_git(
        "config",
        "--get",
        key,
        capture=True
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def main():
    project_dir = Path.cwd()

    print("=" * 60)
    print("                  STARTREPO")
    print("=" * 60)
    print()
    print(f"Project: {project_dir}")
    print()

    # ---------------------------------------------------------
    # 1. Gerekli programları kontrol et
    # ---------------------------------------------------------

    print("[1] Gerekli programlar kontrol ediliyor...")

    check_command("git", "Git")
    check_command("gh", "GitHub CLI")

    print("✓ Git bulundu.")
    print("✓ GitHub CLI bulundu.")
    print()

    # ---------------------------------------------------------
    # 2. GitHub authentication
    # ---------------------------------------------------------

    print("[2] GitHub hesabı kontrol ediliyor...")

    auth = run_gh("auth", "status")

    if auth.returncode != 0:
        print("\n❌ GitHub hesabına giriş yapılmamış.")
        print("Önce:")
        print("    gh auth login")
        sys.exit(1)

    print("✓ GitHub hesabı hazır.")
    print()

    # ---------------------------------------------------------
    # 3. Mevcut Git repository kontrolü
    # ---------------------------------------------------------

    print("[3] Mevcut Git repository kontrol ediliyor...")

    if (project_dir / ".git").exists():
        print("\n❌ Bu klasör zaten bir Git repository.")
        print("startrepo mevcut repository'yi yeniden oluşturmaz.")
        sys.exit(1)

    print("✓ Git repository bulunamadı.")
    print()

    # ---------------------------------------------------------
    # 4. Repository adı
    # ---------------------------------------------------------

    print("[4] Repository bilgileri")

    default_name = project_dir.name

    repo_name = input(
        f"Repository name [{default_name}]: "
    ).strip()

    if not repo_name:
        repo_name = default_name

    if "/" in repo_name or "\\" in repo_name:
        print("\n❌ Repository adı geçersiz.")
        sys.exit(1)

    print()
    print("Visibility:")
    print("  1. Public")
    print("  2. Private")

    while True:
        visibility = input("Seçim [1]: ").strip()

        if visibility in ("", "1"):
            visibility = "public"
            break

        if visibility == "2":
            visibility = "private"
            break

        print("1 veya 2 gir.")

    print()
    print(f"Repository : {repo_name}")
    print(f"Visibility : {visibility}")
    print()

    confirm = input(
        "Bu klasör GitHub'a yüklenecek. Devam? [Y/n]: "
    ).strip().lower()

    if confirm not in ("", "y", "yes", "e", "evet"):
        print("\nİşlem iptal edildi.")
        return

    print()

    # ---------------------------------------------------------
    # 5. Git init
    # ---------------------------------------------------------

    print("[5] Git repository oluşturuluyor...")

    init = run_git("init")

    if init.returncode != 0:
        print("\n❌ git init başarısız.")
        sys.exit(1)

    print("✓ Git repository oluşturuldu.")
    print()

    # ---------------------------------------------------------
    # 6. Git identity
    # ---------------------------------------------------------

    print("[6] Git identity kontrol ediliyor...")

    git_name = get_git_config("user.name")
    git_email = get_git_config("user.email")

    if not git_name or not git_email:
        print("\n❌ Git identity bulunamadı.")

        if not git_name:
            print("user.name eksik.")

        if not git_email:
            print("user.email eksik.")

        print("\nÖrneğin:")
        print('git config --global user.name "enes-muhammed"')
        print('git config --global user.email "44enesmuhammed@gmail.com"')

        sys.exit(1)

    print(f"Name  : {git_name}")
    print(f"Email : {git_email}")
    print("✓ Git identity hazır.")
    print()

    # ---------------------------------------------------------
    # 7. Main branch
    # ---------------------------------------------------------

    print("[7] Main branch hazırlanıyor...")

    branch = run_git("branch", "-M", "main")

    if branch.returncode != 0:
        print("\n❌ Main branch oluşturulamadı.")
        sys.exit(1)

    print("✓ main")
    print()

    # ---------------------------------------------------------
    # 8. Git add
    # ---------------------------------------------------------

    print("[8] Proje dosyaları stage ediliyor...")

    add = run_git("add", ".")

    if add.returncode != 0:
        print("\n❌ git add başarısız.")
        sys.exit(1)

    print("✓ Dosyalar stage edildi.")
    print()

    # ---------------------------------------------------------
    # 9. İlk commit
    # ---------------------------------------------------------

    print("[9] İlk commit oluşturuluyor...")

    commit = run_git(
        "commit",
        "-m",
        "Initial commit"
    )

    if commit.returncode != 0:
        print("\n❌ İlk commit oluşturulamadı.")
        sys.exit(1)

    print("✓ Initial commit")
    print()

    # ---------------------------------------------------------
    # 10. GitHub repository oluştur
    # ---------------------------------------------------------

    print("[10] GitHub repository oluşturuluyor...")

    visibility_flag = f"--{visibility}"

    create = run_gh(
        "repo",
        "create",
        repo_name,
        visibility_flag,
        "--source=.",
        "--remote=origin",
        capture=True
    )

    if create.returncode != 0:
        print("\n❌ GitHub repository oluşturulamadı.")

        if create.stdout:
            print(create.stdout)

        if create.stderr:
            print(create.stderr)

        sys.exit(1)

    if create.stdout:
        print(create.stdout, end="")

    print("✓ GitHub repository oluşturuldu.")
    print()

    # ---------------------------------------------------------
    # 11. Push
    # ---------------------------------------------------------

    print("[11] GitHub'a push ediliyor...")

    push = run_git(
        "push",
        "-u",
        "origin",
        "main"
    )

    if push.returncode != 0:
        print("\n❌ Push başarısız.")
        print("Repository GitHub'da oluşturuldu fakat push tamamlanamadı.")
        sys.exit(1)

    print()
    print("✓ Proje GitHub'a yüklendi.")
    print()

    # ---------------------------------------------------------
    # 12. Sonuç
    # ---------------------------------------------------------

    print("=" * 60)
    print("              REPOSITORY READY")
    print("=" * 60)
    print()
    print(f"Repository : {repo_name}")
    print(f"Visibility : {visibility}")
    print(f"Branch     : main")
    print()
    print("GitHub repository:")
    print(f"https://github.com/{get_github_username()}/{repo_name}")
    print()


def get_github_username():
    result = run_gh(
        "api",
        "user",
        "-q",
        ".login",
        capture=True
    )

    if result.returncode != 0:
        return "unknown"

    return result.stdout.strip()


if __name__ == "__main__":
    main()
