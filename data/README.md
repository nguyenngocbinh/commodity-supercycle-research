# Data directory

- `raw/`: downloaded original files.
- `processed/`: aligned monthly levels and transformed model series.

Generated data are excluded from Git to avoid committing large, frequently revised source files.
For publication-grade reproducibility, archive the exact source workbook, retrieval timestamp,
source URL, SHA-256 checksum and vintage/revision information.

The World Bank Pink Sheet workbook is retrieved from the official Commodity Markets page.
FRED observations are retrieved through the official FRED API.
