#!/bin/bash
# Database Backup Script for LIMS-QMS Platform

set -e

# Configuration
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="lims_qms_db"
DB_USER="lims_user"
DB_HOST="postgres"
RETENTION_DAYS=90

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}LIMS-QMS Database Backup${NC}"
echo -e "${GREEN}====================================${NC}"
echo "Started at: $(date)"
echo ""

# Create backup directory if not exists
mkdir -p "${BACKUP_DIR}"

# Backup filename
BACKUP_FILE="${BACKUP_DIR}/lims_qms_backup_${TIMESTAMP}.sql.gz"

echo -e "${YELLOW}Creating database backup...${NC}"

# Perform backup
if docker exec lims-postgres pg_dump -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}✓ Backup successful!${NC}"
    echo "  File: ${BACKUP_FILE}"
    echo "  Size: ${BACKUP_SIZE}"
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Create checksum
echo -e "${YELLOW}Creating checksum...${NC}"
sha256sum "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
echo -e "${GREEN}✓ Checksum created${NC}"

# Remove old backups
echo -e "${YELLOW}Cleaning old backups (older than ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "lims_qms_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}" -name "lims_qms_backup_*.sql.gz.sha256" -type f -mtime +${RETENTION_DAYS} -delete

REMAINING_BACKUPS=$(find "${BACKUP_DIR}" -name "lims_qms_backup_*.sql.gz" -type f | wc -l)
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo "  Remaining backups: ${REMAINING_BACKUPS}"

# Backup statistics
echo ""
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Backup Summary${NC}"
echo -e "${GREEN}====================================${NC}"
echo "Database: ${DB_NAME}"
echo "Timestamp: ${TIMESTAMP}"
echo "Backup file: ${BACKUP_FILE}"
echo "Backup size: ${BACKUP_SIZE}"
echo "Total backups: ${REMAINING_BACKUPS}"
echo "Completed at: $(date)"
echo -e "${GREEN}====================================${NC}"

exit 0
