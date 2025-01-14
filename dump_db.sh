#!/bin/bash
set -e

while getopts "a:c:d:o:u:h" opt; do
  case ${opt} in
    c )
        CONTAINER_NAME=$OPTARG
        ;;
    d )
        DB_NAME=$OPTARG
        ;;
    o )
        OUTPUT_DIR=$OPTARG
        ;;
    u )
        DB_USER=$OPTARG
        ;;
    a )
        DBA=$OPTARG
        ;;
    h )
      echo "Usage: cmd [-c container_name] [-d db_name] [-o output_dir] [-u db_user] [-a dba]"
      exit 0
      ;;
  esac
done
# Configuration variables
CONTAINER_NAME=${CONTAINER_NAME:-postgres_container}  # Name of the running PostgreSQL container
DBA=${DBA:-postgres}                       # PostgreSQL superuser
DB_NAME=${DB_NAME:-tts}                       # Name of the database to dump
DB_USER=${DB_USER:-postgres}                  # PostgreSQL username
OUTPUT_DIR=${OUTPUT_DIR:-./backup}                # Directory to save the dump files on the host
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Derived variables
ROLES_DUMP_FILE="$OUTPUT_DIR/roles_$TIMESTAMP.sql"
DB_DUMP_FILE="$OUTPUT_DIR/db_$DB_NAME_$TIMESTAMP.dump"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Dump roles (permissions)
echo "Dumping roles and permissions to $ROLES_DUMP_FILE..."
docker exec "$CONTAINER_NAME" sh -c "pg_dumpall -U $DBA --roles-only" |  grep $DB_USER > "$ROLES_DUMP_FILE"
echo "Roles dump completed."

# Dump the database
echo "Dumping database $DB_NAME to $DB_DUMP_FILE..."
docker exec "$CONTAINER_NAME" sh -c "pg_dump -U $DBA -Fc $DB_NAME" > "$DB_DUMP_FILE"
echo "Database dump completed."

# Summary
echo "Backup completed successfully."
echo "Roles saved to: $ROLES_DUMP_FILE"
echo "Database saved to: $DB_DUMP_FILE"