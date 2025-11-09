#!/bin/bash
# Database Restore Script for LIMS-QMS Platform

set -e

# Configuration
BACKUP_DIR="/app/backups"
DB_NAME="lims_qms_db"
DB_USER="lims_user"
DB_HOST="postgres"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}LIMS-QMS Database Restore${NC}"
echo -e "${GREEN}====================================${NC}"

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh "${BACKUP_DIR}"/lims_qms_backup_*.sql.gz | awk '{print $9, "(" $5 ")"}'
    echo ""
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo "Example: $0 ${BACKUP_DIR}/lims_qms_backup_20240101_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}✗ Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo "Backup file: ${BACKUP_FILE}"
echo ""

# Verify checksum if available
if [ -f "${BACKUP_FILE}.sha256" ]; then
    echo -e "${YELLOW}Verifying backup integrity...${NC}"
    if sha256sum -c "${BACKUP_FILE}.sha256" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Checksum verification passed${NC}"
    else
        echo -e "${RED}✗ Checksum verification failed!${NC}"
        exit 1
    fi
fi

# Confirmation prompt
echo -e "${YELLOW}WARNING: This will OVERWRITE the current database!${NC}"
read -p "Are you sure you want to restore? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Drop and recreate database
echo -e "${YELLOW}Dropping existing database...${NC}"
docker exec lims-postgres psql -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
echo -e "${GREEN}✓ Database dropped${NC}"

echo -e "${YELLOW}Creating new database...${NC}"
docker exec lims-postgres psql -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"
echo -e "${GREEN}✓ Database created${NC}"

# Restore backup
echo -e "${YELLOW}Restoring backup...${NC}"
if gunzip -c "${BACKUP_FILE}" | docker exec -i lims-postgres psql -U "${DB_USER}" -d "${DB_NAME}" > /dev/null; then
    echo -e "${GREEN}✓ Restore successful!${NC}"
else
    echo -e "${RED}✗ Restore failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Restore Complete${NC}"
echo -e "${GREEN}====================================${NC}"
echo "Database: ${DB_NAME}"
echo "Restored from: ${BACKUP_FILE}"
echo "Completed at: $(date)"
echo -e "${GREEN}====================================${NC}"

exit 0
