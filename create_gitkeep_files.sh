#!/bin/bash

# Create .gitkeep files to preserve empty directories in git

touch backups/.gitkeep
touch backups/daily/.gitkeep
touch backups/weekly/.gitkeep
touch backups/monthly/.gitkeep
touch backups/manifests/.gitkeep
touch backups/temp/.gitkeep
touch logs/.gitkeep
touch alembic/versions/.gitkeep

echo ".gitkeep files created for empty directories!"
