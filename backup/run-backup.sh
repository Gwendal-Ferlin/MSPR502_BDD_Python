#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 0 ]]; then
  exec "$@"
fi

timestamp="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
out_root="${BACKUP_OUT_DIR:-/backups}"
out_dir="${out_root}/${timestamp}"

mkdir -p "${out_dir}"

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required env var: ${name}" >&2
    exit 1
  fi
}

echo "Backup started at ${timestamp}"
echo "Output dir: ${out_dir}"

# ---- Tools resolution ----
PG_DUMP_BIN="${PG_DUMP_BIN:-}"
if [[ -z "${PG_DUMP_BIN}" ]]; then
  # Prefer an explicit Postgres 16 client if present.
  if [[ -x "/usr/lib/postgresql/16/bin/pg_dump" ]]; then
    PG_DUMP_BIN="/usr/lib/postgresql/16/bin/pg_dump"
  else
    # Try to discover a pg_dump matching server major (16).
    for candidate in /usr/lib/postgresql/*/bin/pg_dump; do
      if [[ -x "${candidate}" ]]; then
        ver="$("${candidate}" --version 2>/dev/null | awk '{print $3}' || true)"
        major="${ver%%.*}"
        if [[ "${major}" == "16" ]]; then
          PG_DUMP_BIN="${candidate}"
          break
        fi
      fi
    done
  fi

  # Fallbacks (may be wrong major; we validate below)
  if [[ -z "${PG_DUMP_BIN}" ]]; then
    if [[ -x "/usr/bin/pg_dump" ]]; then
      PG_DUMP_BIN="/usr/bin/pg_dump"
    else
      PG_DUMP_BIN="$(command -v pg_dump || true)"
    fi
  fi
fi

if [[ -z "${PG_DUMP_BIN}" ]] || [[ ! -x "${PG_DUMP_BIN}" ]]; then
  echo "pg_dump not found in container. Set PG_DUMP_BIN to an executable path." >&2
  exit 1
fi

echo "Using pg_dump: ${PG_DUMP_BIN}"
pg_dump_version="$("${PG_DUMP_BIN}" --version | awk '{print $3}')"
echo "pg_dump version: ${pg_dump_version}"
pg_dump_major="${pg_dump_version%%.*}"
if [[ "${pg_dump_major}" != "16" ]]; then
  echo "ERROR: pg_dump major must be 16 to match Postgres 16.x servers." >&2
  echo "Fix: rebuild the backup image (no-cache) or set PG_DUMP_BIN to the v16 binary path." >&2
  exit 1
fi

# ---- Postgres dumps (custom format) ----
dump_pg() {
  local label="$1"
  local host="$2"
  local port="$3"
  local user="$4"
  local password="$5"
  local db="$6"

  echo "Dumping Postgres ${label} (${db})..."
  PGPASSWORD="${password}" "${PG_DUMP_BIN}" \
    -h "${host}" \
    -p "${port}" \
    -U "${user}" \
    -d "${db}" \
    -F c \
    -Z 6 \
    -f "${out_dir}/${label}.pgdump"
}

require_env POSTGRES_UTILISATEUR_USER
require_env POSTGRES_UTILISATEUR_PASSWORD
require_env POSTGRES_SANTE_USER
require_env POSTGRES_SANTE_PASSWORD
require_env POSTGRES_GAMIFICATION_USER
require_env POSTGRES_GAMIFICATION_PASSWORD

POSTGRES_UTILISATEUR_HOST="${POSTGRES_UTILISATEUR_HOST:-postgres-utilisateur}"
POSTGRES_UTILISATEUR_PORT="${POSTGRES_UTILISATEUR_PORT:-5432}"
POSTGRES_SANTE_HOST="${POSTGRES_SANTE_HOST:-postgres-sante}"
POSTGRES_SANTE_PORT="${POSTGRES_SANTE_PORT:-5432}"
POSTGRES_GAMIFICATION_HOST="${POSTGRES_GAMIFICATION_HOST:-postgres-gamification}"
POSTGRES_GAMIFICATION_PORT="${POSTGRES_GAMIFICATION_PORT:-5432}"

dump_pg "postgres-utilisateur_utilisateur_db" "${POSTGRES_UTILISATEUR_HOST}" "${POSTGRES_UTILISATEUR_PORT}" "${POSTGRES_UTILISATEUR_USER}" "${POSTGRES_UTILISATEUR_PASSWORD}" "utilisateur_db"
dump_pg "postgres-sante_sante_db" "${POSTGRES_SANTE_HOST}" "${POSTGRES_SANTE_PORT}" "${POSTGRES_SANTE_USER}" "${POSTGRES_SANTE_PASSWORD}" "sante_db"
dump_pg "postgres-gamification_gamification_db" "${POSTGRES_GAMIFICATION_HOST}" "${POSTGRES_GAMIFICATION_PORT}" "${POSTGRES_GAMIFICATION_USER}" "${POSTGRES_GAMIFICATION_PASSWORD}" "gamification_db"

# ---- Mongo dumps ----
dump_mongo() {
  local label="$1"
  local host="$2"
  local port="$3"
  local db="$4"

  echo "Dumping Mongo ${label} (${db})..."
  mongodump \
    --host "${host}" \
    --port "${port}" \
    --db "${db}" \
    --archive="${out_dir}/${label}.archive.gz" \
    --gzip
}

MONGODB_LOGS_HOST="${MONGODB_LOGS_HOST:-mongodb-logs}"
MONGODB_LOGS_PORT="${MONGODB_LOGS_PORT:-27017}"
MONGODB_RECO_HOST="${MONGODB_RECO_HOST:-mongodb-reco}"
MONGODB_RECO_PORT="${MONGODB_RECO_PORT:-27017}"

dump_mongo "mongodb-logs_logs_config" "${MONGODB_LOGS_HOST}" "${MONGODB_LOGS_PORT}" "logs_config"
dump_mongo "mongodb-reco_reco" "${MONGODB_RECO_HOST}" "${MONGODB_RECO_PORT}" "reco"

# ---- Optional: upload to cloud (rclone) ----
# Default matches official rclone image: XDG_CONFIG_HOME=/config → .../rclone/rclone.conf
# Legacy single-file layout: /config/rclone.conf
RCLONE_REMOTE="${RCLONE_REMOTE:-}"
RCLONE_PATH="${RCLONE_PATH:-MSPR502/backups}"
RCLONE_CONFIG="${RCLONE_CONFIG:-}"
if [[ -z "${RCLONE_CONFIG}" ]]; then
  if [[ -f /config/rclone/rclone.conf ]]; then
    RCLONE_CONFIG="/config/rclone/rclone.conf"
  elif [[ -f /config/rclone.conf ]]; then
    RCLONE_CONFIG="/config/rclone.conf"
  else
    RCLONE_CONFIG="/config/rclone/rclone.conf"
  fi
fi
upload_status="skipped"
upload_dest=""
upload_exit=0

if [[ -n "${RCLONE_REMOTE}" ]]; then
  if [[ ! -f "${RCLONE_CONFIG}" ]]; then
    echo "ERROR: RCLONE_REMOTE is set but ${RCLONE_CONFIG} not found. Run: docker run -it --rm -v \"\${PWD}/rclone:/config\" rclone/rclone config" >&2
    upload_status="failed"
    upload_exit=1
  else
    # Trim trailing slashes from path for a stable remote path
    rpath="${RCLONE_PATH#/}"
    rpath="${rpath%/}"
    upload_dest="${RCLONE_REMOTE}:${rpath}/${timestamp}"
    echo "Uploading ${out_dir} to ${upload_dest} (rclone)..."
    export RCLONE_CONFIG
    if rclone copy "${out_dir}" "${upload_dest}" --transfers 4 --checkers 8 --fast-list; then
      upload_status="ok"
    else
      echo "ERROR: rclone copy failed." >&2
      upload_status="failed"
      upload_exit=1
    fi
  fi
else
  echo "Rclone upload skipped (set RCLONE_REMOTE in .env to enable)."
fi

# ---- Log into mongodb-logs after completion ----
echo "Writing completion log into mongodb-logs..."
export BK_TS="${timestamp}"
export BK_OUT="${out_dir}"
export BK_UPLOAD_STATUS="${upload_status}"
export BK_UPLOAD_DEST="${upload_dest}"
mongosh "mongodb://${MONGODB_LOGS_HOST}:${MONGODB_LOGS_PORT}/logs_config" --quiet --eval '
db.getCollection("backup_runs").insertOne({
  ts: new Date(),
  status: "success",
  backupTimestamp: process.env.BK_TS,
  outputDir: process.env.BK_OUT,
  uploadStatus: process.env.BK_UPLOAD_STATUS,
  uploadDest: process.env.BK_UPLOAD_DEST ? process.env.BK_UPLOAD_DEST : null,
  artifacts: [
    "postgres-utilisateur_utilisateur_db.pgdump",
    "postgres-sante_sante_db.pgdump",
    "postgres-gamification_gamification_db.pgdump",
    "mongodb-logs_logs_config.archive.gz",
    "mongodb-reco_reco.archive.gz"
  ]
})
'

if [[ "${upload_exit}" -ne 0 ]]; then
  echo "Backup dumps OK but upload failed (see uploadStatus in backup_runs)." >&2
  exit "${upload_exit}"
fi

echo "Backup completed successfully."
