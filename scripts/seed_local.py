"""
Local development seed script — SQLite.
Creates a local SQLite DB with dummy data for manual testing.

Run from project root:
    python scripts/seed_local.py

Creates: local_dev.sqlite3
Then start the identity service pointed at it.
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "local_dev.sqlite3"


def create_tables(conn: sqlite3.Connection):
    cur = conn.cursor()

    cur.executescript(
        """
    -- Tenants (institutions / portals)
    CREATE TABLE IF NOT EXISTS tenants (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        slug        TEXT UNIQUE NOT NULL,
        name        TEXT NOT NULL,
        portal_group INTEGER NOT NULL DEFAULT 3,
        domain      TEXT UNIQUE,
        primary_color TEXT DEFAULT '#1565C0',
        logo_url    TEXT,
        is_active   INTEGER DEFAULT 1,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- Users
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile      TEXT UNIQUE,
        email       TEXT UNIQUE,
        username    TEXT UNIQUE,
        password_hash TEXT,
        full_name   TEXT,
        role        TEXT NOT NULL DEFAULT 'student',
        tenant_id   INTEGER REFERENCES tenants(id),
        is_active   INTEGER DEFAULT 1,
        profile_complete INTEGER DEFAULT 1,
        requires_2fa INTEGER DEFAULT 0,
        has_multiple_roles INTEGER DEFAULT 0,
        subscription TEXT DEFAULT 'free',
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- OTPs (for password reset email OTP)
    CREATE TABLE IF NOT EXISTS otps (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier  TEXT NOT NULL,
        otp_hash    TEXT NOT NULL,
        purpose     TEXT DEFAULT 'reset',
        expires_at  TEXT NOT NULL,
        used        INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- Refresh tokens
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER REFERENCES users(id),
        token_hash  TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        revoked     INTEGER DEFAULT 0
    );
    """
    )
    conn.commit()
    print("Tables created.")


def hash_password(password: str) -> str:
    """Simple SHA-256 for local dev. Real service uses bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_tenants(conn: sqlite3.Connection):
    tenants = [
        # (slug, name, portal_group, domain, primary_color)
        ("platform-admin", "EduForge Platform", 1, "admin.eduforge.in", "#1A237E"),
        ("chain-admin", "EduForge Chain Admin", 2, "app.eduforge.in", "#283593"),
        (
            "greenwood-school",
            "Greenwood High School",
            3,
            "greenwood.school.com",
            "#1B5E20",
        ),
        (
            "sunrise-college",
            "Sunrise Degree College",
            4,
            "sunrise.college.com",
            "#E65100",
        ),
        (
            "toppers-coaching",
            "Toppers Coaching Centre",
            5,
            "toppers.coaching.com",
            "#4A148C",
        ),
        ("ssc-domain", "EduForge SSC", 6, "ssc.eduforge.in", "#1565C0"),
        ("rrb-domain", "EduForge RRB", 6, "rrb.eduforge.in", "#0277BD"),
        ("tsp-demo", "TechEdu TSP", 7, "techedu.in", "#37474F"),
        ("b2b-partner", "ContentPro Partners", 9, "partners.eduforge.in", "#00695C"),
        ("student-unified", "EduForge Student", 10, "student.eduforge.in", "#6A1B9A"),
        ("default", "EduForge", 1, "localhost", "#1565C0"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO tenants (slug,name,portal_group,domain,primary_color) VALUES (?,?,?,?,?)",
        tenants,
    )
    conn.commit()
    print(f"Seeded {len(tenants)} tenants.")


def seed_users(conn: sqlite3.Connection):
    pwd = hash_password("Test@1234")  # same password for all dev users

    users = [
        # (mobile, email, username, password_hash, full_name, role, tenant_slug, subscription)
        # Platform Admin
        (
            "+910000000001",
            "platform@eduforge.in",
            "platform_admin",
            pwd,
            "Arjun Mehta",
            "platform_admin",
            "platform-admin",
            "free",
        ),
        # Chain Admin
        (
            "+910000000002",
            "chain@eduforge.in",
            "chain_admin",
            pwd,
            "Priya Sharma",
            "chain_admin",
            "chain-admin",
            "free",
        ),
        # School — Principal
        (
            "+910000000003",
            "principal@greenwood.com",
            "principal",
            pwd,
            "Dr. Rajan Nair",
            "principal",
            "greenwood-school",
            "free",
        ),
        # School — Teacher
        (
            "+910000000004",
            "teacher@greenwood.com",
            "teacher",
            pwd,
            "Sujata Rao",
            "teacher",
            "greenwood-school",
            "free",
        ),
        # School — Student
        (
            "+910000000005",
            "student@greenwood.com",
            "student1",
            pwd,
            "Rahul Verma",
            "student",
            "greenwood-school",
            "free",
        ),
        # School — Parent
        (
            "+910000000006",
            "parent@greenwood.com",
            "parent1",
            pwd,
            "Meera Verma",
            "parent",
            "greenwood-school",
            "free",
        ),
        # College — Principal
        (
            "+910000000007",
            "hod@sunrise.com",
            "college_principal",
            pwd,
            "Prof. Anil Kumar",
            "principal",
            "sunrise-college",
            "free",
        ),
        # College — Faculty
        (
            "+910000000008",
            "faculty@sunrise.com",
            "faculty1",
            pwd,
            "Dr. Kavitha S",
            "faculty",
            "sunrise-college",
            "free",
        ),
        # College — Student
        (
            "+910000000009",
            "coll_std@sunrise.com",
            "coll_student",
            pwd,
            "Ananya Pillai",
            "student",
            "sunrise-college",
            "free",
        ),
        # Coaching — Director
        (
            "+910000000010",
            "director@toppers.com",
            "director",
            pwd,
            "Naresh Gupta",
            "director",
            "toppers-coaching",
            "free",
        ),
        # Coaching — Student
        (
            "+910000000011",
            "coach_std@toppers.com",
            "coach_student",
            pwd,
            "Vikram Singh",
            "student",
            "toppers-coaching",
            "free",
        ),
        # Exam Domain — Free Student
        (
            "+919876543210",
            "aspirant@ssc.com",
            "aspirant1",
            pwd,
            "Deepak Yadav",
            "student",
            "ssc-domain",
            "free",
        ),
        # Exam Domain — Premium Student
        (
            "+919876543211",
            "premium@ssc.com",
            "premium1",
            pwd,
            "Pooja Mishra",
            "student",
            "ssc-domain",
            "premium",
        ),
        # TSP Admin
        (
            "+910000000014",
            "admin@techedu.in",
            "tsp_admin",
            pwd,
            "Kiran Reddy",
            "tsp_admin",
            "tsp-demo",
            "free",
        ),
        # B2B Partner
        (
            "+910000000015",
            "partner@contentpro.in",
            "b2b_partner",
            pwd,
            "Suresh Joshi",
            "partner",
            "b2b-partner",
            "free",
        ),
        # Student Unified
        (
            "+910000000016",
            "unified@student.in",
            "unified_student",
            pwd,
            "Arun Krishnan",
            "student",
            "student-unified",
            "free",
        ),
    ]

    # Get tenant id mapping
    cur = conn.cursor()
    cur.execute("SELECT slug, id FROM tenants")
    tenant_map = dict(cur.fetchall())

    for mobile, email, username, pw, name, role, t_slug, sub in users:
        t_id = tenant_map.get(t_slug, 1)
        conn.execute(
            """INSERT OR IGNORE INTO users
               (mobile, email, username, password_hash, full_name, role, tenant_id, subscription)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (mobile, email, username, pw, name, role, t_id, sub),
        )

    conn.commit()
    print(f"Seeded {len(users)} users.")


def print_summary(conn: sqlite3.Connection):
    cur = conn.cursor()
    print("\n" + "=" * 60)
    print("LOCAL DEV SEED SUMMARY")
    print("=" * 60)
    print(f"{'Role':<20} {'Login ID':<30} {'Password'}")
    print("-" * 60)

    rows = [
        ("Platform Admin", "platform@eduforge.in", "Test@1234"),
        ("Chain Admin", "chain@eduforge.in", "Test@1234"),
        ("School Principal", "+910000000003", "Test@1234"),
        ("School Teacher", "teacher@greenwood.com", "Test@1234"),
        ("School Student", "student1", "Test@1234"),
        ("School Parent", "parent@greenwood.com", "Test@1234"),
        ("College Principal", "college_principal", "Test@1234"),
        ("College Faculty", "faculty@sunrise.com", "Test@1234"),
        ("College Student", "coll_student", "Test@1234"),
        ("Coaching Director", "director@toppers.com", "Test@1234"),
        ("SSC Aspirant(Free)", "aspirant1", "Test@1234"),
        ("SSC Premium", "+919876543211", "Test@1234"),
        ("TSP Admin", "admin@techedu.in", "Test@1234"),
        ("B2B Partner", "partner@contentpro.in", "Test@1234"),
    ]
    for role, login, pwd in rows:
        print(f"{role:<20} {login:<30} {pwd}")

    print("\nTenants:")
    for row in conn.execute(
        "SELECT slug, name, portal_group, domain FROM tenants ORDER BY portal_group"
    ):
        print(f"  Group {row[2]}: {row[1]:<30} ({row[3]})")
    print("=" * 60)
    print(f"\nDB: {DB_PATH}")
    print("Run portal:  cd portal && python manage.py runserver")
    print("=" * 60)


def main():
    print(f"Creating SQLite database at {DB_PATH} ...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    create_tables(conn)
    seed_tenants(conn)
    seed_users(conn)
    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
