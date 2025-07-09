#!/bin/bash

# Get current timestamp for unique filenames
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Define file paths with timestamps
LAW_LIST_FILE="tmp/law_list_${TIMESTAMP}.txt"
LOG_FILE="run_${TIMESTAMP}.log"

# Ensure tmp directory exists
mkdir -p tmp

# Get the number of laws to process from the first argument, default to 50 if not provided
NUM_LAWS=1

echo "--- Step 1: Generating law list to ${LAW_LIST_FILE} (limit: ${NUM_LAWS}) ---"
psql "postgresql://lawdb:StGdZKiShNeZjc84sdRdynOdvyzXb43h@211.73.81.235:30198/lawdb" -c "SELECT
    l.xml_law_name
FROM
    laws l
WHERE
    l.law_metadata IS NULL
ORDER BY
    (
        SELECT COUNT(*)
        FROM law_relationships lr
        WHERE lr.main_law_id = l.id OR lr.related_law_id = l.id
    ) DESC,
    CASE l.xml_law_nature
        WHEN '憲法' THEN 3
        WHEN '法律' THEN 2
        WHEN '命令' THEN 1
        ELSE 0
    END DESC,
    l.xml_latest_change_date DESC limit ${NUM_LAWS};" | sed '1,2d; $d' | sed '$d' > "${LAW_LIST_FILE}"

if [ $? -ne 0 ]; then
    echo "Error: Step 1 failed. Exiting."
    exit 1
fi

echo "--- Step 2: Exporting law list from ${LAW_LIST_FILE} ---"
python law_cli.py --export-law-list "${LAW_LIST_FILE}" --output-dir output

if [ $? -ne 0 ]; then
    echo "Error: Step 2 failed. Exiting."
    exit 1
fi

echo "--- Step 2.1: Generating summary files and importing them ---"
python law_cli.py --generate-summary-from-md --law-list "${LAW_LIST_FILE}" --summary-example-file output/summary_sample.md --output-dir output
if [ $? -ne 0 ]; then
    echo "Error: Step 2.1 (Generate Summary) failed. Exiting."
    exit 1
fi
python law_cli.py --update-summary output/all_laws_summary.md --law-list "${LAW_LIST_FILE}"
if [ $? -ne 0 ]; then
    echo "Error: Step 2.1 (Import Summary) failed. Exiting."
    exit 1
fi

echo "--- Step 2.2: Generating keyword files and importing them ---"
python law_cli.py --generate-keywords-from-md --law-list "${LAW_LIST_FILE}" --output-file output/keywords_sample.csv
if [ $? -ne 0 ]; then
    echo "Error: Step 2.2 (Generate Keywords) failed. Exiting."
    exit 1
fi
python law_cli.py --update-keywords output/keywords_sample.csv --law-list "${LAW_LIST_FILE}"
if [ $? -ne 0 ]; then
    echo "Error: Step 2.2 (Import Keywords) failed. Exiting."
    exit 1
fi

echo "--- Step 3: Generating meta list and logging to ${LOG_FILE} ---"
python law_cli.py --generate-meta-list --law-list "${LAW_LIST_FILE}" | tee "${LOG_FILE}"

if [ $? -ne 0 ]; then
    echo "Error: Step 3 failed. Exiting."
    exit 1
fi

echo "--- Step 4: Importing meta list from ${LAW_LIST_FILE} ---"
python law_cli.py --import-meta-list --law-list "${LAW_LIST_FILE}"

if [ $? -ne 0 ]; then
    echo "Error: Step 4 failed. Exiting."
    exit 1
fi

echo "--- Step 5: Sending Discord notification ---"
curl -X POST -H 'Content-type: application/json' --data "{\"content\": \"灌 ${NUM_LAWS} 筆資料完成\"}" https://discord.com/api/webhooks/1279669331235704893/1Y447iPwiipRWgo4BrOWr65tEHSu3WebYyOyLSNlerBpey1L2RHqrGMU0r-qHeLkAf2g

if [ $? -ne 0 ]; then
    echo "Warning: Discord notification failed."
fi

echo "--- Automation script finished ---"
